#!/usr/bin/env python3
"""V1.7 digital reference images from generated CadQuery shapes (not photographs)."""
from pathlib import Path
import sys,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
import generate_v17_integrated_7008 as v
out=ROOT/'hardware/cad/v17_generated';out.mkdir(parents=True,exist_ok=True)

fig=plt.figure(figsize=(12,8),facecolor='#f6f8fc')
ax=fig.add_subplot(111,projection='3d')
raw=[{'shape':v.adapter_local(),'role':'adapter'}]+[{'shape':p['shape'].translate((0,0,v.CARTRIDGE_Z_ABOVE_BRIDGE)),'role':p['role']} for p in v.v16.cartridge_parts()]
colors={'adapter':'#55ad83','stator':'#4c85b8','cap':'#8cb7a3','bearing':'#ecbb60','shaft':'#a1d2df','fastener':'#dc855d','guard':'#bba2d5'}
for p in raw:
    verts,faces=p['shape'].val().tessellate(1.3,.6)
    pts=[(q.x,q.y,q.z) for q in verts]
    polys=[[pts[j] for j in f] for f in faces]
    role=p['role']
    alpha=.32 if role=='stator' else (.60 if role=='guard' else .92)
    ax.add_collection3d(Poly3DCollection(polys,facecolor=colors[role],edgecolor='#25384d',linewidth=.05,alpha=alpha))
ax.set_box_aspect((1,1,.72));ax.set_xlim(-71,71);ax.set_ylim(-71,71);ax.set_zlim(-5,85)
ax.set_xlabel('Local X (mm)');ax.set_ylabel('Local Y (mm)');ax.set_zlabel('ROT Z (mm)')
ax.view_init(elev=24,azim=-58)
ax.set_title('OpenEQMount V1.7 | Metal transition plate + NSK 7008AWDB cartridge',fontsize=15,pad=22,fontweight='bold')
fig.text(.5,.038,'DEC bridge PCD110  →  provisional cartridge PCD80  |  no camera coupling / no load / no power',ha='center',color='#a64d32',fontsize=11)
fig.savefig(out/'OpenEQMount_V17_DEC_ROT_interface_preview.png',dpi=160,bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(10.4,9.2),facecolor='#f6f8fc');ax.set_facecolor('#f9fbfe')
outer=Circle((0,0),v.PLATE_OD/2,facecolor='#bcd9c9',edgecolor='#3d8065',lw=2)
inner=Circle((0,0),v.PLATE_BORE/2,facecolor='#f9fbfe',edgecolor='#2e6f58',lw=1.5)
ax.add_patch(outer);ax.add_patch(inner)
for r,d,col in ((v.BRIDGE_PCD/2,5.5,'#316eb3'),(v.CARTRIDGE_PCD/2,4.5,'#c76642')):
    ax.add_patch(Circle((0,0),r,fill=False,linestyle='--',edgecolor=col,lw=1.5))
    for j in range(6):
        a=j*math.pi/3
        x,y=r*math.cos(a),r*math.sin(a)
        ax.add_patch(Circle((x,y),d/2,facecolor='#f9fbfe',edgecolor=col,lw=2))
ax.plot([-68,68],[0,0],lw=.5,c='#8fa2b2',ls=':');ax.plot([0,0],[-68,68],lw=.5,c='#8fa2b2',ls=':')
ax.annotate('Outer 6× Ø5.5 on PCD110',xy=(55,0),xytext=(74,52),fontsize=11,arrowprops=dict(arrowstyle='->',color='#316eb3'),color='#316eb3')
ax.annotate('Inner 6× Ø4.5 on PCD80',xy=(40,0),xytext=(74,35),fontsize=11,arrowprops=dict(arrowstyle='->',color='#c76642'),color='#c76642')
ax.annotate('Ø64 open bore',xy=(30,0),xytext=(74,-36),fontsize=11,arrowprops=dict(arrowstyle='->'),color='#243748')
ax.set_xlim(-80,165);ax.set_ylim(-83,84);ax.set_aspect('equal');ax.grid(alpha=.15)
ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)')
ax.set_title('V1.7 Candidate machined-metal transfer plate — NOT fabrication drawing',fontsize=14,fontweight='bold')
fig.text(.5,.038,'Nominal only | 8 mm plate | proposed bolt spacing | min nominal radial ligament 5.75 mm (nominal) | Gate B/C PENDING',ha='center',color='#ae5338',fontsize=10)
fig.savefig(out/'OpenEQMount_V17_PCD110_80_adapter_plan.png',dpi=160,bbox_inches='tight');plt.close(fig)
print('V1.7 CAD preview generated.')
