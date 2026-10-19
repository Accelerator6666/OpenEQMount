#!/usr/bin/env python3
"""Strict Gate A for V0.6 FDM pieces; NEVER makes structural claims."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import trimesh
REQUIRED=('name','material','status','role','print_orientation','layer_direction',
 'load_path','overhang_strategy','metal_joint','min_wall_mm','slicer_gate_B','physical_gate_C','bbox_mm')

def check(root:Path):
    d=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    errors=[]; parts=[]
    if d.get('release')!='V0.6' or d.get('status')!='prototype_unqualified_Gate_A_only':
        errors.append('Unexpected release status')
    if len(d.get('printed_parts',[]))!=4:errors.append('Need four controlled printed parts')
    if len(d.get('metal_parts',[]))!=11:errors.append('Metal reference inventory mismatch')
    for p in d.get('printed_parts',[]):
        n=p.get('name','UNKNOWN')
        for field in REQUIRED:
            if p.get(field) in (None,'',[]):errors.append(n+': missing '+field)
        if p.get('status')!='prototype_unqualified' or p.get('slicer_gate_B')!='pending' or p.get('physical_gate_C')!='pending':
            errors.append(n+': failed safety status')
        for ext in ('.step','.stl'):
            if not (root/(n+ext)).is_file():errors.append(n+': missing '+ext)
        if (root/(n+'.stl')).is_file():
            mesh=trimesh.load(root/(n+'.stl'),force='mesh')
            bodies=len(mesh.split(only_watertight=False))
            if not mesh.is_watertight or bodies!=1:errors.append(n+': nonclosed STL')
            if abs(float(mesh.bounds[0][2]))>.02:errors.append(n+': incorrect build plate')
            if max(mesh.extents[:2])>220:errors.append(n+': oversized print')
            parts.append({'name':n,'closed':bool(mesh.is_watertight),'connected':bodies==1})
    for m in d.get('metal_parts',[]):
        n=m['name']
        if not (root/(n+'.step')).is_file():errors.append(n+': missing STEP')
        if (root/(n+'.stl')).exists():errors.append(n+': unsafe METAL-as-STL export')
    if not (root/'OpenEQMount_V06_UNQUALIFIED_assembly.step').exists():errors.append('Assembly STEP missing')
    return {'release':'V0.6','gate':'A: digital geometry only','result':'FAIL' if errors else 'PASS',
            'not_load_rated':True,'gate_B':'PENDING','gate_C':'PENDING','parts':parts,'errors':errors}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--dir',type=Path,default=Path(__file__).parents[1]/'hardware/cad/v06_generated')
    p.add_argument('--report',type=Path)
    a=p.parse_args();result=check(a.dir)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return bool(result['errors'])
if __name__=='__main__':sys.exit(main())
