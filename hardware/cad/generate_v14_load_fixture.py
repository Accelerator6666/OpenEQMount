#!/usr/bin/env python3
"""OpenEQMount V1.4 removable camera fixture datum + mass/CG visual study.

NO clamp, bearing or tether is qualified; the camera models are *hollow*/solid
reference envelopes only. This assembly must NEVER receive a live payload.
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import cadquery as cq
import generate_v10_rotator_bench as v10
import generate_v11_three_axis_mated_concept as v11
import generate_v13_rot_retention as v13
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.rotator_load_cases import LoadCase,estimate,write_reports

VERSION='V1.4_VENDOR_ADAPTER_CG_ENVELOPE_GATE_A_UNQUALIFIED'
CAMERA_INTERFACE_DIAMETER=118.
PROPOSED_M6_SLOT_CENTRES_MM=(25.,35.) # Per side: 50-70mm across nominal range
REFERENCE_CAMERA_BODY_MM=(125.,85.,65.)
REFERENCE_LENS_DIAMETER_MM=90.
REFERENCE_LENS_LENGTH_MM=105.
BEARING_AXIAL_GAP_MM=30.

def slotted_camera_interface():
    """Replace V1.3 two fixed M6 holes; metal stock; slots are NOT verified vendor dimensions."""
    part=v10.ring(CAMERA_INTERFACE_DIAMETER,42,8,67)
    part=v10.bolt(part,88,6,4.5,z=66.5,depth=9)
    # 2x 6.6-mm wide M6 clearance slots with X centers at +/-30mm,
    # travel from +/-25 to +/-35; dimensional checks are digital only.
    for sign in (-1,1):
        x=30*sign
        slot=(cq.Workplane('XY').center(x,0).slot2D(16.6,6.6,0)
              .extrude(10).translate((0,0,66)))
        part=part.cut(slot)
    if len(part.solids().vals())!=1:raise ValueError('adapter lost solid topology')
    return part

def metal_camera_anchor_study():
    """Separate L-shaped load-eye *envelope*; NOT attached to real camera, NOT a safety device."""
    body=cq.Workplane('XY').center(0,72).box(18,32,5,centered=(True,True,False)).translate((0,0,83))
    body=body.cut(cq.Workplane('XY').center(0,83).circle(3.4).extrude(7).translate((0,0,82)))
    return body

def cg_marker_print_flat():
    """Only a 3-mm-thick PETG *ruler coupon*; NEVER a payload spacer."""
    base=cq.Workplane('XY').box(150,24,3,centered=(True,True,False))
    # 3mm-wide reference holes 40/80/120 mm from 0 position along local X.
    for x in (-60,-20,20,60):
        base=base.cut(cq.Workplane('XY').center(x,0).circle(1.5).extrude(4).translate((0,0,-.5)))
    return base

def camera_body_envelope():
    """Visual reference centered on optical axis, NOT a solid part to fabricate."""
    return cq.Workplane('XY').box(*REFERENCE_CAMERA_BODY_MM,centered=(True,True,False)).translate((0,0,83))

def lens_envelope():
    return cq.Workplane('XY').circle(REFERENCE_LENS_DIAMETER_MM/2).extrude(REFERENCE_LENS_LENGTH_MM).translate((0,0,148))

def design_parts():
    return {
      'v14_METAL_SLOTTED_CAMERA_VENDOR_FIXTURE_STOCK_UNQUALIFIED':slotted_camera_interface(),
      'v14_METAL_SEPARATE_CAMERA_CAGE_ANCHOR_UNCONNECTED_REFERENCE':metal_camera_anchor_study(),
    }

def camera_envelopes():
    return {'v14_REFERENCE_CAMERA_BODY_NOT_MANUFACTURING':camera_body_envelope(),
            'v14_REFERENCE_LENS_NOT_MANUFACTURING':lens_envelope()}

def assembly_records(latitude=35.,dec_angle=25.,rot_angle=0.):
    old=v13.assembly_records(latitude,dec_angle,rot_angle)
    records=[r for r in old if r['name'] not in (
        'v13_METAL_CAMERA_VENDOR_CLAMP_INTERFACE_TWO_M6_CANDIDATE',
        'v13_METAL_CAMERA_CAGE_EYE_FLOATING_NOT_CONNECTED')]
    for n,s in design_parts().items():
        records.append(dict(name=n,shape=v11.rotor_local_to_mount(s,latitude,dec_angle,rot_angle,True),
                            role='unqualified_metal_reference_only',color=cq.Color(.27,.74,.58)))
    for n,s in camera_envelopes().items():
        records.append(dict(name=n,shape=v11.rotor_local_to_mount(s,latitude,dec_angle,rot_angle,True),
                            role='reference_only_camera_occupancy_NOT_AN_ATTACHED_CAMERA',color=cq.Color(.75,.47,.83)))
    if len({x['name'] for x in records})!=len(records):raise ValueError('duplicate names')
    return records

def verify_candidate_slot():
    p=slotted_camera_interface()
    # point probes must be absent from slot inside candidate 50-70 mm spacing
    for x in (-35.,-30.,-25.,25.,30.,35.):
        probe=cq.Workplane('XY').center(x,0).circle(3).extrude(8).translate((0,0,67))
        if p.intersect(probe).val().Volume()>1e-4:raise RuntimeError('hole/slot does not clear M6 candidate')
    return True

def export(out:Path,latitude=35.,dec_preview=25.,rot_preview=0.,mass_kg=4.,cg_from_mount_mm=80.,eccentricity_mm=20.):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if not (25<=latitude<=45 and -65<=dec_preview<=65 and -150<=rot_preview<=150):
        raise ValueError('angle is outside preview guardrails')
    case=LoadCase(mass_kg,cg_from_mount_mm,eccentricity_mm)
    verify_candidate_slot()
    r=assembly_records(latitude,dec_preview,rot_preview)
    name='OpenEQMount_V14_THREE_AXIS_CAMERA_LOAD_ENVELOPE_UNQUALIFIED.step'
    assembly=cq.Assembly(name='V14_NO_CAMERA_NO_POWER_DIGITAL_GATE_A_ONLY')
    for x in r:assembly.add(x['shape'],name=x['name'],color=x['color'])
    assembly.save(str(out/name),exportType='STEP')
    for n,s in design_parts().items():cq.exporters.export(s,str(out/(n+'.step')),exportType='STEP')
    # NOTE: These visual occupancy volumes are NOT separate engineering part files.
    coupon=cg_marker_print_flat();print_name='v14_NONLOAD_CG_RANGE_REFERENCE_COUPON_PRINT_FLAT'
    cq.exporters.export(coupon,str(out/(print_name+'.step')),exportType='STEP')
    cq.exporters.export(coupon,str(out/(print_name+'.stl')),exportType='STL',tolerance=.07,angularTolerance=.14)
    load=write_reports(out,case)
    man={
      'release':VERSION,'assembled_step':name,'parts_in_assembly':len(r),
      'metal_reference_exports':list(design_parts()),'camera_visual_only':list(camera_envelopes()),
      'nonload_printed_parts':[dict(name=print_name,material='PETG fit coupon ONLY',
          print_orientation='XY flat on Z0',layer_direction='+Z',load_path='none',
          overhang_strategy='planar through holes',metal_joint='NO printed mounting structure',
          field_load_approved=False,slicer_gate_B='pending',physical_gate_C='pending')],
      'candidate_adjustable_2xM6_spacing_mm':[50,70],
      'camera_vendor_clamp_selected':False,'camera_attached_to_cad':False,
      'photographic_cg_measured':False,'bearing_catalogue_fatigue_confirmed':False,
      'bearing_pair_deflection_model_completed':False,'shaft_thread_specified':False,
      'bearing_preload_defined':False,'independent_camera_tether_attached':False,
      'tether_length_and_sweep_qualified':False,'camera_saddle_strength_qualified':False,
      'full_three_axis_kinematic_collision_verified':False,
      'belt_efficiency_measured':False,'motor_torque_qualified':False,
      'physical_gates_completed':False,'safe_to_energize':False,'payload_approved':False,
      'Gate_B':'pending','Gate_C':'pending',
      'nominal_theoretical_case':load['nominal_example'],
      'load_case_count':load['case_count'],
      'critical_findings':[
        'Visual camera/lens envelopes overlap unqualified ROT output and use fictional geometry; not a camera/lens mounting solution.',
        'Candidate slotted 2xM6 adapter is NOT a universal Arca clamp interface; obtain actual clamp manufacturer drawing.',
        'Bearing-reaction model assumes transverse gravity, two simple radial supports; 6808 contact geometry and deflection unknown.',
        '2x illustration multiplier is NOT a safety factor; load cells, slip, dynamic impact and all-axis collision still need testing.',
        'Separate camera eye study is not connected to a real camera cage; a true independent metal tether/cable and drop test are still missing.',
        'No camera, motors, or astrophotography payload may be mounted or energized under this version.'
      ],
    }
    (out/'manifest.json').write_text(json.dumps(man,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return man

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=Path(__file__).parent/'v14_generated')
    p.add_argument('--latitude',type=float,default=35.)
    p.add_argument('--dec-preview',type=float,default=25.)
    p.add_argument('--rot-preview',type=float,default=0.)
    p.add_argument('--mass-kg',type=float,default=4.)
    p.add_argument('--cg-from-mount-mm',type=float,default=80.)
    p.add_argument('--eccentricity-mm',type=float,default=20.)
    a=p.parse_args()
    m=export(a.out,a.latitude,a.dec_preview,a.rot_preview,a.mass_kg,a.cg_from_mount_mm,a.eccentricity_mm)
    print('V1.4',m['parts_in_assembly'],'STEP solids / load scenarios',m['load_case_count'])
