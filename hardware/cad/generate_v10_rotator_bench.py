#!/usr/bin/env python3
"""V1.0 ROT bench-fit CAD, not manufactured or approved for payload/power.

Metal parts are rough-fit proposals. The proposed dual 6808 bearings (40x52x7)
have unverified moment capacity in this assembly. Source mm, Z=optical axis.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import cadquery as cq

VERSION='V1.0_ROT_BENCH_GATE_A'
BED_MM=220
BEARING_ID,BEARING_OD,BEARING_WIDTH=40.0,52.0,7.0
BEARING_Z=(7.0,37.0)             # 30 mm separation, example, not qualified
MOTOR_CENTRE_X=105.0             # adjuster range 100–110 mm
MOTOR_TRAVEL_MM=5.0
DRIVE_TEETH,MOTOR_TEETH,BELT_PITCH=80,20,2.0
SOFT_LIMIT_DEG=150
HARD_LIMIT_REFERENCE_DEG=160


def ring(outer:float,inner:float,height:float,z:float=0):
    assert outer>inner>0 and height>0
    return cq.Workplane('XY').circle(outer/2).circle(inner/2).extrude(height).translate((0,0,z))


def points(pcd,n=6,phase=30.):
    return [(pcd/2*math.cos(math.radians(phase+i*360/n)),pcd/2*math.sin(math.radians(phase+i*360/n))) for i in range(n)]


def bolt(body,pcd,n,diam,z=-1,depth=90,phase=30):
    cutter=cq.Workplane('XY').pushPoints(points(pcd,n,phase)).circle(diam/2).extrude(depth).translate((0,0,z))
    return body.cut(cutter)


def bearing_seat_housing():
    # Metal shell; machining concept only. 50 mm clearance core, bearing counterbores 52 mm.
    sh=ring(128,50,54)
    for z in BEARING_Z:
        sh=sh.cut(cq.Workplane('XY').circle(52/2).extrude(BEARING_WIDTH+.2).translate((0,0,z)))
    # Nominal fastening interface is NOT adapted to a real DEC output saddle.
    return bolt(sh,110,6,5.5,z=-1,depth=56)


def rotor_spindle():
    # Hollow metal sleeve; needs metal shoulder, axial preload and tolerancing.
    return ring(40,32,64,-5)


def output_plate():
    return bolt(ring(108,34,8,59),88,6,4.5,z=58,depth=10)


def independent_retention_collar():
    # Metal reference only, not a qualified axial retention or shoulder stack.
    return bolt(ring(65,33,5,-10),55,6,3.5,z=-11,depth=7)


def fixed_stop_plate():
    # Metal fixed-sector reference and two 'flags'. Stops are NOT kinematic certified.
    a=ring(136,110,5,54)
    for angle in (-HARD_LIMIT_REFERENCE_DEG,HARD_LIMIT_REFERENCE_DEG):
        px=61*math.cos(math.radians(angle));py=61*math.sin(math.radians(angle))
        flag=cq.Workplane('XY').center(px,py).circle(3).extrude(8).translate((0,0,58.9))
        a=a.union(flag)
    return a


def motor_carrier():
    # Clearance inside the metal motor mount avoids the 128 mm stator housing.
    base=ring(156,130,6,14)
    disk=cq.Workplane('XY').center(MOTOR_CENTRE_X,0).circle(39).extrude(6).translate((0,0,14))
    bridge=cq.Workplane('XY').center(90,0).box(32,42,6,centered=(True,True,False)).translate((0,0,14))
    body=base.union(bridge).union(disk)
    # 31x31 motor hole pitch, +/-5 mm radial tension; four through slots.
    for dx in (-15.5,15.5):
        for dy in (-15.5,15.5):
            cut=(cq.Workplane('XY').center(MOTOR_CENTRE_X+dx,dy)
                 .slot2D(2*MOTOR_TRAVEL_MM+3.5,3.5,angle=0).extrude(8).translate((0,0,13)))
            body=body.cut(cut)
    # Clearance for nominal spindle, plus bolt patterns on the central portion.
    body=body.cut(cq.Workplane('XY').circle(52/2).extrude(8).translate((0,0,13)))
    return body


def motor_clearance():
    return cq.Workplane('XY').center(MOTOR_CENTRE_X,0).box(42,42,38,centered=(True,True,False)).translate((0,0,-25))


def metal_parts():
    p={
      'v10_METAL_STATOR_DUAL_6808_SEATS_PROPOSAL':bearing_seat_housing(),
      'v10_METAL_HOLLOW_ROT_SPINDLE_PROPOSAL':rotor_spindle(),
      'v10_METAL_CAMERA_OUTPUT_FLANGE_PROPOSAL':output_plate(),
      'v10_METAL_INDEPENDENT_CAPTURE_COLLAR_PROPOSAL':independent_retention_collar(),
      'v10_METAL_FIXED_STOP_ARC_REFERENCE':fixed_stop_plate(),
      'v10_METAL_NEMA17_TENSIONER_PLATE_PROPOSAL':motor_carrier(),
    }
    for i,z in enumerate(BEARING_Z,1):
        p[f'v10_6808_2RS_BEARING_{i}_REFERENCE']=ring(BEARING_OD,BEARING_ID,BEARING_WIDTH,z)
    return p


def loose_print_parts():
    # None of these printable parts restrains the load, moving belt or camera.
    bezel=ring(150,139,3)
    coupon=(cq.Workplane('XY').box(90,26,5,centered=(True,True,False))
            .edges('|Z').fillet(3))
    coupon=coupon.cut(cq.Workplane('XY').pushPoints([(-30,0),(-10,0),(10,0),(30,0)]).circle(2.3).extrude(7).translate((0,0,-1)))
    cable=(cq.Workplane('XY').box(96,35,5,centered=(True,True,False)).edges('|Z').fillet(4))
    cable=cable.cut(cq.Workplane('XY').center(0,0).slot2D(55,10).extrude(7).translate((0,0,-1)))
    return {'v10_NONLOAD_ROT_INDEX_BEZEL_PRINT_FLAT':bezel,
            'v10_NONLOAD_M4_CALIBRATION_COUPON_PRINT_FLAT':coupon,
            'v10_NONLOAD_CABLE_CLEARANCE_COUPON_PRINT_FLAT':cable}


def pitch_diameter(teeth): return teeth*BELT_PITCH/math.pi


def belt_estimated_length(center=MOTOR_CENTRE_X):
    r=pitch_diameter(MOTOR_TEETH)/2;R=pitch_diameter(DRIVE_TEETH)/2
    return 2*center+math.pi*(R+r)+(R-r)**2/center


def print_record(name,shape):
    bb=shape.val().BoundingBox()
    return {'name':name,'status':'prototype_unqualified','material':'PETG fit specimen only',
      'print_orientation':'XY flat bed Z=0','layer_direction':'+Z',
      'role':'unpowered non-load removable gauge','load_path':'none - never restrain camera or bearing',
      'overhang_strategy':'planar reference; slicer review still required',
      'metal_joint':'no structural printed threads; test clearances only',
      'min_wall_mm':'requires slicer and actual printer measurement',
      'slicer_gate_B':'pending','physical_gate_C':'pending','field_load_approved':False,
      'bbox_mm':[round(bb.xlen,3),round(bb.ylen,3),round(bb.zlen,3)]}


def export(out:Path):
    out.mkdir(parents=True,exist_ok=True)
    metals=metal_parts();gauges=loose_print_parts()
    info={
        'release':VERSION,'status':'digital_Gate_A_only_unqualified',
        'axis':'ROT around optical +Z; exact DEC saddle and camera coaxial alignment not provided',
        'bearing_candidate':'2 x 6808-2RS (40x52x7) 30mm nominal separation',
        'bearing_moment_qualified':False,
        'load_qualified':False,'safe_to_energize':False,
        'soft_limit_deg':[-SOFT_LIMIT_DEG,SOFT_LIMIT_DEG],
        'hard_stop_reference_deg':[-HARD_LIMIT_REFERENCE_DEG,HARD_LIMIT_REFERENCE_DEG],
        'hard_stop_force_verified':False,
        'drive_pulley_teeth_reference':[DRIVE_TEETH,MOTOR_TEETH],
        'belt_ratio_reference':DRIVE_TEETH/MOTOR_TEETH,
        'belt_pitch_reference_mm':BELT_PITCH,'motor_center_nominal_mm':MOTOR_CENTRE_X,
        'motor_slide_plus_minus_mm':MOTOR_TRAVEL_MM,
        'belt_length_estimate_mm':round(belt_estimated_length(),2),
        'belt_cad_status':'pitch-only; no belt wrap, gear tooth geometry, shaft/hub or belt tension verification',
        'physical_switches_implemented':False, 'independent_motor_cutoff_implemented':False,
        'camera_adapter_implemented':False,'camera_fall_restraint_qualified':False,
        'DEC_output_mated':False,'rotator_cable_route_qualified':False,
        'printed_parts':[],'metal_parts':[],
        'unfinished':['DEC rotating output to rotator fixed stator CAD connection',
          'camera saddle/ring/tailored lens collar and optical axis centring',
          'actual 6808 fits, spindle shoulders and metal capture verified for axial load',
          'bearing pair bending deflection/fatigue/tilt under 3-5 kg payload',
          'timing belt teeth, actual pulley hubs and real-length belt selection',
          'motor mount collision, winding constraints, cable clamp and continuous movement',
          'real home sensor, hard stop, watchdog, E-Stop, STO or power interlock',
          '3-axis integrated collision, counterweight, cable, meridian flip checks',
          'Gate B and Gate C physical testing'],
    }
    for n,s in metals.items():
        cq.exporters.export(s,str(out/(n+'.step')),exportType='STEP')
        info['metal_parts'].append({'name':n,'status':'vendor fit / machining approval pending','printed_load_part':False})
    for n,s in gauges.items():
        bb=s.val().BoundingBox()
        if len(s.solids().vals())!=1 or abs(bb.zmin)>1e-6 or max(bb.xlen,bb.ylen)>BED_MM:raise RuntimeError('DfAM print geometry error '+n)
        cq.exporters.export(s,str(out/(n+'.step')),exportType='STEP')
        cq.exporters.export(s,str(out/(n+'.stl')),exportType='STL',tolerance=.09,angularTolerance=.16)
        info['printed_parts'].append(print_record(n,s))
    assembly=cq.Assembly(name='OpenEQMount_V10_BENCH_ONLY_NO_CAMERA_LOAD')
    for n,s in metals.items():
        col=cq.Color(.85,.61,.38) if 'BEARING_' in n else (cq.Color(.34,.56,.75) if 'STATOR' in n else cq.Color(.75,.79,.83))
        assembly.add(s,name=n,color=col)
    # Partially assembled, not claimed collision-free / fit-approved.
    assembly.add(loose_print_parts()['v10_NONLOAD_ROT_INDEX_BEZEL_PRINT_FLAT'].translate((0,0,68)),
                 name='v10_NONLOAD_BEZEL_IN_ASSEMBLY_SPACE_ONLY',color=cq.Color(.16,.7,.6))
    assembly.save(str(out/'OpenEQMount_V10_ROTATOR_BENCH_UNQUALIFIED.step'),exportType='STEP')
    (out/'manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return info

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).parent/'v10_generated');a=p.parse_args()
    m=export(a.out)
    print(f"V1.0 generated {len(m['metal_parts'])} metal reference parts and {len(m['printed_parts'])} non-load prints")
