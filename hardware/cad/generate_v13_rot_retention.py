#!/usr/bin/env python3
"""V1.3 OPTICAL ROT bearing axial path and camera interface design study.

Digital Gate A geometry ONLY, NOT a drawing for machining, camera mounting,
structural certification, or powered motion. All dimensions millimetres.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import cadquery as cq
import generate_v10_rotator_bench as v10
import generate_v11_three_axis_mated_concept as v11
import generate_v12_rot_cartridge as v12

VERSION='V1.3_ROT_AXIAL_RETENTION_CAMERA_DATUM_GATE_A'
INNER_RACE_REFERENCE=(40.,45.) # 45mm contact OD is HYPOTHETICAL, OEM race faces unknown
BEARING_INTERVALS=((7.,14.),(37.,44.))
AXIAL_SPACER_INTERVAL=(14.,37.)
SPINDLE_SHOULDER_INTERVAL=(3.,7.)
LOCKNUT_REFERENCE_INTERVAL=(44.,50.)
CAMERA_PLATE_INTERVAL=(67.,75.)
CAMERA_CLAMP_BOLT_DISTANCE=60.
CABLE_ENVELOPE_LENGTH_MM=220. # not qualified cable or routing


def stepped_metal_spindle():
    """Continuous metal shaft with INTEGRAL inner-ring lower shoulder.

    z7..44 OD40 bearing fit, z44..53 OD38 thread *envelope* (NOT a thread),
    z53..64 OD33.5 flange pilot. Pilot/threads cannot be manufactured from
    this CAD without real tolerances and thread details.
    """
    a=v10.ring(40,32,49,-5)           # -5 .. 44
    a=a.union(v10.ring(45,32,4,3))    # integral stop z3..7
    a=a.union(v10.ring(38,32,9,44))   # symbolic nut/thread engagement
    a=a.union(v10.ring(33.5,32,11,53))
    assert len(a.solids().vals())==1
    return a


def inner_ring_distance_sleeve():
    # Example OD=45, ID=40.2: geometry hypothesis ONLY; 6808 inner race face
    # and shielding may NOT permit that contact OD. No preload defined.
    return v10.ring(45,40.2,23,14)


def symbolic_positive_locknut():
    # Overlaps nominal OD38 thread envelope by 0.15mm radially, representing
    # an UNMODELLED threaded fastening, not a specified thread or preload.
    return v10.ring(47,37.7,6,44)


def secondary_lock_tab_reference():
    # A separate all-metal retention feature must be dimensioned in a later
    # design; this flat washer is NOT mechanically keyed, staked or captured.
    return v10.ring(50,38,1.5,50)


def vendor_camera_clamp_mating_plate():
    """Metal adapter from nominal 6x M4 PCD88 rotor flange to *candidate*
    2xM6 clearance clamp bolt locations, not a camera clamp or Arca profile.
    """
    a=v10.ring(108,40,8,67)
    a=v10.bolt(a,88,6,4.5,z=66.5,depth=9)
    for x in (-CAMERA_CLAMP_BOLT_DISTANCE/2,CAMERA_CLAMP_BOLT_DISTANCE/2):
        a=a.cut(cq.Workplane('XY').center(x,0).circle(3.3).extrude(10).translate((0,0,66)))
    return a


def unconnected_camera_cage_eye_envelope():
    """NOT PART OF LOAD PATH; must attach to camera or lens collar independently.
    Rejected as a finished safety component until camera selection and drop tests.
    """
    p=cq.Workplane('XY').center(0,82).box(25,25,6,centered=(True,True,False)).translate((0,0,76))
    return p.cut(cq.Workplane('XY').center(0,84).circle(3.25).extrude(8).translate((0,0,75)))


def nonload_gauges():
    # Flat FDM coupons, no primary strength or load retention whatsoever.
    r=v10.ring(76,40.2,3)
    for x in (-30,30):
        r=r.cut(cq.Workplane('XY').center(x,0).circle(3.3).extrude(5).translate((0,0,-1)))
    shaft=v10.ring(78,38.2,3)
    return {'v13_NONLOAD_CAMERA_TWO_M6_LOCATOR_GAUGE_PRINT_FLAT':r,
            'v13_NONLOAD_SHAFT_NUT_CLEARANCE_GAUGE_PRINT_FLAT':shaft}


def tether_clearance_reference():
    """Pin-centre separation in local (X,Y,Z); NOT cable flex/obstacle proof."""
    fixed=(-81.,0.,30.)
    d={}
    for angle in range(-150,151,30):
        # rotating anchor centre after 90deg phase offset; from V12 proposal
        t=math.radians(angle+90)
        moving=(69*math.cos(t),69*math.sin(t),71.)
        dist=math.dist(fixed,moving)
        d[str(angle)]=round(dist,2)
    return d


def metal_parts():
    return {
       'v13_METAL_INTEGRAL_SHOULDER_STEPPED_SPINDLE_HYPOTHESIS':stepped_metal_spindle(),
       'v13_METAL_INNER_RACE_DISTANCE_SLEEVE_HYPOTHESIS':inner_ring_distance_sleeve(),
       'v13_METAL_LOCKNUT_THREAD_ENVELOPE_NO_THREAD':symbolic_positive_locknut(),
       'v13_METAL_SECONDARY_WASHER_UNKEYED_NOT_A_LOCK':secondary_lock_tab_reference(),
       'v13_METAL_CAMERA_VENDOR_CLAMP_INTERFACE_TWO_M6_CANDIDATE':vendor_camera_clamp_mating_plate(),
       'v13_METAL_CAMERA_CAGE_EYE_FLOATING_NOT_CONNECTED':unconnected_camera_cage_eye_envelope(),
    }


def assembly_records(lat=35.,dec_angle=25.,rot_angle=0.):
    originals=v12.part_records(lat,dec_angle,rot_angle)
    deprecated=('v10_METAL_HOLLOW_ROT_SPINDLE_PROPOSAL',
                'v10_METAL_INDEPENDENT_CAPTURE_COLLAR_PROPOSAL',
                'v11_CAMERA_MATING_FLANGE_METAL_BLANK_NO_LENS_CLAMP',
                'v12_METAL_INNER_RING_SPACER_NARROW_REFERENCE')
    records=[r for r in originals if r['name'] not in deprecated]
    for name,shape in metal_parts().items():
        if len(shape.solids().vals())!=1:raise RuntimeError('broken part '+name)
        placed=v11.rotor_local_to_mount(shape,lat,dec_angle,rot_angle,rotating=True)
        # All six references follow the ROT for display; floating eye is deliberately
        # not mechanically attached, its display transform is not an approved mate.
        color=cq.Color(.3,.72,.57) if 'CAMERA_' in name else cq.Color(.91,.65,.25)
        records.append(dict(name=name,shape=placed,role='unqualified_metal_reference',color=color))
    assert len({r['name'] for r in records})==len(records)
    return records


def validate_axial_stack():
    assert BEARING_INTERVALS == ((7.,14.),(37.,44.))
    assert SPINDLE_SHOULDER_INTERVAL[1]==BEARING_INTERVALS[0][0]
    assert AXIAL_SPACER_INTERVAL==(BEARING_INTERVALS[0][1],BEARING_INTERVALS[1][0])
    assert LOCKNUT_REFERENCE_INTERVAL[0]==BEARING_INTERVALS[1][1]
    assert CAMERA_PLATE_INTERVAL[0]==v10.output_plate().val().BoundingBox().zmax
    assert stepped_metal_spindle().val().BoundingBox().zmax==64
    return True


def export(out:Path,latitude=35.,dec_preview=25.,rot_preview=0.):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if not (25<=latitude<=45 and -65<=dec_preview<=65 and -150<=rot_preview<=150):
        raise ValueError('out of conceptual RA/DEC/ROT preview ranges')
    validate_axial_stack()
    rec=assembly_records(latitude,dec_preview,rot_preview)
    name='OpenEQMount_V13_THREE_AXIS_RETENTION_DATUM_CONCEPT_UNQUALIFIED.step'
    whole=cq.Assembly(name='OpenEQMount_V13_GATE_A_NO_POWER_NO_CAMERA')
    for p in rec:whole.add(p['shape'],name=p['name'],color=p['color'])
    whole.save(str(out/name),exportType='STEP')
    for key,shape in metal_parts().items():
        cq.exporters.export(shape,str(out/(key+'.step')),exportType='STEP')
    gauges=[]
    for key,shape in nonload_gauges().items():
        bb=shape.val().BoundingBox()
        if len(shape.solids().vals())!=1 or abs(bb.zmin)>1e-5 or max(bb.xlen,bb.ylen)>220:
            raise RuntimeError('DfAM nonload geometry failure: '+key)
        cq.exporters.export(shape,str(out/(key+'.step')),exportType='STEP')
        cq.exporters.export(shape,str(out/(key+'.stl')),exportType='STL',tolerance=.10,angularTolerance=.18)
        gauges.append(dict(name=key,role='nonload_dimensional_check_only',material='PETG coupon',load_path='none',
            print_orientation='XY flat Z=0',layer_direction='+Z',overhang_strategy='through-holes; slicer Gate B required',
            metal_joint='NO printed safety or load joint',field_load_approved=False,
            slicer_gate_B='pending',physical_gate_C='pending',bbox_mm=[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)]))
    separations=tether_clearance_reference()
    manifest={
      'release':VERSION,'assembled_step':name,'parts_in_assembly':len(rec),
      'metal_reference_exports':list(metal_parts()),'nonload_printed_parts':gauges,
      'bearing_candidate':'2x6808-2RS 40x52x7; 30mm nominal spacing; NOT qualified for overturning moment',
      'bearing_axial_stack_geometry_consistent':True,'bearing_actual_shoulder_race_face_confirmed':False,
      'bearing_inner_ring_spacer_face_mm_hypothesis':[40.2,45],
      'thread_model_is_functional':False,'real_locknut_specified':False,'positive_locking_qualified':False,
      'bearing_preload_defined':False,'bearing_fit_tolerance_defined':False,
      'camera_clamp_vendor_confirmed':False,'camera_clamp_attached':False,
      'camera_clamp_candidate_M6_hole_spacing_mm':CAMERA_CLAMP_BOLT_DISTANCE,
      'camera_lens_collar_selected':False,'camera_mating_interface_qualified':False,
      'fall_arrest_complete':False,'fall_arrest_cable_in_CAD':False,
      'fall_arrest_anchor_strength_qualified':False,'independent_camera_eye_attached':False,
      'tether_reference_centre_spacing_mm_by_rot_angle':separations,
      'tether_unapproved_slack_length_mm':CABLE_ENVELOPE_LENGTH_MM,
      'tether_path_cleared_for_collision':False,
      'stop_fasteners_qualified':False,'stop_strength_qualified':False,
      'full_RA_DEC_ROT_collision_proved':False,
      'safe_to_energize':False,'payload_approved':False,
      'Gate_B':'pending','Gate_C':'pending',
      'reference_only':True,
      'critical_findings':[
        'Shaft shoulder z3..7, inner bearings z7..14 and z37..44, spacer z14..37, symbolic locknut z44..50 form a NOMINAL axial stack; shaft tolerance/preload nut threads and inner-race contacts unknown.',
        'V1.2 outer-ring 1mm contact lips remain unqualified: maker race and seal clearance drawings required.',
        'Candidate clamp plate has nominal 2xM6 60mm spacing with 6xM4 PCD88. No measured camera clamp; ARCA 38mm width is not an interchangeable vendor mount hole standard.',
        'Unconnected camera-side eye is a FLOATING shape; a fall-arrest cable needs a separately fastened camera cage/lens collar anchor and measured cable sweep. No cable is supplied.',
        'Load, torque, axial shaft backlash, witness marks, full motor-overrun impact, power-loss, and 3-axis collision/flexibility tests are NOT complete.',
      ],
    }
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).parent/'v13_generated')
    ap.add_argument('--latitude',type=float,default=35.)
    ap.add_argument('--dec-preview',type=float,default=25.)
    ap.add_argument('--rot-preview',type=float,default=0.)
    args=ap.parse_args();m=export(args.out,args.latitude,args.dec_preview,args.rot_preview)
    print('V1.3 generated',m['parts_in_assembly'],'metal/concept entities; Gate A only')
