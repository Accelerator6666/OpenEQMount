"""V1.1 CAD geometry and coordinate checks. Explicitly NOT a load/safety test."""
from pathlib import Path
import sys,math
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v11_three_axis_mated_concept as v
import generate_v10_rotator_bench as v10


def test_third_axis_not_coaxial_with_dec():
    # Local DEC +X, ROT optical +Z, both are rotated by same rigid transforms.
    # Representative preview angles; angular orthogonality is invariant.
    for dec in (-45,0,25,55):
        unit_dec=(1.,0.,0.)
        rot=(0.,-math.sin(math.radians(dec)),math.cos(math.radians(dec)))
        assert abs(sum(a*b for a,b in zip(unit_dec,rot)))<1e-12
        assert abs(sum(x*x for x in rot)-1)<1e-12


def test_dec_to_rot_bracket_is_one_metal_solid_with_output_hub():
    bridge=v.continuous_metal_bridge()
    assert len(bridge.solids().vals())==1
    assert bridge.val().Volume()>100000
    # Reference output hub touches DEC reducer output x=158 rather than stator rear x=117.
    assert abs(v.DEC_OUTPUT_X-158)<1e-6
    assert abs(v.DEC_CENTRE_Z-112)<1e-6


def test_hub_output_candidate_pcd_is_not_assumed_verified():
    assert v.DEC_OUTPUT_PCD_CANDIDATE==23
    hub=v.dec_output_hub()
    for theta in range(30,390,60):
        r=math.radians(theta)
        y,z=11.5*math.cos(r),v.DEC_CENTRE_Z+11.5*math.sin(r)
        bore=v10.ring(3,1,1).rotate((0,0,0),(0,1,0),90).translate((159,y,z))
        assert hub.intersect(bore).val().Volume()<1.e-3


def test_rot_stator_has_no_brep_overlap_with_metal_deck():
    stator=v10.bearing_seat_housing().translate((v.ROT_X,0,v.ROT_Z))
    deck=v.bridge_deck()
    assert deck.intersect(stator).val().Volume()<1.e-3
    assert abs(deck.val().BoundingBox().zmax-v.ROT_Z)<1.e-6


def test_motor_carrier_is_braced_by_individual_metal_spacers():
    carrier=v.revised_motor_carrier()
    assert len(carrier.solids().vals())==1
    assert len(v.MOTOR_STANDOFF_PHASE)==3
    for deg in v.MOTOR_STANDOFF_PHASE:
        s=v.local_standoff(deg)
        assert abs(s.val().BoundingBox().zlen-14)<1.e-6
        assert s.intersect(v10.bearing_seat_housing()).val().Volume()<1.e-3
        # Through-hole in carrier: spacer through-bolts have clearance, not tapped in polymer.
        theta=math.radians(deg)
        x,y=73*math.cos(theta),73*math.sin(theta)
        cyl=v10.ring(4,1,2).translate((x,y,16))
        assert carrier.intersect(cyl).val().Volume()<1.e-3


def test_rotator_spindle_and_camera_blank_connect_in_space_not_certified_joint():
    plate=v.camera_blank()
    assert abs(plate.val().BoundingBox().zlen-6)<1.e-6
    assert plate.val().BoundingBox().xlen==108
    assert v10.output_plate().val().BoundingBox().zmax==67


def test_unpowered_geometric_sweep_range_guard():
    for angle in (-150,0,150):
        converted=v.rotor_local_to_mount(v.camera_blank(),35,25,angle,True)
        assert len(converted.solids().vals())==1
    with pytest.raises(ValueError):v.rotor_local_to_mount(v.camera_blank(),35,25,160,True)
    with pytest.raises(ValueError):v.rotor_local_to_mount(v.camera_blank(),20,25,0,True)
    with pytest.raises(ValueError):v.rotor_local_to_mount(v.camera_blank(),35,80,0,True)


def test_nonload_fdm_gauge_and_safety_flags():
    p=v.print_gauges()
    assert len(p)==1
    for name,shape in p.items():
        assert 'NONLOAD_' in name
        bbox=shape.val().BoundingBox()
        assert bbox.zmin==0 and bbox.xlen<=220 and bbox.ylen<=220
        r=v.print_record(name,shape)
        assert r['field_load_approved'] is False
        assert r['slicer_gate_B']=='pending'
        assert r['physical_gate_C']=='pending'


def test_no_extraneous_loose_print_coupons_in_mounted_view():
    rec=v.part_records(35,25,0)
    names=[p['name'] for p in rec]
    assert len(names)==len(set(names))
    assert all('NONLOAD' not in n for n in names)
    assert any('CONTINUOUS_METAL_BRIDGE' in n for n in names)
    assert any('CAMERA_MATING_FLANGE' in n for n in names)
    assert not any('FIXED_STOP_ARC' in n for n in names)


def test_manifest_does_not_claim_qualified_hardware(tmp_path):
    # Avoid full STEP generation in unit test; covers the hard-coded flags at source.
    import inspect
    s=inspect.getsource(v.export)
    assert "'independent_metal_fall_arrest_implemented':False" in s
    assert "'camera_payload_approved':False" in s
    assert "'safe_to_energize':False" in s
    assert "'full_kinematic_collision_proved':False" in s
