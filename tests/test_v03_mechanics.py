"""Bench CAD validation only; no stress testing or metrology implied."""
from __future__ import annotations
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v03 as v


def test_oem_patterns_exact_counts():
    assert (v.RA.output_pcd,v.RA.output_thread,v.RA.rear_pcd)==(27.,'M5x10',71.)
    assert (v.DEC.output_pcd,v.DEC.output_thread,v.DEC.rear_pcd)==(23.,'M4x8',65.)
    for r in (v.RA,v.DEC):
        assert len(v.circle_points(r.output_pcd,6,90))==6
        assert all(math.isclose(math.hypot(x,y),r.output_pcd/2,abs_tol=1e-8)
                   for x,y in v.circle_points(r.output_pcd,6,90))


def test_positive_clearance_and_printability():
    for r in (v.RA,v.DEC):
        assert r.od+v.BODY_DIAMETRAL_CLEARANCE>r.od
        for shape in (v.housing(r),v.output_adapter(r),v.nema_motor_carrier(r),v.bearing_bridge(r)):
            assert len(shape.solids().vals())==1
            assert shape.val().Volume()>1000
            bb=shape.val().BoundingBox()
            assert max(bb.xlen,bb.ylen,bb.zlen)<220  # common 220x220 print bed


def test_no_hard_component_intersections():
    for r in (v.RA,v.DEC):
        items=[v.housing(r),v.output_adapter(r),v.nema_motor_carrier(r),v.bearing_bridge(r),v.reducer_envelope(r)]
        for i in range(len(items)):
            for j in range(i+1,len(items)):
                assert items[i].intersect(items[j]).val().Volume()<1e-4, (r.key,i,j)


def test_output_and_rear_holes_are_clear_at_expected_centres():
    for r in (v.RA,v.DEC):
        o=v.output_adapter(r); h=v.housing(r)
        # Check each OEM fastener axis is through-air at the screw location.
        for x,y in v.circle_points(r.output_pcd,6,90):
            sample=v.cylinder(1,1,r.length+0.5).translate((x,y,0))
            assert o.intersect(sample).val().Volume()<1e-4
        for x,y in v.circle_points(r.rear_pcd,6,v.BOLT_ORIENTATION_DEG):
            sample=v.cylinder(1,1,-4).translate((x,y,0))
            assert h.intersect(sample).val().Volume()<1e-4


def test_motor_slots_allow_31_mm_nominal_pattern():
    for r in (v.RA,v.DEC):
        m=v.nema_motor_carrier(r)
        for dx in [-15.5,15.5]:
            for dy in [-15.5,15.5]:
                for travel in [-5.,0.,5.]:
                    s=v.cylinder(1,1,-23).translate((85+dx+travel,dy,0))
                    assert m.intersect(s).val().Volume()<1e-4


def test_belt_length_provisional():
    R=60*2/(2*math.pi);r=20*2/(2*math.pi);C=85
    L=2*C+math.pi*(R+r)+(R-r)**2/C
    assert 250 < L < 254
