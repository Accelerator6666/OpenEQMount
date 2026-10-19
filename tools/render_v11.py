#!/usr/bin/env python3
"""Static CAD preview of V1.1, derived from source shapes; not an FE/stress plot."""
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v11_three_axis_mated_concept as v

OUT=Path(__file__).resolve().parents[1]/'hardware'/'cad'/'v11_generated'
OUT.mkdir(parents=True,exist_ok=True)
records=v.part_records(35,25,0)

def draw(ax,sh,color,alpha=.95,detail=3.7):
    verts,faces=sh.val().tessellate(detail,.75)
    points=[(p.x,p.y,p.z) for p in verts]
    poly=[[points[i] for i in face] for face in faces]
    ax.add_collection3d(Poly3DCollection(poly,facecolor=color,linewidth=.045,edgecolor='#303e4e',alpha=alpha))

fig=plt.figure(figsize=(11.8,10),facecolor='#f6f8fc')
ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
for p in records:
    n=p['name'];role=p['role']
    if 'cheek_' in n:continue
    if role=='metal_lock' and 'sector' not in n and 'pin_' not in n:continue
    if 'ANGLE_METAL' in n.upper() or 'ra_angle_METAL' in n:continue
    if 'BEARING_' in n:color='#e0b05d';alpha=.82
    elif 'DEC_OUTPUT_TO_ROT' in n:color='#2698b9';alpha=.9
    elif 'CAMERA_MATING_FLANGE' in n:color='#38b9a4';alpha=.92
    elif 'REVISED_METAL_NEMA17' in n:color='#8eacc4';alpha=.85
    elif 'DEC_HARMONIC' in n or 'RA_HARMONIC' in n:color='#d78c46';alpha=.30
    elif role=='rot_stator_reference':color='#98aebb';alpha=.76
    elif role=='motor_metal_support_unqualified':color='#c89965';alpha=.94
    elif role=='rotating_metal_reference':color='#adbecc';alpha=.96
    elif role=='metal_base':color='#606d7a';alpha=.88
    else: color='#b1bfcc';alpha=.72
    draw(ax,p['shape'],color,alpha)
ax.view_init(elev=22,azim=-65)
ax.set_xlim(-285,130);ax.set_ylim(-180,180);ax.set_zlim(-10,490)
ax.set_box_aspect((1.05,.80,1.50))
ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('Z (mm)')
ax.set_title('OpenEQMount V1.1 | Three-axis integrated metal-path CONCEPT',fontweight='bold',size=15,pad=18)
fig.text(.5,.044,'DEC rotating output -> metal bridge -> ROT housing -> camera blank | Not rated for camera or powered movement',ha='center',size=10,color='#98573c')
fig.savefig(OUT/'OpenEQMount_V11_three_axis_full_preview.png',dpi=160,bbox_inches='tight')
plt.close(fig)

# A close-up based on native local orientation (not rotated by RA/wedge).
fig=plt.figure(figsize=(11.8,8.5),facecolor='#f6f8fc')
ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
draw(ax,v.continuous_metal_bridge(),'#298bad',.86,detail=2.5)
for n,s in v.v10.metal_parts().items():
    if 'STOP_' in n or 'NEMA17_TENSIONER_' in n:continue
    color='#d3a45a' if 'BEARING_' in n else '#aec2d4'
    draw(ax,s.translate((v.ROT_X,0,v.ROT_Z)),color,.70,3.1)
draw(ax,v.revised_motor_carrier().translate((v.ROT_X,0,v.ROT_Z)),'#7293b0',.80,3.3)
for a in v.MOTOR_STANDOFF_PHASE:
    draw(ax,v.local_standoff(a).translate((v.ROT_X,0,v.ROT_Z)),'#cca473',.96,3)
draw(ax,v.camera_blank().translate((v.ROT_X,0,v.ROT_Z+67)),'#41b5a0',.91,2)
ax.view_init(elev=25,azim=-66)
ax.set_xlim(130,365);ax.set_ylim(-110,110);ax.set_zlim(90,265)
ax.set_box_aspect((1.4,1.2,1))
ax.set_title('V1.1 | DEC output flange to ROT bearing deck (local view)',fontweight='bold',size=15,pad=18)
ax.set_xlabel('DEC output direction +X (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('optical direction +Z (mm)')
fig.text(.5,.045,'Reference PCD only | No verified welds, axial bearing capture, lens clamp, safe tether or powered limit switches',ha='center',size=10,color='#98573c')
fig.savefig(OUT/'OpenEQMount_V11_DEC_ROT_connection_preview.png',dpi=160,bbox_inches='tight')
plt.close(fig)
print('Rendered V1.1 full and detailed preview')
