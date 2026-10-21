"""V1.7 Gate A regression: structure and honest safety gating, not proof of strength."""
import sys,math,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
import generate_v17_integrated_7008 as v

def test_legacy_remove():
    a=v.base_parts()
    assert len(a)==42
    assert any('DEC_OUTPUT_TO_ROT' in p['name'] for p in a)
    assert not any('6808' in p['name'] or 'v12_' in p['name'] or 'v13_' in p['name'] for p in a)

def test_candidate_alignment():
    assert v.BRIDGE_PCD==110 and v.CARTRIDGE_PCD==80
    assert v.CARTRIDGE_Z_ABOVE_BRIDGE==13
    assert v.spatial_checks()['lower_cap_z_nominal_mm'][0]==v.PLATE_HEIGHT

def test_cad_clearance_and_ligament():
    p=v.adapter_local()
    assert len(p.solids().vals())==1
    assert abs(p.val().BoundingBox().zmin)<1e-5
    assert v.minimum_radial_ligament_mm()>=5
    assert p.val().BoundingBox().xlen==pytest.approx(v.PLATE_OD,abs=.1)

def test_12_holes_open():
    import cadquery as cq
    p=v.adapter_local()
    for rad,diam in [(v.BRIDGE_PCD/2,5.5),(v.CARTRIDGE_PCD/2,4.5)]:
        for n in range(6):
            theta=n*math.pi/3
            probe=cq.Workplane('XY').center(rad*math.cos(theta),rad*math.sin(theta)).circle((diam-.4)/2).extrude(8)
            assert p.intersect(probe).val().Volume()<1e-3

def test_dfam_coupon_nonload():
    q=v.print_flat_gauge()
    assert len(q.solids().vals())==1
    assert q.val().BoundingBox().zmin==pytest.approx(0,abs=.0001)
    assert q.val().BoundingBox().zlen==pytest.approx(3,abs=.0001)

def test_mated_no_6808():
    r=v.records()
    assert len(r)==52
    names=[x['name'] for x in r]
    assert not any('6808' in x for x in names)
    assert sum('7008AWDB_RING' in x for x in names)==2
    assert any('PCD110_TO_PCD80' in x for x in names)

def test_valid_preview_ranges():
    for args in [(24,25,0),(46,25,0),(35,66,0),(35,0,151)]:
        with pytest.raises(ValueError):v.integration_parts(*args)

def test_7008_manufacturer_width_not_a0():
    checks=v.spatial_checks()
    assert checks['manufacturer_a0_load_centre_mm']==46.2
    assert checks['physical_matched_width_mm']==30
    assert checks['bearing_z_nominal_mm'][0][1]==checks['bearing_z_nominal_mm'][1][0]

def test_fixed_and_rotating_roles():
    names=v.integration_parts(35,0,20)
    assert len(names)==10
    assert sum('rotating' in p['role'] for p in names)==4
    assert sum('fixed' in p['role'] for p in names)==6

def test_manifest_digital_only():
    # Fast integration source contract; full STEP and manifest exercised in Actions.
    source=Path(v.__file__).read_text()
    assert 'payload_approved=False' in source
    assert 'safe_to_energize=False' in source
    assert 'gate_B=\'PENDING\'' in source
    assert v.minimum_radial_ligament_mm()>=5
