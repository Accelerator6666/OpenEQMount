#!/usr/bin/env python3
"""V1.8 positive-drive DEC/ROT metal flange proposal; CAD Gate A ONLY.

One-piece metal spindle-to-hub shoulder; two shear dowels + six through-bolt
stacks at the camera fixture blank. NO OEM mating hole, joint fatigue, fit,
axial bearing preload, independent fall arrest or camera clamp is qualified.
The previous V1.6 floating camera plate is deliberately REMOVED.
"""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
import cadquery as cq
import generate_v17_integrated_7008 as v17

NAME='OpenEQMount_V18_THREE_AXIS_POSITIVE_DRIVE_CONCEPT_UNQUALIFIED.step'
SUB='OpenEQMount_V18_DEC_ROT_SHAFT_TO_CAMERA_JOINT_UNQUALIFIED.step'
SPINDLE_NAME='v18_ONE_PIECE_METAL_HOLLOW_SPINDLE_INTEGRAL_110MM_FLANGE_UNQUALIFIED'
CAMERA_NAME='v18_METAL_REMOVABLE_CAMERA_INTERFACE_BLANK_NO_CLAMP'
BOLT_PCD=90.0
BOLT_N=6
BOLT_D=6.0
BOLT_CLEARANCE_D=6.6
DOWEL_PCD=68.0
DOWEL_N=2
DOWEL_D=6.0
DOWEL_HOLE_D=6.2   # geometrical placeholder; NOT a fit specification
FLANGE_OD=110.0
FLANGE_BOTTOM=45.0
FLANGE_TOP=53.0
CAMERA_TOP=61.0
CAMERA_OD=122.0
CAMERA_BORE=36.0
# Bearing group z=0..30, upper cap z=30..35, locknut envelope z=32..38.
# Connector geometry is in V1.6 LOCAL ROT frame before V1.7 +13 mm offset.
SHAFT_END=45.0
NUT_TOP=38.0
PIN_BOTTOM=48.2
PIN_TOP=57.8

METAL=cq.Color(.36,.68,.82)
CAMERA=cq.Color(.38,.72,.49)
DOWEL=cq.Color(.90,.60,.30)
BOLT=cq.Color(.80,.47,.36)


def ring(od,id_,z0,z1):
    assert od>id_>0 and z1>z0
    return cq.Workplane('XY').circle(od/2).circle(id_/2).extrude(z1-z0).translate((0,0,z0))


def drill(shape,x,y,diameter,z0,z1):
    tool=cq.Workplane('XY').center(x,y).circle(diameter/2).extrude(z1-z0).translate((0,0,z0))
    return shape.cut(tool)


def centers(n,pcd,offset_degrees=0.):
    return [(pcd/2*math.cos(math.radians(offset_degrees+360*i/n)),
             pcd/2*math.sin(math.radians(offset_degrees+360*i/n))) for i in range(n)]


def spindle():
    # One contiguous metal body: nominal 40 mm bearing journal, Ø30 through-bore,
    # Ø48 bottom bearing abutment, extended journal, and Ø110 integral hub.
    s=ring(40,30,-7,SHAFT_END).union(ring(48,30,-7,0))
    s=s.union(ring(FLANGE_OD,30,FLANGE_BOTTOM,FLANGE_TOP))
    for x,y in centers(BOLT_N,BOLT_PCD,30):
        s=drill(s,x,y,BOLT_CLEARANCE_D,FLANGE_BOTTOM,FLANGE_TOP)
    for x,y in centers(DOWEL_N,DOWEL_PCD):
        s=drill(s,x,y,DOWEL_HOLE_D,48,FLANGE_TOP) # blind drilling datum only
    return s


def camera_blank():
    # This is NOT an Arca clamp and has no model-specific vendor hole pattern.
    p=ring(CAMERA_OD,CAMERA_BORE,FLANGE_TOP,CAMERA_TOP)
    for x,y in centers(BOLT_N,BOLT_PCD,30):
        p=drill(p,x,y,BOLT_CLEARANCE_D,FLANGE_TOP,CAMERA_TOP)
    for x,y in centers(DOWEL_N,DOWEL_PCD):
        p=drill(p,x,y,DOWEL_HOLE_D,FLANGE_TOP,58) # blind pocket; unqualified fit
    return p


def dowel(x,y):
    return cq.Workplane('XY').center(x,y).circle(DOWEL_D/2).extrude(PIN_TOP-PIN_BOTTOM).translate((0,0,PIN_BOTTOM))


def fastener(x,y):
    # Single connected illustrative M6 bolt: smooth Ø6 shank and Ø10.5 head.
    # No thread, anti-rotation washer, preload or tightening access certified.
    s=(cq.Workplane('XY').center(x,y).circle(BOLT_D/2).extrude(20)
       .translate((0,0,41)))
    s=s.union(cq.Workplane('XY').center(x,y).circle(10.5/2).extrude(4).translate((0,0,CAMERA_TOP)))
    return s


def nut(x,y):
    # A reference envelope, not a modeled ISO hex nut or verified thread.
    return (cq.Workplane('XY').center(x,y).circle(12/2).circle(6.2/2)
            .extrude(4).translate((0,0,41)))


def joint_parts():
    parts=[dict(name=SPINDLE_NAME,shape=spindle(),role='spindle',rotating=True,color=METAL),
           dict(name=CAMERA_NAME,shape=camera_blank(),role='camera',rotating=True,color=CAMERA)]
    for i,(x,y) in enumerate(centers(DOWEL_N,DOWEL_PCD),1):
        parts.append(dict(name=f'v18_METAL_POSITIVE_SHEAR_DOWEL_{i}_DIAM6_FIT_PENDING',
                          shape=dowel(x,y),role='dowel',rotating=True,color=DOWEL))
    for i,(x,y) in enumerate(centers(BOLT_N,BOLT_PCD,30),1):
        parts.append(dict(name=f'v18_METAL_M6_THROUGH_BOLT_{i}_NO_THREAD',
                          shape=fastener(x,y),role='bolt',rotating=True,color=BOLT))
        parts.append(dict(name=f'v18_METAL_M6_NUT_ENVELOPE_{i}_NO_LOCK',
                          shape=nut(x,y),role='nut',rotating=True,color=BOLT))
    return parts


def reference_checks():
    assert 6==BOLT_N and 2==DOWEL_N
    # Radial ligaments of flange and blank; NOT mechanical resistance estimates.
    outer_ligament=FLANGE_OD/2-BOLT_PCD/2-BOLT_CLEARANCE_D/2
    inner_ligament=DOWEL_PCD/2-DOWEL_HOLE_D/2-30/2
    shortest= min(math.hypot(xb-xd,yb-yd) for xb,yb in centers(BOLT_N,BOLT_PCD,30)
                  for xd,yd in centers(DOWEL_N,DOWEL_PCD))
    assert outer_ligament>5 and inner_ligament>5 and shortest>(BOLT_CLEARANCE_D+DOWEL_HOLE_D)/2+5
    assert FLANGE_BOTTOM>NUT_TOP+5 and CAMERA_TOP>FLANGE_TOP
    return dict(bolt_pcd_mm=BOLT_PCD,bolt_count=BOLT_N,bolt_nominal_d_mm=BOLT_D,
        bolt_clearance_d_mm=BOLT_CLEARANCE_D,dowel_pcd_mm=DOWEL_PCD,dowel_count=DOWEL_N,
        dowel_nominal_d_mm=DOWEL_D,dowel_nominal_hole_mm=DOWEL_HOLE_D,
        shaft_journal_mm=40.0,shaft_bore_mm=30.0,integral_flange_od_mm=FLANGE_OD,
        flange_z_mm=[FLANGE_BOTTOM,FLANGE_TOP],plate_z_mm=[FLANGE_TOP,CAMERA_TOP],
        worst_outer_radial_ligament_mm=round(outer_ligament,2),
        minimum_center_separation_bolt_dowel_mm=round(shortest,2),
        upper_nut_to_flange_clearance_mm=FLANGE_BOTTOM-NUT_TOP,
        torque_path='camera plate -> 2 dowels (after fit clearance) -> one-piece spindle flange; M6 bolts clamp the metal faces',
        axial_path='camera blank -> 6 provisional bolts/nuts -> one-piece flange -> spindle; no independent fall arrest',
        groove_or_coupler_qualified=False,bolt_tension_fatigue_qualified=False,
        dowel_shear_bearing_stress_qualified=False,independent_tether_installed=False,
        bearing_preload_qualified=False)


def pin_torque_study(torque_Nm:float,n=2,pcd_mm=68,diam_mm=6):
    """Nominal equal-sharing single-shear arithmetic ONLY (not pin qualification)."""
    if min(torque_Nm,n,pcd_mm,diam_mm)<=0:raise ValueError('positive inputs required')
    force_N=1000*torque_Nm/(n*(pcd_mm/2))
    stress_MPa=force_N/(math.pi*(diam_mm/2)**2)
    return dict(torque_Nm=torque_Nm,pin_force_N=round(force_N,3),
                nominal_single_shear_MPa=round(stress_MPa,4),
                caveat='Equal force sharing and simple shear only; no shock, clearance impact, bending, fatigue, hole bearing or pullout')


def old_part_retained(row):
    return not ('V16_HOLLOW_METAL_SPINDLE_' in row['name'] or 'V16_CAMERA_FIXTURE_INTERFACE_BLANK' in row['name'])


def integration_parts(lat=35.,dec=25.,rot=0.):
    original=[p for p in v17.integration_parts(lat,dec,rot) if old_part_retained(p)]
    inserted=[]
    for p in joint_parts():
        s=p['shape'].translate((0,0,v17.CARTRIDGE_Z_ABOVE_BRIDGE))
        s=v17.v11.rotor_local_to_mount(s,lat,dec,rot,rotating=True)
        inserted.append(dict(name=p['name'],shape=s,role='metal_joint_UNQUALIFIED',color=p['color']))
    return original+inserted


def records(lat=35.,dec=25.,rot=0.):
    rec=v17.base_parts(lat,dec)+integration_parts(lat,dec,rot)
    if len({p['name'] for p in rec})!=len(rec):raise ValueError('duplicate names')
    return rec


def print_flat_nonload_gauge():
    # PETG alignment gauge only: dual Ø6.2 holes at PCD68 plus central pilot bore,
    # flat XY at z0. NEVER part of the metal joint or retention load path.
    s=ring(84,30,0,3)
    for x,y in centers(DOWEL_N,DOWEL_PCD):s=drill(s,x,y,DOWEL_HOLE_D,0,3)
    return s


def save_assy(path,parts,name):
    a=cq.Assembly(name=name)
    for row in parts:a.add(row['shape'],name=row['name'],color=row['color'])
    a.save(str(path),exportType='STEP')


def build(out:Path,latitude=35.,dec_angle=25.,rot_angle=0.):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    metrics=reference_checks()
    parts=joint_parts()
    whole=records(latitude,dec_angle,rot_angle)
    sub=integration_parts(latitude,dec_angle,rot_angle)
    save_assy(out/NAME,whole,'V18_FULL_3AXIS_METAL_POSITIVE_JOINT_UNQUALIFIED')
    save_assy(out/SUB,sub,'V18_DEC_ROT_JOINT_UNQUALIFIED')
    save_assy(out/'OpenEQMount_V18_LOCAL_SHAFT_TO_CAMERA_INTERFACE_UNQUALIFIED.step',parts,
              'V18_LOCAL_METAL_JOINT_UNQUALIFIED')
    for p in parts[:2]:
        cq.exporters.export(p['shape'],str(out/(p['name']+'.step')),exportType='STEP')
    gauge=print_flat_nonload_gauge()
    gauge_name='v18_NONLOAD_DOWEL_PCD68_TRANSFER_COUPON_PRINT_FLAT'
    cq.exporters.export(gauge,str(out/(gauge_name+'.step')),exportType='STEP')
    cq.exporters.export(gauge,str(out/(gauge_name+'.stl')),exportType='STL',tolerance=.08,angularTolerance=.16)
    study=[pin_torque_study(t) for t in (0.785,2.4525,5.0)]
    (out/'torque_study_ILLUSTRATIVE.json').write_text(json.dumps(study,indent=2)+'\n')
    m=dict(release='V1.8',status='prototype_unqualified',whole_step=NAME,
         subassembly_step=SUB,whole_solids=len(whole),subassembly_solids=len(sub),local_joint_solids=len(parts),
         replaces_V16_floating_camera_blank=True, replaces_V16_spindle=True,
         metrics=metrics,angle_reference=dict(latitude=latitude,dec=dec_angle,rot=rot_angle),
         reference_dowels=2,reference_through_bolts=6,metal_primary_path_only=True,
         nominal_positive_drive_concept=True,transmission_and_axial_retention_PHYSICALLY_verified=False,
         actual_M6_fasteners_installed=False,actual_pin_fit_installed=False,
         independent_payload_tether_attached=False,camera_cage_lens_clamp_selected=False,
         bearing_pair_preload_verified=False,OEM_reducer_bolt_pattern_verified=False,
         fail_safe_completed=False,whole_mount_collision_sweep_completed=False,
         safe_to_energize=False,payload_approved=False,gate_A='digital geometry and naming ONLY',
         gate_B='PENDING',gate_C='PENDING',
         nonload_printed_parts=[dict(name=gauge_name,material='PETG NONSTRUCTURAL print-only gauge',
          print_orientation='XY flat Z0',layer_direction='+Z',stress_in_Z='none; no mechanical load',
          minimum_nominal_wall_mm=6.9,overhang_strategy='vertical through holes, slicer review PENDING',
          metal_joint='NO metal contact, must never be installed in loaded joint',
          field_load_approved=False,gate_B='PENDING',gate_C='PENDING')],
         unresolved=['V16 7008AWDB bearings CN clearance is NOT validated preload',
          'Dowel fit ISO 8734/pin retention/true pin bearing pressure and fatigue require engineer signoff',
          'M6 fastener grade, preload, lock, cyclic loads, washer/nut retention and wrench access pending',
          'Positive torque interface is only a model; metal primary axial joint still has no independent tether',
          'One-piece spindle flange must be assessed for CNC feasibility, wall thickness and fatigue',
          'Camera cage/lens clamp OEM interface and secondary anchor cannot be resolved without real hardware',
          'Axis envelope, cable sweep and all Gate B/C physical qualifications remain pending'])
    (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'V1.8 digital CAD: {len(whole)} whole bodies; {len(sub)} integration bodies; {len(parts)} joint bodies')
    return m

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).parent/'v18_generated')
    p.add_argument('--latitude',type=float,default=35.);p.add_argument('--dec-angle',type=float,default=25.);p.add_argument('--rot-angle',type=float,default=0.)
    a=p.parse_args();build(a.out,a.latitude,a.dec_angle,a.rot_angle)
