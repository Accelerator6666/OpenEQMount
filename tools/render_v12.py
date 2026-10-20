#!/usr/bin/env python3
"""Reproducible Gate-A visualizations (not engineering/stress certification)."""
from pathlib import Path
import sys,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v12_rot_cartridge as v
import generate_v11_three_axis_mated_concept as v11
import generate_v10_rotator_bench as v10

out=Path(__file__).resolve().parents[1]/'hardware'/'cad'/'v12_generated'
out.mkdir(parents=True,exist_ok=True)

def draw(ax,sh,color,alpha=.88,detail=3):
    verts,faces=sh.val().tessellate(detail,.70)
    ps=[(p.x,p.y,p.z) for p in verts]
    polygons=[[ps[k] for k in face] for face in faces]
    ax.add_collection3d(Poly3DCollection(polygons,facecolor=color,edgecolor='#2e3f50',linewidth=.033,alpha=alpha))

fig=plt.figure(figsize=(11.5,9.4),facecolor='#f6f8fb')
ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
for p in v.part_records(35,25,0):
    n=p['name'];r=p['role']
    if 'cheek_' in n.lower() or 'gauge' in n.lower():continue
    if 'v10_METAL_INDEPENDENT_CAPTURE_COLLAR' in n:continue  # incomplete predecessor
    if 'v12_METAL_INNER_RING_SPACER' in n or 'v12_METAL_OUTER_RING_SPACER' in n:continue # internal stack in exploded view
    if 'v12_METAL_' in n:
        col='#e36d40' if 'STOP' in n else '#2c9e85' if 'TETHER' in n else '#6da2d5'
        alpha=.96
    elif 'DEC_OUTPUT_TO_ROT' in n:col='#3385ab';alpha=.91
    elif 'BEARING_' in n:col='#e8bd6d';alpha=.84
    elif 'HARMONIC' in n:col='#d8a06f';alpha=.30
    elif 'CAMERA_MATING' in n:col='#45af97';alpha=.91
    elif r=='metal_base':col='#778692';alpha=.85
    else:col='#adbcc9';alpha=.70
    draw(ax,p['shape'],col,alpha)
ax.view_init(elev=24,azim=-63)
ax.set_box_aspect((1,.85,1.5));ax.set_xlim(-290,150);ax.set_ylim(-185,190);ax.set_zlim(-15,490)
ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('Z (mm)')
ax.set_title('OpenEQMount V1.2 | Three-axis ROT cartridge / physical-stop concept',fontsize=14,fontweight='bold',pad=20)
fig.text(.5,.047,'64 bodies / UNQUALIFIED CAD | Orange=reference stops  Green=tether tabs (no cable)  Blue=serviceable metal bearing housing',ha='center',color='#9b4d2d',size=10)
fig.savefig(out/'OpenEQMount_V12_full_three_axis_preview.png',dpi=150,bbox_inches='tight')
plt.close(fig)

fig=plt.figure(figsize=(11.7,8.6),facecolor='#f6f8fb')
ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
parts=v.metal_parts()
for n,s in parts.items():
    if 'INNER_RING_SPACER' in n:color='#b4d2df';alpha=.65
    elif 'OUTER_RING_SPACER' in n:color='#eac06d';alpha=.74
    elif 'STOP' in n:color='#e07546';alpha=.95
    elif 'TETHER' in n:color='#30ac89';alpha=.92
    else:color='#659ec6';alpha=.60 if 'STATOR' in n else .86
    draw(ax,s,color,alpha,detail=2.7)
for n,s in v10.metal_parts().items():
    if 'BEARING_' in n:draw(ax,s,'#e6ae4f',.62,2.8)
    if 'OUTPUT_FLANGE_' in n:draw(ax,s,'#98a9b9',.39,3)
ax.view_init(elev=29,azim=-60)
ax.set_box_aspect((1.3,1.25,.9));ax.set_xlim(-105,146);ax.set_ylim(-110,105);ax.set_zlim(-14,103)
ax.set_title('ROT local housing | removable caps, spacer references & contacting hard-stop blocks',fontsize=13,fontweight='bold',pad=18)
ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('Z (mm)')
fig.text(.5,.045,'CAD contact verified at +/-160 deg; physical stop fasteners, bearing preload and independent tether still MISSING',ha='center',color='#9b4d2d',fontsize=10)
fig.savefig(out/'OpenEQMount_V12_cartridge_details_preview.png',dpi=155,bbox_inches='tight')
plt.close(fig)
print('Rendered V1.2 full assembly and cartridge detail')
