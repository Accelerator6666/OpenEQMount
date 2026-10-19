#!/usr/bin/env python3
"""V0.9 conceptual ROT axis, coordinate-matched view with V0.8.

MECHANICAL INTERFACES ARE UNMEASURED. METAL BEARING, CAPTURE, OEM DEC
OUTPUT, CAMERA COUPLER AND DRIVE ARE UNQUALIFIED. NOTHING SAFE TO ENERGIZE.
This script emits no motion control/firmware. All dimensions millimetres.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import cadquery as cq
import generate_v08_concept_assembly as v08
import generate_v04 as v04
import generate_v05 as v05

VERSION='V0.9_Gate_A_CONCEPT'
BED_MM=220
ROT_SOFT_MIN,ROT_SOFT_MAX=-160.0,160.0
ROT_PLACEMENT_X=169.0      # unqualified camera/lens mounting offset; not a DEC spindle
ROT_PLACEMENT_Z=207.0      # above DEC envelope and frame, *floating concept*
DEC_PREVIEW_ANGLE_DEG=25.0  # only used to show optical axis perpendicular to DEC shaft
ROT_STATOR_OD=138.0
ROT_STATOR_ID=92.0
ROT_ROTOR_OD=118.0
ROT_ROTOR_ID=76.0
BEARING_OUTER_REFERENCE=112.0
BEARING_INNER_REFERENCE=82.0
MOTOR_CENTRE_REFERENCE=100.0
GT2_BIG_TEETH=180
GT2_MOTOR_TEETH=20


def pcd_points(pcd,n=6,phase=30.0):
    return [(pcd/2*math.cos(math.radians(phase+i*360/n)),
             pcd/2*math.sin(math.radians(phase+i*360/n))) for i in range(n)]


def ring(od,id_,h,z=0):
    if not (od>id_>0 and h>0):raise ValueError('Ring dimensions invalid')
    return cq.Workplane('XY').circle(od/2).circle(id_/2).extrude(h).translate((0,0,z))


def bolt_holes(body,pcd,n,d,z0,height,phase=30):
    drill=cq.Workplane('XY').pushPoints(pcd_points(pcd,n,phase)).circle(d/2).extrude(height).translate((0,0,z0))
    return body.cut(drill)


def metal_components():
    # The bearing's dimensions are a *bounding-space proposal*, not a purchasable part.
    stator=bolt_holes(ring(ROT_STATOR_OD,ROT_STATOR_ID,6),122,6,5.5,-1,8)
    rotor=bolt_holes(ring(ROT_ROTOR_OD,ROT_ROTOR_ID,6,17),102,6,4.5,16,8)
    bearing=ring(BEARING_OUTER_REFERENCE,BEARING_INNER_REFERENCE,11,6)
    # Independent capture proposed as METAL; this is only a spatial reference.
    # Its exact axial clearance and anti-drop force require physical redesign.
    capture=bolt_holes(ring(134,110,4,24),122,6,5.5,23,6)
    return {
        'v09_DEC_STATOR_INTERFACE_METAL_PROPOSAL':stator,
        'v09_ROT_OUTPUT_CARRIER_METAL_PROPOSAL':rotor,
        'v09_BEARING_ENVELOPE_UNSPECIFIED':bearing,
        'v09_INDEPENDENT_RETENTION_RING_METAL_REFERENCE':capture,
    }


def printable_components():
    # These three prototypes NEVER retain a camera, bearing, belt or motor.
    bezel=bolt_holes(ring(150,132,3),140,6,4.5,-1,5)
    guide=(cq.Workplane('XY').box(86,34,5,centered=(True,True,False))
           .edges('|Z').fillet(5))
    guide=guide.cut(cq.Workplane('XY').pushPoints([(-32,0),(32,0)]).circle(3).extrude(7).translate((0,0,-1)))
    coupon=(cq.Workplane('XY').box(98,25,5,centered=(True,True,False))
            .edges('|Z').fillet(4))
    coupon=coupon.cut(cq.Workplane('XY').pushPoints([(-34,0),(-12,0),(12,0),(34,0)])
          .circle(2.3).extrude(7).translate((0,0,-1)))
    return {
        'v09_ROT_NONLOAD_POSITION_SCALE_BEZEL_PRINT_FLAT':bezel,
        'v09_ROT_LOOSE_CABLE_ROUTE_GAUGE_PRINT_FLAT':guide,
        'v09_ROT_M4_CLEARANCE_COUPON_PRINT_FLAT':coupon,
    }


def pitch_diameter(teeth):
    return 2*teeth/math.pi


def belt_reference():
    # These are only pitch-cylinder spatial references, not manufacturable teeth,
    # fabricated hubs, motor spindle, bearing, belt path or cable-clearance design.
    return {
      'v09_180T_GT2_PITCH_ONLY_NOT_A_PULLEY': cq.Workplane('XY').circle(pitch_diameter(GT2_BIG_TEETH)/2).extrude(4).translate((0,0,24)),
      'v09_20T_GT2_PITCH_ONLY_NOT_A_PULLEY': cq.Workplane('XY').center(MOTOR_CENTRE_REFERENCE,0).circle(pitch_diameter(GT2_MOTOR_TEETH)/2).extrude(4).translate((0,0,24)),
    }


def local_to_dec(shape, dec_angle_deg=DEC_PREVIEW_ANGLE_DEG):
    """ROT local +Z is optical axis; DEC pivot axis is +X (perpendicular).

    Pitch the ROT around a virtual DEC +X axis. The actual DEC-to-camera saddle
    does NOT exist. This is a kinematic view, not a mechanical connection.
    """
    if not -85 <= dec_angle_deg <= 85:
        raise ValueError('Unqualified DEC preview angle')
    pivot=(158.,0.,v04.DEC_CENTER_Z)
    return (shape.translate((ROT_PLACEMENT_X,0,ROT_PLACEMENT_Z))
            .rotate(pivot,(pivot[0]+1,pivot[1],pivot[2]),dec_angle_deg))


def to_mount(shape,latitude):
    # V0.4 RA output-face origin at V0.7 reducer local z=138.
    return v05.pivot_rotate(local_to_dec(shape).translate((0,0,138)),90-latitude)


def print_record(name,shape):
    bb=shape.val().BoundingBox()
    return {
        'name':name, 'material':'PETG for fit coupons only', 'status':'prototype_unqualified',
        'role':'loose nonstructural scale, cable routing sample, or printer fit gauge',
        'print_orientation':'flat XY on bed; bottom surface Z=0',
        'layer_direction':'+Z normal to print bed; no certified load direction',
        'load_path':'NONE. Never retain lens/camera/metal bearing or cover powered drivetrain',
        'overhang_strategy':'bed-flat planar prototype; slicer Gate B not performed',
        'metal_joint':'No structural polymer threaded joints or compression/clamping',
        'min_wall_mm':'slicer and real printed wall audit pending',
        'slicer_gate_B':'pending', 'physical_gate_C':'pending',
        'field_load_approved':False,
        'bbox_mm':[round(bb.xlen,3),round(bb.ylen,3),round(bb.zlen,3)],
    }


def export(out:Path,latitude=35.0):
    if not 25 <= latitude <= 45:raise ValueError('V0.5 polar concept requires 25..45 deg')
    out.mkdir(parents=True,exist_ok=True)
    metals=metal_components(); prints=printable_components()
    manifest={
        'release':VERSION, 'status':'prototype_unqualified_Gate_A_only',
        'rot_axis':'Optical-axis roll, perpendicular to DEC rotation axis at all DEC angles',
        'optical_axis_verified':False,
        'travel_limit_deg':[-160,160], 'limit_status':'soft proposal; NO tested physical end stop',
        'motor_pitch_teeth_reference':[GT2_BIG_TEETH,GT2_MOTOR_TEETH],
        'gear_ratio_reference':GT2_BIG_TEETH/GT2_MOTOR_TEETH,
        'field_derotation_not_implemented':True,
        'ASCOM_INDI_drivers_not_implemented':True,
        'hardware_motor_drive_not_implemented':True,
        'is_load_qualified':False,'is_safe_to_energize':False,
        'vendor_interface_verified':False,
        'unspecified':['DEC-to-camera saddle and optical axis-to-camera flange geometry; ROT is not coaxial with DEC' , 'DEC rotating output screw pattern and reference face','thin section crossed roller bearing real model and torque',
           'camera lens support or optical clearance and weight shift under DEC motion','independent metal capture and fastener engagement',
           'rotator hard stops, cable snag/strain relief, home switch, firmware E-stop',
           'belt teeth/belt stock/motor mount geometry', 'balance, moment, deflection, Gate B/C tests'],
        'printed_parts':[], 'metal_parts':[],
        'camera_payload_target_kg':[3,5], 'camera_payload_safe_kg':None,
        'combined_mount':'spatial concept only: ROT floats above an unmodeled DEC-to-camera saddle; camera coupling unverified',
    }
    for name,sh in prints.items():
        bb=sh.val().BoundingBox()
        if len(sh.solids().vals())!=1 or abs(bb.zmin)>1e-5 or max(bb.xlen,bb.ylen)>BED_MM:
            raise ValueError('Unprintable digital part: '+name)
        cq.exporters.export(sh,str(out/(name+'.stl')),exportType='STL',tolerance=.1,angularTolerance=.15)
        cq.exporters.export(sh,str(out/(name+'.step')),exportType='STEP')
        manifest['printed_parts'].append(print_record(name,sh))
    for name,sh in metals.items():
        cq.exporters.export(sh,str(out/(name+'.step')),exportType='STEP')
        manifest['metal_parts'].append({'name':name,'status':'unspecified metal spatial envelope / not for manufacture'})
    rotator=cq.Assembly(name='OpenEQMount_V09_ROT_PROPOSAL_GATE_A_ONLY')
    for name,sh in metals.items():
        color=cq.Color(.93,.63,.30) if 'ENVELOPE' in name else cq.Color(.61,.68,.73)
        rotator.add(sh,name=name,color=color)
    for name,sh in prints.items():
        if 'BEZEL' in name:
            rotator.add(sh.translate((0,0,31)),name=name,color=cq.Color(.13,.60,.76))
    rotator.save(str(out/'OpenEQMount_V09_ROT_AXIS_ONLY_UNQUALIFIED.step'),exportType='STEP')
    # Combined viewer: inherited V0.8 + ROT without mechanically mating unseen parts.
    combined=cq.Assembly(name='OpenEQMount_V09_THREE_AXIS_CONCEPT_UNQUALIFIED')
    prev=v08.make_components(latitude)
    for item in prev:
        combined.add(item['shape'],name=item['name'],color=item['color'])
    for name,sh in metals.items():
        combined.add(to_mount(sh,latitude),name=name,color=cq.Color(.35,.75,.63) if 'OUTPUT' in name else cq.Color(.68,.69,.77))
    bezel=prints['v09_ROT_NONLOAD_POSITION_SCALE_BEZEL_PRINT_FLAT']
    combined.add(to_mount(bezel.translate((0,0,31)),latitude),name='v09_ROT_BEZEL_DISPLAY_ONLY',color=cq.Color(.13,.60,.76))
    combined.save(str(out/'OpenEQMount_V09_THREE_AXIS_MOUNT_CONCEPT_UNQUALIFIED.step'),exportType='STEP')
    manifest['mount_body_count']=len(prev)+len(metals)+1
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=Path(__file__).parent/'v09_generated')
    parser.add_argument('--latitude',type=float,default=35.0)
    args=parser.parse_args()
    m=export(args.out,args.latitude)
    print('Generated',len(m['printed_parts']),'DfAM unqualified print gauges and',m['mount_body_count'],'combined spatial bodies')
