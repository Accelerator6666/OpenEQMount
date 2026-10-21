#!/usr/bin/env python3
"""V1.6 NSK 7008AWDB DB cartridge CAD envelopes, unqualified for manufacture.

Only standard external bearing 40x68x15 outlines are claimed. CAD contains
no precision fit, bearing internals, preload nut thread, retaining screw data,
transfer-cage, independent payload safety or verified camera mounting.
"""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.rotator_db7008_study import BEARING,generate_reports,load_centres_z_mm,dimensions_review

OUT_NAME='OpenEQMount_V16_NSK7008AWDB_DB_SERVICE_CARTRIDGE_UNQUALIFIED.step'
EXPLODED_NAME='OpenEQMount_V16_DB7008_INSTALLATION_SEQUENCE_UNQUALIFIED.step'
ROLE_COLOR={
 'bearing':cq.Color(.93,.70,.37),'stator':cq.Color(.36,.53,.73),
 'shaft':cq.Color(.58,.75,.85),'cap':cq.Color(.47,.64,.58),
 'fastener':cq.Color(.84,.43,.37),'guard':cq.Color(.69,.55,.79),
}

def ring(outer_d:float,inner_d:float,h:float,z:float=0):
    if not (outer_d>inner_d>0 and h>0): raise ValueError('invalid annulus')
    return cq.Workplane('XY').circle(outer_d/2).circle(inner_d/2).extrude(h).translate((0,0,z))

def holes_in_ring(shape,pcd=80.,hole_d=4.5,z0=-15.,length=70.,n=6):
    # bolt clearance only, no thread engagement or torque verification.
    for i in range(n):
        theta=2*math.pi*i/n
        tool=(cq.Workplane('XY').center(pcd/2*math.cos(theta),pcd/2*math.sin(theta))
              .circle(hole_d/2).extrude(length).translate((0,0,z0)))
        shape=shape.cut(tool)
    return shape


def cartridge_parts()->list[dict]:
    """Paired bearings occupy z=[0,30] with no inter-bearing spacers."""
    d=BEARING
    p=[]
    def add(name,s,role,load_carrying_reference=True):
        p.append(dict(name=name,shape=s,role=role,metal_reference=load_carrying_reference))
    # Straight-through bearing entry; nominal ID chosen to visualize insertion, NOT final interference/transition fit.
    housing=holes_in_ring(ring(90,68.2,30,z=0),pcd=80, hole_d=4.5,z0=0,length=30)
    add('V16_STATOR_METAL_68_2_REFERENCE_BORE_NOT_FIT',housing,'stator')
    # Serviceable caps: opening Ø60 mm (< OEM Db max 63); only provisional shoulder contact.
    lowcap=holes_in_ring(ring(89,60,5,z=-5),pcd=80,hole_d=4.5,z0=-5,length=5)
    topcap=holes_in_ring(ring(89,60,5,z=30),pcd=80,hole_d=4.5,z0=30,length=5)
    add('V16_LOWER_REMOVABLE_METAL_OUTER_RING_CAP',lowcap,'cap')
    add('V16_UPPER_REMOVABLE_METAL_OUTER_RING_CAP',topcap,'cap')
    # Only 40x68x15 envelopes; real raceway, ball/cage and face offset do not appear.
    for n,z in enumerate((0.,15.),1):
        add(f'V16_NSK_7008AWDB_RING_{n}_OEM_EXTERNAL_ENVELOPE_ONLY',ring(68,40,15,z),'bearing')
    # Bearing journal extends through adjacent DB pair, with a 48mm metal bottom abutment.
    # A real shaft MUST be one-piece with shoulder; union avoids an illusory bolted shoulder.
    spindle=ring(40,30,47,z=-7).union(ring(48,30,7,z=-7))
    add('V16_HOLLOW_METAL_SPINDLE_WITH_INTEGRAL_48_SHOULDER_NO_TOLERANCE',spindle,'shaft')
    # Upper axial clamp reference (no contact with other metal caps); no thread or keyed locking.
    add('V16_LOCKNUT_ENVELOPE_NO_THREAD_OR_PRELOAD',ring(50,40.2,6,z=32),'fastener')
    add('V16_FLAT_ANTI_LOOSENING_WASHER_PLACEHOLDER_NO_KEY',ring(52,40.2,2,z=30),'fastener')
    # Remote reference plate: mounting geometry unresolved, not OEM adapter.
    add('V16_CAMERA_FIXTURE_INTERFACE_BLANK_NO_CLAMP',ring(102,33,5,z=40),'guard')
    return p


def bed_flat_coupons()->dict[str,cq.Workplane]:
    return {
        'V16_NONLOAD_68MM_BORE_PRINT_CALIBRATION_FLAT':ring(88,68,4,0),
        'V16_NONLOAD_40MM_SHAFT_DIA_CALIBRATION_FLAT':ring(52,40,4,0),
    }


def assembly(parts=None,explode:bool=False):
    a=cq.Assembly(name='V16_7008AWDB_DB_STUDY_NO_LOAD_NO_POWER')
    parts=parts or cartridge_parts()
    offsets={
      'V16_LOWER_REMOVABLE_METAL_OUTER_RING_CAP':-18.,
      'V16_UPPER_REMOVABLE_METAL_OUTER_RING_CAP':18.,
      'V16_NSK_7008AWDB_RING_1_OEM_EXTERNAL_ENVELOPE_ONLY':-5.,
      'V16_NSK_7008AWDB_RING_2_OEM_EXTERNAL_ENVELOPE_ONLY':5.,
      'V16_HOLLOW_METAL_SPINDLE_WITH_INTEGRAL_48_SHOULDER_NO_TOLERANCE':-34.,
      'V16_LOCKNUT_ENVELOPE_NO_THREAD_OR_PRELOAD':32.,
      'V16_FLAT_ANTI_LOOSENING_WASHER_PLACEHOLDER_NO_KEY':28.,
      'V16_CAMERA_FIXTURE_INTERFACE_BLANK_NO_CLAMP':44.,
    }
    for p in parts:
        offset=offsets.get(p['name'],0) if explode else 0
        a.add(p['shape'].translate((0,0,offset)) if offset else p['shape'],
              name=p['name'],color=ROLE_COLOR[p['role']])
    return a


def generate(out:Path)->dict:
    out=Path(out);out.mkdir(exist_ok=True,parents=True)
    parts=cartridge_parts()
    assembly(parts).save(str(out/OUT_NAME),exportType='STEP')
    assembly(parts,explode=True).save(str(out/EXPLODED_NAME),exportType='STEP')
    # Explicit separate metal reference STEP solids for inspecting dimensions and replacement.
    for p in parts:
        cq.exporters.export(p['shape'],str(out/(p['name']+'.step')),exportType='STEP')
    coupons=bed_flat_coupons()
    for name,obj in coupons.items():
        cq.exporters.export(obj,str(out/(name+'.step')),exportType='STEP')
        cq.exporters.export(obj,str(out/(name+'.stl')),exportType='STL',tolerance=.08,angularTolerance=.18)
    report=generate_reports(out)
    manifest={
      'version':'V1.6','architecture':'NSK 7008AWDB matched DB pair, unqualified',
      'main_step':OUT_NAME,'exploded_step':EXPLODED_NAME,
      'assembly_solids':len(parts),
      'bearing_pair_physical_width_mm':30.,
      'bearing_a0_load_centres_mm':46.2,
      'axial_pair_abutting_faces_z_mm':[0.,15.,30.],
      'NO_spacing_between_matched_bearings':True,
      'shaft_bearing_journal_mm':40.,'nominal_housing_bearing_entry_mm':68.2,
      'housing_bore_fit_is_UNQUALIFIED':True,
      'matched_OEM_part':BEARING['exact_catalog_designation'],
      'manufacturer_catalog_source':BEARING['source'],
      'diameter_abutment_review':dimensions_review(),
      'preload_selected':False,'bearing_clearance_CN_NOT_preload':True,
      'shaft_locknut_thread_complete':False,'fastener_strength_qualified':False,
      'camera_mount_tested':False,'power_safe':False,'payload_approved':False,
      'dfam_prints':[{
         'name':name,'role':'nonstructural single-plane PETG dimension coupon',
         'print_orientation':'flat XY at Z=0', 'layer_direction':'+Z',
         'XY_load':'none - bench dimensional gauge only', 'Z_load':'none',
         'min_nominal_wall_mm':6.0 if 'SHAFT' in name else 10.,
         'overhang':'vertical walls, no supports intended (slicer still required)',
         'metal_joint':'none; NEVER trapped in structural joint',
         'material':'PETG fit coupon only','support_in_slicer':'PENDING',
         'print_fit':'PENDING','field_load_approved':False,
         'gate_B':'PENDING','gate_C':'PENDING'
         } for name in coupons],
      'test_status':{'A':'geometry/metadata only','B':'PENDING','C':'PENDING'},
      'critical_uncertainties':report['engineering_blocks'],
    }
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'V1.6 created {len(parts)} reference solids, {len(coupons)} flat PETG gauges; unqualified DB pair')
    return manifest

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=Path(__file__).with_name('v16_generated'))
    opts=a.parse_args();generate(opts.out)
