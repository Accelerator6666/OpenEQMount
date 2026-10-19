#!/usr/bin/env python3
"""OpenEQMount V0.8 preview: combined positioning of V0.4–V0.7 concepts.

Only an engineering VIEW ASSEMBLY for FreeCAD. No claim of mechanical compatibility,
fit, fastener engagement, collision-free articulation, drive coupling, or load safety.
Measured real parts, selected tripod, and hardware qualification remain necessary.
The GT2 drive cassettes are detached bench models; NOT included as installed parts.
No print STLs are generated, because this project assembly is NOT a printable part.
"""
from __future__ import annotations
import sys, json, argparse
from pathlib import Path
import cadquery as cq
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
import generate_v04 as v04
import generate_v05 as v05
import generate_v06 as v06
import generate_v07 as v07

PREVIEW_STATUS='V0.8 VIEW ASSEMBLY — UNQUALIFIED, NOT MANUFACTURING CAD'

def make_components(latitude=35.):
    if not v05.LAT_MIN <= latitude <= v05.LAT_MAX:
        raise ValueError('latitude outside prototype range')
    records=[]
    def add(name,shape,category,color,notes=''):
        records.append(dict(name=name,shape=shape,category=category,color=color,notes=notes))

    # Fixed and rotating wedge components, with explicit replacement selection.
    for name,part in v05.metals(latitude).items():
        if name in ('v05_azimuth_slew_DECK_METAL','v05_tripod_anchor_BASE_METAL','v05_tilt_ra_INTERFACE_METAL'):
            continue # V0.6 / V0.7 SUPSERSEDE these earlier variants.
        add(name,part,'metal_wedge',cq.Color(.64,.67,.72),'V0.5 kinematic reference')
    add('TRIPOD_FIXED_MAIN_BASE',v05.fixed_triad_base(),'metal_base',cq.Color(.37,.42,.48))
    for name,part in v06.metal_parts(latitude).items():
        if name.endswith('_OPTION'):
            continue # alternative M10 / 3/8 inch interfaces never installed together
        add(name,part,'metal_lock',cq.Color(.38,.56,.67) if 'sector' in name else cq.Color(.84,.51,.22) if 'pin_' in name else cq.Color(.63,.69,.74),
            'Lock/stop are geometry-only references, not load/anti-fall proven')
    for name,part in v07.ra_interface_metal(latitude).items():
        add(name,part,'metal_ra_stator',cq.Color(.34,.63,.76) if 'FLANGE' in name else cq.Color(.59,.72,.79),
            'Stationary RA connection only; OEM bolt phase unverified')
    add('RA_HARMONIC_GEARBOX_ENVELOPE_NOT_PURCHASED',v05.pivot_rotate(v07.reducer_envelope_local(),90-latitude),
        'reference_gearbox',cq.Color(.93,.62,.25),'RA CSF17 size envelope only; no input coupling modeled')

    # V0.4 native RA output face is z=0. It is located against the top end of
    # the V0.7 RA reduction envelope z=93+45=138, BEFORE the latitude rotation.
    ra_output_local_z=v07.RA_FLANGE_Z1+v07.RA_REDUCER_HEIGHT
    def position_frame(shape):
        return v05.pivot_rotate(shape.translate((0,0,ra_output_local_z)),90-latitude)
    for name,part in v04.metal_parts().items():
        add(name,position_frame(part),'metal_ra_dec_frame',cq.Color(.76,.78,.81),
            'V0.4 orthogonal frame conceptual alignment, NOT certified attachment')

    # Add DEC harmonic reducer housing volume but no camera, DEC output saddle,
    # drive pulley or fabricated shaft coupling.
    dec_reference=(cq.Workplane('YZ').center(0,v04.DEC_CENTER_Z)
                   .circle(v07.GEARBOX_DEC_OD/2).extrude(41)
                   .translate((117,0,0)))
    add('DEC_HARMONIC_GEARBOX_ENVELOPE_NOT_PURCHASED',position_frame(dec_reference),
        'reference_gearbox',cq.Color(.96,.67,.32),
        'DEC CSF14 approximate envelope only; rear bolts/rotation not verified')

    # Only skins with a clearly established assembly placement may be shown.
    # These are not load-rated. Do not place loose test gauges into the mount.
    for name,part in v04.printable_parts().items():
        if name=='v04_cheek_left_PRINT_FLAT':
            p=v04.in_global_side(part,False,True)
        elif name=='v04_cheek_right_PRINT_FLAT':
            p=v04.in_global_side(part,True,True)
        else:continue
        add(name+'_ASSEMBLY_POSITION',position_frame(p),'printed_nonstructural',cq.Color(.14,.55,.75),
            'Non-load-bearing decorative cover; print-file orientations remain unchanged')

    return records

def export(out:Path,latitude:float=35.):
    out.mkdir(parents=True,exist_ok=True)
    records=make_components(latitude)
    assy=cq.Assembly(name=f'OpenEQMount_V08_VIEW_UNQUALIFIED_Lat{latitude:g}')
    manifest=[]
    for item in records:
        shape=item['shape']
        if len(shape.solids().vals())!=1 or shape.val().Volume()<=0:
            raise ValueError('Non-solid component: '+item['name'])
        assy.add(shape,name=item['name'],color=item['color'])
        b=shape.val().BoundingBox()
        manifest.append({'name':item['name'],'category':item['category'],
                         'bbox':[round(b.xmin,2),round(b.ymin,2),round(b.zmin,2),round(b.xmax,2),round(b.ymax,2),round(b.zmax,2)],
                         'notes':item['notes']})
    name='OpenEQMount_V08_WHOLE_MOUNT_CONCEPT_UNQUALIFIED.step'
    assy.save(str(out/name),exportType='STEP')
    (out/'manifest.json').write_text(json.dumps({
        'release':'V0.8-view','status':'prototype_unqualified_Gate_A_preview_only',
        'purpose':'one selectable assembly document for FreeCAD STEP viewer',
        'latitude_degrees':latitude,'not_a_print_model':True,'structural_qualified':False,
        'selected_tripod_interface':'generic M10 reference only',
        'subassemblies':['V0.5 wedge','V0.6 mechanical lock','V0.7 RA stator','V0.4 RA/DEC orthogonal frame'],
        'excluded_from_installed_mount':['separate V0.7 RA/DEC belt fixtures','loose fit gauges / coupons',
           'alternative 3/8-in tripod adapter','V0.5 superseded deck and pivot top'],
        'unresolved':['OEM reducer input geometry and rotor/output constraints','V0.7-to-V0.4 output flange mating proof',
           'DEC stationary/stator support and moving outputs','fastener access, retention, collision at full motion',
           'metal stress/deflection calculations','DfAM Gate B and Gate C real-world testing'],
        'contains_working_drivetrain':False,'safe_for_payload':False,
        'parts':manifest},ensure_ascii=False,indent=2)+'\n')
    return records

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=HERE/'v08_generated')
    parser.add_argument('--latitude',type=float,default=35.)
    args=parser.parse_args()
    things=export(args.out,args.latitude)
    print('Wrote OpenEQMount concept STEP with',len(things),'color-coded solids')
