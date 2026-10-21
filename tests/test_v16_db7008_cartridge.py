"""V1.6 NSK matched DB 7008AWDB boundary/datum and DfAM reference checks."""
import json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
from tools.rotator_db7008_study import BEARING, load_centres_z_mm, external_simple_reactions, dimensions_review, generate_reports
import generate_v16_db7008_cartridge as v


def test_exact_vendor_db_reference():
    assert BEARING['exact_catalog_designation']=='7008AWDB'
    assert (BEARING['bore_mm'],BEARING['outside_diameter_mm'],BEARING['matched_pair_width_mm'])==(40,68,30)
    assert BEARING['db_arrangement']=='back_to_back'
    assert BEARING['contact_angle_deg']==30


def test_oem_load_centres_distinct_from_physical_width():
    a,b=load_centres_z_mm()
    assert a == pytest.approx(-8.1)
    assert b == pytest.approx(38.1)
    assert b-a==pytest.approx(46.2)
    assert b-a != BEARING['matched_pair_width_mm']


def test_clearance_not_mislabelled_preload():
    assert 'CN' in BEARING['nominal_pair_internal_clearance']
    assert 'NOT' in BEARING['nominal_pair_internal_clearance']


def test_bearing_abutment_diameters_basic_reference_only():
    d=dimensions_review()
    assert d['simple_diameter_limits_satisfied']
    assert d['shaft_shoulder_reference_diameter_mm']>=BEARING['shaft_abutment_da_min_mm']
    assert d['housing_cap_opening_reference_diameter_mm']<=BEARING['housing_abutment_Db_max_mm']
    assert d['matched_pair_axial_clamp_stack_verified'] is False


def test_calculation_baseline_rigid_virtual_supports_only():
    r=external_simple_reactions(4,80,20)
    assert r['near_opposed_simple_reaction_N']==pytest.approx(99.255,abs=.25)
    assert r['far_simple_reaction_N']==pytest.approx(138.48,abs=.25)
    assert r['NOT_actual_angular_contact_internal_loads']
    assert not (r['a0_mm']==r['bearing_stack_physical_width_mm'])


def test_external_equilibrium():
    r=external_simple_reactions(4,80,20)
    assert r['far_simple_reaction_N']-r['near_opposed_simple_reaction_N']==pytest.approx(r['force_n'],abs=.0001)


def test_invalid_inputs_guarded():
    for args in [(0,80,20),(4,-1,20),(4,80,-1),(40,80,20)]:
        with pytest.raises(ValueError):external_simple_reactions(*args)


def test_primary_shapes_count_and_unique():
    p=v.cartridge_parts()
    assert len(p)==9
    assert len(set(x['name'] for x in p))==len(p)
    assert all(len(x['shape'].solids().vals())==1 for x in p)


def test_db_pair_bearings_are_abutting_no_spacer():
    p=[x for x in v.cartridge_parts() if '_RING_' in x['name'] and '_ENVELOPE_ONLY' in x['name']]
    assert len(p)==2
    z=sorted([x['shape'].val().BoundingBox().zmin for x in p])
    assert z==pytest.approx([0,15])
    zmax=sorted([x['shape'].val().BoundingBox().zmax for x in p])
    assert zmax==pytest.approx([15,30])


def test_housing_entry_allows_68_diameter_nominal():
    # Reference only, makes insertion geometric possible; actual FIT is not specified.
    assert v.ring(90,68.2,30).val().isValid()
    p=v.cartridge_parts()[0]
    assert p['shape'].val().BoundingBox().zlen==pytest.approx(30)


def test_metal_shoulder_contacts_nominal_lower_race_at_z0():
    p=next(x['shape'] for x in v.cartridge_parts() if 'SPINDLE' in x['name'])
    assert p.val().BoundingBox().zmin==pytest.approx(-7)
    assert p.val().BoundingBox().zmax==pytest.approx(40)
    assert len(p.solids().vals())==1


def test_coupon_flat_nonstructural():
    gauges=v.bed_flat_coupons()
    assert len(gauges)==2
    for x in gauges.values():
        box=x.val().BoundingBox()
        assert box.zmin==pytest.approx(0,abs=1e-6)
        assert box.zlen==pytest.approx(4)


def test_27_cases_and_no_payload_approval(tmp_path):
    data=generate_reports(tmp_path)
    assert data['sweep_count']==27
    assert (tmp_path/data['csv']).exists()
    assert data['camera_payload_approved'] is False and data['may_energize'] is False
    assert 'not' in data['clarification'].lower()


def test_CAD_manifest_and_export(tmp_path):
    manifest=v.generate(tmp_path)
    assert manifest['assembly_solids']==9
    assert manifest['preload_selected'] is False
    assert manifest['NO_spacing_between_matched_bearings']
    assert (tmp_path/v.OUT_NAME).stat().st_size>50000
    assert (tmp_path/v.EXPLODED_NAME).stat().st_size>50000
    assert len(list(tmp_path.glob('*.stl')))==2
    assert json.loads((tmp_path/'manifest.json').read_text())['payload_approved'] is False
