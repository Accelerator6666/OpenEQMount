#!/usr/bin/env python3
"""Gate A verifier for V0.5. NEVER treat this as mechanical certification."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import trimesh

REQUIRED=('name','material','status','role','print_orientation','layer_direction',
          'load_path','overhang_strategy','metal_joint','min_wall_mm',
          'slicer_gate_B','physical_gate_C','bbox_mm')


def check(directory:Path):
    data=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    errors=[];items=[]
    if data.get('release')!='V0.5':errors.append('wrong release')
    if data.get('status')!='prototype_unqualified_Gate_A_only':errors.append('not unqualified')
    pp=data.get('printed_parts',[])
    if len(pp)<5:errors.append('missing printable pieces')
    if len(data.get('metal_parts',[]))<7:errors.append('missing metal mechanism references')
    for part in pp:
        name=part.get('name','UNKNOWN')
        for key in REQUIRED:
            if not part.get(key):errors.append(f'{name}: missing {key}')
        if part.get('slicer_gate_B')!='pending' or part.get('physical_gate_C')!='pending':
            errors.append(f'{name}: mechanical qualification must remain pending')
        if part.get('status')!='prototype_unqualified':errors.append(f'{name}: bad status')
        for suffix in ('.stl','.step'):
            if not (directory/(name+suffix)).exists():errors.append(f'{name}: missing {suffix}')
        path=directory/(name+'.stl')
        if path.exists():
            mesh=trimesh.load(path,force='mesh')
            count=len(mesh.split(only_watertight=False))
            if not mesh.is_watertight or count!=1:errors.append(f'{name}: mesh invalid, bodies {count}')
            if abs(float(mesh.bounds[0][2]))>0.01:errors.append(f'{name}: not on Z=0')
            if max(mesh.extents[0],mesh.extents[1])>220:errors.append(f'{name}: bed oversize')
            items.append({'name':name,'watertight':bool(mesh.is_watertight),'bodies':count,
                'extents_mm':mesh.extents.round(2).tolist()})
    for metal in data.get('metal_parts',[]):
        if not (directory/(metal['name']+'.step')).exists():errors.append('missing metal '+metal['name'])
    if not (directory/'OpenEQMount_V05_UNQUALIFIED_assembly.step').exists():errors.append('missing assembly')
    # Gate A deliberately does NOT check print supports, fastening, tolerances or load ratings.
    return dict(version='V0.5',gate='A geometry only',result='FAIL' if errors else 'PASS',
         not_load_qualified=True,gate_B='PENDING',gate_C='PENDING',
         items=items,errors=errors)


def main():
    p=argparse.ArgumentParser();p.add_argument('--dir',type=Path,default=Path(__file__).parents[1]/'hardware/cad/v05_generated')
    p.add_argument('--report',type=Path)
    a=p.parse_args();result=check(a.dir)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'gate':result['gate'],'result':result['result'],'printed':len(result['items']),'errors':result['errors']},indent=2))
    return 1 if result['errors'] else 0
if __name__=='__main__':sys.exit(main())
