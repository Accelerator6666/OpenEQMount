"""V1.8 torque-interface regression: CAD Gate A is NOT proof of shaft/payload safety."""
import sys,math
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
import generate_v18_positive_drive as v


def test_legacy_floating_output_removed():
    parts=v.integration_parts()
    names=[r['name'] for r in parts]
    assert not any('V16_CAMERA_FIXTURE_INTERFACE_BLANK' in n for n in names)
    assert not any('V16_HOLLOW_METAL_SPINDLE_' in n for n in names)
    assert any('ONE_PIECE_METAL_HOLLOW_SPINDLE' in n for n in names)
    assert len(parts)==24


def test_whole_mount_contains_66_named_entities():
    p=v.records()
    assert len(p)==66
    assert len(set(r['name'] for r in p))==66
    assert sum('7008AWDB_RING_' in r['name'] for r in p)==2
    assert not any('6808' in r['name'] for r in p)


def test_integral_one_piece_shaft_connected():
    s=v.spindle()
    assert len(s.solids().vals())==1
    bbox=s.val().BoundingBox()
    assert bbox.zmin==pytest.approx(-7)
    assert bbox.zmax==pytest.approx(53)
    assert bbox.xlen==pytest.approx(110)


def test_unqualified_camera_plate_is_distinct():
    p=v.camera_blank()
    assert len(p.solids().vals())==1
    assert p.val().BoundingBox().zmin==pytest.approx(v.FLANGE_TOP)
    assert p.val().BoundingBox().zmax==pytest.approx(v.CAMERA_TOP)
    assert v.CAMERA_BORE>=30


def test_bolt_pattern_and_ligament_values():
    m=v.reference_checks()
    assert m['worst_outer_radial_ligament_mm']>=5
    assert m['minimum_center_separation_bolt_dowel_mm']>15
    assert len(v.centers(6,90,30))==6
    assert len(v.centers(2,68))==2


def test_6_metal_through_bolts_and_2_steel_dowels():
    names=[p['name'] for p in v.joint_parts()]
    assert len(names)==16
    assert sum('THROUGH_BOLT_' in x for x in names)==6
    assert sum('NUT_ENVELOPE' in x for x in names)==6
    assert sum('POSITIVE_SHEAR_DOWEL' in x for x in names)==2
    assert all(len(p['shape'].solids().vals())==1 for p in v.joint_parts())


def test_dowel_blind_pocket_and_correct_z_overlap():
    assert v.PIN_BOTTOM< v.FLANGE_TOP < v.PIN_TOP
    assert v.PIN_BOTTOM>=48
    assert v.PIN_TOP<=58
    assert v.DOWEL_D<v.DOWEL_HOLE_D


def test_nut_mounting_space_separated_from_upper_locknut():
    assert v.NUT_TOP==38
    assert v.FLANGE_BOTTOM-v.NUT_TOP>=5
    assert v.BOLT_PCD/2-v.BOLT_D/2>25+5


def test_bolt_pin_pattern_not_same_locations():
    mindist=min(math.hypot(a[0]-b[0],a[1]-b[1]) for a in v.centers(6,90,30) for b in v.centers(2,68))
    assert mindist>20


def test_nominal_pin_shear_math():
    x=v.pin_torque_study(.785)
    assert x['pin_force_N']==pytest.approx(11.544,abs=.003)
    assert x['nominal_single_shear_MPa']>0
    assert v.pin_torque_study(1.57)['pin_force_N']==pytest.approx(2*x['pin_force_N'],abs=.01)


def test_negative_inputs_rejected():
    for t in (0,-1):
        with pytest.raises(ValueError):v.pin_torque_study(t)
    with pytest.raises(ValueError):v.integration_parts(35,25,180)


def test_nonload_coupon_orientation_geometry():
    g=v.print_flat_nonload_gauge()
    assert len(g.solids().vals())==1
    assert g.val().BoundingBox().zmin==pytest.approx(0)
    assert g.val().BoundingBox().zmax==pytest.approx(3)


def test_safety_flags_explicit_in_source():
    source=Path(v.__file__).read_text()
    for literal in ('safe_to_energize=False','payload_approved=False',
                    'independent_payload_tether_attached=False','gate_B=\'PENDING\'','gate_C=\'PENDING\''):
        assert literal in source
