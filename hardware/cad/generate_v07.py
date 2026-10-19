#!/usr/bin/env python3
"""OpenEQMount V0.7: stationary RA adapter and RA/DEC isolated belt test fixtures.

No physical load rating. Units: mm. ALL upper wedge coordinates before latitude
rotation follow generate_v05. No pulley is a fabricated wave-generator coupling.
No fabricated FDM part belongs to the transmission torque or payload load path.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
import json
import math
from pathlib import Path
import cadquery as cq
import generate_v05 as v05

VERSION = 'V0.7'
STATUS = 'prototype_unqualified_Gate_A_only'
PRINT = 'PETG bench-fit only, no mechanical load approval'
METAL = 'metal prototype; dimensions/strength/retention unqualified'
REAR_PCD_RA = 71.0           # supplier drawing requires hole ANGULAR PHASE confirmation
REAR_PCD_DEC = 65.0          # as above
GEARBOX_RA_OD = 79.0
GEARBOX_DEC_OD = 73.0
RA_MOUNT_BOLT_X = (-43.0, 65.0)  # NEW holes: replacement wedge deck needed
RA_MOUNT_BOLT_Y = (-27.0, 27.0)  # clear of V0.6 upper lock lugs, subject to physical review
REDUCER_PHASE_DEG = 30.0   # NOT OEM-confirmed; do not freeze as manufacturing specification
BASE_Z0, BASE_Z1 = 56.0, 64.0
RISER_Z0, RISER_Z1 = BASE_Z1, 85.0
RA_FLANGE_Z0, RA_FLANGE_Z1 = RISER_Z1, 93.0
RA_REDUCER_HEIGHT = 45.0
MOTOR_CENTER_NOMINAL = 115.0
MOTOR_CENTER_TRAVEL = 5.0
BELT_PITCH = 2.0
PULLEY_TEETH = (60, 20)      # larger gear pulley nominal 60T; motor 20T


def hole_xy(points,diameter,z0,z1):
    return (cq.Workplane('XY').pushPoints(points).circle(diameter/2)
            .extrude(z1-z0).translate((0,0,z0)))


def circle_points(pcd,count=6,phase=0):
    return [(pcd/2*math.cos(math.radians(phase+360*i/count)),
             pcd/2*math.sin(math.radians(phase+360*i/count))) for i in range(count)]


def wedge_holes():
    return [(x,y) for x in RA_MOUNT_BOLT_X for y in RA_MOUNT_BOLT_Y]


def upgraded_wedge_top_local():
    # V0.5 top deck requires FOUR EXTRA METAL holes. Original V0.6 holes stay untouched.
    p=v05.tilt_assembly_local()
    return p.cut(hole_xy(wedge_holes(),6.6,23.0,31.0))


def ra_wedge_interface_plate_local():
    """Metal adapter BASE over V0.5 top deck; does not attach to rotating RA output."""
    p=(cq.Workplane('XY').box(172,110,BASE_Z1-BASE_Z0,centered=(True,True,False))
       .translate((10,0,BASE_Z0)))
    p=p.cut(hole_xy(wedge_holes(),6.6,BASE_Z0-1,BASE_Z1+1))
    p=p.cut(hole_xy([(0,0)],58,BASE_Z0-1,BASE_Z1+1))
    return p


def ra_lower_post_local(x,y):
    # Independent 26mm metal post lifts the stator structure ABOVE V0.6 locking lugs.
    return (cq.Workplane('XY').center(x,y).circle(8.0).circle(3.3)
            .extrude(BASE_Z0-30.0).translate((0,0,30.0)))


def ra_riser_local(x,y):
    """Machined metal annular spacer; continuous metal bolts, not polymer columns."""
    h=RISER_Z1-RISER_Z0
    p=(cq.Workplane('XY').center(x,y).circle(8.0).circle(3.3)
       .extrude(h).translate((0,0,RISER_Z0)))
    return p


def ra_fixed_stator_flange_local():
    """REDUCER REAR HOUSING ONLY; provisional bolt-angle phase must be verified."""
    p=(cq.Workplane('XY').box(172,110,RA_FLANGE_Z1-RA_FLANGE_Z0,
        centered=(True,True,False)).translate((10,0,RA_FLANGE_Z0)))
    p=p.cut(hole_xy([(0,0)],58,RA_FLANGE_Z0-1,RA_FLANGE_Z1+1))
    p=p.cut(hole_xy(wedge_holes(),6.6,RA_FLANGE_Z0-1,RA_FLANGE_Z1+1))
    p=p.cut(hole_xy(circle_points(REAR_PCD_RA,6,REDUCER_PHASE_DEG),4.5,
                    RA_FLANGE_Z0-1,RA_FLANGE_Z1+1))
    return p


def reducer_envelope_local():
    """V0.3-sized spatial cylinder, NOT OEM installation detail."""
    return (cq.Workplane('XY').circle(GEARBOX_RA_OD/2).extrude(RA_REDUCER_HEIGHT)
            .translate((0,0,RA_FLANGE_Z1)))


def ra_interface_metal(lat=35.0):
    if not v05.LAT_MIN <= lat <= v05.LAT_MAX:
        raise ValueError('Latitude is outside the V0.5 prototype 25–45 degree range')
    result={
       'v07_wedge_RA_STATOR_BASE_METAL':ra_wedge_interface_plate_local(),
       'v07_WEDGE_REPLACEMENT_TOP_DECK_METAL':upgraded_wedge_top_local(),
       'v07_RA_STATOR_REAR_FLANGE_METAL':ra_fixed_stator_flange_local(),
    }
    for i,(x,y) in enumerate(wedge_holes(),1):
        result[f'v07_RA_RISER_{i}_METAL']=ra_riser_local(x,y)
        result[f'v07_RA_LOWER_POST_{i}_METAL']=ra_lower_post_local(x,y)
    # Latitude rotation is applied to ALL stationary parts as one body,
    # around the V0.5 *actual* hinge pivot.
    return {k:v05.pivot_rotate(shape,90-lat) for k,shape in result.items()}


def belt_pitch_diameter(teeth):
    return teeth*BELT_PITCH/math.pi


def belt_pitch_length(center_distance):
    if center_distance<=0:raise ValueError('center_distance must be positive')
    d_big=belt_pitch_diameter(PULLEY_TEETH[0]);d_small=belt_pitch_diameter(PULLEY_TEETH[1]);
    if center_distance <= (d_big-d_small)/2:
        raise ValueError('pulley circles would overlap')
    # Conventional open belt preliminary approximation, not an orderable SKU.
    return (2*center_distance+math.pi/2*(d_big+d_small)
            +(d_big-d_small)**2/(4*center_distance))


def motor_screw_centers(center=MOTOR_CENTER_NOMINAL):
    return [(center+dx,dy) for dx in (-15.5,15.5) for dy in (-15.5,15.5)]


def belt_cassette_metal(axis):
    """Flat BENCH ONLY steel/aluminum fixture. Not fitted to the polar wedge."""
    if axis not in ('ra','dec'):raise ValueError(axis)
    # Concentric bearing-free clearance, no assumed input diameter / output bearing.
    inlet=58.0 if axis=='ra' else 54.0
    p=cq.Workplane('XY').circle(53).extrude(7)
    p=p.union(cq.Workplane('XY').box(115,42,7,centered=(True,True,False)).translate((57.5,0,0)))
    p=p.union(cq.Workplane('XY').center(MOTOR_CENTER_NOMINAL,0).circle(40).extrude(7))
    p=p.cut(hole_xy([(0,0)],inlet, -1,8))
    for x,y in circle_points(92,4,45):
        p=p.cut(hole_xy([(x,y)],5.5,-1,8))
    # The motor pilot centre slot is >=23 mm wide to avoid body interference.
    p=p.cut((cq.Workplane('XY').center(MOTOR_CENTER_NOMINAL,0)
             .slot2D(23+2*MOTOR_CENTER_TRAVEL,23).extrude(9).translate((0,0,-1))))
    for x,y in motor_screw_centers():
        p=p.cut((cq.Workplane('XY').center(x,y)
                .slot2D(3.6+2*MOTOR_CENTER_TRAVEL,3.6).extrude(9)
                .translate((0,0,-1))))
    return p


def pulley_pitch_envelope(teeth,center_x):
    # Reference pitch cylinder *not* a CAD GT2 toothed pulley, hub or wave input.
    return (cq.Workplane('XY').center(center_x,0)
            .circle(belt_pitch_diameter(teeth)/2).extrude(6).translate((0,0,12)))


def printable_covers():
    """Optional loose identification/geometry gauges; NEVER moving guards under power."""
    out={}
    for axis in ('ra','dec'):
        # A nonstructural translucent-view panel; intentionally no mechanical mounting interface.
        p=(cq.Workplane('XY').box(100,34,3,centered=(True,True,False))
           .edges('|Z').fillet(5))
        p=p.cut(hole_xy([(-38,0),(38,0)],5.4,-1,5))
        # Different outline for axis to avoid confusing RA/DEC labels
        p=p.cut(cq.Workplane('XY').box(8,6,5).translate((0, 17 if axis=='ra' else -17,1.5)))
        out[f'v07_{axis}_NONLOAD_LID_GAUGE_PRINT_FLAT']=p
    coupon=(cq.Workplane('XY').box(96,25,4,centered=(True,True,False))
            .edges('|Z').fillet(3))
    for x,d in zip((-34.,-12.,12.,34.),(3.4,3.6,4.4,4.6)):
        coupon=coupon.cut(hole_xy([(x,0)],d,-1,6))
    out['v07_M3_M4_TOLERANCE_GAUGE_PRINT_FLAT']=coupon
    return out


def print_record(name,shape):
    b=shape.val().BoundingBox()
    return dict(name=name,material=PRINT,status='prototype_unqualified',
      role='loose decorative bench panel / dimensional calibration coupon only',
      print_orientation='bottom XY surface on Z=0, +Z layer build',
      layer_direction='XY face, no approved structural load along XY or Z',
      load_path='NONE. Not a belt guard or fastener, do not install on powered assembly',
      overhang_strategy='flat design; mandatory manual slicer review',
      metal_joint='NONE — not permitted to restrain any axis or moving part',
      min_wall_mm='pending Gate B slicer/actual extrusion width',
      slicer_gate_B='pending',physical_gate_C='pending',
      field_load_approved=False,bbox_mm=[round(b.xlen,2),round(b.ylen,2),round(b.zlen,2)],
      volume_cc=round(shape.val().Volume()/1000,2))


def export(out:Path,lat=35):
    if not v05.LAT_MIN <= lat <= v05.LAT_MAX:raise ValueError('latitude out of range')
    out.mkdir(parents=True,exist_ok=True)
    prints=printable_covers()
    metal=ra_interface_metal(lat)
    metal.update({f'v07_{axis}_BELT_BENCH_ONLY_METAL':belt_cassette_metal(axis)
                  for axis in ('ra','dec')})
    data=dict(release=VERSION,status=STATUS,latitude_deg=lat,
      manufacturing_approval=False,mechanical_load_approved=False,
      input_coupling_verified=False, OEM_bolt_phase_verified=False,
      payload_rated_kg=None,
      wedge_RA_mount=dict(mode='stationary reducer housing only',
           wedge_pilot_holes_mm=wedge_holes(),wedge_requires_replacement_drilled_deck=True,reducer_rear_pcd_mm=REAR_PCD_RA,
           phase_deg=REDUCER_PHASE_DEG,phase_verified=False),
      belt=dict(pitch_mm=BELT_PITCH,teeth={'driven':60,'motor':20},
          motor_distance_nominal_mm=MOTOR_CENTER_NOMINAL,
          adjustment_plus_minus_mm=MOTOR_CENTER_TRAVEL,
          ratio=3.0,approx_pitch_length_mm={str(v):round(belt_pitch_length(v),3)
               for v in (110.,115.,120.)},
          coupling='UNKNOWN; no wave generator bore, keyway, clamping or axial location specified'),
      metal_parts=[],printed_parts=[],
      warnings=[
        'Prototype only: NEVER power the motor or carry camera payload using this release.',
        'RA fixed casing / rotating RA output MUST remain distinct. Do not tie either to a moving wedge member incorrectly.',
        'The adapter has an UNVERIFIED rear M4 angular phase; OEM/actual reducer rear layout must be checked first.',
        'Gearbox 2UH INPUT wave-generator shaft/bore/axial plane is UNKNOWN. The pulley drawings are pitch envelopes only.',
        'Belt cassette is an UNATTACHED desk fixture. No connection to the reducer or polar wedge is implied.',
        'Replacement wedge deck adds four NEW metal through-holes to avoid V0.6 upper lock lugs. Original V0.5 top plate cannot directly accept this adapter.',
        'Two levels of metal posts are needed to lift RA stator OVER V0.6 lock lugs; bolt stack and driver/tool access not approved.',
        'Upper fixed adaptor standoffs and bolts are METAL ONLY and not statically or fatigue verified.',
        'DfAM Gate A is digital only. Gate B print & fit and Gate C actual load/creep/retention testing pending.'])
    for name,part in prints.items():
        bb=part.val().BoundingBox()
        if bb.zmin < -1e-5 or len(part.solids().vals())!=1 or max(bb.xlen,bb.ylen)>220:
            raise RuntimeError('Print model failed geometry constraints: '+name)
        cq.exporters.export(part,str(out/(name+'.step')),exportType='STEP')
        cq.exporters.export(part,str(out/(name+'.stl')),exportType='STL',tolerance=.12,angularTolerance=.15)
        data['printed_parts'].append(print_record(name,part))
    for name,part in metal.items():
        if len(part.solids().vals())!=1:raise RuntimeError('bad metal solid '+name)
        cq.exporters.export(part,str(out/(name+'.step')),exportType='STEP')
        b=part.val().BoundingBox()
        data['metal_parts'].append(dict(name=name,material=METAL,
            role='metal only. NO printed structural replacements.',
            bbox_mm=[round(b.xlen,2),round(b.ylen,2),round(b.zlen,2)]))
    asm=cq.Assembly(name='V07_STATOR_INTERFACE_UNQUALIFIED')
    # Replacement top deck is exported in the assembly already; original deck is omitted.
    # V0.6 clamp lugs are included solely to highlight clearances in a CAD viewer.
    for name,part in ra_interface_metal(lat).items():
        asm.add(part,name=name,color=cq.Color(.70,.75,.78) if 'WEDGE_REPLACEMENT' in name else cq.Color(.28,.56,.72))
    asm.add(v05.pivot_rotate(reducer_envelope_local(),90-lat),
            name='RA_REDUCER_UNQUALIFIED_ENVELOPE',color=cq.Color(.85,.55,.20))
    asm.save(str(out/'OpenEQMount_V07_RA_STATOR_UNQUALIFIED_assembly.step'),exportType='STEP')
    for axis in ('ra','dec'):
        fixture=cq.Assembly(name=f'V07_{axis.upper()}_BELT_BENCH_ONLY')
        fixture.add(belt_cassette_metal(axis),name='METAL_UNQUALIFIED',color=cq.Color(.6,.66,.7))
        fixture.add(pulley_pitch_envelope(60,0),name='LARGE_PULLEY_PITCH_ONLY',color=cq.Color(.88,.56,.2))
        fixture.add(pulley_pitch_envelope(20,MOTOR_CENTER_NOMINAL),
                    name='MOTOR_PULLEY_PITCH_ONLY',color=cq.Color(.2,.55,.78))
        fixture.save(str(out/f'OpenEQMount_V07_{axis}_BELT_PITCH_ONLY_assembly.step'),exportType='STEP')
    (out/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=Path(__file__).parent/'v07_generated')
    p.add_argument('--latitude',type=float,default=35)
    args=p.parse_args()
    r=export(args.out,args.latitude)
    print(f'{VERSION}: {len(r["metal_parts"])} metal ref, {len(r["printed_parts"])} printable non-load coupons; no physical approval')

if __name__=='__main__':main()
