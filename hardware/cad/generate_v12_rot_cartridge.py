#!/usr/bin/env python3
"""OpenEQMount V1.2 serviceable ROT cartridge and limit-interface CAD study.

DIGITAL GATE A ONLY. Neither the nominal bearing stack nor stop / tether lugs
are structurally or dimensionally qualified. All dimensions mm. Camera loading
and motor energization are prohibited until physical safety qualification.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import cadquery as cq
import generate_v10_rotator_bench as v10
import generate_v11_three_axis_mated_concept as v11

VERSION='V1.2_ROT_CARTRIDGE_STOP_CONTACT_GATE_A'
BORE_DIAMETER_REFERENCE=52.2  # NOT ISO fit or machinist tolerance, allowance draft only
BEARING_Z=(7.,37.)
BEARING_WIDTH=7.
OUTER_SPACER_Z=((0.,7.),(14.,37.),(44.,54.))
BEARING_INSTALL_ENTRY_DIAMETER=52.2
FIXED_STOP_ANGLES=(-166.,166.)
SOFT_LIMIT=150.
REFERENCE_CONTACT_ANGLE=160.
ROTOR_STOP_HEIGHT=9.


def split_cartridge_housing():
    """Continuous through bore permits loading both 52 mm bearings axially."""
    s=v10.ring(128,BORE_DIAMETER_REFERENCE,54)
    s=v10.bolt(s,110,6,5.5,z=-1,depth=56)
    return v10.bolt(s,90,4,4.5,z=-1,depth=56,phase=45.)  # cap-fastener CLEARANCE only


def outer_ring_spacers():
    # OD=52, ID=50 *REFERENCE ONLY*: narrow radial contact 1mm needs OEM ring
    # geometry check + manufacturer fit. Not released for machining.
    return {f'v12_METAL_OUTER_RING_SPACER_{i}_UNQUALIFIED':v10.ring(52,50,hi-lo,lo)
            for i,(lo,hi) in enumerate(OUTER_SPACER_Z,1)}


def outer_retaining_cap(z):
    return v10.bolt(v10.ring(108,50,4,z),90,4,4.5,z=z-.5,depth=5,phase=45.)


def inner_ring_spacer_reference():
    # 1mm annular lip! Cannot be assumed manufacturable or bearing-safe.
    # Explicitly marks missing OEM inner ring face geometry.
    return v10.ring(42,40,23,14)


def fixed_stop_block(angle):
    # Monolithic block with intended overlap to stator; actual attachment
    # machining, service screw access and torque not specified.
    s=cq.Workplane('XY').center(68,0).box(24,11,26,centered=(True,True,False)).translate((0,0,49))
    return s.rotate((0,0,0),(0,0,1),angle)


def rotating_stop_dog(angle):
    # Intentional overlap with OUTPUT flange reference, requires true fasteners.
    s=cq.Workplane('XY').center(61,0).box(38,9,9,centered=(True,True,False)).translate((0,0,65))
    return s.rotate((0,0,0),(0,0,1),angle)


def stop_contact_volume(angle):
    dog=rotating_stop_dog(angle)
    return sum(dog.intersect(fixed_stop_block(a)).val().Volume() for a in FIXED_STOP_ANGLES)


def fixed_tether_anchor():
    s=cq.Workplane('XY').center(-74,0).box(34,19,6,centered=(True,True,False)).translate((0,0,27))
    return s.cut(cq.Workplane('XY').center(-81,0).circle(3.5).extrude(8).translate((0,0,26)))


def moving_tether_anchor(angle):
    s=cq.Workplane('XY').center(69,0).box(36,17,6,centered=(True,True,False)).translate((0,0,68))
    s=s.cut(cq.Workplane('XY').center(79,0).circle(3.5).extrude(8).translate((0,0,67)))
    return s.rotate((0,0,0),(0,0,1),angle+90)  # tether lug is intentionally angularly separated from stop dog


def nonload_coupons():
    # Fit-test geometry, flat on bed; PETG parts have NO retention role.
    od=cq.Workplane('XY').circle(74).circle(26.1).extrude(3)
    id_=cq.Workplane('XY').circle(42).circle(20.1).extrude(3)
    return {
        'v12_NONLOAD_6808_HOUSING_BORE_COUPON_PRINT_FLAT':od,
        'v12_NONLOAD_6808_SHAFT_CLEARANCE_COUPON_PRINT_FLAT':id_,
    }


def metal_parts():
    p={
        'v12_METAL_SERVICEABLE_THROUGH_BORE_STATOR_PROPOSAL':split_cartridge_housing(),
        'v12_METAL_LOWER_OUTER_RING_CAP_UNQUALIFIED':outer_retaining_cap(-4),
        'v12_METAL_UPPER_OUTER_RING_CAP_UNQUALIFIED':outer_retaining_cap(54),
        'v12_METAL_INNER_RING_SPACER_NARROW_REFERENCE':inner_ring_spacer_reference(),
        'v12_METAL_FIXED_ROT_STOP_NEGATIVE_PROPOSAL':fixed_stop_block(-166),
        'v12_METAL_FIXED_ROT_STOP_POSITIVE_PROPOSAL':fixed_stop_block(166),
        'v12_METAL_FIXED_TETHER_ANCHOR_NO_CABLE':fixed_tether_anchor(),
        'v12_METAL_MOVING_ROT_STOP_DOG_NO_FASTENERS':rotating_stop_dog(0),
        'v12_METAL_MOVING_TETHER_ANCHOR_NO_CABLE':moving_tether_anchor(0),
    }
    p.update(outer_ring_spacers())
    return p


def part_records(lat,dec_angle,rot_angle):
    original=v11.part_records(lat,dec_angle,rot_angle)
    out=[]
    for item in original:
        n=item['name']
        if 'v10_METAL_STATOR_DUAL_6808_SEATS_PROPOSAL' in n:
            continue
        out.append(item)
    for n,s in metal_parts().items():
        rotating=('MOVING_' in n)
        if rotating:
            placed=v11.rotor_local_to_mount(s,lat,dec_angle,rot_angle,True)
        else:
            placed=v11.rotor_local_to_mount(s,lat,dec_angle,rot_angle,False)
        if len(s.solids().vals())!=1:raise ValueError(f'Invalid CAD BREP: {n}')
        color=cq.Color(.8,.32,.2) if 'STOP' in n else cq.Color(.3,.64,.48) if 'TETHER_' in n else cq.Color(.48,.66,.88)
        out.append(dict(name=n,shape=placed,role='unqualified_metal_interface',color=color))
    if len({p['name'] for p in out})!=len(out):raise ValueError('duplicate assembly names')
    return out


def export(out,latitude=35.,dec_preview=25.,rot_preview=0.):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if not 25<=latitude<=45 or not -65<=dec_preview<=65 or not -150<=rot_preview<=150:raise ValueError('reference envelope exceeded')
    records=part_records(latitude,dec_preview,rot_preview)
    name='OpenEQMount_V12_THREE_AXIS_SERVICEABLE_CARTRIDGE_CONCEPT_UNQUALIFIED.step'
    asm=cq.Assembly(name='OpenEQMount_V12_GATE_A_NO_POWER_NO_CAMERA')
    for p in records:asm.add(p['shape'],name=p['name'],color=p['color'])
    asm.save(str(out/name),exportType='STEP')
    metals=metal_parts()
    for k,v in metals.items():cq.exporters.export(v,str(out/(k+'.step')),exportType='STEP')
    coupons=nonload_coupons();prints=[]
    for n,s in coupons.items():
        bb=s.val().BoundingBox()
        if len(s.solids().vals())!=1 or abs(bb.zmin)>1e-5 or max(bb.xlen,bb.ylen)>220:raise ValueError(n)
        cq.exporters.export(s,str(out/(n+'.stl')),exportType='STL',tolerance=.09,angularTolerance=.16)
        cq.exporters.export(s,str(out/(n+'.step')),exportType='STEP')
        prints.append(dict(name=n,material='PETG coupon only',role='non-load clearance specimen',load_path='none',
            print_orientation='XY flat Z=0',layer_direction='+Z',
            overhang_strategy='planar through opening; slicer Gate B pending',
            metal_joint='no printed structural fasteners',min_wall_mm='inspection needed',
            field_load_approved=False,slicer_gate_B='pending',physical_gate_C='pending',
            bbox_mm=[round(bb.xlen,3),round(bb.ylen,3),round(bb.zlen,3)]))
    contact={str(x):round(stop_contact_volume(x),4) for x in (-150.,0.,150.,-160.,160.)}
    manifest=dict(release=VERSION,assembled_step=name,parts_in_assembly=len(records),
        metal_reference_exports=list(metals),nonload_printed_parts=prints,
        status='unqualified_digitally_checked_concept_not_for_manufacturing',
        bearing_candidate='6808-2RS / 40x52x7 mm',through_bore_nominal_diameter_mm=52.2,
        through_bore_is_manufacturing_tolerance=False,
        outer_ring_retention_path_assembled=False,
        inner_ring_positive_retention_qualified=False,
        bearing_preload_defined=False,approved_bearing_fit=False,
        camera_mating_plate_qualified=False,fall_arrest_complete=False,
        fall_arrest_anchor_strength_qualified=False,stop_strength_qualified=False,
        stop_fasteners_qualified=False,independent_limit_switches_implemented=False,
        safe_to_energize=False,payload_approved=False,
        full_RA_DEC_ROT_collision_proved=False,Gate_B='pending',Gate_C='pending',
        soft_angle_range_deg=[-SOFT_LIMIT,SOFT_LIMIT],
        fixed_stop_pin_centre_deg=[-166,166],
        stop_overlap_mm3_reference=contact,
        stop_contacts_beyond_soft_range=contact['-160.0']>0 and contact['160.0']>0,
        cleared_at_soft_range=contact['-150.0']==0 and contact['150.0']==0 and contact['0.0']==0,
        critical_findings=[
            'V1.0 single-piece blind 52mm counterbore cannot insert bearings through 50mm end openings; V1.2 serviceable bore is a geometry study',
            '6808 40/52mm thin section leaves narrow 42/40mm nominal inner spacer, 50/52mm outer spacer; check manufacturer ring face and installation shoulder diameters',
            'Shaft axial retention thread/circlip/nut, rotating hub fastening and bearing preload NOT designed; no approval',
            'Tether anchors are only holes and pads: cable, routing, fastening and fall-drop proof ABSENT',
            'Stop contact is merely BREP overlap for a narrow angular sweep; bracket machining, strength and clearance all NOT tested',
            'Camera interface is still a blank flange; actual camera lens collar and load path absent'],
        source_dependency=['generate_v11_three_axis_mated_concept.py','generate_v10_rotator_bench.py'])
    if not (manifest['stop_contacts_beyond_soft_range'] and manifest['cleared_at_soft_range']):
        raise RuntimeError('ROT reference end-stop CAD sweep not consistent')
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).parent/'v12_generated')
    p.add_argument('--latitude',type=float,default=35.)
    p.add_argument('--dec-preview',type=float,default=25.)
    p.add_argument('--rot-preview',type=float,default=0.)
    a=p.parse_args();m=export(a.out,a.latitude,a.dec_preview,a.rot_preview)
    print('V1.2 generated',m['parts_in_assembly'],'parts; stop contacts',m['stop_overlap_mm3_reference'])
