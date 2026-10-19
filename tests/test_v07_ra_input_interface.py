"""V0.7 non-rated CAD and belt ratio tests; physical load qualification excluded."""
import math
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v07 as v
import generate_v06 as previous


def test_stationary_ra_is_independent_of_rotating_output():
    assert len(v.wedge_holes()) == 4
    assert v.RA_REDUCER_HEIGHT == 45
    assert v.REAR_PCD_RA == 71
    assert len(v.circle_points(v.REAR_PCD_RA,6,v.REDUCER_PHASE_DEG)) == 6
    for x,y in v.wedge_holes():
        assert not (x == 45 and abs(y) == 45)  # V0.6 upper lock bolts reserved


def test_wedge_replacement_deck_has_new_through_bores():
    deck = v.upgraded_wedge_top_local()
    for p in v.wedge_holes():
        b=v.hole_xy([p],5,24,30)
        assert deck.intersect(b).val().Volume()<0.001
    # Old upper M6 hole locations are unchanged, not cannibalized.
    for x in (-43,45):
        for y in (-45,45):
            b=v.hole_xy([(x,y)],5,24,30)
            assert deck.intersect(b).val().Volume()<0.001


def test_ra_stator_stack_and_reducer_no_bore_violations():
    stack = [v.ra_wedge_interface_plate_local(), v.ra_fixed_stator_flange_local()]
    for i, part in enumerate(stack):
        for x,y in v.wedge_holes():
            tool=v.hole_xy([(x,y)],4.5,[v.BASE_Z0,v.RA_FLANGE_Z0][i]-1,
                                [v.BASE_Z1,v.RA_FLANGE_Z1][i]+1)
            assert part.intersect(tool).val().Volume()<.001
        assert len(part.solids().vals()) == 1
    ring=v.ra_fixed_stator_flange_local()
    for x,y in v.circle_points(v.REAR_PCD_RA,6,v.REDUCER_PHASE_DEG):
        tool=v.hole_xy([(x,y)],3.7,v.RA_FLANGE_Z0-1,v.RA_FLANGE_Z1+1)
        assert ring.intersect(tool).val().Volume()<.001
    assert v.RA_FLANGE_Z0 == v.RISER_Z1
    assert v.RA_FLANGE_Z1 == 93


def test_v06_upper_lock_lugs_and_new_posts_do_not_intersect():
    # All calculations are in V0.5 local coordinates before the common rotation.
    for side in (-1,1):
        lug = previous.lock_upper_lug(side,35)
        for x,y in v.wedge_holes():
            post=v.v05.pivot_rotate(v.ra_lower_post_local(x,y),55)
            assert post.intersect(lug).val().Volume()<.001, (side,x,y)
        top=v.v05.pivot_rotate(v.ra_wedge_interface_plate_local(),55)
        assert top.intersect(lug).val().Volume()<.001


def test_ra_axis_angle_stays_aligned_to_geographic_latitude():
    for lat in (25,35,45):
        p=v.v05.tilted_point((0,0,93),lat)
        q=v.v05.tilted_point((0,0,138),lat)
        dx,dz=q[0]-p[0],q[2]-p[2]
        # Tilted local +Z becomes south? Nominal RA altitude = latitude.
        assert math.isclose(math.degrees(math.atan2(dz,abs(dx))),lat,abs_tol=1e-9)
    with pytest.raises(ValueError):v.ra_interface_metal(50)


def test_belt_ratio_pitch_and_tension_range():
    assert v.PULLEY_TEETH==(60,20)
    assert (v.PULLEY_TEETH[0]/v.PULLEY_TEETH[1])*100 == 300
    assert math.isclose(v.belt_pitch_diameter(60),120/math.pi)
    vals=[v.belt_pitch_length(c) for c in (110,115,120)]
    assert vals == sorted(vals)
    assert 300<vals[0]<310
    assert 310<vals[1]<315
    assert 320<vals[2]<325
    with pytest.raises(ValueError):v.belt_pitch_length(0)


def test_motor_four_slots_allow_full_10mm_adjustment():
    for axis in ('ra','dec'):
        plate=v.belt_cassette_metal(axis)
        for travel in (-5,0,5):
            for p in v.motor_screw_centers(v.MOTOR_CENTER_NOMINAL+travel):
                probe=v.hole_xy([p],2.8,-1,8)
                assert plate.intersect(probe).val().Volume()<.001,(axis,travel,p)
        for p in v.circle_points(92,4,45):
            probe=v.hole_xy([p],4.6,-1,8)
            assert plate.intersect(probe).val().Volume()<.001


def test_printable_parts_and_safety_metadata_are_unqualified():
    parts=v.printable_covers()
    assert len(parts)==3
    for name,shape in parts.items():
        box=shape.val().BoundingBox()
        assert name.endswith('PRINT_FLAT')
        assert len(shape.solids().vals())==1
        assert box.zmin>=-1e-5 and box.zmax<10
        assert max(box.xlen,box.ylen)<220
        assert v.print_record(name,shape)['slicer_gate_B']=='pending'
        assert v.print_record(name,shape)['physical_gate_C']=='pending'
    assert v.STATUS=='prototype_unqualified_Gate_A_only'
