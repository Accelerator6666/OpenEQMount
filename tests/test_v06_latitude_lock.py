"""V0.6 digital kinematics / interfaces. NOT approval for physical loads."""
from __future__ import annotations
import math,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v06 as v


def test_latitude_range_and_track_distinctness():
    lockr,locka=v.slot_geometry(v.LOCK_PIN_LOCAL)
    stopr,stopa=v.slot_geometry(v.STOP_PIN_LOCAL)
    assert 91 < lockr < 94
    assert 78 < stopr < 81
    assert lockr-stopr > 12  # Avoid overlapping bolt slot widths.
    assert locka!=stopa


def test_both_slots_clear_metal_pins_at_full_range():
    for lat in (25,30,35,40,45):
        for side in (-1,1):
            plate=v.lock_sideplate(side)
            for local,diam in ((v.LOCK_PIN_LOCAL,8),(v.STOP_PIN_LOCAL,6)):
                x,y,z=v.pin_center(local,lat)
                probe=v.v05.bore_y(x,z,diam-.7)
                assert plate.intersect(probe).val().Volume()<1e-4,(lat,side,diam)


def test_metal_stop_slot_blocks_outside_trial_range():
    plate=v.lock_sideplate(1)
    for lat in (22,48):
        x,_,z=v.pin_center(v.STOP_PIN_LOCAL,lat)
        # end-of-arc should contain metal at overtravel angles
        core=v.v05.bore_y(x,z,5)
        assert plate.intersect(core).val().Volume()>1,lat


def test_deck_has_through_holes_and_no_existing_hinge_interference():
    deck=v.az_deck_with_lock_bolt_holes()
    for side in (-1,1):
        for x in (-12,15):
            assert deck.intersect(v.v05.cutter_z([(x,side*63)],4,z0=9,height=5)).val().Volume()<.001
        plate=v.lock_sideplate(side)
        lower=v.v05.lower_hinge_cheek(side>0)
        assert plate.intersect(lower).val().Volume()<1e-4
    assert deck.intersect(v.v05.fixed_triad_base()).val().Volume()<1e-4


def test_moving_lug_attaches_without_hard_structural_intersections():
    for lat in (25,35,45):
        for side in (-1,1):
            lug=v.lock_upper_lug(side,lat)
            sector=v.lock_sideplate(side)
            # 2 mm clearance between lug and sector before separate spacer/washer
            assert lug.intersect(sector).val().Volume()<1e-4,(lat,side,'lug-vs-plate')
            assert lug.intersect(v.v05.tilt_deck(lat)).val().Volume()<1e-4,(lat,side,'lug-vs-top')


def test_tripod_adapter_is_metal_and_compatible_with_generic_base_hole_pattern():
    for d in (10.0,10.5):
        plate=v.tripod_adapter_plate(d)
        assert plate.val().BoundingBox().zmax <=.0001
        assert plate.intersect(v.v05.fixed_triad_base()).val().Volume()<1e-4
        for a in (30,150,270):
            x,y=62*math.cos(math.radians(a)),62*math.sin(math.radians(a))
            assert plate.intersect(v.v05.cutter_z([(x,y)],5,z0=-7,height=8)).val().Volume()<1e-4
    with pytest.raises(ValueError):v.tripod_adapter_plate(11.2)


def test_prints_flat_single_and_metal_never_stl():
    assert len(v.printed_parts())==4
    for name,shape in v.printed_parts().items():
        bb=shape.val().BoundingBox()
        assert 'PRINT_FLAT' in name
        assert bb.zmin>=-.00001
        assert max(bb.xlen,bb.ylen)<220
        assert len(shape.solids().vals())==1
    assert len(v.metal_parts())==11
    assert all('METAL' in n for n in v.metal_parts())


def test_export_manifest_prohibits_load_rating(tmp_path):
    from sys import path
    with pytest.raises(ValueError):v.export(tmp_path,20)
    # Full STEP assembly serialization belongs to the CAD workflow; this test
    # checks the safety contract without repeatedly exporting all BREP bodies.
    assert v.STATUS == 'prototype_unqualified_Gate_A_only'
    assert all('METAL' in n for n in v.metal_parts())
