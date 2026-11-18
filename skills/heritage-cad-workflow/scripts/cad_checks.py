"""Read-only DXF checks adapted from the native-transfer verification workflows."""
import argparse
from collections import Counter
import hashlib
import importlib
import json
from pathlib import Path
import sys


def load_ezdxf(library=None):
    if library:
        # Prefer this interpreter's binary dependencies over unrelated vendored
        # numpy/scipy wheels that may have been built for another Python ABI.
        sys.path.append(str(Path(library).resolve()))
    return importlib.import_module('ezdxf')


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def tags(entity,layer=None,identity=False):
    from ezdxf.lldxf.tagwriter import TagCollector
    ignored=set() if identity else {5,330,67}
    return tuple((t.code,layer if t.code==8 and layer is not None else t.value)
                 for t in TagCollector.dxftags(entity) if t.code not in ignored)


def inspect(path,body_layers=()):
    import ezdxf
    from ezdxf import bbox
    doc=ezdxf.readfile(path)
    model=list(doc.modelspace())
    body=[e for e in model if e.dxf.layer in body_layers]
    box=bbox.extents(body) if body else None
    # This detects equal native definitions, including layer/style. Geometric
    # equivalence under reversed paths and partial overlap requires other checks.
    keys=Counter(tags(e) for e in model)
    result={'path':str(Path(path).resolve()),'sha256':digest(path),
            'version':doc.dxfversion,'insunits':doc.units,'model_count':len(model),
            'types':dict(Counter(e.dxftype() for e in model)),
            'layers':dict(Counter(e.dxf.layer for e in model)),
            'same_definition_excess':sum(n-1 for n in keys.values() if n>1),
            'body_bounds':{'min':list(box.extmin),'max':list(box.extmax)} if box and box.has_data else None,
            'viewports':[],
            'not_checked':['partial_overlap','short_line_meaning','self_intersection',
                           'curve_continuity','ornament_semantics','raster_correspondence']}
    for layout in doc.layouts:
        if layout.name=='Model':
            continue
        for viewport in layout.query('VIEWPORT'):
            if viewport.dxf.id<=1:
                continue
            result['viewports'].append({'layout':layout.name,'handle':viewport.dxf.handle,
                'scale':viewport.get_scale(),'status':viewport.dxf.status,
                'frozen_layers':viewport.frozen_layers})
    audit=doc.audit()
    result['audit_errors']=len(audit.errors)
    result['audit_fixes_in_memory']=len(audit.fixes)
    return result


def retained_objects(before,after):
    """Compare all original native model, block, layer and layout definitions."""
    for entity in before.modelspace():
        if tags(entity,identity=True)!=tags(after.entitydb[entity.dxf.handle],identity=True):
            raise ValueError(f'Original entity changed: {entity.dxf.handle}')
    for old in before.blocks:
        new=after.blocks[old.name]
        old_items=list(old)
        new_items=list(new)
        if old.name.lower()=='*model_space':
            new_items=new_items[:len(old_items)]
        if [tags(e,identity=True) for e in old_items]!=[tags(e,identity=True) for e in new_items]:
            raise ValueError(f'Original block changed: {old.name}')
        for a,b in ((old.block,new.block),(old.endblk,new.endblk),(old.block_record,new.block_record)):
            if tags(a,identity=True)!=tags(b,identity=True):
                raise ValueError(f'Original block metadata changed: {old.name}')
    for old in before.layers:
        if tags(old,identity=True)!=tags(after.layers.get(old.dxf.name),identity=True):
            raise ValueError(f'Original layer changed: {old.dxf.name}')
    resource_counts={}
    for resource in ('styles','linetypes','dimstyles'):
        original_table=getattr(before,resource)
        current_table=getattr(after,resource)
        for old in original_table:
            if tags(old,identity=True)!=tags(current_table.get(old.dxf.name),identity=True):
                raise ValueError(f'Original {resource} resource changed: {old.dxf.name}')
        resource_counts[resource]=len(original_table)
    for old in before.layouts:
        if tags(old.dxf_layout,identity=True)!=tags(after.layout(old.name).dxf_layout,identity=True):
            raise ValueError(f'Original layout changed: {old.name}')
    return {'original_model_entities':len(before.modelspace()),'original_blocks':len(before.blocks),
            'original_layers':len(before.layers),'original_layouts':len(before.layouts),
            'original_resource_tables':resource_counts}


def definition_points(entity):
    import numpy as np
    kind=entity.dxftype()
    if kind=='LINE':
        return np.array([entity.dxf.start,entity.dxf.end])
    if kind=='LWPOLYLINE':
        return np.array(list(entity.vertices_in_wcs()))
    if kind=='SPLINE':
        return np.concatenate([np.asarray(entity.control_points).reshape(-1,3),
                               np.asarray(entity.fit_points).reshape(-1,3)])
    if kind in ('CIRCLE','ARC'):
        return np.array([entity.dxf.center])
    raise ValueError(f'Inverse comparison unsupported type: {kind}')


def verify_native(source,result,block_name,exclude=(),layer_map=None,handle_layer_map=None,tolerance=1e-8):
    """Check copied definitions first, then the inverse of the actual INSERT matrix."""
    import numpy as np
    from ezdxf.disassemble import recursive_decompose
    layer_map=layer_map or {}
    handle_layer_map=handle_layer_map or {}
    selected=[e for e in source.modelspace() if e.dxf.handle not in exclude]
    root=result.blocks[block_name]
    if len(selected)!=len(root):
        raise ValueError(f'Copy count differs: source {len(selected)}, block {len(root)}')
    for old,new in zip(selected,root):
        layer=handle_layer_map.get(old.dxf.handle,layer_map.get(old.dxf.layer,old.dxf.layer))
        if tags(old,layer)!=tags(new):
            raise ValueError(f'Copied native definition differs: source {old.dxf.handle}')
    references=[e for e in result.modelspace().query('INSERT') if e.dxf.name==block_name]
    if len(references)!=1:
        raise ValueError(f'Expected one model reference, got {len(references)}')
    ref=references[0]
    matrix=ref.matrix44()
    axes=np.array([matrix.transform_direction(v) for v in ((1,0,0),(0,1,0),(0,0,1))])
    sizes=np.linalg.norm(axes,axis=1)
    if min(sizes)<=0 or not np.allclose(sizes[:2],sizes[0],rtol=0,atol=tolerance):
        raise ValueError('Non-uniform or zero XY scale')
    if abs(np.dot(axes[0],axes[1]))>tolerance*max(1.,sizes[0]*sizes[1]):
        raise ValueError('Skewed XY transform')
    inverse=matrix.copy()
    inverse.inverse()
    expected=list(recursive_decompose(selected))
    actual=list(recursive_decompose([ref]))
    if len(expected)!=len(actual):
        raise ValueError('Expanded entity count differs')
    # Nested source definitions must remain native. Renamed dependencies require
    # an explicit extension of this comparison, rather than ignoring them.
    names={e.dxf.name for e in selected if e.dxftype()=='INSERT'}
    seen=set()
    while names:
        name=names.pop()
        if name in seen:
            continue
        seen.add(name)
        old,new=source.blocks[name],result.blocks[name]
        if old.block.dxf.base_point!=new.block.dxf.base_point or [tags(e) for e in old]!=[tags(e) for e in new]:
            raise ValueError(f'Nested block changed: {name}')
        names.update(e.dxf.name for e in old if e.dxftype()=='INSERT')
    maximum=curve_maximum=0.
    for old,new in zip(expected,actual):
        if old.dxftype()!=new.dxftype():
            raise ValueError('Expanded entity type differs')
        lhs=definition_points(old)
        rhs=np.array(list(inverse.transform_vertices(definition_points(new))))
        maximum=max(maximum,float(np.linalg.norm(lhs-rhs,axis=1).max()))
        if old.dxftype() in ('CIRCLE','ARC'):
            maximum=max(maximum,abs(old.dxf.radius-new.dxf.radius/sizes[0]))
        if old.dxftype()=='SPLINE':
            a,b=old.construction_tool(),new.construction_tool()
            u=np.linspace(0,a.max_t,71)
            lhs=np.array(list(a.points(u)))
            rhs=np.array(list(inverse.transform_vertices(b.points(u))))
            curve_maximum=max(curve_maximum,float(np.linalg.norm(lhs-rhs,axis=1).max()))
    if max(maximum,curve_maximum)>tolerance:
        raise ValueError(f'Inverse geometry mismatch: {max(maximum,curve_maximum)}')
    return {'copied_entities':len(selected),'expanded_entities':len(actual),'insert_handle':ref.dxf.handle,
            'scale_axes':sizes.tolist(),'mirrored':float(np.linalg.det(axes))<0,
            'max_definition_error_source_units':maximum,'max_spline_error_source_units':curve_maximum,
            'tolerance_source_units':tolerance,'nested_definitions_checked':sorted(seen)}


def record(doc,layout):
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy
    from ezdxf.addons.drawing.recorder import Recorder

    class ViewportFrontend(Frontend):
        def draw_entities_callback(self,ctx,entities):
            previous=self.ctx
            self.ctx=ctx
            try:
                super().draw_entities_callback(ctx,entities)
            finally:
                self.ctx=previous

    backend=Recorder()
    ViewportFrontend(RenderContext(doc),backend,
        config=Configuration(background_policy=BackgroundPolicy.WHITE)).draw_layout(layout)
    return backend.player()


def points(record):
    import numpy as np
    from ezdxf.addons.drawing.recorder import PointsRecord, SolidLinesRecord, PathRecord, FilledPathsRecord
    if isinstance(record,PointsRecord):
        return np.array(record.points.vertices())
    if isinstance(record,SolidLinesRecord):
        return np.array(record.lines.vertices())
    if isinstance(record,PathRecord):
        return np.array(record.path.control_vertices())
    if isinstance(record,FilledPathsRecord):
        return np.concatenate([np.array(p.control_vertices()) for p in record.paths])
    raise ValueError(f'Layout comparison unsupported record: {type(record).__name__}')


def verify_viewport(doc,layout_name,prefix,tolerance=5e-7):
    import numpy as np
    layout=doc.layout(layout_name)
    vps=[v for v in layout.query('VIEWPORT') if v.dxf.id>1 and v.dxf.status>0]
    if len(vps)!=1 or not vps[0].is_top_view:
        raise ValueError('This checker supports one active top-view viewport per layout')
    viewport=vps[0]
    model=record(doc,doc.modelspace())
    paper=record(doc,layout)
    frozen={name.lower() for name in viewport.frozen_layers}
    lhs=[(r,p) for r,p in model.recordings() if p.layer.startswith(prefix) and p.layer.lower() not in frozen]
    rhs=[(r,p) for r,p in paper.recordings() if p.layer.startswith(prefix)]
    if len(lhs)!=len(rhs) or not lhs:
        raise ValueError(f'Model/viewport record count differs or is empty: {len(lhs)}, {len(rhs)}')
    matrix=viewport.get_transformation_matrix()
    maximum=0.
    for (a,pa),(b,pb) in zip(lhs,rhs):
        if type(a)!=type(b) or pa.layer!=pb.layer or pa.handle!=pb.handle:
            raise ValueError('Model/viewport record identity differs')
        v=points(a)
        v=np.array(list(matrix.transform_vertices(np.column_stack((v,np.zeros(len(v)))))))[:,:2]
        w=points(b)
        if v.shape!=w.shape:
            raise ValueError('Viewport clipping or different path dimensions require regional comparison')
        maximum=max(maximum,float(np.linalg.norm(v-w,axis=1).max()))
    if maximum>tolerance:
        raise ValueError(f'Model/viewport error exceeds paper-unit tolerance: {maximum}')
    return {'layout':layout_name,'prefix':prefix,'viewport':viewport.dxf.handle,'scale':viewport.get_scale(),
            'records':len(lhs),'max_paper_error':maximum,'frozen_layers':viewport.frozen_layers,
            'paperspace_direct_inserts':len(layout.query('INSERT'))}


def run_spec(spec_path,project_root):
    import ezdxf
    spec=json.loads(Path(spec_path).read_text(encoding='utf-8'))
    root=Path(project_root)
    results=[]
    for case in spec['cases']:
        paths={k:(root/case[k]).resolve() for k in ('source','before','after')}
        initial={k:digest(p) for k,p in paths.items()}
        docs={k:ezdxf.readfile(p) for k,p in paths.items()}
        outcome={'case':case['name'],'input_sha256':initial}
        outcome['native']=verify_native(docs['source'],docs['after'],case['block'],
            exclude=case.get('exclude_source_handles',()),layer_map=case.get('layer_map'),
            handle_layer_map=case.get('handle_layer_map'))
        outcome['preserved']=retained_objects(docs['before'],docs['after'])
        outcome['viewports']=[verify_viewport(docs['after'],v['layout'],v['prefix'])
                              for v in case.get('viewports',())]
        outcome['readback_audits']={}
        for role,doc in docs.items():
            audit=doc.audit()
            outcome['readback_audits'][role]={'errors':len(audit.errors),'fixes_in_memory':len(audit.fixes)}
            if audit.errors or audit.fixes:
                raise ValueError(f'DXF structure requires review: {case["name"]}, {role}')
        final={k:digest(p) for k,p in paths.items()}
        if initial!=final:
            raise ValueError('Input files changed during verification')
        outcome['input_hashes_unchanged']=True
        outcome['status']='PASS_WITHIN_CHECKED_SCOPE'
        results.append(outcome)
    return {'cases':results,'cad_files_written':0}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ezdxf-path',type=Path)
    command=parser.add_subparsers(dest='command',required=True)
    info=command.add_parser('inspect')
    info.add_argument('dxf',type=Path)
    info.add_argument('--body-layer',action='append',default=[])
    info.add_argument('--report',type=Path)
    verify=command.add_parser('verify')
    verify.add_argument('spec',type=Path)
    verify.add_argument('--project-root',type=Path,default=Path.cwd())
    verify.add_argument('--report',type=Path)
    args=parser.parse_args()
    load_ezdxf(args.ezdxf_path)
    if args.command=='inspect':
        initial=digest(args.dxf)
        result=inspect(args.dxf,args.body_layer)
        if initial!=digest(args.dxf):
            raise ValueError('Input changed during read-only inspection')
    else:
        result=run_spec(args.spec,args.project_root)
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if args.report:
        with args.report.open('x',encoding='utf-8') as stream:
            stream.write(text+'\n')
    else:
        print(text)


if __name__=='__main__':
    main()
