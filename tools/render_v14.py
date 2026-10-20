#!/usr/bin/env python3
"""Source-derived V1.4 FreeCAD assembly preview + load sensitivity plots."""
from __future__ import annotations
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
from generate_v14_load_fixture import assembly_records
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.rotator_load_cases import estimate,LoadCase
OUT=Path(__file__).resolve().parents[1]/'hardware/cad/v14_generated';OUT.mkdir(exist_ok=True,parents=True)

def draw(ax,shape,col,alpha=.85):
    verts,faces=shape.val().tessellate(3.7,.70)
    pts=[(v.x,v.y,v.z) for v in verts]
    ax.add_collection3d(Poly3DCollection([[pts[k] for k in face] for face in faces],
                           facecolor=col,edgecolor='#2a4653',linewidth=.025,alpha=alpha))

fig=plt.figure(figsize=(11.4,8.8),facecolor='#f7f9fb')
ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
for r in assembly_records():
    n=r['name']
    if 'gauge' in n.lower() or 'cheek' in n.lower() or 'SPACER_' in n:continue
    if 'v14_REFERENCE_CAMERA' in n or 'v14_REFERENCE_LENS' in n:col='#a783c7';alpha=.19
    elif 'v14_' in n:col='#2aa58a';alpha=.95
    elif 'v13_' in n:col='#d7a352';alpha=.89
    elif 'v12_' in n:col='#5d97c2';alpha=.7
    elif 'DEC_OUTPUT_TO_ROT' in n:col='#388bab';alpha=.94
    elif 'ENVELOPE' in n:col='#d8ae7e';alpha=.30
    else:col='#a4b1c0';alpha=.72
    draw(ax,r['shape'],col,alpha)
ax.view_init(elev=23,azim=-65);ax.set_box_aspect((1.13,.97,1.65))
ax.set_xlim(-310,165);ax.set_ylim(-215,215);ax.set_zlim(-20,580)
ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('Z (mm)')
ax.set_title('OpenEQMount V1.4 | 3-axis nominal camera load envelopes',pad=17,fontsize=14,weight='bold')
fig.text(.5,.042,'PINK = fictional camera/lens occupancy | GREEN = unqualified metal interface | NO CAMERA / NO POWER',ha='center',fontsize=10,color='#944b33')
fig.savefig(OUT/'OpenEQMount_V14_three_axis_load_envelope.png',dpi=150,bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(10.4,6.4),facecolor='#fafbfe')
for m in (3.,4.,5.):
    x=list(range(20,161,10))
    y=[estimate(LoadCase(m,v,20))['radial_reaction_upper_N_example'] for v in x]
    ax.plot(x,y,lw=2,label=f'{int(m)} kg scenario')
ax.set_xlabel('Distance from camera-mount face to CG (mm)')
ax.set_ylabel('Illustrative upper 6808 radial support reaction (N)')
ax.set_title('Two 6808 bearings only 30 mm apart | transverse-gravity example',pad=12,weight='bold')
ax.grid(alpha=.23);ax.legend()
fig.text(.5,.025,'Not a bearing-rating comparison. Ignores preload, stiffness, cage, impacts and all-axis orientations.',ha='center',color='#9a4c35',fontsize=9)
fig.savefig(OUT/'OpenEQMount_V14_bearing_reaction_sensitivity.png',dpi=160,bbox_inches='tight');plt.close(fig)
print('V1.4 previews generated')
