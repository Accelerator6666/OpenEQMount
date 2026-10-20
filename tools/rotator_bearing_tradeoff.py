#!/usr/bin/env python3
"""V1.5 bearing architecture *envelope* comparisons; NOT bearing life or ratings.

Two simple supports are mathematical abstractions. A 7008 DB matched/preloaded pair
and a THK RU66 integrated ring require OEM-specific moment/stiffness calculations.
"""
from __future__ import annotations
import argparse, csv, json
from dataclasses import asdict, dataclass
from pathlib import Path

G = 9.80665
CAMERA_MOUNT_FACE_Z_MM = 75.0

@dataclass(frozen=True)
class Candidate:
    key: str
    product: str
    kind: str
    bore_mm: float
    od_mm: float
    width_mm: float
    count: int
    theoretical_support_centers_mm: tuple[float, ...]
    previous_40mm_spindle_compatible: bool
    rated_static_radial_kN_per_bearing: float | None = None
    manufacturer_reference: str = ''

CANDIDATES = (
    Candidate('6808_pair','6808-2RS', 'two_deep_groove',40,52,7,2,(10.5,40.5),True,
              None,'ISO envelope; exact manufacturer and rating not selected'),
    Candidate('7008_db_pair','NSK 7008C family','two_angular_contact_DB_proposed',40,68,15,2,(7.5,57.5),True,
              None,'https://www.nsk.com/eu-en/engineering/7008ctrv1vsuelp4y-apn.html'),
    Candidate('ru66_single','THK RU66UUCC0', 'integrated_cross_roller',35,95,15,1,(32.0,),False,
              22.3,'https://store-na.thk.com/Product/ru66uucc0'),
)

def simple_support_radial_reactions(force_n: float, load_z_mm: float, supports_mm:tuple[float,float]):
    if force_n < 0: raise ValueError('force cannot be negative')
    a,b=supports_mm
    if b <= a: raise ValueError('support ordering invalid')
    # Load lies past far support. At b reaction acts with the load, at a the opposite way.
    b_reaction_n=force_n*(load_z_mm-a)/(b-a)
    a_opposed_n=force_n*(load_z_mm-b)/(b-a)
    return {'near_support_opposed_abs_N':round(a_opposed_n,5),
            'far_support_same_direction_abs_N':round(b_reaction_n,5),
            'center_distance_mm':round(b-a,5),
            'simple_support_only_NOT_a_real_bearing_internal_load':True}

def case(mass_kg:float, cg_from_face_mm:float, eccentricity_mm:float=20.0)->dict:
    if not (0<mass_kg<=20 and 0<=cg_from_face_mm<=400 and 0<=eccentricity_mm<=200):
        raise ValueError('illustrative cases outside permitted mathematical range')
    F=mass_kg*G
    z=CAMERA_MOUNT_FACE_Z_MM+cg_from_face_mm
    rows=[]
    for c in CANDIDATES:
        r={'key':c.key,'product':c.product,'kind':c.kind,
           'mass_kg':mass_kg,'cg_from_face_mm':cg_from_face_mm,
           'radial_eccentricity_mm':eccentricity_mm,
           'transverse_force_N':round(F,5),
           'cg_z_mm':round(z,5),
           'ext_bending_moment_about_z0_Nm':round(F*z/1000,5),
           'ideal_gravity_roll_torque_Nm':round(F*eccentricity_mm/1000,5),
           'hole_pattern_OEM_verified':False,
           'actual_stiffness_known':False,
           'bearing_moment_capacity_verified':False,
           'rotation_accuracy_verified':False,
           'payload_certified':False,
           'claim_comparable_bearing_rating':False}
        if len(c.theoretical_support_centers_mm)==2:
            r.update(simple_support_radial_reactions(F,z,c.theoretical_support_centers_mm))
            r['status']='Illustrative two-simple-support reaction only; contact geometry/preload NOT modeled'
        else:
            r.update({'near_support_opposed_abs_N':None,'far_support_same_direction_abs_N':None,
                      'center_distance_mm':None,'simple_support_only_NOT_a_real_bearing_internal_load':False,
                      'status':'RU single crossed roller: do NOT apply two-support reactions; obtain OEM moment and mounting calculation'})
        rows.append(r)
    return {'assumptions':{'G_m_s2':G,'camera_mount_face_z_mm':CAMERA_MOUNT_FACE_Z_MM,
            'loading':'transverse gravity illustrative worst-orientation envelope, no dynamics',
            'preload_and_internal_load_distribution':'not calculated'},'results':rows}

def write_reports(out:Path, mass_kg:float=4,cg_from_face_mm:float=80,eccentricity_mm:float=20)->dict:
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    baseline=case(mass_kg,cg_from_face_mm,eccentricity_mm)
    rows=[r for m in (3.,4.,5.) for x in (40.,80.,120.) for e in (0.,20.,40.)
          for r in case(m,x,e)['results']]
    with (out/'v15_bearing_support_sensitivity_UNQUALIFIED.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    report={
      'release':'V1.5_COMPARE_BEARING_ARCHITECTURES_DIGITAL_GATE_A_NO_LOAD_APPROVAL',
      'candidate_boundary_dimensions':[asdict(c) for c in CANDIDATES],
      'baseline':baseline,
      'sweep_count':len(rows),
      'output_csv':'v15_bearing_support_sensitivity_UNQUALIFIED.csv',
      'critical_uncertainties':[
        '7008 single bearing catalogue radial C/C0 ratings cannot be used as paired-bearing moment/stiffness ratings.',
        '7008 is a family: exact matched DB pair contact angle and preload are not selected.',
        'RU66 inner bore is 35 mm, incompatible with existing 40 mm ROT spindle; a full redesign is mandatory.',
        'RU66 C0=22.3 kN is a basic radial static rating, NOT an allowable tilting moment.',
        'Two-deep-groove 6808 supports cannot be assumed preloaded or suitable for precision tracking.',
        'Candidate CAD holes/races and shoulder interfaces are visual reference only, NOT OEM CAD.',
        'No actual camera clamp, independent tether, fastener strength, runout, thermal, safety, or life validation.',
      ],
      'gates':{'Gate_A':'math and visual envelope only','Gate_B':'pending','Gate_C':'pending'},
      'power_on_allowed':False,'camera_payload_allowed':False,
    }
    (out/'v15_bearing_tradeoff_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=Path('hardware/cad/v15_generated'))
    args=parser.parse_args()
    r=write_reports(args.out)
    print('V1.5 theoretical bearing cases:',r['sweep_count'])
