#!/usr/bin/env python3
"""Render V1.8 CadQuery shaft/flange fastener concept, not manufacturing release."""
import sys,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
import generate_v18_positive_drive as v
out=ROOT/'hardware'/'cad'/'v18_generated';out.mkdir(parents=True,exist_ok=True)

fig=plt.figure(figsize=(12.2,8.4),facecolor='#f7f8fb')
ax=fig.add_subplot(111,projection='3d')
palette={'spindle':'#6ca9cc','camera':'#6bb68d','dowel':'#edac50','bolt':'#c37158','nut':'#af796d'}
for p in v.joint_parts():
    pts,fac=p['shape'].val().tessellate(1.8,.6)
    xyz=[(t.x,t.y,t.z) for t in pts]
    tris=[[xyz[j] for j in f] for f in fac]
    alpha=.40 if p['role']=='camera' else (.85 if p['role']=='spindle' else .95)
    ax.add_collection3d(Poly3DCollection(tris,facecolor=palette[p['role']],edgecolor='#415568',linewidth=.055,alpha=alpha))
ax.set(xlim=(-66,66),ylim=(-66,66),zlim=(-12,74),xlabel='X mm',ylabel='Y mm',zlabel='Local ROT Z mm')
ax.set_box_aspect((1,1,.7));ax.view_init(elev=27,azim=-58)
ax.set_title('OpenEQMount V1.8 | one-piece hub + pinned camera interface',fontsize=16,pad=20)
fig.text(.5,.033,'Metal hub: 6x M6 through-bolts, 2x Ø6 alignment/shear dowels (FIT UNVERIFIED) | NO load / power / independent tether',ha='center',color='#9f4a31',fontsize=10)
fig.savefig(out/'OpenEQMount_V18_shaft_camera_joint_preview.png',dpi=160,bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(9.8,8.5),facecolor='#f7f8fb');ax.set_aspect('equal');ax.set_facecolor('#fcfcff')
for r,c,ls in [(61,'#50aa77','-'),(55,'#2c87b5','--'),(18,'#b4bec8','-'),(15,'#526777','--')]:
    ax.add_patch(Circle((0,0),r,fill=False,edgecolor=c,linewidth=2,linestyle=ls))
for x,y in v.centers(6,90,30):
    ax.add_patch(Circle((x,y),v.BOLT_CLEARANCE_D/2,facecolor='#c97254',edgecolor='#723f31',lw=1))
for x,y in v.centers(2,68):
    ax.add_patch(Circle((x,y),v.DOWEL_HOLE_D/2,facecolor='#f2b554',edgecolor='#a36b1e',lw=1.3))
ax.set(xlim=(-80,102),ylim=(-78,76),xlabel='mm',ylabel='mm')
ax.grid(alpha=.17);ax.set_title('V1.8 metal joint plan | 6x Ø6.6 on PCD90; 2x Ø6.2 on PCD68',fontsize=13)
ax.annotate('through-bolt Ø6.6',xy=(39,22),xytext=(62,47),arrowprops=dict(arrowstyle='->',color='#ab6345'),color='#a7563d')
ax.annotate('dowel hole Ø6.2',xy=(34,0),xytext=(58,-35),arrowprops=dict(arrowstyle='->',color='#bb893a'),color='#a77827')
fig.text(.5,.035,'Nominal only. No pin fit / fastener fatigue / preload / CNC tolerance / independent payload catch qualification.',ha='center',fontsize=10,color='#984b32')
fig.savefig(out/'OpenEQMount_V18_joint_PCD_layout.png',dpi=155,bbox_inches='tight');plt.close(fig)
print('V1.8 source-derived engineering previews rendered')
