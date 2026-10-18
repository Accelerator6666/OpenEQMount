"""Regression tests for binding DfAM policy; not a mechanical certification."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v03 as v


def test_all_v03_printable_parts_have_dfam_contract():
    parts=v.assign_parts()
    assert len(parts)==20
    for name in parts:
        m=v.dfam_profile(name)
        assert m['status']=='prototype_unqualified'
        assert m['process']=='FFF/FDM'
        assert m['print_orientation']=='model_+Z_up;_XY_plane_on_bed'
        assert m['structural_load_verified'] is False
        assert m['overhang_support_status']=='slicer_review_pending'


def test_no_heatset_insert_is_default_in_cyclic_load_joints():
    for name in v.assign_parts():
        d=v.dfam_profile(name)
        if d['role'] in ('rear_mount_housing','motor_carrier','auxiliary_bearing_bridge'):
            assert d['fastener_strategy']=='metal_through_bolts_washers_and_nuts'


def test_axial_housing_fasteners_are_through_holes():
    for r in (v.RA,v.DEC):
        body=v.housing(r)
        for x,y in [(57,-25),(57,25)]+v.circle_points(v.BRIDGE_PCD,4,45):
            probe=v.cylinder(1,9,-9).translate((x,y,0))
            assert body.intersect(probe).val().Volume()<1e-5


def test_legacy_v02_only_exports_stl_explicitly():
    import inspect
    import generate_v02
    src=inspect.getsource(generate_v02.write_models)
    assert 'export_unsafe_concept_stl' in src
    assert generate_v02.write_models.__defaults__==(False,)
