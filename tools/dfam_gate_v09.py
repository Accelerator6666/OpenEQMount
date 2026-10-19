#!/usr/bin/env python3
"""Gate A only for V0.9 ROT calibration prints; never certifies load safety."""
import argparse
import json
from pathlib import Path
import sys
import trimesh
REQ=('name','material','status','role','print_orientation','layer_direction','load_path',
     'overhang_strategy','metal_joint','min_wall_mm','slicer_gate_B','physical_gate_C',
     'field_load_approved','bbox_mm')

def audit(directory:Path):
    m=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    errors=[];inventory=[]
    if m.get('release')!='V0.9_Gate_A_CONCEPT':errors.append('wrong release')
    if m.get('is_load_qualified') is not False or m.get('is_safe_to_energize') is not False:
        errors.append('illegal qualification state')
    if m.get('ASCOM_INDI_drivers_not_implemented') is not True:
        errors.append('driver status not explicit')
    if m.get('optical_axis_verified') is not False:
        errors.append('optical axis not physically verified')
    if len(m.get('printed_parts',[]))!=3:errors.append('expected 3 non-load print models')
    for p in m.get('printed_parts',[]):
        n=p.get('name','MISSING')
        for key in REQ:
            if key not in p or p[key] in ('',None,[]):errors.append(n+': '+key+' missing')
        if p.get('status')!='prototype_unqualified' or p.get('slicer_gate_B')!='pending' or p.get('physical_gate_C')!='pending' or p.get('field_load_approved') is not False:
            errors.append(n+': incorrect qualification')
        if not (directory/(n+'.step')).exists():errors.append(n+': STEP absent')
        f=directory/(n+'.stl')
        if not f.exists():errors.append(n+': STL absent');continue
        mesh=trimesh.load(f,force='mesh')
        one=len(mesh.split(only_watertight=False))==1
        valid=bool(mesh.is_watertight and one and abs(mesh.bounds[0,2])<.02 and max(mesh.extents[:2])<=220)
        if not valid:errors.append(n+': invalid or non-print-oriented mesh')
        inventory.append({'name':n,'single_body':one,'watertight':bool(mesh.is_watertight)})
    for p in m.get('metal_parts',[]):
        n=p['name']
        if not (directory/(n+'.step')).exists():errors.append(n+': metal STEP absent')
        if (directory/(n+'.stl')).exists():errors.append(n+': forbidden load-bearing metal STL')
    for n in ('OpenEQMount_V09_ROT_AXIS_ONLY_UNQUALIFIED.step',
              'OpenEQMount_V09_THREE_AXIS_MOUNT_CONCEPT_UNQUALIFIED.step'):
        if not (directory/n).exists():errors.append(n+': assembly missing')
    return {'gate':'A digital model ONLY','passed':not errors,'printed_count':len(inventory),
            'gate_B':'pending','gate_C':'pending','load_qualified':False,'errors':errors,'prints':inventory}

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--dir',type=Path,default=Path('hardware/cad/v09_generated'))
    cli.add_argument('--report',type=Path)
    args=cli.parse_args()
    r=audit(args.dir)
    if args.report:
        args.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False,indent=2))
    return 0 if r['passed'] else 1
if __name__=='__main__':sys.exit(main())
