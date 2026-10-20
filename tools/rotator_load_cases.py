#!/usr/bin/env python3
"""V1.4 ROT load-case arithmetic; preliminary bounding assumptions, NO qualification.

Axis: local Z; bearing centers 10.5 and 40.5 mm; camera mounting plane z75.
'Radial reactions' are a single illustrative gravity-perpendicular-axis case
with gravity aligned to the axial cantilever, NOT a certified maximum over poses.
Axial gravity / eccentric loading and dynamic accelerations need separate FEA.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import argparse, csv, json, math
from pathlib import Path

GRAVITY=9.80665
BEARINGS_MM=(10.5,40.5)
MOUNTING_FACE_Z_MM=75.0
ROT_BELT_REDUCTION=4.0

@dataclass(frozen=True)
class LoadCase:
    mass_kg:float
    cg_from_mount_mm:float
    eccentricity_mm:float
    illustration_multiplier:float=1.0
    def __post_init__(self):
        if not (0 < self.mass_kg <= 20):raise ValueError('mass must be positive and <=20 kg (math guard, not rating)')
        if not (0<=self.cg_from_mount_mm<=400):raise ValueError('CG axial offset 0..400mm only')
        if not (0<=self.eccentricity_mm<=200):raise ValueError('CG radial eccentricity 0..200mm only')
        if not (1<=self.illustration_multiplier<=5):raise ValueError('illustration multiplier 1..5 only')

def estimate(case:LoadCase)->dict:
    a,b=BEARINGS_MM
    x=MOUNTING_FACE_Z_MM+case.cg_from_mount_mm
    f=case.mass_kg*GRAVITY*case.illustration_multiplier
    # Transverse force applied at axial CG; bearing pair reaction forces may
    # point in opposite directions. Neither bearing contact angle nor preload
    # is known, so do NOT compare these with catalogue C / C0 ratings.
    reaction_near_n=f*(x-a)/(b-a)
    reaction_far_n=f*(x-b)/(b-a)
    moment_n_m=f*math.hypot((x-(a+b)/2)/1000,case.eccentricity_mm/1000)
    roll_torque_n_m=f*case.eccentricity_mm/1000
    # No friction/efficiency and no acceleration torque assumed here.
    motor_ideal_n_m=roll_torque_n_m/ROT_BELT_REDUCTION
    return {
        **asdict(case),
        'cg_z_mm':round(x,3),'gravity_force_N':round(f,4),
        'radial_reaction_upper_N_example':round(reaction_near_n,4),
        'radial_reaction_lower_N_example_opposite':round(reaction_far_n,4),
        'cg_moment_about_bearing_midpoint_Nm_envelope':round(moment_n_m,4),
        'roll_gravity_torque_Nm_envelope':round(roll_torque_n_m,4),
        'motor_static_torque_Nm_ideal_no_losses':round(motor_ideal_n_m,4),
        'bearing_rating_comparison_permitted':False,
        'system_payload_approved':False,
    }

def grid_cases():
    # 3-5 kg remains TARGET, not demonstrated capacity.
    return [estimate(LoadCase(m,z,e,k)) for k in (1.,2.) for m in (3.,4.,5.)
            for z in (40.,80.,120.) for e in (0.,20.,40.)]

def write_reports(out:Path, nominal:LoadCase=LoadCase(4.,80.,20.)):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    cases=grid_cases()
    with (out/'rotator_load_cases_ILLUSTRATIVE.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(cases[0]));writer.writeheader();writer.writerows(cases)
    data={
       'release':'V1.4_LOAD_ENVELOPE_GATE_A_NOT_QUALIFIED',
       'units':'kg, mm, N, Nm',
       'gravity_m_per_s2':GRAVITY,
       'bearings_candidate':'2x 6808-2RS, 40x52x7 mm (NO manufacturer load verification)',
       'bearing_z_centers_mm':list(BEARINGS_MM),
       'camera_mount_face_z_mm':MOUNTING_FACE_Z_MM,
       'rot_belt_ideal_ratio':ROT_BELT_REDUCTION,
       'nominal_example':estimate(nominal),
       'case_count':len(cases),
       'cases_csv':'rotator_load_cases_ILLUSTRATIVE.csv',
       'two_times_multiplier_is_NOT_safety_factor_or_rating':True,
       'reaction_model_is_complete':False,
       'reaction_model_limit':'Radial reaction example under gravity perpendicular to optical axis; ignores true contact stiffness, races, shaft/bridge deflection and simultaneous axial/radial loads.',
       'roll_torque_model_limit':'Gravity eccentricity only; ignores belt friction, transmission efficiency, tracking acceleration and motor holding-current derating.',
       'preload_selected':False,'bearing_rated':False,'power_authorized':False,'camera_load_authorized':False,
       'gates':{'A':'illustrative mathematical checks only','B':'pending','C':'pending'},
    }
    (out/'rotator_load_report.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return data

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=Path('hardware/cad/v14_generated'))
    ap.add_argument('--mass-kg',type=float,default=4.)
    ap.add_argument('--cg-from-mount-mm',type=float,default=80.)
    ap.add_argument('--eccentricity-mm',type=float,default=20.)
    ap.add_argument('--multiplier',type=float,default=1.)
    a=ap.parse_args()
    d=write_reports(a.out,LoadCase(a.mass_kg,a.cg_from_mount_mm,a.eccentricity_mm,a.multiplier))
    print(json.dumps(d['nominal_example'],indent=2,ensure_ascii=False))
