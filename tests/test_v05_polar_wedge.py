"""V0.5 kinematic CAD checks; no certified load or fastener test."""
from __future__ import annotations
import math,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v05 as v


def test_true_orthogonal_ra_altitude():
    for lat in (25,30,35,40,45):
        th=math.radians(90-lat)
        normal=(-math.sin(th),0,math.cos(th))
        elevation=math.degrees(math.asin(normal[2]))
        assert math.isclose(elevation,lat,abs_tol=1e-10)
        assert normal[0]<0  # RA axis faces -X = north, never +X by mistake


def test_pivot_unchanged_and_jack_travel():
    for lat in (25,35,45):
        center=v.tilted_point(v.PIVOT,lat)
        assert all(math.isclose(a,b,abs_tol=1e-10) for a,b in zip(center,v.PIVOT))
    lo,mid,hi=[v.jack_length(p) for p in (45,35,25)]
    assert 50<lo<mid<hi<170
    assert (hi-lo)<45


def test_latitude_range_rejects_unverified_angles(tmp_path):
    with pytest.raises(ValueError):v.export(tmp_path,0)
    with pytest.raises(ValueError):v.export(tmp_path,60)


def test_prints_are_bed_oriented_singular():
    p=v.prints();assert len(p)==5
    for name,s in p.items():
        b=s.val().BoundingBox()
        assert len(s.solids().vals())==1,name
        assert b.zmin>-0.001 and b.xlen<220 and b.ylen<220
        assert s.val().Volume()>150,name


def test_top_adapter_four_bolt_pattern_is_open_not_load_approved():
    # Provisional holes in the local wedge deck. NOT approved for mounting rotating RA output.
    plate=v.tilt_assembly_local()
    for x in (-43,45):
        for y in (-45,45):
            probe=v.cutter_z([(x,y)],2.0,z0=24,height=6)
            assert plate.intersect(probe).val().Volume()<0.001,(x,y)


def test_full_azimuth_swept_slots_are_open():
    plate=v.azimuth_deck()
    for nominal in (90.,270.):
        for offset in (-5.,0.,5.):
            angle=math.radians(nominal+offset)
            x,y=58*math.cos(angle),58*math.sin(angle)
            s=v.cutter_z([(x,y)],5.0,z0=8,height=6)
            assert plate.intersect(s).val().Volume()<0.001,(nominal,offset)


def test_primary_metal_base_and_turntable_do_not_penetrate():
    assert v.fixed_triad_base().intersect(v.azimuth_deck()).val().Volume()<1e-4
    for lat in (25.,35.,45.):
        tilted=v.tilt_deck(lat)
        for positive in (False,True):
            fixed=v.lower_hinge_cheek(positive)
            assert tilted.intersect(fixed).val().Volume()<1e-4,(lat,positive)


def test_metal_pin_axis_intersects_hinge_through_holes_without_material_contact():
    pin=v.hinge_pin()
    for positive in (False,True):
        assert pin.intersect(v.lower_hinge_cheek(positive)).val().Volume()<1e-5
    for lat in (25,35,45):
        assert pin.intersect(v.tilt_deck(lat)).val().Volume()<1e-5


def test_metal_parts_are_not_printed_or_classified_as_printable():
    assert len(v.metals())==10
    assert all('METAL' in name for name in v.metals())
    assert all('PRINT_FLAT' in name for name in v.prints())


def test_mandatory_unqualified_dfam_export(tmp_path):
    data=v.export(tmp_path,35)
    assert data['status']=='prototype_unqualified_Gate_A_only'
    assert len(data['printed_parts'])==5
    assert len(data['metal_parts'])==10
    assert all(p['physical_gate_C']=='pending' for p in data['printed_parts'])
    assert any('locking clamp' in w for w in data['warnings'])
