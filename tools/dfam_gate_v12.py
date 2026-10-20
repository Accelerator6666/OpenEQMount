#!/usr/bin/env python3
"""OpenEQMount V1.2 CAD / DfAM Gate A: purely digital, not a safety certificate."""
import argparse,json,sys
from pathlib import Path
import trimesh
FALSE=('outer_ring_retention_path_assembled','inner_ring_positive_retention_qualified',
       'bearing_preload_defined','approved_bearing_fit','camera_mating_plate_qualified',
       'fall_arrest_complete','fall_arrest_anchor_strength_qualified','stop_strength_qualified',
       'stop_fasteners_qualified','independent_limit_switches_implemented',
       'safe_to_energize','payload_approved','full_RA_DEC_ROT_collision_proved')

def audit(folder):
    f=Path(folder);m=json.loads((f/'manifest.json').read_text('utf-8'));fail=[];reports=[]
    if m.get('release')!='V1.2_ROT_CARTRIDGE_STOP_CONTACT_GATE_A':fail.append('version')
    for k in FALSE:
        if m.get(k) is not False:fail.append(f'Unsafe approval: {k}')
    if m.get('Gate_B')!='pending' or m.get('Gate_C')!='pending':fail.append('physical gates not pending')
    if m.get('stop_contacts_beyond_soft_range') is not True or m.get('cleared_at_soft_range') is not True:fail.append('stop contact sweep')
    if m.get('parts_in_assembly',0)<60:fail.append('missing pieces')
    if not (f/m.get('assembled_step','')).is_file():fail.append('missing assembly')
    for p in m.get('metal_reference_exports',[]):
        if not (f/(p+'.step')).exists():fail.append('missing metal STEP '+p)
        if (f/(p+'.stl')).exists():fail.append('NO printable load-part '+p)
    for p in m.get('nonload_printed_parts',[]):
        n=p.get('name','');src=f/(n+'.stl')
        if not src.exists() or not (f/(n+'.step')).exists():fail.append('missing gauge '+n);continue
        if 'NONLOAD_' not in n or p.get('field_load_approved') is not False:fail.append('unsafe gauge '+n)
        if p.get('slicer_gate_B')!='pending' or p.get('physical_gate_C')!='pending':fail.append('gates '+n)
        mesh=trimesh.load_mesh(src)
        ok=bool(mesh.is_watertight and len(mesh.split(only_watertight=False))==1 and
                abs(mesh.bounds[0,2])<.02 and max(mesh.extents[:2])<=220)
        reports.append(dict(name=n,watertight_single_flat=ok))
        if not ok:fail.append('invalid STL '+n)
    if len(reports)!=2:fail.append('expected 2 coupons')
    return dict(gate='A digital only',passed=not fail,errors=fail,printed=reports,Gate_B='pending',Gate_C='pending',qualified_for_motor_or_camera=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dir',type=Path,default=Path('hardware/cad/v12_generated'))
    p.add_argument('--report',type=Path);a=p.parse_args();r=audit(a.dir)
    if a.report:a.report.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(r,indent=2,ensure_ascii=False));sys.exit(0 if r['passed'] else 1)
