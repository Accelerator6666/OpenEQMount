#!/usr/bin/env python3
"""V1.0 digital Gate A only; intentionally refuses any safety qualification."""
import argparse
import json
import sys
from pathlib import Path
import trimesh

FIELDS=('name','status','material','print_orientation','layer_direction','load_path',
        'overhang_strategy','metal_joint','min_wall_mm','slicer_gate_B','physical_gate_C',
        'field_load_approved','bbox_mm')


def audit(out:Path):
    m=json.loads((out/'manifest.json').read_text('utf-8'));err=[];parts=[]
    if m.get('release')!='V1.0_ROT_BENCH_GATE_A':err.append('unexpected release')
    for key in ('load_qualified','safe_to_energize','camera_adapter_implemented',
                'physical_switches_implemented','DEC_output_mated','camera_fall_restraint_qualified'):
        if m.get(key) is not False:err.append('illegal qualification flag: '+key)
    if len(m.get('metal_parts',[]))!=8:err.append('missing metal references')
    if len(m.get('printed_parts',[]))!=3:err.append('missing print candidates')
    for p in m.get('printed_parts',[]):
        name=p.get('name','MISSING')
        for key in FIELDS:
            if key not in p or p[key] in ('',None,[]):err.append(name+' missing '+key)
        if p.get('status')!='prototype_unqualified' or p.get('field_load_approved') is not False:
            err.append(name+' wrongly approved')
        if p.get('slicer_gate_B')!='pending' or p.get('physical_gate_C')!='pending':err.append(name+' gate prematurely closed')
        for ext in ('.step','.stl'):
            if not (out/(name+ext)).exists():err.append(name+' missing '+ext)
        f=out/(name+'.stl')
        if f.exists():
            mesh=trimesh.load_mesh(f)
            ok=bool(mesh.is_watertight and len(mesh.split(only_watertight=False))==1
                    and abs(mesh.bounds[0,2])<0.02 and max(mesh.extents[:2])<=220)
            if not ok:err.append(name+' mesh/plate invalid')
            parts.append({'name':name,'digital_mesh_valid':ok})
    for p in m.get('metal_parts',[]):
        n=p['name']
        if not (out/(n+'.step')).exists():err.append(n+' STEP missing')
        if (out/(n+'.stl')).exists():err.append(n+' structural part exported as STL')
    if not (out/'OpenEQMount_V10_ROTATOR_BENCH_UNQUALIFIED.step').exists():
        err.append('assembly STEP missing')
    return {'gate':'A digital only','passed':not err,'errors':err,
            'Gate_B':'pending','Gate_C':'pending','load_qualified':False,'parts':parts}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dir',type=Path,default=Path('hardware/cad/v10_generated'))
    p.add_argument('--report',type=Path);a=p.parse_args();result=audit(a.dir)
    if a.report:a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(0 if result['passed'] else 1)
