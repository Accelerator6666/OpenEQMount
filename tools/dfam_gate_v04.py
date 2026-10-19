#!/usr/bin/env python3
"""Digital DfAM Gate A for V0.4 bench-only prints; never a strength certification."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import trimesh

REQUIRED=('name','material','status','role','print_orientation','layer_direction',
          'load_path','overhang_strategy','metal_joint','min_wall_mm',
          'slicer_gate_B','physical_gate_C','bbox_mm')

def evaluate(directory:Path)->dict:
    data=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    failures=[];items=[]
    if data.get('release')!='V0.4':failures.append('wrong manifest version')
    if data.get('status')!='prototype_unqualified_Gate_A_only':failures.append('status must be unqualified')
    for record in data.get('printed_parts',[]):
        name=record.get('name','UNNAMED')
        for k in REQUIRED:
            if not record.get(k):failures.append(f'{name}: missing {k}')
        if record.get('status')!='prototype_unqualified':failures.append(f'{name}: invalid approval state')
        if record.get('slicer_gate_B')!='pending' or record.get('physical_gate_C')!='pending':
            failures.append(f'{name}: unearned Gate B/C status')
        stl=directory/f'{name}.stl';step=directory/f'{name}.step'
        if not stl.exists() or not step.exists():
            failures.append(f'{name}: missing STL or STEP');continue
        mesh=trimesh.load(stl,force='mesh')
        bad=not mesh.is_watertight or len(mesh.split(only_watertight=False))!=1
        if bad:failures.append(f'{name}: open or disconnected mesh')
        if abs(mesh.bounds[0,2])>0.01:failures.append(f'{name}: not placed on print bed')
        if max(mesh.extents[0],mesh.extents[1])>220.001:failures.append(f'{name}: exceeds 220 mm square bed')
        items.append({'name':name,'watertight':mesh.is_watertight,
                      'body_count':len(mesh.split(only_watertight=False)),
                      'extent_mm':mesh.extents.round(2).tolist()})
    for record in data.get('metal_parts',[]):
        name=record.get('name','UNNAMED')
        if not (directory/f'{name}.step').exists():failures.append(f'missing metal STEP: {name}')
    if len(items)<5:failures.append('expected >=5 printable gauge/cover parts')
    if not (directory/'OpenEQMount_V04_BENCH_assembly.step').exists():
        failures.append('missing assembly STEP')
    return {'release':'V0.4','gate':'A digital-only',
        'result':'PASS' if not failures else 'FAIL',
        'explicit_not_load_qualified':True,'slicer_gate_B':'PENDING','physical_gate_C':'PENDING',
        'parts_checked':len(items),'items':items,'failures':failures}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dir',type=Path,default=Path(__file__).parents[1]/'hardware/cad/v04_generated')
    ap.add_argument('--report',type=Path)
    a=ap.parse_args();r=evaluate(a.dir)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r[k] for k in ('gate','result','parts_checked','failures')},indent=2))
    return 0 if r['result']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
