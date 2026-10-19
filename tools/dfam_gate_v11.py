#!/usr/bin/env python3
"""V1.1 digital Gate A checks; never certifies physical welds, retention or payload."""
import argparse,json,sys
from pathlib import Path
import trimesh
FIELDS=('name','status','material','print_orientation','layer_direction','load_path',
        'overhang_strategy','metal_joint','min_wall_mm','slicer_gate_B','physical_gate_C',
        'field_load_approved','bbox_mm')
FALSE_FIELDS=('vendor_DEC_output_PCD23_confirmed','bearing_6808_pair_moment_qualified',
              'camera_or_lens_clamp_implemented','independent_metal_fall_arrest_implemented',
              'hard_stop_moving_contact_implemented','limit_switch_implemented',
              'motor_drive_implemented','safe_to_energize','camera_payload_approved',
              'full_kinematic_collision_proved')

def audit(out:Path):
    mf=json.loads((out/'manifest.json').read_text('utf-8'));errors=[];checked=[]
    if mf.get('release')!='V1.1_DEC_TO_ROT_CONTINUOUS_METAL_CONCEPT_GATE_A':errors.append('incorrect release')
    for key in FALSE_FIELDS:
        if mf.get(key) is not False:errors.append(key+' cannot be qualified')
    if mf.get('DfAM_Gate_B')!='pending' or mf.get('physical_safety_Gate_C')!='pending':errors.append('premature gate closure')
    if not (out/mf.get('assembled_step','')).exists():errors.append('missing combined STEP')
    if mf.get('parts_in_assembly',0)<45:errors.append('incomplete 3-axis assembly')
    if len(mf.get('nonload_printed_parts',[]))!=1:errors.append('expect one loose gauge')
    for p in mf.get('nonload_printed_parts',[]):
        n=p.get('name','')
        for key in FIELDS:
            if not p.get(key) and p.get(key) is not False:errors.append(n+' missing '+key)
        if p.get('field_load_approved') is not False or p.get('slicer_gate_B')!='pending' or p.get('physical_gate_C')!='pending':errors.append(n+' wrongly approved')
        if 'NONLOAD_' not in n:errors.append(n+' missing nonload label')
        for ext in ('.stl','.step'):
            if not (out/(n+ext)).exists():errors.append('missing '+n+ext)
        f=out/(n+'.stl')
        if f.exists():
            m=trimesh.load_mesh(f)
            ok=bool(m.is_watertight and len(m.split(only_watertight=False))==1 and
                    abs(m.bounds[0,2])<.02 and max(m.extents[:2])<=220)
            checked.append({'name':n,'valid':ok})
            if not ok:errors.append(n+' bad mesh')
    for n in mf.get('metal_reference_exports',[]):
        if not (out/(n+'.step')).exists():errors.append(n+' missing STEP')
        if (out/(n+'.stl')).exists():errors.append(n+' MUST NOT be released as printable')
    return {'gate':'A digital only','passed':not errors,'errors':errors,'gauges':checked,
            'Gate_B':'pending','Gate_C':'pending','camera_load_approved':False,
            'motor_power_authorized':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dir',type=Path,default=Path('hardware/cad/v11_generated'))
    p.add_argument('--report',type=Path);a=p.parse_args();r=audit(a.dir)
    if a.report:a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(r,ensure_ascii=False,indent=2))
    sys.exit(0 if r['passed'] else 1)
