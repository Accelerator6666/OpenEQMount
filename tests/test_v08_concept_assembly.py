"""V0.8 positional preview checks. NOT a mechanical or safety test."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v08_concept_assembly as asm

def test_singles_selected_and_no_coupling():
    parts=asm.make_components(35.)
    names=[x['name'] for x in parts]
    assert len(names)==len(set(names))
    assert len(parts)>=35
    assert names.count('TRIPOD_FIXED_MAIN_BASE')==1
    assert sum('TRIPOD_PCD62' in n.upper() for n in names)==1
    assert 'v07_WEDGE_REPLACEMENT_TOP_DECK_METAL' in names
    assert 'v04_ra_output_plate_METAL' in names
    assert 'DEC_HARMONIC_GEARBOX_ENVELOPE_NOT_PURCHASED' in names
    assert all('BELT_BENCH' not in n for n in names)
    assert all('COUPON' not in n and 'GAUGE' not in n for n in names)

def test_fit_to_kinematic_wedge_and_envelope():
    parts=asm.make_components(35.)
    byname={x['name']:x['shape'].val().BoundingBox() for x in parts}
    bottom=byname['TRIPOD_FIXED_MAIN_BASE']
    upper=byname['v04_ra_output_plate_METAL']
    assert bottom.zmin==pytest.approx(0,abs=.001)
    assert upper.zmin>bottom.zmax+20
    assert upper.zmax<400
    assert byname['v04_dec_rear_plate_METAL'].zmax>upper.zmax

def test_invalid_latitude_rejected():
    with pytest.raises(ValueError):asm.make_components(10)
