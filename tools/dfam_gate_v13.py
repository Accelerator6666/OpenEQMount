#!/usr/bin/env python3
"""V1.3 Gate A digital STL / metadata audit. NOT a structural approval."""
import argparse, json,sys
from pathlib import Path
import trimesh
REQUIRED_FALSE=(
 'thread_model_is_functional','real_locknut_specified','positive_locking_qualified',
 'bearing_preload_defined','bearing_fit_tolerance_defined','camera_clamp_vendor_confirmed',
 'camera_clamp_attached','camera_lens_collar_selected','camera_mating_interface_qualified',
 'fall_arrest_complete','fall_arrest_cable_in_CAD','fall_arrest_anchor_strength_qualified',
 'independent_camera_eye_attached','tether_path_cleared_for_collision',
 'stop_fasteners_qualified','stop_strength_qualified','full_RA_DEC_ROT_collision_proved',
 'safe_to_energize','payload_approved','bearing_actual_shoulder_race_face_confirmed')

def audit(folder):
    folder=Path(folder);m=json.loads((folder/'manifest.json').read_text('utf-8'));errors=[];parts=[]
    if m.get('release')!='V1.3_ROT_AXIAL_RETENTION_CAMERA_DATUM_GATE_A':errors.append('wrong version')
    if not m.get('bearing_axial_stack_geometry_consistent'):errors.append('nominal z stack')
    if any(m.get(k) is not False for k in REQUIRED_FALSE):errors.append('unqualified interfaces falsely approved')
    if m.get('Gate_B')!='pending' or m.get('Gate_C')!='pending':errors.append('physical gates')
    if m.get('parts_in_assembly')!=66:errors.append('missing assembly solids')
    if not (folder/m.get('assembled_step','_missing.step')).exists():errors.append('missing whole STEP')
    for name in m.get('metal_reference_exports',[]):
        if not (folder/(name+'.step')).exists() or (folder/(name+'.stl')).exists():
            errors.append('unsafe metal export '+name)
    for item in m.get('nonload_printed_parts',[]):
        name=item.get('name','');f=folder/(name+'.stl')
        if item.get('field_load_approved') is not False or not name.startswith('v13_NONLOAD_'):
            errors.append('unsafe print name or flag '+name)
        if item.get('slicer_gate_B')!='pending' or item.get('physical_gate_C')!='pending':errors.append('gate status '+name)
        if not f.is_file() or not (folder/(name+'.step')).is_file():errors.append('missing print '+name);continue
        mesh=trimesh.load_mesh(f)
        okay=bool(mesh.is_watertight and len(mesh.split(only_watertight=False))==1 and abs(mesh.bounds[0,2])<.02 and max(mesh.extents[:2])<=220)
        parts.append(dict(name=name,closed_single_body_flat=okay))
        if not okay:errors.append('STL manifold / printing layout '+name)
    if len(parts)!=2:errors.append('not exactly two nonstructural coupons')
    return dict(gate='A digital ONLY',passed=not errors,errors=errors,parts=parts,field_load_or_power_qualified=False,Gate_B='pending',Gate_C='pending')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dir',type=Path,default=Path('hardware/cad/v13_generated'));p.add_argument('--report',type=Path)
    a=p.parse_args();r=audit(a.dir)
    if a.report:a.report.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(r,indent=2,ensure_ascii=False));sys.exit(0 if r['passed'] else 1)
