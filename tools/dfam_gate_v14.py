#!/usr/bin/env python3
"""V1.4 DfAM Gate A: only digital shape/metadata checks, NEVER load approval."""
from __future__ import annotations
import argparse, json,sys
from pathlib import Path
import trimesh
FALSE_FLAGS=('camera_vendor_clamp_selected','camera_attached_to_cad','photographic_cg_measured',
             'bearing_catalogue_fatigue_confirmed','bearing_pair_deflection_model_completed',
             'shaft_thread_specified','bearing_preload_defined','independent_camera_tether_attached',
             'tether_length_and_sweep_qualified','camera_saddle_strength_qualified',
             'full_three_axis_kinematic_collision_verified','belt_efficiency_measured',
             'motor_torque_qualified','physical_gates_completed','safe_to_energize','payload_approved')

def audit(folder):
    folder=Path(folder);m=json.loads((folder/'manifest.json').read_text('utf-8'))
    load=json.loads((folder/'rotator_load_report.json').read_text('utf-8'))
    failures=[]
    if m.get('release')!='V1.4_VENDOR_ADAPTER_CG_ENVELOPE_GATE_A_UNQUALIFIED':failures.append('release mismatch')
    if m.get('parts_in_assembly')!=68:failures.append('assembly does not contain 68 bodies')
    if any(m.get(k) is not False for k in FALSE_FLAGS):failures.append('unsupported safety claims')
    if m.get('Gate_B')!='pending' or m.get('Gate_C')!='pending':failures.append('physical gates mislabeled')
    if not (folder/m.get('assembled_step','_missing')).is_file():failures.append('STEP missing')
    if load.get('case_count')!=54 or load.get('camera_load_authorized') is not False:failures.append('load report invalid')
    if not (folder/'rotator_load_cases_ILLUSTRATIVE.csv').is_file():failures.append('CSV missing')
    for name in m.get('metal_reference_exports',[]):
        if not (folder/(name+'.step')).is_file() or (folder/(name+'.stl')).exists():failures.append('unsafe metal STL: '+name)
    for name in m.get('camera_visual_only',[]):
        if (folder/(name+'.stl')).exists():failures.append('reference camera is NOT printable: '+name)
    parts=m.get('nonload_printed_parts',[])
    if len(parts)!=1:failures.append('expected a single nonload print coupon')
    for p in parts:
        n=p.get('name','');f=folder/(n+'.stl')
        if not n.startswith('v14_NONLOAD_') or p.get('field_load_approved') is not False:failures.append('unsafe printed part')
        if p.get('slicer_gate_B')!='pending' or p.get('physical_gate_C')!='pending':failures.append('incorrect gate status')
        if not f.is_file() or not (folder/(n+'.step')).is_file():failures.append('missing printed specimen');continue
        mesh=trimesh.load_mesh(f)
        if not(mesh.is_watertight and len(mesh.split(only_watertight=False))==1 and
               abs(mesh.bounds[0,2])<.02 and max(mesh.extents[:2])<=220):failures.append('STL manifold/flat failure')
    return dict(gate='Gate A DIGITAL ONLY',passed=not failures,errors=failures,
                print_parts_tested=len(parts),bearing_or_payload_qualified=False,
                motor_energization_authorized=False,Gate_B='pending',Gate_C='pending')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dir',type=Path,default=Path('hardware/cad/v14_generated'))
    p.add_argument('--report',type=Path)
    a=p.parse_args();result=audit(a.dir)
    if a.report:a.report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2,ensure_ascii=False));sys.exit(0 if result['passed'] else 1)
