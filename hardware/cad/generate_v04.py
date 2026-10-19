#!/usr/bin/env python3
"""OpenEQMount V0.4 orthogonal RA/DEC *bench-fit* frame, not payload approved.

Coordinate system: RA output surface at Z=0, RA axis +Z; DEC rear face
at X=117, DEC axis +X, DEC centre=(Y=0, Z=112). Dimension unit: mm.

Metal plates/rails/angles are a DESIGN PROPOSAL, NOT verified mechanical
fabrication drawings. All OEM fastener clocking and torque paths must be
confirmed from physical parts and official dimensioned drawings. All printed
parts are NON-STRUCTURAL fit jigs, service guards, and cable-safe covers.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import cadquery as cq

V04_STATUS = 'prototype_unqualified_Gate_A_only'
RA_OUTPUT_PCD=27.0
DEC_REAR_PCD=65.0
DEC_CENTER_Z=112.0
SIDE_THICKNESS=5.0
PRINT_CHEEK_THICKNESS=8.0
MAX_BED=220.0

# A side profile drawn in XY *as printed*: profile-Y maps to global +Z.
# This makes the dominant in-plane stresses follow the printable XY toolpaths.
PROFILE_OUTER=[(-55,0),(112,0),(112,145),(94,145),(94,98),(76,76),(42,48),(-55,18)]
PROFILE_RELIEF=[(-10,23),(65,23),(81,56)]
SIDE_FASTENERS=[(-25,10),(35,10),(102,55),(102,117)]
COVER_SERVICE_HOLES=[(-45,10),(102,138)]


def points_on_pcd(pcd, n, clock=0.0):
    return [(pcd/2*math.cos(math.radians(clock + i*360/n)),
             pcd/2*math.sin(math.radians(clock + i*360/n))) for i in range(n)]


def drill(shape, centers, diameter, zlo, depth):
    tool=(cq.Workplane('XY').pushPoints(centers).circle(diameter/2)
          .extrude(depth).translate((0,0,zlo)))
    return shape.cut(tool)


def side_shape(thick, printed=False):
    shape=cq.Workplane('XY').polyline(PROFILE_OUTER).close().extrude(thick)
    relief=(cq.Workplane('XY').polyline(PROFILE_RELIEF).close().extrude(thick+2)
            .translate((0,0,-1)))
    shape=shape.cut(relief)
    # Metal connections use M5 normal to the side sheet. Printed cover gets
    # Ø11 head/nut clearance: never compress polymer in these structural joints.
    shape=drill(shape,SIDE_FASTENERS,11.0 if printed else 5.6,-1,thick+2)
    shape=drill(shape,COVER_SERVICE_HOLES,3.6 if printed else 3.3,-1,thick+2)
    if len(shape.solids().vals())!=1:raise ValueError('side shape disconnected')
    return shape


def ra_drill_template():
    template=cq.Workplane('XY').rect(142,142).extrude(3.5)
    template=drill(template,[(0,0)],12.0,-1,6)
    # Supplier RA output flange: clock provisional until drawing and metal part inspected.
    template=drill(template,points_on_pcd(RA_OUTPUT_PCD,6,90),5.5,-1,6)
    template=drill(template,[(x,y) for x in (-43,45) for y in (-45,45)],5.6,-1,6)
    # Corner gauge windows permit visual inspection of the alignment.
    return template


def dec_drill_template():
    template=cq.Workplane('XY').rect(150,150).extrude(3.5)
    template=drill(template,[(0,0)],54.0,-1,6)
    template=drill(template,points_on_pcd(DEC_REAR_PCD,6,30),4.5,-1,6)
    template=drill(template,[(y,z) for y in (-45,45) for z in (-47,15)],5.6,-1,6)
    return template


def clearance_coupons():
    block=cq.Workplane('XY').box(92,25,6,centered=(True,True,False))
    # M4 and M5 are cut as calibration samples, not certified slip fits.
    for x,dia in zip((-32,-12,12,32),(4.4,4.6,5.4,5.6)):
        block=drill(block,[(x,0)],dia,-1,8)
    return block


def ra_aluminum_plate():
    plate=cq.Workplane('XY').box(150,150,5,centered=(True,True,False))
    plate=drill(plate,[(0,0)],12.,-1,7)
    plate=drill(plate,points_on_pcd(RA_OUTPUT_PCD,6,90),5.5,-1,7)
    # Side rail anchorage: outboard of Ø79 RA reducer body and Ø100.5 V0.3 shell.
    plate=drill(plate,[(x,y) for x in (-43,45) for y in (-45,45)],5.6,-1,7)
    return plate


def dec_aluminum_plate():
    # Defined in assembly global coordinates. Rear of DEC reducer x=117 mm.
    plate=cq.Workplane('XY').box(5,150,150).translate((114.5,0,DEC_CENTER_Z))
    bore=cq.Workplane('YZ').center(0,DEC_CENTER_Z).circle(27).extrude(7).translate((111,0,0))
    plate=plate.cut(bore)
    # This hole clock is provisional; actual DEC rear thread/clearance phase must be measured.
    for y,z in points_on_pcd(DEC_REAR_PCD,6,30):
        c=(cq.Workplane('YZ').center(y,DEC_CENTER_Z+z).circle(2.25).extrude(7)
           .translate((111,0,0)))
        plate=plate.cut(c)
    for y in (-45,45):
        for z in (65,127):
            c=(cq.Workplane('YZ').center(y,z).circle(2.8).extrude(7).translate((111,0,0)))
            plate=plate.cut(c)
    return plate


def in_global_side(shape, positive, is_cover=False):
    # printed XY -> assembly XZ; printed thickness Z -> global Y (negative).
    # Positive hardware rail Y=[56,61]; its cover is outboard [61,69].
    # Negative hardware rail Y=[-61,-56]; its cover is outboard [-69,-61].
    if is_cover:
        y=69 if positive else -61
    else:
        y=61 if positive else -56
    return shape.rotate((0,0,0),(1,0,0),90).translate((0,y,10))


def ra_angle(positive):
    # A proposed 105 mm long, 4 mm thick aluminum 90° cleat. Real bend radii,
    # section tolerances and fastening wrench access are still to be engineered.
    side=1 if positive else -1
    foot=cq.Workplane('XY').box(105,18,4).translate((2.5,side*45,7))
    stand=cq.Workplane('XY').box(105,4,25).translate((2.5,side*52,17.5))
    a=foot.union(stand)
    # vertical M5 screws to RA plate
    for x in (-43,45):
        a=a.cut(cq.Workplane('XY').center(x,side*45).circle(2.8).extrude(10).translate((0,0,3)))
    # horizontal M5 screws to the *metal* side rail (polymer cover has head windows)
    for x in (-25,35):
        hole=cq.Workplane('XZ').center(x,20).circle(2.8).extrude(150,both=True)
        a=a.cut(hole)
    return a


def dec_angle(positive):
    side=1 if positive else -1
    # L in XY extruded in Z, x=112 is contact plane to DEC plate; metal side
    # rail is Y≈56..61 and x≈102 at this part of the load path.
    face=cq.Workplane('XY').box(5,14,122).translate((109.5,side*47,101))
    leg=cq.Workplane('XY').box(25,4,122).translate((99.5,side*52,101))
    a=face.union(leg)
    for z in (65,127):
        hole=(cq.Workplane('YZ').center(side*45,z).circle(2.8).extrude(12)
              .translate((104,0,0)))
        a=a.cut(hole)
        tie=cq.Workplane('XZ').center(102,z).circle(2.8).extrude(150,both=True)
        a=a.cut(tie)
    return a


def printable_parts():
    return {'v04_cheek_left_PRINT_FLAT':side_shape(PRINT_CHEEK_THICKNESS,True),
            'v04_cheek_right_PRINT_FLAT':side_shape(PRINT_CHEEK_THICKNESS,True),
            'v04_ra_bolt_pattern_GAUGE':ra_drill_template(),
            'v04_dec_bolt_pattern_GAUGE':dec_drill_template(),
            'v04_fastener_fit_GAUGE':clearance_coupons()}


def metal_parts():
    return {'v04_ra_output_plate_METAL':ra_aluminum_plate(),
            'v04_dec_rear_plate_METAL':dec_aluminum_plate(),
            'v04_left_side_web_METAL':in_global_side(side_shape(SIDE_THICKNESS,False),False),
            'v04_right_side_web_METAL':in_global_side(side_shape(SIDE_THICKNESS,False),True),
            'v04_left_ra_angle_METAL':ra_angle(False),
            'v04_right_ra_angle_METAL':ra_angle(True),
            'v04_left_dec_angle_METAL':dec_angle(False),
            'v04_right_dec_angle_METAL':dec_angle(True)}


def dfam_record(name,shape):
    bb=shape.val().BoundingBox()
    role='removable_nonstructural_alignment_cover' if 'cheek' in name else 'nonstructural_drill_or_fit_gauge'
    return dict(name=name, material='PETG trial only (nonstructural)', status='prototype_unqualified',
      role=role, print_orientation='bed oriented XY profile, bottom face Z=0',
      layer_direction='+Z perpendicular to main planar profile',
      load_path='no structural load permitted; metal-to-metal structural fasteners only',
      overhang_strategy='flat on bed, no planned supports; slicer confirmation required',
      metal_joint='M5 joint heads pass through Ø11 windows; printed cheek held only by service M3',
      min_wall_mm='not certified; measure slicer perimeters and critical ligaments',
      slicer_gate_B='pending', physical_gate_C='pending',
      bbox_mm=[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],
      volume_cc=round(shape.val().Volume()/1000,2))


def export(out:Path):
    out.mkdir(parents=True,exist_ok=True)
    prints=printable_parts()
    metals=metal_parts()
    manifest=dict(release='V0.4',status=V04_STATUS,
      target='3–5 kg payload and ≤500 mm focal length only AFTER field qualification',
      oem_holes='nominal interface and angular clocking not physically verified',
      mechanism='metal RA plate -> metal angle cleats -> metal side webs -> metal DEC cleats -> metal DEC rear plate',
      printed_parts=[],metal_parts=[],open_items=[
        'OEM CSF input/rear thread angular clock & counterbore access',
        'DEC rear bearing/output torque path, fastener embedment, and central 54mm aperture',
        'aluminum grade, real angle section, bend radii & joining process',
        'bolt head/wrench clearance, torque and vibration locking',
        'verified metal fail-safe strap, physical pull test and field safety interlocks',
        'slicer inspection and print coupon metrology',
        'gravity/accelerated force calculations with actual camera and RA polar orientation'])
    # print STLs at Z=0, regardless of assembly view rotation
    for name,part in prints.items():
        bb=part.val().BoundingBox()
        if bb.zmin < -1e-5:raise ValueError('Print below Z=0 '+name)
        if max(bb.xlen,bb.ylen)>MAX_BED:raise ValueError('Does not fit build plate '+name)
        cq.exporters.export(part,str(out/f'{name}.step'),exportType='STEP')
        cq.exporters.export(part,str(out/f'{name}.stl'),exportType='STL',tolerance=.12,angularTolerance=.15)
        manifest['printed_parts'].append(dfam_record(name,part))
    for name,part in metals.items():
        cq.exporters.export(part,str(out/f'{name}.step'),exportType='STEP')
        bb=part.val().BoundingBox()
        manifest['metal_parts'].append(dict(name=name,source='fabricated metal — not 3D printed',
          material='6061-T6 aluminum proposed; engineer must approve',
          bbox_mm=[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],
          volume_cc=round(part.val().Volume()/1000,2)))
    assembly=cq.Assembly(name='OpenEQMount_V04_BENCH_LAYOUT_NOT_FOR_PAYLOAD')
    for name,part in metals.items():
        assembly.add(part,name=name,color=cq.Color(.70,.72,.74))
    for name,part in prints.items():
        if 'cheek_left' in name:body=in_global_side(part,False,True)
        elif 'cheek_right' in name:body=in_global_side(part,True,True)
        else:continue  # drill templates printed separately, not permanent components
        assembly.add(body,name=name,color=cq.Color(.13,.52,.69))
    assembly.save(str(out/'OpenEQMount_V04_BENCH_assembly.step'),exportType='STEP')
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=Path(__file__).parent/'v04_generated')
    args=p.parse_args()
    mf=export(args.out)
    print(f"V0.4 Gate A geometry generated: {len(mf['printed_parts'])} printable, {len(mf['metal_parts'])} metal parts; NOT PAYLOAD RATED")

if __name__=='__main__':main()
