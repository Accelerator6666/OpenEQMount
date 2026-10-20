#!/usr/bin/env python3
"""OpenEQMount V1.5 three independent bearing candidate envelopes, NOT installable parts.

These are side-by-side alternatives; no alternative has been mated to the ROT
spindle, camera clamp or original V1.4 full-mount STEP.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.rotator_bearing_tradeoff import CANDIDATES,write_reports

X_CENTERS=(0.,185.,390.)
COLORS={'bearing':cq.Color(.87,.69,.32),'spindle':cq.Color(.46,.63,.79),'stator':cq.Color(.44,.48,.59),'bracket':cq.Color(.42,.69,.57)}

def ring(od,id_,height,z,x=0):
    if not (od>id_>0 and height>0):raise ValueError('bad annular geometry')
    return cq.Workplane('XY').circle(od/2).circle(id_/2).extrude(height).translate((x,0,z))

def candidate_parts(key:str):
    opts={c.key:c for c in CANDIDATES}
    c=opts[key]
    x=X_CENTERS[list(opts).index(key)]
    out=[]
    if key in ('6808_pair','7008_db_pair'):
        spindle=ring(39.8,32,69,0,x)
        stator_od=76 if key=='6808_pair' else 90
        stator=ring(stator_od,c.od_mm+.4,69,-3,x)
        out.extend([('40mm_SPINDLE_PLACEHOLDER_NO_FIT',spindle,'spindle'),
                    ('ONE_PIECE_STATOR_SLEEVE_ENVELOPE_NO_ASSEMBLY_PATH',stator,'stator')])
        for j,z in enumerate(c.theoretical_support_centers_mm):
            brg=ring(c.od_mm,c.bore_mm,c.width_mm,z-c.width_mm/2,x)
            out.append((f'{key.upper()}_BEARING_{j+1}_OEM_OUTLINE_ONLY',brg,'bearing'))
        # These plate references don't add shaft retention; do not imply preload.
        out.append(('FIXED_SIDE_REFERENCE_PLATE_NO_BOLTS',ring(stator_od+16,44,5,-12,x),'bracket'))
    else:
        out.extend([
            ('35mm_REPLACEMENT_SPINDLE_NEEDED_NO_REUSE_V14',ring(34.8,25,68,0,x),'spindle'),
            ('THK_RU66_BOUNDARY_ONLY_NOT_VENDOR_GEOMETRY',ring(95,35,15,27.5-7.5,x),'bearing'),
            ('FIXED_RING_INTERFACE_NO_OEM_HOLES',ring(113,96,7,10,x),'stator'),
            ('ROTATING_RING_INTERFACE_NO_OEM_HOLES',ring(110,36,7,45,x),'bracket')
        ])
    return out

def records():
    out=[]
    for c in CANDIDATES:
        for name,shape,role in candidate_parts(c.key):
            out.append({'name':f'v15_{c.key}_{name}', 'shape':shape,'role':role,'color':COLORS[role]})
    return out

def nonload_flat_coupons():
    # Nonload printing coupons check bores and visual fit independently, NOT spindle interfaces.
    # 6808 / 7008 annular calibration, 2 mm thick, flat XY, no actual radial/axial capacity.
    return {
      'v15_NONLOAD_6808_BORE_FIT_COUPON': ring(72,52,3,0),
      'v15_NONLOAD_7008_BORE_FIT_COUPON': ring(89,68,3,0),
      'v15_NONLOAD_RU66_BORE_FIT_COUPON': ring(108,95,3,0),
    }

def export(out:Path):
    out=Path(out);out.mkdir(exist_ok=True,parents=True)
    rec=records()
    assembly=cq.Assembly(name='V15_THREE_DETACHED_CHOICES_NO_PAYLOAD_NO_POWER')
    for r in rec:assembly.add(r['shape'],name=r['name'],color=r['color'])
    final_name='OpenEQMount_V15_ROT_BEARING_ARCHITECTURE_COMPARISON_UNQUALIFIED.step'
    assembly.save(str(out/final_name),exportType='STEP')
    for c in CANDIDATES:
        sub=cq.Assembly(name=f'V15_{c.key.upper()}_NO_OEM_FITS')
        for name,s,role in candidate_parts(c.key):sub.add(s,name=name,color=COLORS[role])
        sub.save(str(out/f'OpenEQMount_V15_{c.key}_OPTION_UNQUALIFIED.step'),exportType='STEP')
    coupons=nonload_flat_coupons()
    for name,p in coupons.items():
        cq.exporters.export(p,str(out/(name+'.step')),exportType='STEP')
        cq.exporters.export(p,str(out/(name+'.stl')),exportType='STL',tolerance=.08,angularTolerance=.18)
    report=write_reports(out)
    manifest={
      'release':'V1.5_ROT_BEARING_COMPARISON_GATE_A_NOT_MANUFACTURING',
      'assembled_step':final_name,'parts_in_assembly':len(rec),
      'architecture_choices':[dict(key=c.key,bearing=c.product,diameters=[c.bore_mm,c.od_mm,c.width_mm],count=c.count,
          spindle_40mm_compatible=c.previous_40mm_spindle_compatible) for c in CANDIDATES],
      'separate_options_not_installable':True,'machining_dimensions_qualified':False,
      'RU66_35mm_requires_redesign':True,'7008_DB_preload_selected':False,
      'bearing_moment_stiffness_verified':False,'vendor_bolt_pattern_verified':False,
      'spindle_locknut_preload_qualified':False,'camera_clamp_and_tether_qualified':False,
      'three_axis_motion_verified':False,'camera_attached':False,
      'nonload_printed_parts':[dict(name=n,material='PETG coupon only',print_orientation='flat XY on Z0',
         layer_direction='+Z',load_path='none',overhang_strategy='vertical bore/flat layers',
         joint='no mounting or load-bearing function',field_load_approved=False,
         Gate_B='pending',Gate_C='pending') for n in coupons],
      'numerical_cases':report['sweep_count'],'digital_gate_A':'candidate geometry/data sanity only',
      'Gate_B':'pending','Gate_C':'pending','safe_to_energize':False,'payload_approved':False,
      'warnings':report['critical_uncertainties'],
    }
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).parent/'v15_generated')
    a=p.parse_args();m=export(a.out)
    print('V1.5 detached bearing architecture CAD:',m['parts_in_assembly'],'solid bodies')
