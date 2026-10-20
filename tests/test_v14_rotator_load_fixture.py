"""V1.4 safe-gated dimensions and mechanics. NOT a load certificate."""
from pathlib import Path
import sys, json, math
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'hardware/cad'))
import cadquery as cq
import generate_v14_load_fixture as v
from tools.rotator_load_cases import LoadCase,estimate,grid_cases,write_reports

def test_gravity_and_reactions_are_equilibrium_consistent():
    x=estimate(LoadCase(5,120,40))
    assert math.isclose(x['gravity_force_N'],49.03325,abs_tol=1e-3)
    assert x['radial_reaction_upper_N_example']>x['radial_reaction_lower_N_example_opposite']>0
    assert math.isclose(x['radial_reaction_upper_N_example']-x['radial_reaction_lower_N_example_opposite'],x['gravity_force_N'],abs_tol=.002)
    assert math.isclose(x['roll_gravity_torque_Nm_envelope'],49.03325*.04,abs_tol=.001)
    assert math.isclose(x['motor_static_torque_Nm_ideal_no_losses']*4,x['roll_gravity_torque_Nm_envelope'],abs_tol=.001)

def test_cg_axial_offset_increases_radial_reaction():
    a=estimate(LoadCase(4,40,20))
    b=estimate(LoadCase(4,120,20))
    assert b['radial_reaction_upper_N_example']>a['radial_reaction_upper_N_example']
    assert a['roll_gravity_torque_Nm_envelope']==b['roll_gravity_torque_Nm_envelope']

def test_roll_torque_scales_with_eccentricity():
    a=estimate(LoadCase(5,80,0));b=estimate(LoadCase(5,80,40))
    assert a['roll_gravity_torque_Nm_envelope']==0
    assert b['roll_gravity_torque_Nm_envelope']>1.9
    assert b['motor_static_torque_Nm_ideal_no_losses']>0.49

def test_multiplier_is_illustrative_not_approval():
    a=estimate(LoadCase(4,80,20,1));b=estimate(LoadCase(4,80,20,2))
    assert b['gravity_force_N']==2*a['gravity_force_N']
    assert b['system_payload_approved'] is False
    assert b['bearing_rating_comparison_permitted'] is False

def test_bad_load_inputs_rejected():
    for kw in [{'mass_kg':0},{'mass_kg':-1},{'mass_kg':21},{'cg_from_mount_mm':-1},
               {'eccentricity_mm':-1},{'illustration_multiplier':0},{'illustration_multiplier':6}]:
        d={'mass_kg':4,'cg_from_mount_mm':80,'eccentricity_mm':20}
        d.update(kw)
        with pytest.raises(ValueError):LoadCase(**d)

def test_scenarios_are_not_a_capacity_claim(tmp_path):
    d=write_reports(tmp_path)
    assert d['case_count']==54
    assert len(grid_cases())==54
    assert not d['camera_load_authorized'] and not d['bearing_rated']
    assert (tmp_path/'rotator_load_cases_ILLUSTRATIVE.csv').exists()
    assert d['gates']['C']=='pending'

def test_metal_camera_adapter_has_real_clearance_slots():
    assert v.verify_candidate_slot()
    a=v.slotted_camera_interface()
    assert len(a.solids().vals())==1
    assert abs(a.val().BoundingBox().zlen-8)<1e-3
    for x,y in v.v10.points(88,6,30):
        # Six PCD holes are nominal and must be clear at nominal centers.
        probe=cq.Workplane('XY').center(x,y).circle(2).extrude(8).translate((0,0,67))
        assert a.intersect(probe).val().Volume()<1e-4

def test_cg_print_coupons_have_no_load_path():
    s=v.cg_marker_print_flat();bb=s.val().BoundingBox()
    assert len(s.solids().vals())==1
    assert bb.zmin==0 and bb.zlen==3
    assert bb.xlen==150 and bb.ylen==24

def test_assembly_replaces_old_unverified_camera_plate_not_both():
    r=v.assembly_records()
    names=[x['name'] for x in r]
    assert len(names)==68 and len(set(names))==68
    assert not any('v13_METAL_CAMERA_VENDOR_CLAMP' in n for n in names)
    assert any('v14_METAL_SLOTTED_CAMERA' in n for n in names)
    assert sum('REFERENCE_CAMERA_BODY' in n for n in names)==1
    assert sum('REFERENCE_LENS' in n for n in names)==1

def test_export_has_conspicuous_no_power_and_no_camera_flags(tmp_path):
    m=v.export(tmp_path)
    assert m['parts_in_assembly']==68
    for key in ['camera_vendor_clamp_selected','camera_attached_to_cad','photographic_cg_measured',
                'bearing_catalogue_fatigue_confirmed','bearing_pair_deflection_model_completed',
                'bearing_preload_defined','independent_camera_tether_attached',
                'camera_saddle_strength_qualified','motor_torque_qualified',
                'safe_to_energize','payload_approved']:
        assert m[key] is False, key
    assert m['Gate_B']==m['Gate_C']=='pending'
    f=tmp_path/m['assembled_step']
    assert f.stat().st_size>200000
    assert len(cq.importers.importStep(str(f)).solids().vals())==68
    assert not (tmp_path/'v14_METAL_SLOTTED_CAMERA_VENDOR_FIXTURE_STOCK_UNQUALIFIED.stl').exists()
