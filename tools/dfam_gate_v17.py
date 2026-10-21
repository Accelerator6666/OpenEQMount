#!/usr/bin/env python3
"""V1.7 digital DfAM A: validates only PETG NONSTRUCTURAL fit gauge."""
import json,argparse
from pathlib import Path
import trimesh

def validate(folder:Path,report:Path):
    m=json.loads((folder/'manifest.json').read_text())
    assert m['payload_approved'] is False and m['safe_to_energize'] is False
    assert m['previous_6808_parts_removed'] is True
    assert m['spindle_camera_connection_qualified'] is False
    assert m['gate_B']==m['gate_C']=='PENDING'
    checked=[]
    for it in m['nonload_printed_parts']:
        assert it['field_load_approved'] is False
        mesh=trimesh.load_mesh(folder/(it['name']+'.stl'),force='mesh')
        assert mesh.is_watertight and len(mesh.split())==1
        assert abs(mesh.bounds[0,2])<0.03
        checked.append(dict(name=it['name'],watertight=True,zmin=float(mesh.bounds[0,2]),size=mesh.extents.tolist()))
    out=dict(gate='A',status='PASS',checked=checked,not_field_approved=True,Gate_B='PENDING',Gate_C='PENDING')
    report.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print('V1.7 DfAM Gate A pass; field safety NOT established.')
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dir',type=Path,default=Path('hardware/cad/v17_generated'))
    p.add_argument('--report',type=Path,default=Path('hardware/cad/v17_generated/dfam-gate-report.json'))
    a=p.parse_args();validate(a.dir,a.report)
