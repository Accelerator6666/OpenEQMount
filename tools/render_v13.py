#!/usr/bin/env python3
"""V1.3 machine-generated CAD overview and nominal bearing stack section."""
import sys,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v13_rot_retention as v
import generate_v10_rotator_bench as v10
out=Path(__file__).resolve().parents[1]/'hardware/cad/v13_generated';out.mkdir(parents=True,exist_ok=True)

def draw(ax,part,col,alpha=.83,detail=3.):
    vert,fac=part.val().tessellate(detail,.62)
    vec=[(p.x,p.y,p.z) for p in vert]
    ax.add_collection3d(Poly3DCollection([[vec[k] for k in tri] for tri in fac],facecolor=col,edgecolor='#364659',linewidth=.025,alpha=alpha))

fig=plt.figure(figsize=(11.7,9.0),facecolor='#f6f8fc')
ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
for part in v.assembly_records():
    name=part['name'];role=part['role']
    if 'gauge' in name.lower() or 'cheek' in name.lower() or 'SPACER_' in name:continue
    if 'FLOATING' in name: col='#b64684';opacity=.9
    elif 'v13_' in name:col='#e0a344' if 'SPINDLE' in name or 'NUT' in name else '#36a888';opacity=.97
    elif 'v12_' in name:col='#dc8a58' if 'STOP' in name else '#689cce';opacity=.67
    elif 'DEC_OUTPUT_TO_ROT' in name:col='#378aae';opacity=.95
    elif 'BEARING_' in name:col='#d8b35b';opacity=.75
    elif 'GEARBOX' in name or 'ENVELOPE' in name:col='#d69c70';opacity=.33
    else:col='#aab6c5';opacity=.72
    draw(ax,part['shape'],col,opacity,detail=3.5)
ax.view_init(elev=26,azim=-64);ax.set_box_aspect((1.2,.9,1.5))
ax.set_xlim(-290,150);ax.set_ylim(-185,195);ax.set_zlim(-15,490)
ax.set_xlabel('X mm');ax.set_ylabel('Y mm');ax.set_zlabel('Z mm')
ax.set_title('OpenEQMount V1.3 | 3-axis geometry with candidate ROT metal retention',pad=16,fontsize=14,weight='bold')
fig.text(.5,.045,'CAD GATE A ONLY | GREEN: camera clamp interface | PINK: unattached camera eye | NO POWER / NO CAMERA',ha='center',fontsize=10,color='#a05129')
fig.savefig(out/'OpenEQMount_V13_three_axis_overview.png',dpi=145,bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(11,7.5),facecolor='#f7f9fb')
ax.set_facecolor('#f7f9fb')
# Cross-section schematic: abscissa radius, ordinate axial z. Nominal CAD envelopes only.
for label,ri,ro,z0,z1,color in [
 ('stepped hollow shaft',16,20,-5,44,'#6da4cf'),
 ('integral shoulder',20,22.5,3,7,'#4d83bd'),
 ('thread envelope',16,19,44,53,'#6da4cf'),
 ('spindle pilot',16,16.75,53,64,'#6da4cf'),
 ('bearing A',20,26,7,14,'#e6ba5b'),
 ('bearing B',20,26,37,44,'#e6ba5b'),
 ('distance sleeve hypothesis',20.1,22.5,14,37,'#53bfa0'),
 ('symbolic nut',18.85,23.5,44,50,'#da7951'),
 ('unkeyed washer',19,25,50,51.5,'#e6a25a'),
 ('clamp datum',20,54,67,75,'#42a987')]:
    for direction in (-1,1):
        x=ri if direction==1 else -ro
        ax.add_patch(Rectangle((x,z0),ro-ri,z1-z0,facecolor=color,edgecolor='#33495a',lw=.6,alpha=.8))
# e.g. 6808 outer ring candidate 40..52 envelope, no preload claim
for z in (7,14,37,44,50,59,67,75):
    ax.axhline(z,color='#7b8794',lw=.45,ls='--')
    ax.text(60,z,str(z)+' mm',fontsize=8,va='center',color='#536474')
ax.set_xlim(-68,78);ax.set_ylim(-9,84);ax.set_xlabel('Radial envelope / mm (not drawing for machining)')
ax.set_ylabel('ROT local axial Z / mm')
ax.set_title('V1.3 | Two 6808 inner rings and axial shaft/nut stack - conceptual cutaway',weight='bold',pad=16)
ax.grid(alpha=.16,axis='x');fig.text(.5,.035,'Thin-section bearing face/fit/preload not verified | Thread is only a cylinder | Caution: no structural or safety approval',ha='center',color='#a05129',fontsize=10)
fig.savefig(out/'OpenEQMount_V13_axial_stack_section.png',dpi=150,bbox_inches='tight');plt.close(fig)
print('V1.3 PNGs generated')
