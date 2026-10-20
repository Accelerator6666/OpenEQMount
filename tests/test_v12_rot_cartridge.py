"""Digital checks only: bore pass-through and numerical stop contact, not strength approval."""
from pathlib import Path
import sys,math,inspect
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import cadquery as cq
import pytest
import generate_v12_rot_cartridge as v


def test_through_bore_allows_bearing_axial_assembly():
    h=v.split_cartridge_housing()
    # 52mm bearing envelope does not collide along the WHOLE insertion shaft.
    cyl=cq.Workplane('XY').circle(26).extrude(70).translate((0,0,-8))
    assert h.intersect(cyl).val().Volume()<1.e-3
    assert v.BORE_DIAMETER_REFERENCE>=52
    assert len(h.solids().vals())==1


def test_two_bearings_and_outer_spacer_sequence():
    assert v.BEARING_Z==(7.,37.)
    assert v.OUTER_SPACER_Z==((0.,7.),(14.,37.),(44.,54.))
    assert v.BEARING_WIDTH==7
    assert abs((37-7)-30)<1e-12


def test_outer_cap_fastener_pattern_matches_housing():
    h=v.split_cartridge_housing()
    cap=v.outer_retaining_cap(54)
    for i in range(4):
        a=math.radians(45+i*90); x,y=45*math.cos(a),45*math.sin(a)
        probe=cq.Workplane('XY').center(x,y).circle(2).extrude(58)
        assert h.intersect(probe).val().Volume()<1e-3
        assert cap.intersect(probe).val().Volume()<1e-3


def test_positive_contact_beyond_soft_reference_and_clear_within():
    for a in (-150, -90, 0,90,150):assert v.stop_contact_volume(a)<1e-5
    assert v.stop_contact_volume(-160)>100
    assert v.stop_contact_volume(160)>100
    assert abs(v.stop_contact_volume(-160)-v.stop_contact_volume(160))<1e-5


def test_stop_dog_and_anchor_are_metal_reference_not_print_stl():
    assert v.rotating_stop_dog(0).val().BoundingBox().xmax>75
    assert v.fixed_tether_anchor().val().Volume()>100
    assert v.moving_tether_anchor(0).val().Volume()>100
    assert all('METAL_' in n for n in v.metal_parts())


def test_thin_spacer_is_reference_only_not_a_qualified_bearing_stack():
    s=v.inner_ring_spacer_reference()
    b=s.val().BoundingBox()
    assert abs(b.zlen-23)<1e-5
    assert abs(b.xlen-42)<1e-5
    assert 'inner_ring_positive_retention_qualified=False' in inspect.getsource(v.export)


def test_loose_coupons_bed_flat_and_nonstructural():
    p=v.nonload_coupons();assert len(p)==2
    for name,s in p.items():
        b=s.val().BoundingBox()
        assert 'NONLOAD_' in name
        assert abs(b.zmin)<1e-6 and b.zlen<=5
        assert max(b.xlen,b.ylen)<=220


def test_new_parts_carry_through_existing_v11_three_axis_view():
    rec=v.part_records(35,25,0)
    names=[p['name'] for p in rec]
    assert len(names)==len(set(names))
    assert len(rec)>53
    assert 'v10_METAL_STATOR_DUAL_6808_SEATS_PROPOSAL' not in names
    assert 'v12_METAL_SERVICEABLE_THROUGH_BORE_STATOR_PROPOSAL' in names
    assert any('DEC_OUTPUT_TO_ROT' in n for n in names)


def test_out_of_range_rejected_without_export(tmp_path):
    with pytest.raises(ValueError):v.export(tmp_path,latitude=24)
    with pytest.raises(ValueError):v.export(tmp_path,dec_preview=70)
    with pytest.raises(ValueError):v.export(tmp_path,rot_preview=155)


def test_guarded_pending_flags_present():
    s=inspect.getsource(v.export)
    for q in ('safe_to_energize=False','fall_arrest_complete=False','payload_approved=False',
              'stop_strength_qualified=False','bearing_preload_defined=False',"Gate_C='pending'"):
        assert q in s
