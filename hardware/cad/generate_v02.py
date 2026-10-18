#!/usr/bin/env python3
"""Generate conceptual V0.2 mechanical solids with cadquery.

All reducer bodies, motors and clamp shapes are envelopes/placeholders.
This is a layout model, NOT CNC-ready, load-validated, or collision-free.
Units: mm. No vendor STEP content or CAD geometry is included.

Usage:
    pip install 'cadquery>=2.5,<3'
    python hardware/cad/generate_v02.py --out hardware/cad/generated
    python hardware/cad/generate_v02.py --latitude 42 --out /tmp/cad42
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import cadquery as cq

from params import MountParams

COLORS = {
    'base_plate': cq.Color(0.20,0.24,0.30),
    'fixed_latitude_wedge': cq.Color(0.45,0.49,0.56),
    'ra_housing': cq.Color(0.13,0.42,0.56),
    'ra_gearbox_envelope': cq.Color(0.76,0.79,0.81),
    'ra_output_flange_placeholder': cq.Color(0.89,0.68,0.25),
    'ra_crosshead': cq.Color(0.16,0.50,0.61),
    'dec_support_bracket': cq.Color(0.21,0.50,0.58),
    'dec_housing': cq.Color(0.12,0.42,0.56),
    'dec_gearbox_envelope': cq.Color(0.76,0.79,0.81),
    'dec_output_flange_placeholder': cq.Color(0.89,0.68,0.25),
    'camera_clamp_adapter_blank': cq.Color(0.22,0.24,0.27),
    'ra_stepper_envelope': cq.Color(0.83,0.42,0.25),
    'dec_stepper_envelope': cq.Color(0.83,0.42,0.25),
}


def cyl_z(diameter: float, height: float, start_z: float = 0.0):
    return cq.Workplane('XY').circle(diameter / 2).extrude(height).translate((0, 0, start_z))


def ring_z(od: float, inner: float, length: float, start_z: float=0):
    return cq.Workplane('XY').circle(od/2).circle(inner/2).extrude(length).translate((0,0,start_z))


def cyl_x(diameter: float, length: float, start_x: float, z: float):
    return cyl_z(diameter, length).rotate((0,0,0),(0,1,0),90).translate((start_x,0,z))


def ring_x(od: float, inner: float, length: float, start_x:float, z:float):
    return ring_z(od,inner,length).rotate((0,0,0),(0,1,0),90).translate((start_x,0,z))


def generate(p: MountParams) -> dict[str, cq.Workplane]:
    p.validate()
    a = math.radians(p.latitude_deg)
    y_lo = p.wedge_origin_y - p.wedge_half_depth
    y_hi = p.wedge_origin_y + p.wedge_half_depth
    top_at_ylo = p.wedge_top_z_center - (y_lo-p.wedge_origin_y)/math.tan(a)
    top_at_yhi = p.wedge_top_z_center - (y_hi-p.wedge_origin_y)/math.tan(a)
    base = cq.Workplane('XY').box(p.base_width,p.base_depth,p.base_thickness,centered=(True,True,False))
    # Generic unthreaded fixture holes. Tripod standard still TBD.
    base = base.faces('>Z').workplane().pushPoints([(-48,-42),(-48,42),(48,-42),(48,42)]).hole(6.6)
    wedge = (cq.Workplane('YZ')
             .polyline([(y_lo,p.base_thickness),(y_hi,p.base_thickness),
                        (y_hi,top_at_yhi),(y_lo,top_at_ylo)])
             .close().extrude(p.wedge_width/2,both=True))
    # Parts below are in an RA-axis-aligned coordinate system with local +Z = north celestial pole.
    local: dict[str,cq.Workplane] = {}
    local['ra_housing'] = ring_z(p.ra_housing_od,p.ra_housing_id,p.ra_housing_length)
    local['ra_gearbox_envelope'] = cyl_z(p.ra_gear_diameter,p.ra_gear_length,3)
    local['ra_output_flange_placeholder'] = cyl_z(51,14,51)
    local['ra_crosshead'] = cq.Workplane('XY').box(132,39,14).translate((-2,0,71))
    # Bracket reaches around reducer, currently shown as a solid block with NO verified fasteners.
    local['dec_support_bracket'] = cq.Workplane('XY').box(46,37,39).translate((-30,0,99))
    center_z = p.dec_axis_z_local
    local['dec_housing'] = ring_x(p.dec_housing_od,p.dec_housing_id,p.dec_housing_length,-65,center_z)
    local['dec_gearbox_envelope'] = cyl_x(p.dec_gear_diameter,p.dec_gear_length,-61,center_z)
    local['dec_output_flange_placeholder'] = cyl_x(50,14,-15,center_z)
    # Blank mounting plate, no specific proprietary Vixen saddle hole spacing assumed.
    # Fully separate commercially rated saddle will bolt onto a later custom adapter.
    saddle = cq.Workplane('YZ').rect(p.saddle_width,p.saddle_length).extrude(10).translate((3,0,center_z))
    saddle = saddle.cut(cq.Workplane('YZ').pushPoints([(-18,-22),(-18,22),(18,-22),(18,22)])
                        .circle(3.3).extrude(20).translate((0,0,center_z)))
    local['camera_clamp_adapter_blank'] = saddle
    # Optional motor envelopes, without a real belt path or motor mounting pattern.
    local['ra_stepper_envelope'] = cq.Workplane('XY').box(42,42,40).translate((76,0,8))
    local['dec_stepper_envelope'] = cq.Workplane('XY').box(40,42,42).translate((-43,0,center_z+69))

    result = {'base_plate':base,'fixed_latitude_wedge':wedge}
    for name, solid in local.items():
        result[name] = (solid.rotate((0,0,0),(1,0,0),p.latitude_deg-90)
                         .translate((0,p.wedge_origin_y,p.wedge_top_z_center)))
    return result


def write_models(parts, out:Path, p:MountParams, export_unsafe_concept_stl:bool=False):
    out.mkdir(parents=True,exist_ok=True)
    assembly = cq.Assembly(name='OpenEQMount_V02_CONCEPT')
    part_catalogue=[]
    # STEP assembly includes each part only ONCE, in model coordinates.
    for name, solid in parts.items():
        assembly.add(solid,name=name,color=COLORS[name])
        cq.exporters.export(solid, str(out/f'{name}.step'), exportType='STEP')
        # Motors and reducer envelopes intentionally not issued as printable STL parts.
        if export_unsafe_concept_stl and name in {'base_plate','fixed_latitude_wedge','ra_housing',
                    'ra_crosshead','dec_support_bracket','dec_housing','camera_clamp_adapter_blank'}:
            cq.exporters.export(solid, str(out/f'{name}.stl'), exportType='STL', tolerance=0.18, angularTolerance=0.2)
        bb=solid.val().BoundingBox()
        part_catalogue.append({'name':name,'approx_world_bbox_mm':
                [round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],
                'type':'nominal_envelope' if 'envelope' in name else 'concept_geometry'})
    assembly.save(str(out/'OpenEQMount_V02_assembly.step'),exportType='STEP')
    (out/'manifest.json').write_text(json.dumps({'status':'concept_only_NOT_manufacturing_ready',
        'latitude_deg':p.latitude_deg,'axis_reduction':'100:1 harmonic x 3:1 belt (belt not modelled)',
        'dfam_status':'legacy_layout_not_DfAM_not_printable',
        'parts':part_catalogue,'critical_note':'Mechanical mating holes, belt drive, hinges, cable paths and fit verification are NOT implemented.'},
        ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Created {len(parts)} solids, STEP assembly, individual STEP/STL: {out}')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--latitude',type=float,default=35)
    parser.add_argument('--out',type=Path,default=Path(__file__).parent/'generated')
    parser.add_argument('--export-unsafe-concept-stl',action='store_true',
        help='Legacy visual meshes ONLY; not DfAM-qualified or safe for manufacture')
    args=parser.parse_args()
    p=MountParams(latitude_deg=args.latitude)
    write_models(generate(p),args.out,p,args.export_unsafe_concept_stl)

if __name__=='__main__':
    main()
