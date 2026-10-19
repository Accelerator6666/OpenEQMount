#!/usr/bin/env python3
"""OpenEQMount V0.5 DfAM polar wedge *kinematic bench prototype*.

Units mm. Coordinates: tripod base XY at z=0; geographic north is -X.
The top plate normal points toward -X/+Z after Y-axis rotation through
90-latitude degrees, so a perpendicular RA axis has altitude=latitude.

All proposed structural load paths use METAL elements; prints are only covers,
scales, fit gauges. No load rating, fastener engagement or OEM fit is implied.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import cadquery as cq

VERSION = 'V0.5'
STATUS = 'prototype_unqualified_Gate_A_only'
LAT_MIN, LAT_MAX, LAT_DEFAULT = 25., 45., 35.
MAX_BED = 220.0
PIVOT = (-61., 0., 29.)
LOWER_JACK = (64., 0., 25.)
UPPER_JACK_LOCAL = (53., 0., 17.)
BASE_Z = (0., 6.)
AZ_Z = (8., 14.)
AZ_TRAVEL_DEG = 5.


def radians(d): return math.radians(d)

def cutter_z(points, diameter, z0=-1., height=200.):
    return cq.Workplane('XY').pushPoints(points).circle(diameter/2).extrude(height).translate((0,0,z0))

def bore_y(x,z,diameter=8.5):
    return cq.Workplane('XZ').center(x,z).circle(diameter/2).extrude(200,both=True)

def pivot_rotate(part, tilt):
    return part.rotate(PIVOT,(PIVOT[0],PIVOT[1]+1,PIVOT[2]),-tilt)

def tilted_point(point,latitude):
    theta=radians(90-latitude)
    dx,dz=point[0]-PIVOT[0], point[2]-PIVOT[2]
    return (PIVOT[0]+dx*math.cos(theta)-dz*math.sin(theta),point[1],
            PIVOT[2]+dx*math.sin(theta)+dz*math.cos(theta))

def jack_length(latitude):
    up=tilted_point(UPPER_JACK_LOCAL,latitude)
    return math.dist(up,LOWER_JACK)

def along(a,b,r):
    va=cq.Vector(*a); vb=cq.Vector(*b); vec=vb.sub(va)
    return cq.Workplane('XY').newObject([cq.Solid.makeCylinder(r,vec.Length,va,vec.normalized())])

def az_arc_cutter(center_angle, radius=58., sweep=AZ_TRAVEL_DEG,diameter=6.6):
    """Continuous swept arc slot: annular strip plus two round endcaps.

    Do not cut with a compound of intersecting cylinders: OCC may silently
    leave the overlapping cutters unjoined, creating blind islands.
    """
    aa=[center_angle-sweep+i*2*sweep/40 for i in range(41)]
    high=[((radius+diameter/2)*math.cos(radians(a)),
           (radius+diameter/2)*math.sin(radians(a))) for a in aa]
    low=[((radius-diameter/2)*math.cos(radians(a)),
          (radius-diameter/2)*math.sin(radians(a))) for a in reversed(aa)]
    strip=cq.Workplane('XY').polyline(high+low).close().extrude(9).translate((0,0,6.5))
    for a in (aa[0],aa[-1]):
        point=(radius*math.cos(radians(a)),radius*math.sin(radians(a)))
        strip=strip.union(cutter_z([point],diameter,z0=6.5,height=9))
    return strip


def fixed_triad_base():
    base=cq.Workplane('XY').box(210,158,6,centered=(True,True,False))
    base=base.cut(cutter_z([(0,0)],10.5,z0=-1,height=9))
    # Generic tripod stud/gauge pattern. NOT a confirmed tripod interface.
    for a in (30.,150.,270.):
        x,y=62*math.cos(radians(a)),62*math.sin(radians(a))
        base=base.cut(cutter_z([(x,y)],6.5,z0=-1,height=9))
    for y in [-58.,58.]:
        base=base.cut(cutter_z([(0.,y)],6.5,z0=-1,height=9))
    # Opposed azimuth screw ears are part of the metal base.
    for y in (-34.,34.):
        ear=cq.Workplane('XY').box(15,8,19).translate((96,y,15.5))
        base=base.union(ear)
    base=base.cut(cq.Workplane('XZ').center(96,21).circle(3.5).extrude(200,both=True))
    return base

def azimuth_deck():
    deck=cq.Workplane('XY').box(166,145,6).translate((0,0,11))
    deck=deck.cut(cutter_z([(0,0)],10.5,z0=7,height=9))
    for a in (90.,270.): deck=deck.cut(az_arc_cutter(a))
    nub=cq.Workplane('XY').box(28,14,16).translate((96,0,22))  # azimuth tangent jack contact metal
    deck=deck.union(nub)
    # M6 metal lower-hinge cheek anchorage, not through plastic.
    for y in (-62.,62.):
        deck=deck.cut(cutter_z([(-61,y),(-37,y)],6.6,z0=7,height=11))
    # Vertical safety-bolt receivers (not a verified lock)
    return deck

def lower_hinge_cheek(positive):
    y=62. if positive else -62.
    foot=cq.Workplane('XY').box(44,15,5).translate((-49,y,16.5))
    cheek=cq.Workplane('XY').box(35,5,31).translate((-61,y,30))
    obj=foot.union(cheek)
    obj=obj.cut(bore_y(-61,29,8.5))
    for x in (-61.,-37.):
        obj=obj.cut(cutter_z([(x,y)],6.6,z0=13,height=7))
    return obj

def tilt_assembly_local():
    # Top metal deck supports the RA interface with still-UNVERIFIED generic hole pattern.
    top=cq.Workplane('XY').box(158,106,6).translate((10,0,27))
    for x in (-43.,45.):
        for y in (-45.,45.):
            top=top.cut(cutter_z([(x,y)],6.6,z0=23,height=9))
    for y in (-47.,47.):
        ear=cq.Workplane('XY').box(28,5,27).translate((-61,y,28))
        top=top.union(ear)
    # Metal double-clevis cheeks leave a through-gap for the M8 jack eye.
    for y in (-11.,11.):
        top=top.union(cq.Workplane('XY').box(19,5,15).translate((53,y,18)))
    top=top.cut(bore_y(PIVOT[0],PIVOT[2],8.5))
    top=top.cut(bore_y(UPPER_JACK_LOCAL[0],UPPER_JACK_LOCAL[2],8.5))
    return top

def tilt_deck(latitude=LAT_DEFAULT):
    return pivot_rotate(tilt_assembly_local(),90-latitude)

def lower_jack_clevis():
    # Physical metal fork pair on the azimuth deck, never a printed load-bearing lug.
    foot=cq.Workplane('XY').box(28,31,5).translate((64,0,16.5))
    for y in (-11.,11.):
        foot=foot.union(cq.Workplane('XY').box(19,5,18).translate((64,y,25)))
    foot=foot.cut(bore_y(LOWER_JACK[0],LOWER_JACK[2],8.5))
    return foot


def hinge_pin():
    # Model-only M8 through-pin/shaft. Requires shoulder length/retention selection.
    return along((-61,-75,29),(-61,75,29),4)

def jack_rod(latitude=LAT_DEFAULT):
    return along(LOWER_JACK,tilted_point(UPPER_JACK_LOCAL,latitude),4)

def azimuth_jack_screws():
    return {f'v05_az_push_screw_{side}_METAL_REFERENCE':
      along((96.,side*29.,21.),(96.,side*7.,21.),3) for side in (-1,1)}


def printable_left_right_cover(sign):
    # Simple printable planar cover with continuous perimeter, XY radii and bolt-access windows.
    plate=cq.Workplane('XY').box(111,29,4,centered=(True,True,False)).edges('|Z').fillet(3)
    plate=plate.cut(cutter_z([(x,0) for x in (-43.,43.)],4.0,z0=-1,height=6))
    # Flat XY gusset-like profile is a cosmetic relief; no force carried.
    plate=plate.cut(cq.Workplane('XY').box(28,7,6).translate((0,sign*12,2)))
    return plate

def altitude_pointer():
    part=cq.Workplane('XY').box(78,28,4,centered=(True,True,False)).edges('|Z').fillet(4)
    part=part.cut(cutter_z([(-29,0),(29,0)],4,z0=-1,height=6))
    # Integrated embossed pointer is omitted: geometry remains supportless and easily annotated.
    return part

def azimuth_scale_ring():
    # Free loose ring. Never share tripod or pivot preload.
    ring=cq.Workplane('XY').circle(55).circle(42).extrude(3)
    for a in range(0,360,30):
        x,y=49.5*math.cos(radians(a)),49.5*math.sin(radians(a))
        ring=ring.cut(cutter_z([(x,y)],1.7,z0=-1,height=5))
    return ring

def fit_coupon():
    gauge=cq.Workplane('XY').box(104,27,6,centered=(True,True,False)).edges('|Z').fillet(3)
    for x,d in zip((-36.,-12.,12.,36.),(4.4,4.6,6.4,6.6)):
        gauge=gauge.cut(cutter_z([(x,0)],d,z0=-1,height=9))
    return gauge

def prints():
    return {'v05_left_wedge_cover_PRINT_FLAT':printable_left_right_cover(-1),
            'v05_right_wedge_cover_PRINT_FLAT':printable_left_right_cover(1),
            'v05_altitude_pointer_PRINT_FLAT':altitude_pointer(),
            'v05_azimuth_scale_RING_PRINT_FLAT':azimuth_scale_ring(),
            'v05_screw_fit_COUPON_PRINT_FLAT':fit_coupon()}

def metals(latitude=LAT_DEFAULT):
    parts={
      'v05_tripod_anchor_BASE_METAL':fixed_triad_base(),
      'v05_azimuth_slew_DECK_METAL':azimuth_deck(),
      'v05_hinge_lower_LEFT_METAL':lower_hinge_cheek(False),
      'v05_hinge_lower_RIGHT_METAL':lower_hinge_cheek(True),
      'v05_tilt_ra_INTERFACE_METAL':tilt_deck(latitude),
      'v05_lower_jack_CLEVIS_METAL':lower_jack_clevis(),
      'v05_hinge_M8_PIN_METAL_REFERENCE':hinge_pin(),
      'v05_altitude_M8_JACK_METAL_REFERENCE':jack_rod(latitude),
    }
    parts.update(azimuth_jack_screws())
    return parts

def dfam_entry(name,shape):
    bb=shape.val().BoundingBox()
    return dict(name=name,material='PETG fit/bench only',status='prototype_unqualified',
      role='nonstructural cover / visual alignment / tolerance gauge',
      print_orientation='XY flat bed, 0 <= Z <= part height; +Z layering',
      layer_direction='+Z; cosmetic or gauge part with zero approved primary load',
      load_path='none — metal fasteners and metal plates are separate',
      overhang_strategy='planar top/bottom; inspect bridging and holes in slicer',
      metal_joint='no printed retaining threads; fastener clearance only; no compression path',
      min_wall_mm='pending slicer verification; trial profile, not certification',
      slicer_gate_B='pending',physical_gate_C='pending',
      bbox_mm=[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],
      volume_cc=round(shape.val().Volume()/1000.,2))

def export(out:Path,latitude=LAT_DEFAULT):
    if not LAT_MIN <= latitude <= LAT_MAX:raise ValueError('V0.5 bench latitude range is 25..45 deg')
    out.mkdir(parents=True,exist_ok=True)
    pp,mm=prints(),metals(latitude)
    data=dict(release=VERSION,status=STATUS,latitude_degrees=latitude,
      latitude_trial_range=[LAT_MIN,LAT_MAX],azimuth_travel_degrees=[-AZ_TRAVEL_DEG,AZ_TRAVEL_DEG],
      location='generic tripod interface; not verified against a specific tripod',
      kinematics='RA axis is normal to deck; north-facing RA axis normal has altitude = geographic latitude',
      hinge_axis_mm=list(PIVOT),
      jack_length_mm={str(a):round(jack_length(a),2) for a in (LAT_MIN,LAT_DEFAULT,LAT_MAX)},
      printed_parts=[],metal_parts=[],
      warnings=['All construction and mounting patterns require physical confirmation before load.',
                'No complete altitude locking clamp or rated jack is provided: never deploy unrestrained.',
                'No independently tested metal fall-prevention harness, no safe load rating.',
                'Do not 3D-print metal-labeled parts as structural substitutes.',
                'Center M10/tripod and top RA adapter bolt patterns are provisional. NEVER attach the rotating V0.4 RA output plate to the fixed polar wedge; the RA stator interface remains to be engineered.',
                'M8 jack and azimuth screws are kinematic envelopes, not threaded/strength-qualified mechanisms.',
                'Angle and azimuth range are geometry targets, not certified collision-free travel.'])
    for name,part in pp.items():
        bb=part.val().BoundingBox()
        if bb.zmin < -1e-6 or max(bb.xlen,bb.ylen)>MAX_BED:raise ValueError('DfAM bed '+name)
        if len(part.solids().vals()) != 1:raise ValueError('Disconnected '+name)
        cq.exporters.export(part,str(out/(name+'.step')),exportType='STEP')
        cq.exporters.export(part,str(out/(name+'.stl')),exportType='STL',tolerance=.12,angularTolerance=.15)
        data['printed_parts'].append(dfam_entry(name,part))
    for name,part in mm.items():
        cq.exporters.export(part,str(out/(name+'.step')),exportType='STEP')
        bb=part.val().BoundingBox()
        data['metal_parts'].append(dict(name=name,material='metal reference (aluminum/steel); must be verified',
          bbox_mm=[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],
          volume_cc=round(part.val().Volume()/1000.,2)))
    assembly=cq.Assembly(name='OpenEQMount_V05_UNQUALIFIED_BENCH_35D' if latitude==35 else 'OpenEQMount_V05_UNQUALIFIED')
    for name,part in mm.items():
        color=cq.Color(.69,.71,.73) if ('PIN' not in name and 'JACK' not in name) else cq.Color(.95,.60,.20)
        assembly.add(part,name=name,color=color)
    assembly.save(str(out/'OpenEQMount_V05_UNQUALIFIED_assembly.step'),exportType='STEP')
    (out/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).parent/'v05_generated')
    p.add_argument('--latitude',type=float,default=LAT_DEFAULT)
    a=p.parse_args(); m=export(a.out,a.latitude)
    print(f'Generated {len(m["printed_parts"])} prints and {len(m["metal_parts"])} metal references; UNQUALIFIED, Gate A only')
if __name__=='__main__':main()
