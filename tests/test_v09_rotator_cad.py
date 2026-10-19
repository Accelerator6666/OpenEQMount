import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v09_rotator as m

def test_rot_optical_axis_perpendicular_to_dec_axis():
    # In upper mechanical coordinates DEC = +X; ROT optical axis rotates in YZ.
    bb=m.local_to_dec(m.ring(80,60,4),0).val().BoundingBox()
    assert bb.xlen==pytest.approx(80,abs=1e-5)
    assert bb.ylen==pytest.approx(80,abs=1e-5)
    assert bb.zlen==pytest.approx(4,abs=1e-5)
    pivoted=m.local_to_dec(m.ring(80,60,4),25).val().BoundingBox()
    assert pivoted.xlen==pytest.approx(80,abs=1e-5)
    assert pivoted.zlen>4

def test_metal_load_envelope_not_printed():
    assert len(m.metal_components())==4
    assert all('METAL' not in p for p in m.printable_components())

def test_dfam_print_geometry():
    for name,shape in m.printable_components().items():
        bb=shape.val().BoundingBox()
        assert len(shape.solids().vals())==1 and shape.val().Volume()>100
        assert abs(bb.zmin)<1e-6
        assert max(bb.xlen,bb.ylen)<220
        record=m.print_record(name,shape)
        assert record['status']=='prototype_unqualified'
        assert record['field_load_approved'] is False

def test_rotator_travel_bounded():
    assert m.ROT_SOFT_MIN==-160 and m.ROT_SOFT_MAX==160

def test_ratio_is_not_mechanical_truth():
    assert m.GT2_BIG_TEETH/m.GT2_MOTOR_TEETH==9
    assert m.pitch_diameter(m.GT2_BIG_TEETH)==pytest.approx(360/3.141592653589793)

def test_printed_parts_are_metadata_unqualified():
    for name,part in m.printable_components().items():
        d=m.print_record(name,part)
        assert d['field_load_approved'] is False
        assert d['slicer_gate_B']=='pending'
        assert d['physical_gate_C']=='pending'
