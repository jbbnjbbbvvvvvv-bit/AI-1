"""Geometric behavior tests for warm-colour planar ornament tracing."""
from pathlib import Path
import os
import sys
import tempfile
import unittest
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]/'scripts'))

import trace_coloured_ornament_panels as m

EXTRA_VENDORS = [Path(p) for p in os.environ.get('HERITAGE_CAD_VENDOR_PATHS','').split(os.pathsep) if p]
m.dependencies(EXTRA_VENDORS)


class TraceTests(unittest.TestCase):
    def config(self, h=80, w=80):
        return dict(rows=[[0,h]],columns=[[0,w]],red_chroma_min=10.0,gaussian_sigma_px=.4,geometry_tolerance_px=.32,curve_panels=['R1C1'])

    def test_double_boundaries_preserve_known_strip_width(self):
        a=np.full((80,80,3),255,np.uint8)
        a[10:70,10:70]=[120,50,50]
        a[16:64,16:64]=255
        records,_=m.segment_panels(a,self.config())
        self.assertEqual(len(records),2)
        bounds=sorted([np.min(r['nodes'][:,0]) for r in records])
        self.assertAlmostEqual(bounds[1]-bounds[0],6.0,delta=.65)
        self.assertTrue(all(r['closed'] for r in records))

    def test_cropped_region_remains_open(self):
        a=np.full((80,80,3),255,np.uint8)
        a[0:60,15:65]=[120,50,50]
        records,_=m.segment_panels(a,self.config())
        self.assertEqual(len(records),1)
        self.assertFalse(records[0]['closed'])
        self.assertLess(np.min(records[0]['nodes'][:,1]),.01)

    def test_known_widths_at_different_foreground_brightness(self):
        for width in (3,6,12):
            for colour in ([120,50,50],[180,90,60],[90,35,20]):
                with self.subTest(width=width,colour=colour):
                    a=np.full((80,80,3),245,np.uint8)
                    a[10:70,10:70]=colour
                    a[10+width:70-width,10+width:70-width]=245
                    records,_=m.segment_panels(a,self.config())
                    self.assertEqual(len(records),2)
                    bounds=sorted(np.min(r['nodes'][:,0]) for r in records)
                    self.assertAlmostEqual(bounds[1]-bounds[0],width,delta=.65)

    def test_no_supported_foreground_is_explicitly_refused(self):
        a=np.full((80,80,3),245,np.uint8)
        with self.assertRaises(ValueError):
            m.segment_panels(a,self.config())

    def test_tiny_closed_hole_is_never_silently_collapsed(self):
        points=np.array([[0.,0.],[.08,.04],[.1,.1],[.03,.07],[0.,0.]])
        result=m.fit_path(points,.32,True)
        self.assertIsNotNone(result)
        nodes,bulges,closed=result
        self.assertTrue(closed)
        self.assertGreaterEqual(len(nodes),3)
        self.assertGreater(abs(m.cv2.contourArea(nodes.astype(np.float32))),0)

    def test_straight_rectangle_keeps_corners(self):
        points=np.array([[0,0],[10,0],[10,10],[0,10],[0,0]],float)
        nodes,bulges,closed=m.fit_path(points,.32,True)
        self.assertTrue(closed)
        self.assertEqual(len(nodes),4)
        self.assertTrue(np.all(bulges==0))

    def test_true_circle_arc_is_native_and_bounded(self):
        t=np.linspace(0,np.pi*.7,60)
        points=np.column_stack([20*np.cos(t),20*np.sin(t)])
        nodes,bulges,closed=m.fit_path(points,.32,True)
        self.assertFalse(closed)
        self.assertGreater(np.count_nonzero(bulges),0)
        result=m.error_stats(m.dense(points),m.sample_polyline(nodes,bulges,closed))
        self.assertLess(result['max'],.36)

    def test_sharp_pattern_is_not_replaced_by_circle(self):
        points=np.array([[0,0],[10,0],[10,5],[20,5],[20,15]],float)
        nodes,bulges,_=m.fit_path(points,.32,True)
        self.assertTrue(np.all(bulges==0))
        np.testing.assert_allclose(nodes,points)

    def test_no_material_added_in_neutral_white_region(self):
        a=np.full((80,80,3),245,np.uint8)
        # Red foreground only in one small rectangle.
        a[20:40,20:40]=[120,50,50]
        records,_=m.segment_panels(a,self.config())
        self.assertEqual(len(records),1)
        self.assertTrue(all(np.all(r['nodes']>=19) and np.all(r['nodes']<=40) for r in records))

    def test_native_roundtrip_preserves_geometry_and_mirror_sign(self):
        t=np.linspace(0,np.pi*.7,50)
        points=np.column_stack([20*np.cos(t)+30,20*np.sin(t)+30])
        nodes,bulges,closed=m.fit_path(points,.32,True)
        r=dict(panel='R1C1',nodes=nodes,bulges=bulges,closed=closed,layer='A-PATTERN')
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'test.dxf'
            m.make_dxf([r],[dict(panel='R1C1',x0=0,y1=80)],path)
            doc,geometry=m.read_geometry(path)
            np.testing.assert_allclose(geometry[0]['nodes'],nodes,atol=1e-10)
            np.testing.assert_allclose(geometry[0]['bulges'],bulges,atol=1e-12)
            self.assertEqual(len(doc.modelspace().query('IMAGE')),0)
            self.assertEqual(len(doc.audit().errors),0)

    def test_signature_detects_reversed_duplicate(self):
        nodes=np.array([[0,0],[10,0],[10,10]],float)
        a=dict(nodes=nodes,bulges=np.zeros(3),closed=True)
        b=dict(nodes=nodes[::-1],bulges=np.zeros(3),closed=True)
        self.assertEqual(m.geometry_signature(a),m.geometry_signature(b))


if __name__=='__main__':
    unittest.main()
