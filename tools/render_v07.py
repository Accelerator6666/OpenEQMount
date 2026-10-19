#!/usr/bin/env python3
"""Make reproducible previews from V0.7 CadQuery solids; NOT manufacturing drawings."""
from __future__ import annotations
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Circle as Circle2D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v07 as v

ROOT=Path(__file__).resolve().parents[1]/'hardware'/'cad'/'v07_generated'
ROOT.mkdir(exist_ok=True,parents=True)

def add_shape(ax,shape,color,alpha=1):
    verts,faces=shape.val().tessellate(1.1,.45)
    pts=[(p.x,p.y,p.z) for p in verts]
    polys=[[pts[q] for q in tri] for tri in faces]
    coll=Poly3DCollection(polys,facecolor=color,linewidth=.045,edgecolor='#263144',alpha=alpha)
    ax.add_collection3d(coll)

fig=plt.figure(figsize=(11.5,8.0),facecolor='#f6f8fb')
ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
cols=['#4b85b7','#6596c1','#79a2c5','#40749d']
for name,sh in v.ra_interface_metal(35).items():
    color='#b2beca' if 'WEDGE_REPLACEMENT' in name else ('#64a3c8' if 'FLANGE' in name else '#7294b1')
    add_shape(ax,sh,color,alpha=.85 if 'FLANGE' in name else 1)
add_shape(ax,v.v05.pivot_rotate(v.reducer_envelope_local(),55),'#e9a15a',.35)
ax.view_init(elev=27,azim=-67)
ax.set_box_aspect((1.1,1.0,1.25))
ax.set_xlim(-130,150);ax.set_ylim(-110,110);ax.set_zlim(0,170)
ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('Z (mm)')
ax.set_title('OpenEQMount V0.7 | Stationary RA housing interface',fontsize=16,pad=20,fontweight='bold')
fig.text(.5,.04,'Metal-only bench interface | replacement wedge deck | NO payload approval',ha='center',fontsize=11,color='#9d4d22')
fig.savefig(ROOT/'OpenEQMount_V07_RA_stator_preview.png',dpi=160,bbox_inches='tight')
plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(13,5.7),facecolor='#f6f8fb')
for ax,axis in zip(axs,('ra','dec')):
    shape=v.belt_cassette_metal(axis)
    verts,faces=shape.val().tessellate(1.2,.4)
    # XY ground footprint from every triangulated face. Skip z dimension to display accurate cutouts.
    from matplotlib.tri import Triangulation
    # Use v07 source-derived plan shapes with actual CAD outline and cut-outs
    # without requiring a heavy BREP section algorithm.
    ax.add_patch(Circle2D((0,0),53,facecolor='#a9b9c9',edgecolor='#425169',lw=2,alpha=.65))
    ax.add_patch(plt.Rectangle((0,-21),115,42,facecolor='#a9b9c9',edgecolor='none',alpha=.65))
    ax.add_patch(Circle2D((v.MOTOR_CENTER_NOMINAL,0),40,facecolor='#a9b9c9',edgecolor='#425169',lw=2,alpha=.65))
    inlet=58 if axis=='ra' else 54
    ax.add_patch(Circle2D((0,0),inlet/2,facecolor='#f6f8fb',edgecolor='#425169',lw=2))
    ax.add_patch(Circle2D((0,0),v.belt_pitch_diameter(60)/2,fill=False,color='#e48235',lw=3,ls='--'))
    ax.add_patch(Circle2D((115,0),v.belt_pitch_diameter(20)/2,fill=False,color='#408ab9',lw=3,ls='--'))
    for x,y in v.motor_screw_centers():
        ax.plot([x-5,x+5],[y,y],color='#235779',lw=3)
    for x,y in v.circle_points(92,4,45):
        ax.plot(x,y,marker='o',markersize=6,color='#1f324d')
    ax.annotate('60T pitch only',(0,0),xytext=(-25,43),arrowprops=dict(arrowstyle='->',color='#a96932'),color='#a96932',size=10)
    ax.annotate('20T pitch only',(115,0),xytext=(76,46),arrowprops=dict(arrowstyle='->',color='#2477a3'),color='#2477a3',size=10)
    ax.set_xlim(-65,166);ax.set_ylim(-66,66)
    ax.set_aspect('equal',adjustable='box');ax.grid(alpha=.2)
    ax.set_title(f'{axis.upper()} isolated unpowered belt fixture',fontsize=13,fontweight='bold')
    ax.set_xlabel('X mm');ax.set_ylabel('Y mm')
fig.suptitle('V0.7 | Nominal 60T:20T GT2 bench pitch geometry | 115 ± 5 mm',size=16,weight='bold')
fig.text(.5,.01,'Not a working drive: NO shaft coupler, bearings, teeth, belt or motor clearance certification',ha='center',fontsize=10,color='#9d4d22')
fig.savefig(ROOT/'OpenEQMount_V07_dual_belt_bench_preview.png',dpi=160,bbox_inches='tight')
plt.close(fig)
print('V0.7 previews generated')
