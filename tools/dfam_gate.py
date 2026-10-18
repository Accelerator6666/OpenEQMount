#!/usr/bin/env python3
"""Fail-closed checks for OpenEQMount FDM prototype exports.

Automated checks DO NOT evaluate stresses, delamination, slicer supports, heat
creep, torque retention, supplier hardware alignment, or field safety.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

REQUIRED_FIELDS = {
    'process', 'policy', 'status', 'role', 'print_orientation', 'bed_contact',
    'stl_min_z_mm', 'material_initial', 'slicer_profile', 'fastener_strategy',
    'critical_layer_risk', 'overhang_support_status', 'minimum_wall_analysed',
    'structural_load_verified', 'external_safety_gate',
}


def audit(manifest: Path, stl_dir: Path, require_qualified: bool = False) -> dict:
    import trimesh
    meta = json.loads(manifest.read_text(encoding='utf-8'))
    failures: list[str] = []
    notes: list[str] = []
    items=meta.get('items')
    if meta.get('dfam_contract_version') != '1.0' or not isinstance(items,list) or not items:
        failures.append('Missing DfAM manifest contract or printable parts list')
        return {'pass':False,'errors':failures,'warnings':notes,'checked':0}
    names=[p.get('name') for p in items]
    if len(set(names))!=len(names):
        failures.append('Duplicate printable part names')
    for part in items:
        name=part.get('name','<unnamed>')
        m=part.get('dfam',{})
        missing=REQUIRED_FIELDS-m.keys()
        if missing:
            failures.append(f'{name}: missing fields {sorted(missing)}')
            continue
        if m['process'] != 'FFF/FDM' or m['bed_contact'] != 'min_Z_face':
            failures.append(f'{name}: unknown printing process or bed plane')
        if m['print_orientation']!='model_+Z_up;_XY_plane_on_bed':
            failures.append(f'{name}: explicit print orientation required')
        if m['policy']!='docs/dfam-design-standard.md':
            failures.append(f'{name}: invalid policy path')
        if m['status'] not in {'prototype_unqualified','validated_with_evidence'}:
            failures.append(f'{name}: unrecognized review status')
        if m['status']=='validated_with_evidence' and not m['structural_load_verified']:
            failures.append(f'{name}: cannot mark validated without physical proof')
        if require_qualified and m['status']!='validated_with_evidence':
            failures.append(f'{name}: NOT approved for actual payload or field use')
        if m['role'] in {'rear_mount_housing','motor_carrier','auxiliary_bearing_bridge'} and \
           m['fastener_strategy']!='metal_through_bolts_washers_and_nuts':
            failures.append(f'{name}: reinforced mechanical through-fastener required')
        if m['overhang_support_status'] == 'slicer_review_pending':
            notes.append(f'{name}: slicer support/overhang audit is pending')
        if not m['minimum_wall_analysed']:
            notes.append(f'{name}: minimum web/boss/wall analysis must be done manually')
        p=stl_dir/(name+'.stl')
        if not p.exists():
            failures.append(f'{name}: STL missing')
            continue
        try:
            mesh=trimesh.load_mesh(str(p),process=True)
        except Exception as exc:
            failures.append(f'{name}: STL cannot be loaded: {exc}')
            continue
        if not isinstance(mesh,trimesh.Trimesh) or mesh.faces.shape[0]<12:
            failures.append(f'{name}: invalid/empty triangulated mesh')
            continue
        if not mesh.is_watertight or not mesh.is_winding_consistent:
            failures.append(f'{name}: STL not a watertight consistently wound solid')
        if mesh.body_count != 1:
            failures.append(f'{name}: printable STL must be one connected component')
        if mesh.volume <= 0:
            failures.append(f'{name}: nonpositive enclosed volume')
        lo,hi=mesh.bounds
        if abs(lo[2])>0.05 or abs(m['stl_min_z_mm'])>0.001:
            failures.append(f'{name}: STL is not bed-aligned to Z=0')
        size=hi-lo
        if any(x > 220.05 for x in size):
            failures.append(f'{name}: exceeds declared 220mm print bed envelope')
        declared=part.get('bbox_mm')
        if not declared or any(abs(float(size[i])-float(declared[i]))>1.2 for i in range(3)):
            failures.append(f'{name}: STL dimensions do not match generated STEP bounds')
    actual=set(x.stem for x in stl_dir.glob('*.stl'))
    undeclared=actual-set(names)
    if undeclared:
        failures.append(f'Unreviewed printable meshes present: {sorted(undeclared)}')
    return {'pass':not failures,'errors':failures,'warnings':notes,
            'checked':len(items),'field_ready':not failures and not any(i['dfam']['status']!='validated_with_evidence' for i in items)}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,default=Path('hardware/cad/v03_generated/manifest.json'))
    ap.add_argument('--stl-dir',type=Path,default=Path('hardware/cad/v03_generated'))
    ap.add_argument('--report',type=Path)
    ap.add_argument('--require-qualified',action='store_true')
    args=ap.parse_args()
    r=audit(args.manifest,args.stl_dir,args.require_qualified)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print(f"DfAM digital gate: {'PASS' if r['pass'] else 'FAIL'}; {r['checked']} printable meshes checked")
    print('Slicer review, stress testing and payload safety NOT certified by this test.')
    for e in r['errors']:print('ERROR:',e)
    print(f"Remaining manual warning entries: {len(r['warnings'])}")
    return 0 if r['pass'] else 1

if __name__=='__main__':
    sys.exit(main())
