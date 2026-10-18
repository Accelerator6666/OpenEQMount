#!/usr/bin/env python3
"""OpenEQMount V0.3 printable reducer interface prototypes.

This is a BENCH-FIT PROTOTYPE, NOT a payload rated or collision-validated mount.
The actual reducer 2UH orientations and input wave-generator shaft must be confirmed
with the supplier drawing AND physical reducer before powering any motors.

CAD Z datum: reducer REAR/input face z=0; output face z=+length.
Printed housing rear cap -9..0; gearbox-body clearance sleeve 0..length-2.
All dimensions millimetres. Geometry is original and not copied from OEM CAD.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from dataclasses import dataclass,asdict
import cadquery as cq

@dataclass(frozen=True)
class Reducer:
    key: str
    model: str
    od: float
    length: float
    output_pcd: float
    output_thread: str
    output_clear: float
    head_dia: float
    head_depth: float
    rear_pcd: float
    rear_thread: str
    input_bearing: str
    bearing_id: float
    bearing_od: float
    bearing_width: float

RA = Reducer('ra','CSF-17-100-2UH',79.,45.,27.,'M5x10',5.5,10.,5.5,71.,'M4', '608-2RS',8.,22.,7.)
DEC = Reducer('dec','CSF-14-100-2UH',73.,41.,23.,'M4x8',4.5,8.5,4.5,65.,'M4','626-2RS',6.,19.,6.)

# ALL housing holes in this iteration are print-size nominal; changes required
# based on polymer, printer, orientation, vendor fastener tolerances.
BODY_DIAMETRAL_CLEARANCE=1.5
BOLT_ORIENTATION_DEG=30.0  # rotatable; 2UH rear threaded holes 30deg from alternated clearance row
BRIDGE_PCD=92.0
BRIDGE_M4_CLEAR=4.5
REAR_CAP_THICKNESS=9.0
SLEEVE_WALL=10.0


def circle_points(pcd:float,qty:int,start_deg:float=0.0):
    return [(pcd/2*math.cos(math.radians(start_deg + i*360/qty)),
             pcd/2*math.sin(math.radians(start_deg + i*360/qty))) for i in range(qty)]


def cylinder(d:float,h:float,z:float=0):
    return cq.Workplane('XY').circle(d/2).extrude(h).translate((0,0,z))


def cut_z(body,positions,diam:float,zlo:float,zhi:float):
    if not positions:return body
    punches=(cq.Workplane('XY').pushPoints(positions).circle(diam/2)
             .extrude(zhi-zlo).translate((0,0,zlo)))
    return body.cut(punches)


def output_adapter(r:Reducer):
    # Thread holes in OEM output flange PCD 27 for 17, PCD 23 for 14.
    # Counterbores leave >=6.5mm printed bottom under each cap-screw head.
    t=12 if r.key=='ra' else 11
    od=76 if r.key=='ra' else 70
    z0=r.length
    part=cylinder(od,t,z0)
    part=part.cut(cylinder(12.0 if r.key=='ra' else 10.0,t+2,z0-1))
    bolts=circle_points(r.output_pcd,6,90)
    part=cut_z(part,bolts,r.output_clear,z0-1,z0+t+1)
    part=cut_z(part,bolts,r.head_dia,z0+t-r.head_depth,z0+t+1)
    # Insert holes for project-side load plate only; the specified insert is NOT
    # necessarily structurally rated; require steel load-spreading plate.
    attach_pcd=58. if r.key=='ra' else 54.
    part=cut_z(part,circle_points(attach_pcd,4,45),5.6 if r.key=='ra' else 5.0,
               z0+t-7.,z0+t+0.2)
    return part


def housing(r:Reducer):
    inside=r.od+BODY_DIAMETRAL_CLEARANCE
    outer=inside+2*SLEEVE_WALL
    # Mount flange under the gearbox rear face; leave Ø58 clear on RA, Ø54 on DEC
    # for the actual input assembly. No polymer interference fit on gearbox OD.
    flange_outer=108. if r.key=='ra' else 104.
    center_open=58. if r.key=='ra' else 54.
    rear=cylinder(flange_outer,REAR_CAP_THICKNESS,-REAR_CAP_THICKNESS)
    rear=rear.cut(cylinder(center_open,REAR_CAP_THICKNESS+2,-REAR_CAP_THICKNESS-1))
    sleeve=cylinder(outer,r.length-2.,0).cut(cylinder(inside,r.length-1,0))
    part=rear.union(sleeve)
    # 2UH specific: the REAR face has 6 M4 threaded holes and 6 Ø4.5
    # alternative clearance holes, interleaved by 30 degrees. This flange uses
    # the 6 threaded holes; rotate start angle when physically verifying part.
    part=cut_z(part,circle_points(r.rear_pcd,6,BOLT_ORIENTATION_DEG),4.5,-10,0.5)
    # Bearing bridge heat-set-insert pilot holes (outside reducer bolt PCD),
    # 4 mounting points at 45 degrees on PCD 92. DON'T drill into OEM unit.
    part=cut_z(part,circle_points(BRIDGE_PCD,4,45),5.5,-9.2,-2.0)
    # Side two reinforced ears: 2 M4 heat-set insert pilots for NEMA slider
    # 9mm spacer, mounted from -Z. Size leaves motor separate from reducer.
    for yy in (-25.,25.):
        lug=cq.Workplane('XY').box(26,18,REAR_CAP_THICKNESS,centered=(True,True,False))
        lug=lug.translate((57,yy,-9))
        part=part.union(lug)
    part=cut_z(part,[(57,-25),(57,25)],5.5,-9.2,-2)
    return part


def nema_motor_carrier(r:Reducer):
    # Parallel motor shaft, nominal center x=85, y=0, center distance adjustable +/-5.
    # Motor on -Z side of bracket; 31x31 mm NEMA17 faceplate, M3 mounts.
    # Installation via exactly two metal M4 spacers, nominal 9mm long;
    # add third structural tie before live load testing.
    plate=(cq.Workplane('XY').box(66,68,7, centered=(True,True,False))
           .translate((85,0,-25)))
    plate=cut_z(plate,[(57,-25),(57,25)],4.5,-26,-17)
    # Motor pilot Ø22 => 24mm slot with +-5mm x-travel.
    pilot=(cq.Workplane('XY').center(85,0).slot2D(34,24,0).extrude(9)
           .translate((0,0,-26)))
    plate=plate.cut(pilot)
    # Elongated M3 clearances for tension movement, 31mm square pattern.
    for dx in (-15.5,15.5):
        for dy in (-15.5,15.5):
            cut=(cq.Workplane('XY').center(85+dx,dy).slot2D(13.5,3.6,0)
                 .extrude(9).translate((0,0,-26)))
            plate=plate.cut(cut)
    return plate


def bearing_bridge(r:Reducer):
    # Optional input shaft pilot/bridge only; installer MUST verify wave-generator
    # bore, axial position, OEM rotating/stationary members and bearing preload.
    # CAD frame shows its top face approx z=-12, pulley plane z=-11..-4.
    thick=9 if r.key=='ra' else 8
    bottom=-12-thick
    part=cylinder(106,thick,bottom)
    # bearing at Ø22/Ø19, intentionally nominal bore +0.15 (tune coupon)
    part=part.cut(cylinder(r.bearing_od+0.15,thick+2,bottom-1))
    # Optional 4 short standoffs ensure 3mm gap to rear cap z=-9.
    # At PCD92 corner bosses, material remains 7mm from outer rim.
    for x,y in circle_points(BRIDGE_PCD,4,45):
        part=part.union(cylinder(10,3,bottom+thick).translate((x,y,0)))
    part=cut_z(part,circle_points(BRIDGE_PCD,4,45),4.5,bottom-1,-8.5)
    # Relief against the motor slider: otherwise the outside arcs intersect
    # the moving NEMA17 carrier near +X. Does not remove the 45-degree lugs.
    relief=(cq.Workplane("XY").box(45,46,thick+5)
            .translate((70.5,0,bottom+thick/2)))
    part=part.cut(relief)
    return part


def output_collar_coupon(r:Reducer,extra:float):
    # Full ring 6 mm tall, test OD slip-fit to measured reducer body.
    size=r.od+extra
    return cylinder(size+8,6,0).cut(cylinder(size,8,-1))


def bearing_coupon(r:Reducer,bore_delta:float):
    # Optional test disc, never install with press force on the gearbox itself.
    return cylinder(r.bearing_od+14,6,0).cut(cylinder(r.bearing_od+bore_delta,8,-1))


def reducer_envelope(r:Reducer):
    return cylinder(r.od,r.length)


def assign_parts(only:str='all'):
    parts={}
    for r in [RA,DEC]:
        if only!='all' and only!=r.key:continue
        parts[f'{r.key}_rear_mount_housing']=housing(r)
        parts[f'{r.key}_output_bolt_adapter']=output_adapter(r)
        parts[f'{r.key}_nema17_slider']=nema_motor_carrier(r)
        parts[f'{r.key}_input_bearing_bridge_OPTIONAL']=bearing_bridge(r)
        for d in (0.6,1.2,1.8):
            parts[f'{r.key}_fit_gauge_diam_plus_{str(d).replace(".","p")}']=output_collar_coupon(r,d)
        for d in (0.10,0.20,0.30):
            parts[f'{r.key}_bearing_gauge_bore_plus_{str(d).replace(".","p")}']=bearing_coupon(r,d)
    return parts


def export(out:Path,only='all',include_gauges=True):
    out.mkdir(parents=True,exist_ok=True)
    parts=assign_parts(only)
    if not include_gauges:parts={k:v for k,v in parts.items() if 'gauge' not in k}
    manifest={'release':'V0.3',
       'status':'bench_fit_only_NOT_load_rated_NOT_complete_mount',
       'ra_supplier':asdict(RA),'dec_supplier':asdict(DEC),
       'rear_flange_orientation_deg':'30 provisional: physically verify 2UH thread-vs-clear holes before printed fit',
       'gearbox_mounting_bolts':'6 x M4 on PCD71 RA / PCD65 DEC into metal factory threads; rear cap Ø4.5 clearance',
       'output_adapters':'RA 6 x M5 on PCD27 ; DEC 6 x M4 on PCD23',
       'nema17':'31x31 M3 square holes; x +-5 mm via slots; motor center x85 mm nominal',
       'main_axis_bearing':'integrated cross-roller inside OEM 2UH; NEVER use 608/626 as primary bending support',
       'input_guide_bearings':'608 (8x22x7) RA and 626 (6x19x6) DEC OPTIONAL & not yet compatible-verified',
       'open_items':['verify actual manufacturer drawing revision', 'input wave-generator hub/shaft design',
          'metal reinforcement and polymer creep/load tests','belt stock length and true pulley plane',
          'real CAD yoke RA-DEC load path','saddle bolt holes, polar wedge and tripod interface'],
       'items':[]}
    assembly=cq.Assembly(name='OpenEQMount_V03_BENCH_INTERFACE_LAYOUT')
    for name,shape in parts.items():
        if len(shape.solids().vals())!=1:
            raise ValueError(f'{name} must be one fused, independent solid, got {len(shape.solids().vals())}')
        step=out/f'{name}.step'; stl=out/f'{name}.stl'
        cq.exporters.export(shape,str(step),exportType='STEP')
        cq.exporters.export(shape,str(stl),exportType='STL',tolerance=0.15,angularTolerance=0.22)
        bb=shape.val().BoundingBox()
        manifest['items'].append({'name':name,'bbox_mm':[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],
                    'volume_cc':round(shape.val().Volume()/1000,2),
                    'prototype_only':True})
        if 'gauge' not in name:
            # Keep RA and DEC in separate groups in a layout, not a physically
            # collocated zero-offset assembly that would misleadingly intersect.
            rkey='ra' if name.startswith('ra') else 'dec'
            translation=(0,0,0) if rkey=='ra' else (0,135,0)
            clr={'rear_mount_housing':(0.17,0.51,0.62),
                 'output_bolt_adapter':(0.91,0.64,0.29),
                 'nema17_slider':(0.22,0.28,0.34),
                 'input_bearing_bridge_OPTIONAL':(0.43,0.65,0.77)}
            typ=name.replace(rkey+'_','')
            assembly.add(shape,name=name,loc=cq.Location(cq.Vector(*translation)),color=cq.Color(*clr[typ]))
    # CAD assembly is for interface layout, gearbox envelopes separately as guide.
    for r in (RA,DEC):
        if only!='all' and only!=r.key:continue
        center=(0,0,0) if r.key=='ra' else (0,135,0)
        assembly.add(reducer_envelope(r),name=r.key+'_OEM_reducer_SPACE_ENVELOPE',
                     loc=cq.Location(cq.Vector(*center)),color=cq.Color(0.72,0.73,0.74))
    assembly.save(str(out/'OpenEQMount_V03_interface_layout.step'),exportType='STEP')
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Exported {len(parts)} printable interface / test parts into {out}')
    return parts


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=Path(__file__).parent/'v03_generated')
    ap.add_argument('--only',choices=['all','ra','dec'],default='all')
    ap.add_argument('--no-gauges',action='store_true')
    args=ap.parse_args()
    export(args.out,args.only,not args.no_gauges)

if __name__=='__main__':main()
