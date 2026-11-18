"""Source-preserving colour-panel boundaries -> native editable DXF.

No inpainting, mirrored templates, corner completion or centreline thinning.
Coordinates remain image units. This is not a generic photo rectification tool.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, distance_transform_edt
from scipy.spatial import cKDTree
import contourpy


def dependencies(vendors):
    for vendor in vendors:
        sys.path.append(str(Path(vendor).resolve()))
    global cv2, ezdxf
    import cv2
    import ezdxf


def edge_midpoint(rgb, threshold, chroma_min=10.0):
    a = rgb.astype(float)
    gray = a @ np.array([0.299, 0.587, 0.114])
    red = a[:, :, 0] - np.maximum(a[:, :, 1], a[:, :, 2])
    fg = gray[(gray <= threshold+1.0) & (red > chroma_min)]
    bg = gray[(gray > threshold) & (red < chroma_min)]
    if len(fg) == 0 or len(bg) == 0:
        raise ValueError('Expected separated warm-colour material and neutral light background')
    # Otsu separates classes; it is not a calibrated subpixel edge level.
    # Using its low class endpoint directly can shrink a thin material strip.
    return (float(np.median(fg)) + float(np.median(bg))) / 2


def colour_field(rgb, threshold, chroma_min=10.0, sigma=0.4):
    a = rgb.astype(float)
    gray = a @ np.array([0.299, 0.587, 0.114])
    red = a[:, :, 0] - np.maximum(a[:, :, 1], a[:, :, 2])
    midpoint = edge_midpoint(rgb, threshold, chroma_min)
    field = np.minimum(midpoint - gray, 3.0 * (red - chroma_min))
    return gaussian_filter(field, sigma=sigma, mode='nearest') if sigma else field


def dense(points, step=.15):
    pieces = []
    for a, b in zip(points[:-1], points[1:]):
        count = max(1, int(np.ceil(np.linalg.norm(b-a) / step)))
        pieces.append(a + (b-a) * np.arange(count)[:, None] / count)
    return np.vstack(pieces + [np.asarray(points[-1:])]) if pieces else points.copy()


def line_error(points):
    d = points[-1] - points[0]
    l2 = np.dot(d, d)
    if l2 < 1e-12:
        return float('inf')
    t = np.clip((points-points[0]) @ d / l2, 0, 1)
    return float(np.max(np.linalg.norm(points-points[0]-t[:, None]*d, axis=1)))


def circle_bulge(points, tolerance):
    if len(points) < 5:
        return None
    a, b = points[0], points[-1]
    chord = np.linalg.norm(b-a)
    if chord < .6:
        return None
    center0, *_ = np.linalg.lstsq(2*(points[1:]-a), np.sum(points[1:]**2, axis=1)-np.dot(a, a), rcond=None)
    normal = np.array([-(b-a)[1], (b-a)[0]]) / chord
    mid = (a+b) / 2
    center = mid + normal * np.dot(center0-mid, normal)
    radius = np.linalg.norm(a-center)
    if not .45 < radius < 1e5:
        return None
    if np.max(np.abs(np.linalg.norm(points-center, axis=1)-radius)) > tolerance:
        return None
    angle = np.unwrap(np.arctan2(points[:, 1]-center[1], points[:, 0]-center[0]))
    span = angle[-1] - angle[0]
    if not .025 < abs(span) < 3.05:
        return None
    if np.any(np.diff(angle)*np.sign(span) < -.015):
        return None
    if radius*(1-np.cos(span/2)) < .2:
        return None
    return float(np.tan(span/4))


def fit_path(points, tolerance=.32, allow_arcs=True):
    """Bounded local fitting, not architectural regularization."""
    original = np.asarray(points, float)
    closed = bool(np.linalg.norm(original[0]-original[-1]) < 1e-6)
    def retain_raw():
        # Even a subpixel closed opening must not disappear by simplification.
        base = original[:-1] if closed else original
        if len(base) >= (3 if closed else 2):
            return base.copy(), np.zeros(len(base)), closed
        return None
    if len(original) < 2:
        return None
    # Small pre-simplification only; later raw contour comparison is mandatory.
    reduced = cv2.approxPolyDP(original.astype(np.float32).reshape(-1, 1, 2), .065, closed).reshape(-1, 2).astype(float)
    if closed:
        reduced = np.vstack([reduced, reduced[0]])
    if len(reduced) < 2:
        return retain_raw()
    nodes, bulges = [reduced[0]], []
    i = 0
    fit_tol = max(.04, tolerance - .10)
    while i < len(reduced)-1:
        best, bulge, failures = i+1, 0.0, 0
        for j in range(i+2, min(len(reduced), i+65)):
            sample = reduced[i:j+1]
            value = 0.0 if line_error(sample) <= fit_tol else (circle_bulge(sample, fit_tol) if allow_arcs else None)
            if value is not None:
                best, bulge, failures = j, value, 0
            else:
                failures += 1
                if failures >= 4:
                    break
        bulges.append(bulge)
        nodes.append(reduced[best])
        i = best
    if closed:
        nodes = nodes[:-1]
    else:
        bulges.append(0.0)
    if len(nodes) < (3 if closed else 2):
        return retain_raw()
    return np.asarray(nodes), np.asarray(bulges), closed


def sample_polyline(nodes, bulges, closed, step=.15):
    paths = []
    count = len(nodes) if closed else len(nodes)-1
    for i in range(count):
        a, b = nodes[i], nodes[(i+1) % len(nodes)]
        bulge = bulges[i]
        chord = np.linalg.norm(b-a)
        if chord < 1e-9:
            continue
        if abs(bulge) < 1e-10:
            paths.append(dense(np.array([a, b]), step)[:-1])
        else:
            mid = (a+b)/2
            n = np.array([-(b-a)[1], (b-a)[0]])/chord
            center = mid+n*chord*(1-bulge**2)/(4*bulge)
            radius = np.linalg.norm(a-center)
            sweep = 4*np.arctan(bulge)
            start = np.arctan2(*(a-center)[::-1])
            number = max(2, int(np.ceil(abs(sweep)*radius/step)))
            angles = start+sweep*np.arange(number)/number
            paths.append(center+radius*np.column_stack([np.cos(angles), np.sin(angles)]))
    return np.vstack(paths+[nodes[:1] if closed else nodes[-1:]])


def error_stats(a, b):
    da = cKDTree(b).query(a)[0]
    db = cKDTree(a).query(b)[0]
    return {"mean": float(np.mean(np.r_[da, db])), "p95": float(np.percentile(np.r_[da, db], 95)), "max": float(max(da.max(), db.max()))}


def segment_panels(rgb, cfg):
    records, panel_info = [], []
    for r, (y0, y1) in enumerate(cfg['rows'], 1):
        for c, (x0, x1) in enumerate(cfg['columns'], 1):
            key = f'R{r}C{c}'
            tile = rgb[y0:y1, x0:x1]
            gray = cv2.cvtColor(tile, cv2.COLOR_RGB2GRAY)
            otsu, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            field = colour_field(tile, otsu, cfg['red_chroma_min'], cfg['gaussian_sigma_px'])
            contours = contourpy.contour_generator(z=field, line_type='Separate').lines(0)
            panel_records = []
            for raw in contours:
                raw = raw + [x0, y0]
                fitted = fit_path(raw, cfg['geometry_tolerance_px'], key in cfg['curve_panels'])
                if fitted is None:
                    continue
                nodes, bulges, closed = fitted
                sample = sample_polyline(nodes, bulges, closed)
                err = error_stats(dense(raw), sample)
                # A difficult fit falls back to bounded polyline geometry only.
                if err['max'] > .60:
                    fitted = fit_path(raw, .16, False)
                    if fitted is None:
                        continue
                    nodes, bulges, closed = fitted
                    sample = sample_polyline(nodes, bulges, closed)
                    err = error_stats(dense(raw), sample)
                area = abs(cv2.contourArea(sample.astype(np.float32))) if closed else 0.0
                length = float(np.linalg.norm(np.diff(sample, axis=0), axis=1).sum())
                uncertain = length < 2.0 or (closed and area < 1.2)
                span = np.ptp(nodes, axis=0)
                layer = 'A-CHECK' if uncertain else ('A-FRAME' if span[0] > .85*(x1-x0) and span[1] > .85*(y1-y0) else 'A-PATTERN')
                rec = dict(panel=key, raw=raw, nodes=nodes, bulges=bulges, closed=closed, layer=layer, area=area, length=length, error=err)
                records.append(rec)
                panel_records.append(rec)
            panel_info.append(dict(panel=key, row=r, column=c, x0=x0, x1=x1, y0=y0, y1=y1, otsu=float(otsu), source_contours=len(contours), contour_count=len(panel_records), closed=sum(p['closed'] for p in panel_records), open=sum(not p['closed'] for p in panel_records), raw_vertices=sum(len(p['raw']) for p in panel_records), fitted_vertices=sum(len(p['nodes']) for p in panel_records), arc_segments=sum(np.count_nonzero(p['bulges']) for p in panel_records), check_count=sum(p['layer']=='A-CHECK' for p in panel_records), max_deviation_px=max((p['error']['max'] for p in panel_records), default=0)))
    return records, panel_info


def make_dxf(records, panels, path):
    doc = ezdxf.new('R2010')
    doc.units = 0
    doc.header['$LWDISPLAY'] = True
    for name, width in [('A-FRAME',25),('A-PATTERN',13),('A-CHECK',13),('A-NOTE',13)]:
        doc.layers.new(name, dxfattribs={'color':7,'lineweight':width})
    for p in panels:
        block = doc.blocks.new('ORNAMENT_'+p['panel'])
        origin = np.array([p['x0'], -p['y1']])
        for rec in [rec for rec in records if rec['panel']==p['panel']]:
            # Coordinate orientation reversal also reverses signed arc bulges.
            xy = rec['nodes'] * [1,-1] - origin
            e = block.add_lwpolyline([(x,y,-b) for (x,y),b in zip(xy,rec['bulges'])],format='xyb',close=rec['closed'],dxfattribs={'layer':rec['layer']})
            rec['handle'] = e.dxf.handle
        doc.modelspace().add_blockref(block.name,tuple(origin),dxfattribs={'layer':'A-PATTERN'})
    doc.saveas(path)
    return doc


def read_geometry(path):
    doc = ezdxf.readfile(path)
    result=[]
    for insert in doc.modelspace().query('INSERT'):
        for e in insert.virtual_entities():
            if e.dxftype() != 'LWPOLYLINE':
                raise ValueError('Unexpected native entity')
            a = np.asarray(e.get_points('xyb'))
            nodes = a[:,:2]*[1,-1]
            bulges = -a[:,2]
            result.append(dict(nodes=nodes,bulges=bulges,closed=bool(e.closed),layer=e.dxf.layer))
    return doc,result


def geometry_signature(g):
    a=np.column_stack([g['nodes'],g['bulges']]).round(9)
    n=len(a)
    rev=a[::-1].copy()
    rev[:,2]=[-a[(n-2-i)%n,2] if g['closed'] or i<n-1 else 0 for i in range(n)]
    variants=[]
    for sequence in (a,rev):
        if g['closed']:
            k=min(range(n),key=lambda j:tuple(sequence[j]))
            sequence=np.roll(sequence,-k,axis=0)
        variants.append(tuple(map(tuple,sequence)))
    return (g['closed'],min(variants))


def render(geometry, filename, width, height, scale=4):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    paths=[sample_polyline(g['nodes'],g['bulges'],g['closed'],.12) for g in geometry]
    dpi=200
    fig=plt.figure(figsize=(width*scale/dpi,height*scale/dpi),dpi=dpi,facecolor='white')
    ax=fig.add_axes([0,0,1,1],facecolor='white')
    # Same stroke for paired boundaries; the material width is geometric.
    ax.add_collection(LineCollection(paths, colors='black', linewidths=.18*scale, antialiased=True))
    ax.set_xlim(-.5,width-.5);ax.set_ylim(height-.5,-.5);ax.set_aspect('equal');ax.axis('off')
    fig.savefig(filename,dpi=dpi,facecolor='white')
    plt.close(fig)


def analysis_image(rgb, geometry, records, outdir):
    """Diagnostic plots, never substitutes their raster into a CAD file."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    h,w=rgb.shape[:2]
    fig,axs=plt.subplots(1,3,figsize=(12,4.5),dpi=180)
    axs[0].imshow(rgb);axs[0].set_title('Original')
    for rec in records:
        axs[1].plot(rec['raw'][:,0],rec['raw'][:,1],color='#0064cc',lw=.35)
    for g in geometry:
        p=sample_polyline(g['nodes'],g['bulges'],g['closed'])
        axs[1].plot(p[:,0],p[:,1],color='#dd2a2a',lw=.25,alpha=.8)
        axs[2].plot(p[:,0],p[:,1],color='black',lw=.35)
    axs[1].set_title('Source boundaries blue / DXF red');axs[2].set_title('Editable DXF rendered')
    for ax in axs:
        ax.set_xlim(-.5,w-.5);ax.set_ylim(h-.5,-.5);ax.set_aspect('equal');ax.axis('off')
    fig.tight_layout();fig.savefig(outdir/'Ornaments_16_Comparison.png',facecolor='white');plt.close(fig)
    # All sixteen positions share the exact same image-coordinate transform.
    source_mask=np.zeros((h,w),np.uint8);cad_mask=np.zeros((h,w),np.uint8)
    for rec in records:
        cv2.polylines(source_mask,[np.rint(rec['raw']).astype(np.int32)],False,1,1)
    for g in geometry:
        p=sample_polyline(g['nodes'],g['bulges'],g['closed'])
        cv2.polylines(cad_mask,[np.rint(p).astype(np.int32)],False,1,1)
    to_cad=distance_transform_edt(cad_mask==0)
    to_source=distance_transform_edt(source_mask==0)
    heat=np.full((h,w),np.nan)
    heat[source_mask>0]=to_cad[source_mask>0]
    heat[cad_mask>0]=np.maximum(np.nan_to_num(heat[cad_mask>0]),to_source[cad_mask>0])
    fig,ax=plt.subplots(figsize=(7,8),dpi=170)
    im=ax.imshow(heat,cmap='inferno',vmin=0,vmax=2);ax.axis('off');fig.colorbar(im,ax=ax,label='Raster edge distance [px]')
    fig.tight_layout();fig.savefig(outdir/'Ornaments_16_Error_Map.png',facecolor='white');plt.close(fig)
    return source_mask


def run(args):
    cfg=json.loads(args.config.read_text(encoding='utf-8'))
    rgb=np.asarray(Image.open(args.input).convert('RGB'))
    h,w=rgb.shape[:2]
    for name in ('Ornaments_16_Editable.dxf','Ornaments_16_Audit.json'):
        if (args.output/name).exists():
            raise FileExistsError('Use a new output directory')
    before=hashlib.sha256(args.input.read_bytes()).hexdigest()
    records,panels=segment_panels(rgb,cfg)
    dxf=args.output/'Ornaments_16_Editable.dxf'
    make_dxf(records,panels,dxf)
    doc,readback=read_geometry(dxf)
    if len(readback)!=len(records):
        raise ValueError('Native geometry count changed')
    if sum(p['source_contours'] for p in panels) != len(records):
        raise ValueError('Source contour omitted; inspect before delivery')
    inverse_error=max(float(np.max(np.abs(a['nodes']-b['nodes']))) for a,b in zip(records,readback))
    bulge_error=max(float(np.max(np.abs(a['bulges']-b['bulges']))) for a,b in zip(records,readback))
    assert inverse_error<1e-9 and bulge_error<1e-12
    geometry_errors=[error_stats(dense(a['raw']),sample_polyline(b['nodes'],b['bulges'],b['closed'])) for a,b in zip(records,readback)]
    audit=doc.audit()
    render(readback,args.output/'Ornaments_16_Front_Lineart.png',w,h,4)
    render(readback,args.output/'Ornaments_16_CAD_Render.png',w,h,1)
    source_mask=analysis_image(rgb,readback,records,args.output)
    candidate={}
    candidate_path=args.output/'diagnostics/AI_Candidate_Not_For_CAD.png'
    if candidate_path.exists():
        a=np.asarray(Image.open(candidate_path).convert('L'))
        resized=cv2.resize(a,(w,h),interpolation=cv2.INTER_AREA)
        mask=resized<155
        d=distance_transform_edt(source_mask==0)[mask]
        candidate={'used_for_dxf':False,'reason':'Generated regular circular fixtures/completed borders and altered fine shapes; rejected after comparison.','mean_line_distance_to_source_px':float(d.mean()),'p95_line_distance_to_source_px':float(np.percentile(d,95)),'max_line_distance_to_source_px':float(d.max())}
    with (args.output/'Ornaments_16_Panels.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(panels[0]));writer.writeheader();writer.writerows(panels)
    with (args.output/'Ornaments_16_Check_Entities.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['panel','handle','layer','closed','area','length'];writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        writer.writerows({k:r[k] for k in fields} for r in records if r['layer']=='A-CHECK' or not r['closed'])
    after=hashlib.sha256(args.input.read_bytes()).hexdigest()
    result=dict(
        source_sha256=before, source_unchanged=before==after, pixel_size=[w,h],
        insunits=int(doc.header['$INSUNITS']), physical_scale_known=False,
        perspective=cfg['perspective_note'], model_inserts=len(doc.modelspace()),
        native_contours=len(records), native_type='LWPOLYLINE with native circular bulges where validated',
        source_contour_count=sum(p['source_contours'] for p in panels),
        duplicate_contours=len(readback)-len(set(geometry_signature(g) for g in readback)),
        raw_vertices=sum(len(r['raw']) for r in records), vertices=sum(len(r['nodes']) for r in records),
        arc_segments=sum(int(np.count_nonzero(r['bulges'])) for r in records),
        closed=sum(r['closed'] for r in records), open=sum(not r['closed'] for r in records),
        suspected_short_retained=sum(r['layer']=='A-CHECK' for r in records),
        max_source_contour_deviation_px=max(e['max'] for e in geometry_errors),
        mean_of_contour_mean_deviations_px=float(np.mean([e['mean'] for e in geometry_errors])),
        cad_roundtrip_coordinate_error_px=inverse_error, cad_roundtrip_bulge_error=bulge_error,
        dxf_errors=len(audit.errors), dxf_fixes=len(audit.fixes),
        raster_entities=len(doc.modelspace().query('IMAGE UNDERLAY OLE2FRAME')),
        candidate=candidate, panels=panels,
    )
    (args.output/'Ornaments_16_Audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('panels',)},ensure_ascii=False,indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--vendor',type=Path,action='append',default=[])
    args=p.parse_args();dependencies(args.vendor);args.output.mkdir(parents=True,exist_ok=True);run(args)


if __name__=='__main__':
    main()
