#!/usr/bin/env python3
"""V1.1 CAD: continuous-metal conceptual DEC-to-ROT bridge and mated 3-axis VIEW.

Not a manufacturing drawing, proof of reducer OEM output bolt pattern, weld
quality, bearing preload, fastener engagement or independent safety restraint.
All lengths millimetres. FDM gauge must NEVER be used structurally.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import cadquery as cq
import generate_v08_concept_assembly as v08
import generate_v10_rotator_bench as v10
import generate_v04 as v04
import generate_v05 as v05

VERSION='V1.1_DEC_TO_ROT_CONTINUOUS_METAL_CONCEPT_GATE_A'
DEC_OUTPUT_X=158.0
DEC_CENTRE_Z=v04.DEC_CENTER_Z
ROT_X=194.0
ROT_Z=165.0
DEC_OUTPUT_PCD_CANDIDATE=23.0
BRIDGE_TOP=ROT_Z
WEB_THICK=6.0
BEARING_MOMENT_QUALIFIED=False
MOTOR_MOUNT_PCD=146.0
MOTOR_STANDOFF_HEIGHT=14.0
MOTOR_STANDOFF_PHASE=(60.,180.,300.)


def dec_output_hub():
    # DEC output face x=158 mm; 6 x M4 PCD23 is only a V0.3 preliminary candidate.
    disk=cq.Workplane('YZ',origin=(DEC_OUTPUT_X,0,DEC_CENTRE_Z)).circle(34).extrude(8)
    disk=disk.cut(cq.Workplane('YZ',origin=(DEC_OUTPUT_X-1,0,DEC_CENTRE_Z)).circle(5).extrude(10))
    for a in range(6):
        theta=math.radians(30+a*60)
        y,z=11.5*math.cos(theta),DEC_CENTRE_Z+11.5*math.sin(theta)
        disk=disk.cut(cq.Workplane('YZ',origin=(DEC_OUTPUT_X-1,y,z)).circle(2.25).extrude(10))
    return disk


def bridge_legs():
    # Two 6-mm-thick metal webs, prototype XY polygons mapped into XZ. Each
    # overlaps the hub by 2 mm and upper metal platform by 2 mm in CAD.
    # Whether this is machinable from billet or welded with qualified joints
    # is deliberately UNRESOLVED; fused CAD does NOT certify a weld.
    profile=[(164,108),(185,108),(218,139),(218,161),(164,161)]
    sheet=cq.Workplane('XY').polyline(profile).close().extrude(WEB_THICK).rotate((0,0,0),(1,0,0),90)
    return [sheet.translate((0,y,0)) for y in (30,-24)]


def bridge_deck():
    plate=cq.Workplane('XY').box(146,146,6,centered=(True,True,False)).translate((ROT_X,0,159))
    # Provide 72-mm bore for reference lower retention collar and wiring space.
    plate=plate.cut(cq.Workplane('XY').center(ROT_X,0).circle(36).extrude(8).translate((0,0,158)))
    # Transfer proposed stator attachment PCD 110 from V1.0; clearance only.
    for a in range(6):
        theta=math.radians(30+a*60)
        cx,cy=ROT_X+55*math.cos(theta),55*math.sin(theta)
        plate=plate.cut(cq.Workplane('XY').center(cx,cy).circle(2.75).extrude(8).translate((0,0,158)))
    # Three metal standoffs connect deck to the revised motor plate.
    for a in MOTOR_STANDOFF_PHASE:
        theta=math.radians(a)
        cx,cy=ROT_X+MOTOR_MOUNT_PCD/2*math.cos(theta),MOTOR_MOUNT_PCD/2*math.sin(theta)
        plate=plate.cut(cq.Workplane('XY').center(cx,cy).circle(2.75).extrude(8).translate((0,0,158)))
    return plate


def continuous_metal_bridge():
    # Single fused *design-intent* solid: DEC hub -> metal side webs -> deck.
    # The exact joining process and material stress are not specified.
    s=dec_output_hub()
    for leg in bridge_legs(): s=s.union(leg)
    s=s.union(bridge_deck())
    if len(s.solids().vals())!=1:raise ValueError('DEC-to-ROT bridge not connected')
    return s


def revised_motor_carrier():
    s=v10.motor_carrier()
    for a in MOTOR_STANDOFF_PHASE:
        theta=math.radians(a)
        x,y=MOTOR_MOUNT_PCD/2*math.cos(theta),MOTOR_MOUNT_PCD/2*math.sin(theta)
        s=s.cut(cq.Workplane('XY').center(x,y).circle(2.75).extrude(9).translate((0,0,13)))
    return s


def local_standoff(angle):
    theta=math.radians(angle)
    x,y=MOTOR_MOUNT_PCD/2*math.cos(theta),MOTOR_MOUNT_PCD/2*math.sin(theta)
    # Local z=0..14. Nominal 10-mm OD, 5.5-mm thru-hole.
    return v10.ring(10,5.5,MOTOR_STANDOFF_HEIGHT).translate((x,y,0))


def camera_blank():
    # Blank mating spacer to future manufacturer's metal saddle/lens collar.
    # PCD88 matches proposed V1.0 output but NO Arca/1/4-20/3/8 interface.
    return v10.bolt(v10.ring(108,36,6),88,6,4.5,z=-1,depth=8)


def print_gauges():
    # Drill-gauge is deliberately printed only for checking candidate holes.
    gauge=v10.ring(78,12,3)
    return {'v11_NONLOAD_DEC_OUTPUT_PCD23_FIT_GAUGE_PRINT_FLAT':
            v10.bolt(gauge,DEC_OUTPUT_PCD_CANDIDATE,6,4.5,z=-1,depth=5)}


def rotor_local_to_mount(shape,lat:float,dec_angle:float=0.,rot_angle:float=0.,rotating=False):
    if not 25<=lat<=45:raise ValueError('latitude outside wedge reference')
    if not -65<=dec_angle<=65:raise ValueError('DEC preview angle outside checked conceptual window')
    if not -150<=rot_angle<=150:raise ValueError('ROT software reference limits exceeded')
    s=shape
    if rotating:
        s=s.rotate((0,0,0),(0,0,1),rot_angle)
    s=s.translate((ROT_X,0,ROT_Z))
    return global_dec_shape_to_mount(s,lat,dec_angle)


def global_dec_shape_to_mount(shape,lat:float,dec_angle:float=0.):
    pivot=(DEC_OUTPUT_X,0,DEC_CENTRE_Z)
    return v05.pivot_rotate(
        shape.rotate(pivot,(pivot[0]+1,pivot[1],pivot[2]),dec_angle).translate((0,0,138)),
        90-lat)


def print_record(name,shape):
    bb=shape.val().BoundingBox()
    return dict(name=name,status='prototype_unqualified',material='PETG gauge specimen only',
                print_orientation='XY flat at Z=0',layer_direction='+Z',
                role='nonstructural DEC output PCD gauge, not a clamp',
                load_path='none, MUST NOT support camera or rotator',
                overhang_strategy='bed-flat through-holes; slicer review pending',
                metal_joint='only a fit gauge; NEVER replace metal hub',
                min_wall_mm='slicer Gate B pending',slicer_gate_B='pending',
                physical_gate_C='pending',field_load_approved=False,
                bbox_mm=[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)])


def part_records(lat,dec_angle,rot_angle):
    # Do not include V0.9 floating ROT envelope or disassembled motor bench.
    out=[]
    def add(name,shape,role,color):
        if len(shape.solids().vals())!=1:raise RuntimeError(name+' not a single solid')
        out.append(dict(name=name,shape=shape,role=role,color=color))
    for item in v08.make_components(lat):
        add(item['name'],item['shape'],item['category'],item['color'])
    add('v11_DEC_OUTPUT_TO_ROT_CONTINUOUS_METAL_BRIDGE_UNQUALIFIED',
        global_dec_shape_to_mount(continuous_metal_bridge(),lat,dec_angle),
        'primary_metal_intent',cq.Color(.25,.58,.75))
    for n,s in v10.metal_parts().items():
        if 'STOP_' in n:
            # V1.0 stop arc does not contact moving rotor; don't suggest it works.
            continue
        if 'NEMA17_TENSIONER_' in n:
            s=revised_motor_carrier()
            n='v11_REVISED_METAL_NEMA17_MOTOR_CARRIER_WITH_MOUNT_PCD146'
        rotating=('SPINDLE_' in n or 'OUTPUT_FLANGE_' in n)
        add(n,rotor_local_to_mount(s,lat,dec_angle,rot_angle,rotating),
            'rotating_metal_reference' if rotating else 'rot_stator_reference',
            cq.Color(.86,.59,.28) if 'BEARING_' in n else cq.Color(.66,.74,.78) if rotating else cq.Color(.44,.68,.71))
    for a in MOTOR_STANDOFF_PHASE:
        add('v11_MOTOR_STANDOFF_METAL_%03d'%a,
            rotor_local_to_mount(local_standoff(a).translate((0,0,0)),lat,dec_angle),
            'motor_metal_support_unqualified',cq.Color(.79,.69,.53))
    add('v11_CAMERA_MATING_FLANGE_METAL_BLANK_NO_LENS_CLAMP',
        rotor_local_to_mount(camera_blank().translate((0,0,67)),lat,dec_angle,rot_angle,True),
        'metal_camera_interface_blank',cq.Color(.26,.70,.55))
    # 2nd reference; no FDM components are installed on the load-carrying view.
    return out


def export(out:Path,lat=35.,dec_angle=25.,rot_angle=0.):
    out.mkdir(parents=True,exist_ok=True)
    rec=part_records(lat,dec_angle,rot_angle)
    model=cq.Assembly(name='OpenEQMount_V11_FULL_THREE_AXIS_METAL_PATH_CONCEPT_NOT_PAYLOAD_RATED')
    inventory=[]
    for p in rec:
        model.add(p['shape'],name=p['name'],color=p['color'])
        inventory.append({'name':p['name'],'role':p['role']})
    assembly_name='OpenEQMount_V11_THREE_AXIS_MATED_CONCEPT_UNQUALIFIED.step'
    model.save(str(out/assembly_name),exportType='STEP')
    local_parts={
        'v11_DEC_OUTPUT_TO_ROT_CONTINUOUS_METAL_BRIDGE_UNQUALIFIED':continuous_metal_bridge(),
        'v11_REVISED_METAL_NEMA17_MOTOR_CARRIER_WITH_MOUNT_PCD146':revised_motor_carrier(),
        'v11_CAMERA_MATING_FLANGE_METAL_BLANK_NO_LENS_CLAMP':camera_blank(),
    }
    for a in MOTOR_STANDOFF_PHASE:
        local_parts['v11_MOTOR_STANDOFF_METAL_%03d'%a]=local_standoff(a)
    for n,s in local_parts.items():
        cq.exporters.export(s,str(out/(n+'.step')),exportType='STEP')
    for n,s in print_gauges().items():
        bb=s.val().BoundingBox()
        if len(s.solids().vals())!=1 or abs(bb.zmin)>1e-6 or max(bb.xlen,bb.ylen)>220:
            raise ValueError('DfAM nonload gauge outside permitted flat plate')
        cq.exporters.export(s,str(out/(n+'.step')),exportType='STEP')
        cq.exporters.export(s,str(out/(n+'.stl')),exportType='STL',tolerance=.09,angularTolerance=.15)
    manifest={
        'release':VERSION,'status':'digital_gate_A_only_not_for_manufacture',
        'purpose':'connected geometric metal path concept from provisional DEC output through ROT bearing bench to camera interface blank',
        'latitude_deg':lat,'dec_preview_deg':dec_angle,'rot_preview_deg':rot_angle,
        'coordinate_system':'DEC rotation local +X about (158,0,112), ROT spin optical +Z before RA/wedge transformations',
        'assembled_step':assembly_name,'parts_in_assembly':len(rec),'parts':inventory,
        'metal_reference_exports':list(local_parts),'nonload_printed_parts':[
            print_record(n,s) for n,s in print_gauges().items()],
        'structural_material':'METAL REQUIRED; alloy/weld/machining design pending',
        'vendor_DEC_output_PCD23_confirmed':False,
        'DEC_to_ROT_path_implemented_in_CAD':True,
        'motor_standoff_bolt_paths_proposed':True,
        'bearing_6808_pair_moment_qualified':False,
        'camera_interface_blank_only':True,
        'camera_or_lens_clamp_implemented':False,
        'independent_metal_fall_arrest_implemented':False,
        'hard_stop_moving_contact_implemented':False,
        'limit_switch_implemented':False,
        'motor_drive_implemented':False,
        'safe_to_energize':False,'camera_payload_approved':False,
        'full_kinematic_collision_proved':False,
        'DfAM_Gate_B':'pending','physical_safety_Gate_C':'pending',
        'todo':['obtain measured DEC output flange and actual screw clocking/grade/engagement',
                'design manufacturable metal bridge, qualified welding or machined joints and verified metal load path',
                'replace 6808 pair if fatigue, moment rigidity or runout fail engineering test',
                'correct V1.0 spindle end shoulders and prove preload and axial positive metal bearing capture',
                'camera/lens collar and independently anchored metal fall-arrest verified for full ROT travel',
                'true hard-stop moving lug and limit sensors, independent motor cutoff',
                'RA/DEC/ROT 25/35/45 latitude, full articulation collision and cable sweep',
                '3-5kg payload structural stiffness/creep/tilt/meridian-flip and cable snags',
                'slicer / printing fit Gate B and real-load/safety Gate C'],
    }
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=Path(__file__).parent/'v11_generated')
    p.add_argument('--latitude',type=float,default=35.)
    p.add_argument('--dec-preview',type=float,default=25.)
    p.add_argument('--rot-preview',type=float,default=0.)
    a=p.parse_args()
    x=export(a.out,a.latitude,a.dec_preview,a.rot_preview)
    print(f"V1.1 generated {x['parts_in_assembly']} solids in complete view; NOT FOR PAYLOAD")
