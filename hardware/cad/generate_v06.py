#!/usr/bin/env python3
"""OpenEQMount V0.6: metal latitude lock / stop / generic tripod interface.

Engineering CAD for bench-fit only; zero structural load certification. mm.
Latitude frame is inherited from V0.5, with north=-X and rotation about Y.
The lock clamp and travel-stop use *different* slot/pin pairs, so releasing the
clamp does not remove geometric end-stop function if pins are retained.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
import json
import math
from pathlib import Path
import cadquery as cq
import generate_v05 as v05

VERSION='V0.6'
STATUS='prototype_unqualified_Gate_A_only'
LOCK_PIN_LOCAL=(31.,0.,42.)   # exact Y of each lug supplied independently
STOP_PIN_LOCAL=(17.,0.,42.)
SIDE_Y=63.                  # nominal plate mid-plane (+/-)
SIDE_T=6.
MIN_LAT,MAX_LAT=v05.LAT_MIN,v05.LAT_MAX
METAL='metal reference, not approved for manufacture or load'
PRINT='PETG bench-fit only; field/structural use prohibited'


def slot_geometry(local_point):
    x,z=local_point[0]-v05.PIVOT[0],local_point[2]-v05.PIVOT[2]
    return math.hypot(x,z),math.degrees(math.atan2(z,x))


def pin_center(local_point,lat):
    return v05.tilted_point(local_point,lat)


def xz_arc_cut(radius,phase,diameter,lat_min=MIN_LAT,lat_max=MAX_LAT,margin_deg=.65):
    # Two independent arcuate slots around the *physical* hinge axis (-61,29).
    a0=90-lat_max+phase-margin_deg
    a1=90-lat_min+phase+margin_deg
    ang=[a0+(a1-a0)*i/80 for i in range(81)]
    def xy(a,r):return (v05.PIVOT[0]+r*math.cos(math.radians(a)),
                       v05.PIVOT[2]+r*math.sin(math.radians(a)))
    outside=[xy(a,radius+diameter/2) for a in ang]
    inside=[xy(a,radius-diameter/2) for a in reversed(ang)]
    sh=cq.Workplane('XZ').polyline(outside+inside).close().extrude(240,both=True)
    for a in (a0,a1):
        x,z=xy(a,radius)
        sh=sh.union(v05.bore_y(x,z,diameter))
    return sh


@lru_cache(maxsize=20)
def lock_sideplate(sign):
    """Metal sheet with separate M8 lock and M6 positive end-stop slots."""
    # Outer profile: foot is not in the V0.5 hinge-cheek bounding range.
    outline=[(-22,19.9),(21,19.9),(21,142),(-51,142),(-39,82),(-29,36)]
    sh=cq.Workplane('XZ').polyline(outline).close().extrude(SIDE_T)
    # XZ normal -Y: shift into +/-63 centered lateral plate.
    y=sign*SIDE_Y
    sh=sh.translate((0,y+SIDE_T/2,0))
    for point,diam in ((LOCK_PIN_LOCAL,9.0),(STOP_PIN_LOCAL,7.0)):
        radius,phase=slot_geometry(point)
        sh=sh.cut(xz_arc_cut(radius,phase,diam))
    foot=cq.Workplane('XY').box(53,16,6).translate((4,y,17))  # x[-22.5,30.5]
    sh=sh.union(foot)
    # Vertical M6 through-fasteners; bolts attach to metal azimuth deck.
    for x in (-12.,15.):
        sh=sh.cut(v05.cutter_z([(x,y)],6.6,z0=12.8,height=9))
    return sh


@lru_cache(maxsize=20)
def az_deck_with_lock_bolt_holes():
    sh=v05.azimuth_deck()
    for sign in (-1,1):
        for x in (-12.,15.):
            sh=sh.cut(v05.cutter_z([(x,sign*SIDE_Y)],6.6,z0=7,height=9))
    return sh


@lru_cache(maxsize=20)
def lock_upper_lug(sign,lat):
    """Metal retrofit block bolts to existing V0.5 top deck x45/y+/-45.

    2 bored crosspins on the metal block: clamp and independent stop.
    The specific M6 bolt/nut/head access and shoulder-pin retention still
    require OEM drawing and real bench assembly review before fabrication.
    """
    y=sign*45.
    # Foot rests on the V0.5 tilted top face z=30 in its local coordinates.
    foot=cq.Workplane('XY').box(55,21,6).translate((35,y+sign*2.5,33))
    block=cq.Workplane('XY').box(32,15,18).translate((24,y+sign*5.5,45))
    lug=foot.union(block)
    for xx,d in ((LOCK_PIN_LOCAL[0],8.6),(STOP_PIN_LOCAL[0],6.6)):
        lug=lug.cut(v05.bore_y(xx,42,d))
    # Existing V0.5 top deck has x45 +/-45 through clearance Ø6.6.
    lug=lug.cut(v05.cutter_z([(45,y)],6.6,z0=29,height=11))
    # Counterbore in the *metal* foot only, avoid interference with tower.
    lug=lug.cut(v05.cutter_z([(45,y)],10.2,z0=34.8,height=1.4))
    return v05.pivot_rotate(lug,90-lat)


def metal_pin_envelope(local_point,lat,diameter,sign):
    p=pin_center(local_point,lat)
    # Only a reference diameter/location, not a pin selection or threaded joint.
    lo=sign*53;hi=sign*77
    return v05.along((p[0],lo,p[2]),(p[0],hi,p[2]),diameter/2)


@lru_cache(maxsize=20)
def tripod_adapter_plate(stud_diameter=10.5):
    """Replaceable metal adapter to V0.5 PCD62, not any specific tripod SKU."""
    if stud_diameter not in (10.5,10.0):raise ValueError('only Ø10.5 / Ø10.0 bench variants')
    sh=cq.Workplane('XY').circle(73).extrude(6).translate((0,0,-6))
    sh=sh.cut(v05.cutter_z([(0,0)],stud_diameter,z0=-7,height=9))
    for a in (30.,150.,270.):
        x,y=62*math.cos(math.radians(a)),62*math.sin(math.radians(a))
        sh=sh.cut(v05.cutter_z([(x,y)],6.6,z0=-7,height=9))
    return sh


def printable_guard(sign):
    # A loose visor/marking guard, printed FLAT, not an end stop or lock.
    sh=cq.Workplane('XY').polyline([(-48,-10),(14,-10),(23,0),(14,10),(-48,10)]).close().extrude(3)
    sh=sh.edges('|Z').fillet(2.5)
    sh=sh.cut(v05.cutter_z([(-36,0),(2,0)],4.4,z0=-1,height=5))
    # Handed inspection notch, no load-bearing purpose.
    sh=sh.cut(cq.Workplane('XY').box(8,4,5).translate((-21,sign*10,1.5)))
    return sh


def fit_gauge():
    sh=cq.Workplane('XY').box(116,28,5,centered=(True,True,False)).edges('|Z').fillet(3)
    for x,d in zip((-45.,-22.,1.,24.,46.),(6.4,6.6,8.4,8.6,10.5)):
        sh=sh.cut(v05.cutter_z([(x,0)],d,z0=-1,height=8))
    return sh


def safe_stop_badge():
    sh=cq.Workplane('XY').box(64,26,3,centered=(True,True,False)).edges('|Z').fillet(3)
    sh=sh.cut(v05.cutter_z([(-25,0),(25,0)],3.4,z0=-1,height=5))
    return sh


def printed_parts():
    return {'v06_left_lock_GUARD_PRINT_FLAT':printable_guard(-1),
            'v06_right_lock_GUARD_PRINT_FLAT':printable_guard(1),
            'v06_bolt_fit_GAUGE_PRINT_FLAT':fit_gauge(),
            'v06_unqualified_WARNING_TAG_PRINT_FLAT':safe_stop_badge()}


def metal_parts(lat=35):
    if not MIN_LAT <= lat <= MAX_LAT:raise ValueError('latitude out of V0.6 trial range')
    out={
        'v06_az_deck_WITH_LOCK_M6_HOLES_METAL':az_deck_with_lock_bolt_holes(),
        'v06_tripod_PCD62_M10_GENERIC_METAL':tripod_adapter_plate(10.5),
        'v06_tripod_PCD62_3_8_CLEARANCE_GENERIC_METAL_OPTION':tripod_adapter_plate(10.0)}
    for sign,label in ((-1,'LEFT'),(1,'RIGHT')):
        out[f'v06_lock_sector_{label}_METAL']=lock_sideplate(sign)
        out[f'v06_upper_lock_lug_{label}_METAL']=lock_upper_lug(sign,lat)
        out[f'v06_M8_clamp_pin_{label}_METAL_ENVELOPE']=metal_pin_envelope(LOCK_PIN_LOCAL,lat,8,sign)
        out[f'v06_M6_stop_pin_{label}_METAL_ENVELOPE']=metal_pin_envelope(STOP_PIN_LOCAL,lat,6,sign)
    return out


def dfam_entry(name,part):
    bb=part.val().BoundingBox()
    return dict(name=name,material=PRINT,status='prototype_unqualified',
      role='non-load-bearing guard or hole calibration coupon',
      print_orientation='flat bottom at Z=0, +Z layers',
      layer_direction='Z interlayer only, no structural load permitted',
      load_path='NONE — all locking, stops, and tripod loads routed through metal parts',
      overhang_strategy='planar horizontal print; slicer review still required',
      metal_joint='loose cover only; printed features NEVER clamp load or stop the mount',
      min_wall_mm='to be measured during slicer Gate B',
      slicer_gate_B='pending',physical_gate_C='pending',
      bbox_mm=[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],
      volume_cc=round(part.val().Volume()/1000,2),
      field_load_approved=False)


def export(out:Path,lat=35):
    if not MIN_LAT <= lat <= MAX_LAT:raise ValueError('Latitude outside 25 to 45 trial range')
    out.mkdir(parents=True,exist_ok=True)
    data={'release':VERSION,'status':STATUS,'latitude_deg':lat,'lat_trial_range':[MIN_LAT,MAX_LAT],
      'printed_parts':[],'metal_parts':[],
      'lock_slot':dict(radius_mm=round(slot_geometry(LOCK_PIN_LOCAL)[0],3),
          angle_offsets_deg=round(slot_geometry(LOCK_PIN_LOCAL)[1],3),
          bolt_nominal='M8 clearance Ø9mm, reference only'),
      'stop_slot':dict(radius_mm=round(slot_geometry(STOP_PIN_LOCAL)[0],3),
          angle_offsets_deg=round(slot_geometry(STOP_PIN_LOCAL)[1],3),
          bolt_nominal='M6 clearance Ø7mm, metal-only end-stop path'),
      'tripod':{'base_variant':'provisional adapter Ø10.5','option':'Ø10.0 for 3/8-in candidate; not threaded',
          'stud_inserts':'NOT included; no rated tripod mounting specified'},
      'warnings':['NOT LOAD RATED: latch/pin yield, clamp friction, structural bolt engagement, hinge tolerances, fatigue and dynamic stopping energy NOT verified.',
                  'No claim of independent fall arrest. A lost/disengaged pin could still permit uncontrolled motion. Use no payload.',
                  'No specific reducer or tripod mating interface is confirmed; RA stator mount remains unverified.',
                  'Plate lock slots limit nominal latitude only if BOTH stop pins have rated metal retaining hardware; NOT yet approved.',
                  'Metal components must never be printed for structural service; metal thickness and fastener accessibility require prototype checks.',
                  'DfAM Gate A means closed STL & metadata only, not slicer Gate B or structural Gate C.']}
    for name,part in printed_parts().items():
        bb=part.val().BoundingBox()
        if bb.zmin < -1e-4 or len(part.solids().vals())!=1 or max(bb.xlen,bb.ylen)>220:
            raise ValueError('Bad FDM geometry '+name)
        cq.exporters.export(part,str(out/(name+'.step')),exportType='STEP')
        cq.exporters.export(part,str(out/(name+'.stl')),exportType='STL',tolerance=.12,angularTolerance=.15)
        data['printed_parts'].append(dfam_entry(name,part))
    mm=metal_parts(lat)
    for name,part in mm.items():
        cq.exporters.export(part,str(out/(name+'.step')),exportType='STEP')
        bb=part.val().BoundingBox()
        data['metal_parts'].append({'name':name,'material':METAL,'role':'METAL ONLY / 3D-print forbidden for load',
          'bbox_mm':[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)]})
    # One selected generic M10 adapter. Never assemble two tripod options at once.
    asm=cq.Assembly(name='V06_UNQUALIFIED_LOCKED_POLAR_WEDGE')
    existing=v05.metals(lat)
    ignored={'v05_azimuth_slew_DECK_METAL', 'v05_tripod_anchor_BASE_METAL'}
    for name,part in existing.items():
        if name not in ignored:
            asm.add(part,name=name,color=cq.Color(.68,.72,.76))
    asm.add(v05.fixed_triad_base(),name='V05_TripodMetalBase',color=cq.Color(.62,.65,.69))
    for name,part in mm.items():
        if 'OPTION' in name:continue
        clr=cq.Color(.91,.54,.20) if 'pin_' in name else cq.Color(.42,.57,.66)
        asm.add(part,name=name,color=clr)
    asm.save(str(out/'OpenEQMount_V06_UNQUALIFIED_assembly.step'),exportType='STEP')
    (out/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=Path(__file__).parent/'v06_generated')
    p.add_argument('--latitude',type=float,default=35.)
    args=p.parse_args();r=export(args.out,args.latitude)
    print(f'V0.6 unqualified: {len(r["printed_parts"])} prints, {len(r["metal_parts"])} metal references')

if __name__=='__main__':main()
