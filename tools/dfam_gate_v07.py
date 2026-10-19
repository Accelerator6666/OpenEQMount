#!/usr/bin/env python3
"""V0.7 Gate A digital/metadata only; NEVER a structural strength certificate."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import trimesh
REQUIRED=('name','material','status','role','print_orientation','layer_direction',
 'load_path','overhang_strategy','metal_joint','min_wall_mm',
 'slicer_gate_B','physical_gate_C','bbox_mm','field_load_approved')

def audit(root:Path):
    m=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    errors=[]; inventory=[]
    if m.get('release')!='V0.7' or m.get('status')!='prototype_unqualified_Gate_A_only':
        errors.append('Unexpected release/status')
    if m.get('manufacturing_approval') is not False or m.get('mechanical_load_approved') is not False:
        errors.append('Invalid certification flags')
    if m.get('input_coupling_verified') is not False or m.get('OEM_bolt_phase_verified') is not False:
        errors.append('Unverified real input coupling/hole orientation cannot be approved')
    if m.get('payload_rated_kg') is not None:errors.append('No payload rating permitted')
    if len(m.get('printed_parts',[]))!=3:errors.append('Expected 3 non-load printing parts')
    if len(m.get('metal_parts',[]))!=13:errors.append('Expected 13 metal-only references')
    for entry in m.get('printed_parts',[]):
        name=entry.get('name','MISSING')
        for k in REQUIRED:
            if k not in entry or entry[k] in (None,'',[]):errors.append(name+': no '+k)
        if (entry.get('status')!='prototype_unqualified' or entry.get('slicer_gate_B')!='pending'
            or entry.get('physical_gate_C')!='pending' or entry.get('field_load_approved') is not False):
            errors.append(name+': illegitimate readiness state')
        for ext in ('.stl','.step'):
            if not (root/(name+ext)).is_file():errors.append(name+': missing '+ext)
        if (root/(name+'.stl')).exists():
            mesh=trimesh.load(root/(name+'.stl'),force='mesh')
            bodies=len(mesh.split(only_watertight=False))
            if not mesh.is_watertight or bodies != 1:errors.append(name+': mesh not single watertight')
            if abs(float(mesh.bounds[0,2]))>.02:errors.append(name+': bad Z bed alignment')
            if max(mesh.extents[:2])>220:errors.append(name+': exceeds 220mm bed')
            inventory.append({'name':name,'watertight':bool(mesh.is_watertight),
                              'connected':bodies==1})
    for part in m.get('metal_parts',[]):
        name=part['name']
        if not (root/(name+'.step')).is_file():errors.append(name+': missing metal STEP')
        if (root/(name+'.stl')).exists():errors.append(name+': metal FDM export prohibited')
    for axis in ('ra','dec'):
        if not (root/f'OpenEQMount_V07_{axis}_BELT_PITCH_ONLY_assembly.step').exists():
            errors.append('Missing belt test assembly '+axis)
    if not (root/'OpenEQMount_V07_RA_STATOR_UNQUALIFIED_assembly.step').exists():
        errors.append('Missing RA fixed body assembly')
    return {'release':'V0.7','gate':'A: geometry and document contract only',
      'result':'FAIL' if errors else 'PASS','not_load_rated':True,
      'gate_B':'PENDING','gate_C':'PENDING','printed_inventory':inventory,'errors':errors}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--dir',type=Path,default=Path(__file__).parents[1]/'hardware/cad/v07_generated')
    p.add_argument('--report',type=Path)
    args=p.parse_args();res=audit(args.dir)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(res,ensure_ascii=False,indent=2))
    return bool(res['errors'])
if __name__=='__main__':sys.exit(main())
