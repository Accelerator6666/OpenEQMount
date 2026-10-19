"""Digital bench validation only: does NOT certify bearing torque or retention."""
from pathlib import Path
import sys
import math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v10_rotator_bench as v


def test_paired_bearings_are_verified_dimensions_only():
    assert (v.BEARING_ID,v.BEARING_OD,v.BEARING_WIDTH)==(40.,52.,7.)
    assert v.BEARING_Z[1]-v.BEARING_Z[0]==30
    for z in v.BEARING_Z:
        assert 0<z<54-v.BEARING_WIDTH


def test_circular_bearing_pockets_occupy_the_reference_bearing_envelopes():
    housing=v.bearing_seat_housing()
    for z in v.BEARING_Z:
        envelope=v.ring(v.BEARING_OD,v.BEARING_ID,v.BEARING_WIDTH,z)
        # Hole is modeled as the nominal same-size seat; zero material overlap.
        assert housing.intersect(envelope).val().Volume()<0.01


def test_motor_clearance_avoids_stator_solid():
    stator=v.bearing_seat_housing()
    carrier=v.motor_carrier()
    assert len(carrier.solids().vals())==1
    assert carrier.intersect(stator).val().Volume()<0.001
    assert abs(v.MOTOR_CENTRE_X - 105.)<1e-7


def test_motor_slots_have_31_pitch_and_radial_adjustment():
    mount=v.motor_carrier()
    for x in (-15.5,15.5):
        for y in (-15.5,15.5):
            for travel in (-5.,0.,5.):
                cutter=(v.ring(3,1,2).translate((v.MOTOR_CENTRE_X+x+travel,y,15)))
                assert mount.intersect(cutter).val().Volume()<1e-4


def test_reference_belt_not_confused_with_real_teeth():
    assert v.DRIVE_TEETH/v.MOTOR_TEETH==4
    assert v.pitch_diameter(80)==80*2/math.pi
    assert 294<v.belt_estimated_length(100)<310
    assert v.SOFT_LIMIT_DEG<v.HARD_LIMIT_REFERENCE_DEG<180


def test_unequivocal_metal_load_path_only():
    assert len(v.metal_parts())==8
    assert all('NONLOAD_' in n for n in v.loose_print_parts())
    for name,sh in v.loose_print_parts().items():
        bb=sh.val().BoundingBox()
        assert len(sh.solids().vals())==1 and abs(bb.zmin)<1e-5 and max(bb.xlen,bb.ylen)<=220
        record=v.print_record(name,sh)
        assert record['field_load_approved'] is False
        assert record['slicer_gate_B']=='pending'
        assert record['physical_gate_C']=='pending'


def test_rotor_and_bearing_concentric_nominally():
    shaft=v.rotor_spindle().val().BoundingBox()
    assert shaft.xlen==v.BEARING_ID and shaft.ylen==v.BEARING_ID
    assert v.output_plate().val().BoundingBox().xlen==108
