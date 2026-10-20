#!/usr/bin/env python3
"""V1.5 gate A: digital mesh sanity ONLY, not sliced, printed or qualified."""
import argparse,json
from pathlib import Path
import trimesh

def main(root:Path,report:Path):
    man=json.loads((root/'manifest.json').read_text('utf8'))
    assert man['safe_to_energize'] is False and man['payload_approved'] is False
    assert man['RU66_35mm_requires_redesign'] is True
    checks=[]
    for r in man['nonload_printed_parts']:
        f=root/(r['name']+'.stl')
        mesh=trimesh.load_mesh(str(f),force='mesh')
        checks.append({'name':r['name'],'exists':f.exists(),'watertight':bool(mesh.is_watertight),
           'components':len(mesh.split()),'zmin_mm':round(float(mesh.bounds[0,2]),5),
           'mesh_extent_mm':mesh.extents.tolist(),'nonload_only':r['field_load_approved'] is False})
        assert checks[-1]['watertight'] and checks[-1]['components']==1
        assert abs(checks[-1]['zmin_mm'])<.05
        assert checks[-1]['nonload_only']
    data={'gate':'A','result':'PASS','qualification':'DIGITAL ONLY','checks':checks,
       'Gate_B':'PENDING','Gate_C':'PENDING','payload_approved':False}
    report.parent.mkdir(exist_ok=True,parents=True)
    report.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print('V1.5 DfAM digital Gate A: PASS',len(checks),'nonload flat-print coupons')
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dir',type=Path,default=Path('hardware/cad/v15_generated'))
    p.add_argument('--report',type=Path,default=Path('hardware/cad/v15_generated/dfam-gate-report.json'))
    a=p.parse_args();main(a.dir,a.report)
