#!/usr/bin/env python3
"""NSK 7008AWDB paired DB *layout* arithmetic, never preload/life approval.

NSK a0=46.2mm is bearing pair LOAD-CENTRE SPACING, not the 30mm external
width and not the independently modelled two-radial-support stiffness.
Do not use support reactions as individual bearing internal force or lifetime.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

NSK_URL = 'https://www.nsk.com/engineering/products/bearings/ball-bearings/angular-contact-ball-bearings/matched-angular-contact-ball-bearings/7008awdb-apn.html'
GRAVITY = 9.80665
BEARING = {
    'exact_catalog_designation':'7008AWDB', 'manufacturer':'NSK',
    'db_arrangement':'back_to_back', 'contact_angle_deg':30.0,
    'bore_mm':40.0,'outside_diameter_mm':68.0,'matched_pair_width_mm':30.0,
    'single_ring_width_mm':15.0,'manufacturer_a0_load_centres_mm':46.2,
    'shaft_abutment_da_min_mm':46.0,'housing_abutment_Db_max_mm':63.0,
    'corner_fillet_ra_max_mm':1.0,'corner_fillet_rb_max_mm':0.6,
    'nominal_pair_internal_clearance':'CN (NOT confirmed preload)',
    'dynamic_radial_catalog_rating_N':35000.0,
    'static_radial_catalog_rating_N':31000.0,
    'source':NSK_URL,
}
CAMERA_FACE_Z_MM=75.0  # illustrative, not verified V1.4 payload datum


def load_centres_z_mm() -> tuple[float,float]:
    """DB pair outer faces z=0, z=30; a0 centre geometry z=-8.1, 38.1."""
    mid=BEARING['matched_pair_width_mm']/2
    half=BEARING['manufacturer_a0_load_centres_mm']/2
    return (round(mid-half,6),round(mid+half,6))


def external_simple_reactions(mass_kg:float, cg_from_face_mm:float, eccentricity_mm:float=20.0)->dict:
    """Rigid simple-support equilibrium demonstration; NOT actual 7008 internal loads."""
    if not (.1<=mass_kg<=20 and 0<=cg_from_face_mm<=350 and 0<=eccentricity_mm<=200):
        raise ValueError('invalid bounded illustrative input')
    a,b=load_centres_z_mm()
    force=mass_kg*GRAVITY
    z=CAMERA_FACE_Z_MM+cg_from_face_mm
    # For a point load beyond the far load-centre, Rb and Ra act oppositely.
    rfar=force*(z-a)/(b-a)
    rnear=force*(z-b)/(b-a)
    return {
        'mass_kg':mass_kg,'cg_from_face_mm':cg_from_face_mm,'eccentricity_mm':eccentricity_mm,
        'force_n':round(force,5),'load_plane_z_mm':z,
        'load_centre_near_z_mm':a,'load_centre_far_z_mm':b,
        'a0_mm':b-a,'bearing_stack_physical_width_mm':BEARING['matched_pair_width_mm'],
        'near_opposed_simple_reaction_N':round(rnear,5),
        'far_simple_reaction_N':round(rfar,5),
        'external_moment_from_z0_Nm':round(force*z/1000,5),
        'gravity_rot_torque_about_optical_axis_Nm':round(force*eccentricity_mm/1000,5),
        'model':'rigid two-virtual-support statics only; force directions can change with orientation',
        'NOT_actual_angular_contact_internal_loads':True,
        'NOT_acceptable_payload_or_bearing_life':True,
    }


def dimensions_review()->dict:
    # Deliberately avoid choosing bearing housing fit and shaft journal tolerances.
    shaft_shoulder_od=48.0
    outer_cap_opening_d=60.0
    return {
        'shaft_shoulder_reference_diameter_mm':shaft_shoulder_od,
        'housing_cap_opening_reference_diameter_mm':outer_cap_opening_d,
        'minimum_shaft_abutment_diameter_per_NSK_mm':BEARING['shaft_abutment_da_min_mm'],
        'maximum_housing_abutment_opening_per_NSK_mm':BEARING['housing_abutment_Db_max_mm'],
        'simple_diameter_limits_satisfied':shaft_shoulder_od>=BEARING['shaft_abutment_da_min_mm'] and outer_cap_opening_d<=BEARING['housing_abutment_Db_max_mm'],
        'cap_and_shoulder_faces_contact_verified':False,
        'shoulder_fillet_radii_selected':False,
        'matched_pair_axial_clamp_stack_verified':False,
        'manufacturer_preload_class_selected':False,
        'bearing_fit_tolerances_selected':False,
    }


def generate_reports(out:Path)->dict:
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    baseline=external_simple_reactions(4,80,20)
    rows=[external_simple_reactions(m,d,e) for m in (3.0,4.0,5.0)
          for d in (40.,80.,120.) for e in (0.,20.,40.)]
    f=out/'v16_db7008_27_external_load_cases_UNQUALIFIED.csv'
    with f.open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    r={
        'release':'V1.6 7008AWDB DB cartridge concept ONLY / Gate A',
        'NSK_citation':NSK_URL, 'catalog_dimensions':BEARING,
        'dimensions_review':dimensions_review(), 'baseline':baseline,
        'sweep_count':len(rows), 'csv':f.name,
        'clarification':'V1.5 50mm hypothetical supports are NOT the 7008AWDB physical pair; NSK a0 46.2mm is a load-centre dimension',
        'engineering_blocks':[ 
            '7008AWDB standard CN clearance does not establish an application-specific bearing preload; confirm OEM matched set exact suffix, axial clearance/preload and allowable installation method',
            'Actual bearing/shaft/housing fits and fillet radii, contact-face flatness, roughness and thermal expansion are unqualified',
            'No usable shaft locknut thread, torque, anti-loosening mechanism, axial thrust clamp path or retaining fasteners defined',
            'No stiffness/tilting/runout/vibration/fatigue, numerical FEA or bearing life / load safety approval',
            'No camera vendor clamp, separate fall arrest cable or actual DEC-to-ROT reducer bolt pattern accepted',
            'Only reference outline STEP; real OEM grooves, contact angles, cages and preload are not modelled',
        ],
        'gate_A':'digital maths + reference geometry', 'gate_B':'PENDING', 'gate_C':'PENDING',
        'camera_payload_approved':False,'may_energize':False,
    }
    (out/'v16_db7008_engineering_report.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path('hardware/cad/v16_generated'))
    args=p.parse_args();print('V1.6 cases',generate_reports(args.out)['sweep_count'])
