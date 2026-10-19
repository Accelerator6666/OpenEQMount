"""V0.4 digital geometry validation, NOT mechanical load certification."""
from __future__ import annotations
import math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v04 as v


def test_axis_geometry_and_oem_pattern():
    assert v.RA_OUTPUT_PCD==27
    assert v.DEC_REAR_PCD==65
    assert v.DEC_CENTER_Z==112
    for pcd in (v.RA_OUTPUT_PCD,v.DEC_REAR_PCD):
        pts=v.points_on_pcd(pcd,6,30)
        assert len(pts)==6
        assert all(math.isclose(math.hypot(x,y),pcd/2,abs_tol=1e-9) for x,y in pts)


def test_printable_parts_single_body_fit_bed():
    parts=v.printable_parts()
    assert len(parts)==5
    for name,part in parts.items():
        assert len(part.solids().vals())==1,name
        bb=part.val().BoundingBox()
        assert bb.zmin >= -1e-5
        assert bb.xlen<=220 and bb.ylen<=220
        assert part.val().Volume()>200


def test_printed_cheek_structural_bolt_heads_not_clamped():
    cover=v.side_shape(8,printed=True)
    metal=v.side_shape(5,printed=False)
    for x,z in v.SIDE_FASTENERS:
        # sample right through center axis; screw-head window in print must be open.
        sample=(v.cq.Workplane('XY').center(x,z).circle(4.9).extrude(10).translate((0,0,-1)))
        assert cover.intersect(sample).val().Volume()<1e-5,(x,z)
        # Metal rail has smaller M5 screw clearance, so Ø4.9 sample intersects.
        assert metal.intersect(sample).val().Volume()>1,(x,z)


def test_metal_parts_single_solid_and_accessible_cut_patterns():
    p=v.metal_parts()
    assert len(p)==8
    for name,part in p.items():
        assert len(part.solids().vals())==1,name
        assert part.val().Volume()>500,name
    ra=p['v04_ra_output_plate_METAL']
    for x in (-43,45):
        for y in (-45,45):
            pin=v.cq.Workplane('XY').center(x,y).circle(2).extrude(7).translate((0,0,-1))
            assert ra.intersect(pin).val().Volume()<1e-4
    dec=p['v04_dec_rear_plate_METAL']
    for y in (-45,45):
        for z in (65,127):
            pin=v.cq.Workplane('YZ').center(y,z).circle(2).extrude(8).translate((110,0,0))
            assert dec.intersect(pin).val().Volume()<1e-4


def test_design_has_metal_primary_path_and_unqualified_state():
    m=v.export(Path('/tmp/oeq-v04-test'))
    assert m['status']=='prototype_unqualified_Gate_A_only'
    assert len(m['metal_parts'])==8
    assert all(r['physical_gate_C']=='pending' for r in m['printed_parts'])
    assert all('metal' in r['load_path'] for r in m['printed_parts'])


def test_no_hard_interference_among_distinct_metal_subassemblies():
    parts=list(v.metal_parts().items())
    for i,(a_name,a_part) in enumerate(parts):
        for b_name,b_part in parts[i+1:]:
            assert a_part.intersect(b_part).val().Volume() < 1e-4,(a_name,b_name)


def test_side_cover_is_not_clamped_between_primary_metal_rails_and_cleats():
    metal=v.metal_parts()
    for positive in (False,True):
        cover=v.in_global_side(v.side_shape(8,True),positive,True)
        rail=metal['v04_right_side_web_METAL' if positive else 'v04_left_side_web_METAL']
        assert cover.intersect(rail).val().Volume() < 1e-4
        for kind in ('ra_angle','dec_angle'):
            name=('v04_right_' if positive else 'v04_left_')+kind+'_METAL'
            assert cover.intersect(metal[name]).val().Volume() < 1e-4
