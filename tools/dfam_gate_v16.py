#!/usr/bin/env python3
"""V1.6 nonstructural gauge DfAM Gate A, strictly digital validation."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import trimesh

def validate(folder:Path,report:Path)->dict:
    folder=Path(folder)
    m=json.loads((folder/'manifest.json').read_text('utf-8'))
    assert m['payload_approved'] is False and m['power_safe'] is False
    assert m['preload_selected'] is False
    assert m['housing_bore_fit_is_UNQUALIFIED'] is True
    assert m['NO_spacing_between_matched_bearings'] is True
    assert len(m['dfam_prints'])==2
    checks=[]
    for p in m['dfam_prints']:
        f=folder/(p['name']+'.stl')
        mesh=trimesh.load_mesh(f,force='mesh')
        bbox=mesh.bounds
        r={'name':p['name'],'watertight':bool(mesh.is_watertight),
           'bodies':len(mesh.split()),'zmin_mm':round(float(bbox[0,2]),4),
           'size_mm':[round(float(x),3) for x in mesh.extents],
           'nonload':not p['field_load_approved']}
        assert r['watertight'] and r['bodies']==1 and abs(r['zmin_mm'])<0.04
        assert r['nonload']
        checks.append(r)
    result={'gate':'A','status':'PASS','scope':'only reference meshes and metadata, not manufacturing',
       'checked':checks,'Gate_B':'PENDING','Gate_C':'PENDING','payload_approved':False}
    report.parent.mkdir(exist_ok=True,parents=True)
    report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('V1.6 DfAM Gate A: PASS, 2 nonload gauge STL only')
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--dir',type=Path,default=Path('hardware/cad/v16_generated'))
    a.add_argument('--report',type=Path,default=Path('hardware/cad/v16_generated/dfam-gate-report.json'))
    p=a.parse_args();validate(p.dir,p.report)
