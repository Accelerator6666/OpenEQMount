"""V1.3 is layout verification only; physical loading remains forbidden."""
from pathlib import Path
import sys, math, json, inspect
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import cadquery as cq
import pytest
import generate_v13_rot_retention as v


def test_nominal_axial_stack_is_contiguous_not_a_preload_spec():
    assert v.validate_axial_stack()
    assert v.BEARING_INTERVALS==((7,14),(37,44))
    assert v.AXIAL_SPACER_INTERVAL==(14,37)
    assert v.LOCKNUT_REFERENCE_INTERVAL==(44,50)


def test_integral_shoulder_and_separate_thread_envelope():
    s=v.stepped_metal_spindle()
    assert len(s.solids().vals())==1
    for z,expected_d in ((-1,40),(5,45),(10,40),(48,38),(58,33.5)):
        # Radius of shell at each z as computed from the clipped CAD.
        probe=cq.Workplane('XY').box(200,200,0.01,centered=(True,True,False)).translate((0,0,z))
        section=s.intersect(probe)
        assert abs(section.val().BoundingBox().xlen-expected_d)<1.e-4,(z,expected_d)


def test_upper_nut_is_only_symbolic_not_a_finished_thread():
    s=v.symbolic_positive_locknut()
    assert s.val().BoundingBox().zmin==44.
    assert s.val().BoundingBox().zmax==50.
    assert 'UNMODELLED' in inspect.getsource(v.symbolic_positive_locknut)


def test_flange_pcd88_alignment_six_holes_and_candidate_clamp_two_holes():
    plate=v.vendor_camera_clamp_mating_plate()
    for x in (-30.,30.):
        c=cq.Workplane('XY').center(x,0).circle(3.05).extrude(9).translate((0,0,66.5))
        assert plate.intersect(c).val().Volume()<1.e-4
    for x,y in v.v10.points(88,6,30):
        c=cq.Workplane('XY').center(x,y).circle(2.05).extrude(9).translate((0,0,66.5))
        assert plate.intersect(c).val().Volume()<1.e-4


def test_camera_eye_is_unconnected_placeholder_not_safety_assembly():
    eye=v.unconnected_camera_cage_eye_envelope()
    assert eye.val().BoundingBox().ymax>90.
    assert 'NOT PART OF LOAD PATH' in inspect.getsource(v.unconnected_camera_cage_eye_envelope)


def test_tether_endpoint_sweep_is_numeric_not_wire_bend_approval():
    d=v.tether_clearance_reference()
    assert len(d)==11
    assert min(d.values())>40 and max(d.values())<200
    assert d['-90']>d['90'] # asymmetric original V1.2 anchor positioning


def test_print_coupons_single_flat_and_genuine_60mm_centre_separation():
    for n,s in v.nonload_gauges().items():
        bb=s.val().BoundingBox()
        assert 'NONLOAD_' in n and len(s.solids().vals())==1
        assert bb.zmin==0 and bb.zlen<=4 and max(bb.xlen,bb.ylen)<=220
    gauge=v.nonload_gauges()['v13_NONLOAD_CAMERA_TWO_M6_LOCATOR_GAUGE_PRINT_FLAT']
    assert gauge.val().BoundingBox().xlen==76
    for x in (-30,30):
        pr=cq.Workplane('XY').center(x,0).circle(3.1).extrude(4)
        assert gauge.intersect(pr).val().Volume()<1.e-4


def test_previous_overlapping_legacy_shaft_and_blank_are_replaced():
    r=v.assembly_records();n=[x['name'] for x in r]
    assert len(n)==66 and len(set(n))==66
    for old in ('v10_METAL_HOLLOW_ROT_SPINDLE_PROPOSAL','v10_METAL_INDEPENDENT_CAPTURE_COLLAR_PROPOSAL',
                'v11_CAMERA_MATING_FLANGE_METAL_BLANK_NO_LENS_CLAMP','v12_METAL_INNER_RING_SPACER_NARROW_REFERENCE'):
        assert old not in n
    assert any('INTEGRAL_SHOULDER_STEPPED_SPINDLE' in s for s in n)
    assert any('DEC_OUTPUT_TO_ROT' in s for s in n)


def test_all_out_of_envelope_positions_rejected(tmp_path):
    for kw in ({'latitude':24},{'latitude':46},{'dec_preview':66},{'rot_preview':151}):
        with pytest.raises(ValueError):v.export(tmp_path,**kw)


def test_export_flags_do_not_allow_manufacturing_or_field_use(tmp_path):
    data=v.export(tmp_path)
    assert data['parts_in_assembly']==66
    assert data['bearing_axial_stack_geometry_consistent'] is True
    for k in ('positive_locking_qualified','camera_clamp_attached','fall_arrest_complete',
              'independent_camera_eye_attached','bearing_preload_defined','payload_approved',
              'safe_to_energize','full_RA_DEC_ROT_collision_proved','tether_path_cleared_for_collision'):
        assert data[k] is False
    assert data['Gate_B']==data['Gate_C']=='pending'
    assert (tmp_path/data['assembled_step']).stat().st_size>200000
