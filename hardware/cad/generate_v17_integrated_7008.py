#!/usr/bin/env python3
"""V1.7 three-axis geometric integration of *candidate* NSK 7008AWDB cartridge.

This is a collision/layout reference, NOT an actionable machining or load design.
V1.4's 6808 rotor is REMOVED rather than overlapped. Camera coupling and
payload fall protection remain OPEN; never attach equipment or energize.
"""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
import cadquery as cq
import generate_v11_three_axis_mated_concept as v11
import generate_v14_load_fixture as v14
import generate_v16_db7008_cartridge as v16

BRIDGE_PCD=110.0
CARTRIDGE_PCD=80.0
PLATE_OD=136.0
PLATE_BORE=64.0
PLATE_HEIGHT=8.0
CARTRIDGE_Z_ABOVE_BRIDGE=13.0
MOUNT_NAME='OpenEQMount_V17_THREE_AXIS_7008AWDB_INTERFACE_STUDY_UNQUALIFIED.step'
INTERFACE_NAME='OpenEQMount_V17_DEC_ROT_7008_AWDB_INTERFACE_SUBASSEMBLY_UNQUALIFIED.step'
SKIP_OLD=('v10_','v11_REVISED_METAL_NEMA17','v11_MOTOR_STANDOFF_',
          'v12_','v13_','v14_METAL_','v14_REFERENCE_')
COLOR_BRIDGE=cq.Color(.35,.71,.79)
COLOR_ADAPTER=cq.Color(.32,.65,.48)
COLOR_ROTATE=cq.Color(.79,.56,.37)


def drilled_pcd(part: cq.Workplane, pcd: float, radius: float, hole_d: float, bottom: float, depth: float):
    for n in range(6):
        theta=math.pi*n/3
        x,y=pcd/2*math.cos(theta),pcd/2*math.sin(theta)
        tool=cq.Workplane('XY').center(x,y).circle(hole_d/2).extrude(depth).translate((0,0,bottom))
        part=part.cut(tool)
    return part


def adapter_local():
    # The larger PCD is V1.1 *proposed* bridge; smaller is V1.6 *proposed*
    # cartridge fastener pattern. These are NOT manufacturer bolt specifications.
    p=v16.ring(PLATE_OD,PLATE_BORE,PLATE_HEIGHT)
    p=drilled_pcd(p,BRIDGE_PCD,0,5.5,-1,PLATE_HEIGHT+2)
    p=drilled_pcd(p,CARTRIDGE_PCD,0,4.5,-1,PLATE_HEIGHT+2)
    if len(p.solids().vals())!=1:raise RuntimeError('adapter not one contiguous body')
    return p


def minimum_radial_ligament_mm():
    # Conservatively evaluate both inner and outer radial ligaments under the
    # candidate 4.5/5.5mm nominal clearance holes; NOT bolt bearing strength.
    holes=[(BRIDGE_PCD/2,5.5/2),(CARTRIDGE_PCD/2,4.5/2)]
    return min(min(r-hole-PLATE_BORE/2,PLATE_OD/2-r-hole) for r,hole in holes)


def print_flat_gauge():
    # Nonstructural PETG bore/PCD transfer gauge, NEVER trapped in a metal joint.
    return adapter_local().intersect(cq.Workplane('XY').box(PLATE_OD+8,PLATE_OD+8,3,centered=(True,True,False)))


def rotating_role(name:str)->bool:
    return any(n in name for n in ('SPINDLE_', 'LOCKNUT_', 'WASHER_', 'CAMERA_FIXTURE_'))


def base_parts(lat=35.,dec=25.):
    full=v14.assembly_records(lat,dec,0.)
    # The V1.1 bridge stays; ALL original 6808 rotor, its housings, old stops,
    # pseudo-nut, and camera fixtures are removed from this view.
    picked=[p for p in full if not p['name'].startswith(SKIP_OLD)]
    assert len(picked)==42,(len(picked),[p['name'] for p in picked])
    return picked


def integration_parts(lat=35.,dec=25.,rot=0.):
    if not (25 <= lat <=45 and -65<=dec<=65 and -150<=rot<=150):
        raise ValueError('angle outside gated conceptual viewing ranges')
    out=[]
    a=adapter_local()
    out.append(dict(name='v17_METAL_PCD110_TO_PCD80_BRIDGE_ADAPTER_UNQUALIFIED',
                    shape=v11.rotor_local_to_mount(a,lat,dec),role='fixed_metal_adapter_reference',color=COLOR_ADAPTER))
    for row in v16.cartridge_parts():
        n='v17_'+row['name']
        s=row['shape'].translate((0,0,CARTRIDGE_Z_ABOVE_BRIDGE))
        moving=rotating_role(row['name'])
        out.append(dict(name=n,
            shape=v11.rotor_local_to_mount(s,lat,dec,rot,rotating=moving),
            role=('rotating_metal_UNQUALIFIED' if moving else 'fixed_reference_metal_UNQUALIFIED'),
            color=COLOR_ROTATE if moving else v16.ROLE_COLOR[row['role']]))
    return out


def records(lat=35.,dec=25.,rot=0.):
    rec=base_parts(lat,dec)+integration_parts(lat,dec,rot)
    assert len({p['name'] for p in rec})==len(rec)
    if not all(len(p['shape'].solids().vals())==1 for p in rec):raise ValueError('non-single-body part')
    return rec


def spatial_checks()->dict:
    p=adapter_local()
    zmin=p.val().BoundingBox().zmin
    # Housing begins z=13 and removable lower cap bottom begins z=8, exactly
    # flush against the adapter top. These are design coordinates, not fit proof.
    bearing_intervals=[(CARTRIDGE_Z_ABOVE_BRIDGE, CARTRIDGE_Z_ABOVE_BRIDGE+15),
                       (CARTRIDGE_Z_ABOVE_BRIDGE+15,CARTRIDGE_Z_ABOVE_BRIDGE+30)]
    lower_cap_z=(CARTRIDGE_Z_ABOVE_BRIDGE-5,CARTRIDGE_Z_ABOVE_BRIDGE)
    housing_z=(CARTRIDGE_Z_ABOVE_BRIDGE,CARTRIDGE_Z_ABOVE_BRIDGE+30)
    assert lower_cap_z[0]==PLATE_HEIGHT
    assert len(v16.cartridge_parts())==9
    assert minimum_radial_ligament_mm()>=5,minimum_radial_ligament_mm()
    assert v16.BEARING['matched_pair_width_mm']==30
    assert v16.BEARING['manufacturer_a0_load_centres_mm']==46.2
    return dict(
      interface_plate_bore_mm=PLATE_BORE,
      pcd_on_V11_bridge_mm=BRIDGE_PCD,
      pcd_on_V16_housing_mm=CARTRIDGE_PCD,
      min_nominal_radial_ligament_mm=round(minimum_radial_ligament_mm(),2),
      bearing_z_nominal_mm=bearing_intervals,
      lower_cap_z_nominal_mm=lower_cap_z,
      nominal_cartridge_housing_z_mm=housing_z,
      manufacturer_a0_load_centre_mm=46.2,
      physical_matched_width_mm=30.,
      fastener_preload_access_verified=False,
      interface_rivet_weld_or_screw_loadpath_verified=False,
      independent_camera_retention_verified=False,
      camera_shaft_connection_verified=False,
    )


def write_assembly(filename: Path, parts:list[dict], name:str):
    assy=cq.Assembly(name=name)
    for p in parts:assy.add(p['shape'],name=p['name'],color=p['color'])
    assy.save(str(filename),exportType='STEP')


def build(out:Path,lat=35.,dec=25.,rot=0.):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    validation=spatial_checks()
    obj=records(lat,dec,rot)
    write_assembly(out/MOUNT_NAME,obj,'V17_3AXIS_NSK7008AWDB_INTEGRATION_LAYOUT_NO_LOAD_NO_POWER')
    sub=integration_parts(lat,dec,rot)
    write_assembly(out/INTERFACE_NAME,sub,'V17_DEC_ROT_7008_INTERFACE_REFERENCE_ONLY')
    standalone=adapter_local()
    cq.exporters.export(standalone,str(out/'v17_METAL_PCD110_TO_PCD80_BRIDGE_ADAPTER_UNQUALIFIED.step'),exportType='STEP')
    coupon=print_flat_gauge()
    gauge='v17_NONLOAD_DUAL_PCD_TRANSFER_CHECK_PETG_PRINT_FLAT'
    cq.exporters.export(coupon,str(out/(gauge+'.step')),exportType='STEP')
    cq.exporters.export(coupon,str(out/(gauge+'.stl')),exportType='STL',tolerance=.09,angularTolerance=.15)
    warnings=[
      'V1.1 DEC PCD23 reducer output is not OEM-verified; bridge attachment remains only a CAD reference.',
      'V1.6 nominal housing PCD80 and V1.1 bridge PCD110 are provisional; fastener grade, service access, length, torque, thread engagement, thread locking, plate stresses and deflections are unverified.',
      'NSK 7008AWDB CN pair is NOT a proven preloaded precision rotor; bearing interference/clearance, shoulders, thread, locknut and heat treatment are pending.',
      'V1.6 camera interface BLANK is geometrically disconnected from the spindle; its ROT rotation is only a viewing transform, not a valid torque/axial load path.',
      'No independent attached metal camera cage tether, catch test, powered stop or motion-sweep clearance is implemented.',
      'Only one conceptual 35/25/0 pose is exported; this is NOT full RA/DEC/ROT collision testing.',
      'Never machine critical components, install camera/lens, or run motors based on this assembly.',
    ]
    manifest=dict(release='V1.7',status='prototype_unqualified',assembled_step=MOUNT_NAME,
      subassembly_step=INTERFACE_NAME,parts_in_assembly=len(obj),parts_in_subassembly=len(sub),
      digital_coordinates_mm=validation,latitude=lat,DEC_angle=dec,ROT_angle=rot,
      previous_6808_parts_removed=True,new_7008AWDB_mated_envelope_count=2,
      old_bearing_housing_present=False,gate_A='digital_only',gate_B='PENDING',gate_C='PENDING',
      safe_to_energize=False,payload_approved=False,fastener_qualified=False,
      OEM_dec_mount_verified=False,OEM_rot_housing_verified=False,camera_lens_collar_selected=False,
      spindle_camera_connection_qualified=False,tether_strongpoint_attached=False,
      preload_qualified=False,whole_mount_collisions_qualified=False,
      nonload_printed_parts=[dict(name=gauge,material='PETG bench gauge ONLY',
        print_orientation='XY flat on Z=0',layer_direction='+Z',
        layer_load='NO structural or field load',minimum_nominal_wall_mm=5,
        overhang_strategy='planar geometry and through holes; slicing still required',
        metal_joint='NONE; gauge MUST NOT be sandwiched between metal faces',
        field_load_approved=False,gate_B='PENDING',gate_C='PENDING')],
      warnings=warnings)
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('V1.7 digital full-mount:',len(obj),'solids; DEC–ROT 7008 subassembly:',len(sub))
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).parent/'v17_generated')
    p.add_argument('--latitude',type=float,default=35.);p.add_argument('--dec-angle',type=float,default=25.);p.add_argument('--rot-angle',type=float,default=0.)
    a=p.parse_args();build(a.out,a.latitude,a.dec_angle,a.rot_angle)
