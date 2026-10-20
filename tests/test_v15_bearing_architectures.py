"""V1.5 data constraints, engineering arithmetic and non-manufacturing CAD geometry."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware/cad'))
import pytest
from tools.rotator_bearing_tradeoff import CANDIDATES,case,write_reports,simple_support_radial_reactions
import generate_v15_bearing_comparison as cad

def test_bearing_dimensions():
    assert [(c.bore_mm,c.od_mm,c.width_mm) for c in CANDIDATES]==[(40,52,7),(40,68,15),(35,95,15)]

def test_single_cross_roller_incompatible_with_existing_spindle():
    assert not CANDIDATES[2].previous_40mm_spindle_compatible
    assert CANDIDATES[1].previous_40mm_spindle_compatible

def test_cannot_compute_single_ring_using_two_support_equations():
    rows=case(4,80,20)['results']
    assert rows[2]['near_support_opposed_abs_N'] is None
    assert rows[2]['bearing_moment_capacity_verified'] is False

def test_numerical_baseline_6808_matches_prior_illustration():
    row=case(4,80,20)['results'][0]
    assert 149<row['near_support_opposed_abs_N']<151
    assert 188<row['far_support_same_direction_abs_N']<190

def test_larger_hypothetical_support_span_reduces_force_reaction():
    r=case(4,80,20)['results']
    assert r[1]['near_support_opposed_abs_N']<r[0]['near_support_opposed_abs_N']
    assert r[1]['far_support_same_direction_abs_N']<r[0]['far_support_same_direction_abs_N']
    assert r[1]['actual_stiffness_known'] is False

def test_footprint_grows_for_ru66():
    assert CANDIDATES[2].od_mm>CANDIDATES[1].od_mm>CANDIDATES[0].od_mm

def test_invalid_cases_raise():
    for args in ((0,80,20),(4,-1,20),(4,80,-1)):
        with pytest.raises(ValueError):case(*args)
    with pytest.raises(ValueError):simple_support_radial_reactions(40,100,(10,10))

def test_concept_geometry_solids_unique_names():
    r=cad.records()
    assert len(r)==14
    assert len(set(a['name'] for a in r))==14
    assert all(len(a['shape'].solids().vals())==1 for a in r)

def test_coupons_are_nonload_annuli_with_flat_base():
    p=cad.nonload_flat_coupons()
    assert len(p)==3
    for shape in p.values():
        assert shape.val().BoundingBox().zmin>=-1e-7
        assert shape.val().BoundingBox().zmax<=3+1e-7

def test_reports_do_not_claim_rating(tmp_path):
    r=write_reports(tmp_path)
    assert r['sweep_count']==81
    assert not r['power_on_allowed']
    assert not r['camera_payload_allowed']
    assert all(not x['claim_comparable_bearing_rating'] for x in r['baseline']['results'])

