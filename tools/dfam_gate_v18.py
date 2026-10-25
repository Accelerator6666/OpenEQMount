#!/usr/bin/env python3
"""V1.8 DfAM Gate A checks a NONSTRUCTURAL PETG datum coupon, never load ratings."""
import argparse,json
from pathlib import Path
import trimesh

def validate(folder:Path,report:Path):
    m=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    assert m['release']=='V1.8' and m['payload_approved'] is False
    assert m['safe_to_energize'] is False and not m['fail_safe_completed']
    assert m['gate_B']==m['gate_C']=='PENDING'
    assert m['metal_primary_path_only'] and m['independent_payload_tether_attached'] is False
    assert m['whole_solids']==66 and m['local_joint_solids']==16
    checks=[]
    for item in m['nonload_printed_parts']:
        assert item['field_load_approved'] is False and item['gate_B']=='PENDING'
        assert item['print_orientation']=='XY flat Z0'
        mesh=trimesh.load_mesh(folder/(item['name']+'.stl'),force='mesh')
        assert mesh.is_watertight and len(mesh.split())==1
        assert abs(float(mesh.bounds[0,2]))<.04
        assert 2.95<=float(mesh.extents[2])<=3.05
        checks.append(dict(name=item['name'],watertight=True,print_Z_min_mm=float(mesh.bounds[0,2]),dimensions_mm=mesh.extents.tolist()))
    report.parent.mkdir(parents=True,exist_ok=True)
    res=dict(gate='A',status='PASS',checked=checks,not_manufacturing_or_field_certification=True,
             Gate_B='PENDING',Gate_C='PENDING')
    report.write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return res
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dir',type=Path,default=Path('hardware/cad/v18_generated'))
    p.add_argument('--report',type=Path,default=Path('hardware/cad/v18_generated/dfam-gate-report.json'))
    a=p.parse_args();print(validate(a.dir,a.report))
