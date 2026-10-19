#!/usr/bin/env python3
"""Static preview of actual V0.9 CAD envelopes for FreeCAD navigation.

View only, not an assembly-fit analysis or physical connection proof.
"""
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.lines import Line2D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v09_rotator as v
import generate_v08_concept_assembly as v08

def draw_shape(ax,shape,color,alpha=1):
    verts,tri=shape.val().tessellate(2.5,.5)
    vts=[(q.x,q.y,q.z) for q in verts]
    poly=[[vts[i] for i in face] for face in tri]
    ax.add_collection3d(Poly3DCollection(poly,facecolor=color,edgecolor='none',alpha=alpha,zsort='average'))

fig=plt.figure(figsize=(12,8),facecolor='#f7f9fc')
ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
for e in v08.make_components(35):
    n=e['name']
    if ('TRIPOD_FIXED_MAIN_BASE' in n or 'WEDGE_REPLACEMENT' in n or
        n=='RA_HARMONIC_GEARBOX_ENVELOPE_NOT_PURCHASED' or
        n=='DEC_HARMONIC_GEARBOX_ENVELOPE_NOT_PURCHASED' or
        ('side_web_METAL' in n) or 'v04_ra_output_plate_METAL' in n or
        'v04_dec_rear_plate_METAL' in n):
        draw_shape(ax,e['shape'],'#aeb7c4' if 'ENVELOPE' not in n else '#dbad73',.85)
for n,s in v.metal_components().items():
    color='#4faca0' if 'OUTPUT' in n else '#527ac1' if 'STATOR' in n else '#7bc2b1'
    draw_shape(ax,v.to_mount(s,35),color,0.9 if 'BEARING' not in n else .36)
bezel=v.printable_components()['v09_ROT_NONLOAD_POSITION_SCALE_BEZEL_PRINT_FLAT']
draw_shape(ax,v.to_mount(bezel.translate((0,0,31)),35),'#2597c0',.78)
ax.view_init(elev=20,azim=-72)
ax.set_xlim(-275,150);ax.set_ylim(-175,135);ax.set_zlim(-50,490)
ax.set_box_aspect((1.25,1.,1.5))
ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('Z (mm)')
ax.set_title('OpenEQMount V0.9  |  RA + DEC + ROT (3-axis concept)',fontsize=16,pad=18)
legend=[Line2D([0],[0],color='#aeb7c4',lw=6,label='existing metal frames / polar base'),
        Line2D([0],[0],color='#dbad73',lw=6,label='gearbox space envelopes'),
        Line2D([0],[0],color='#4faca0',lw=6,label='new ROT metal reference rings'),
        Line2D([0],[0],color='#2597c0',lw=6,label='non-load printed scale')]
fig.legend(handles=legend,loc='lower center',ncol=2,frameon=False)
fig.text(.5,.065,'ROT optical axis is perpendicular to DEC axis. FLOATING interface: no verified camera saddle or payload rating.',
         ha='center',color='#9a5526',fontsize=11)
out=Path(__file__).resolve().parents[1]/'hardware/cad/v09_generated/OpenEQMount_V09_3axis_preview.png'
fig.savefig(out,dpi=155,bbox_inches='tight',facecolor=fig.get_facecolor())
print(out)
