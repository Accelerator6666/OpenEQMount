#!/usr/bin/env python3
"""CAD surface preview plus precise z/r cross-section from V1.6 parametric source."""
from __future__ import annotations
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
import generate_v16_db7008_cartridge as v

out=ROOT/'hardware/cad/v16_generated'
out.mkdir(parents=True,exist_ok=True)
fig=plt.figure(figsize=(12,8),facecolor='#f5f8fc')
ax=fig.add_subplot(111,projection='3d')
for p in v.cartridge_parts():
    verts,faces=p['shape'].val().tessellate(1.35,.6)
    pts=[(u.x,u.y,u.z) for u in verts]
    polys=[[pts[i] for i in face] for face in faces]
    role=p['role']
    colors={'stator':'#487bb4','cap':'#83a79a','bearing':'#e9b455','shaft':'#98c9db','fastener':'#d67f5b','guard':'#ad96c8'}
    alpha=.22 if role in ('stator','guard') else (.5 if role=='cap' else 1)
    coll=Poly3DCollection(polys,facecolor=colors[role],edgecolor='#27394b',linewidth=.04,alpha=alpha)
    ax.add_collection3d(coll)
ax.set_box_aspect((1,1,.85));ax.set_xlim(-54,54);ax.set_ylim(-54,54);ax.set_zlim(-12,78)
ax.view_init(elev=24,azim=-55);ax.set_xlabel('X mm');ax.set_ylabel('Y mm');ax.set_zlabel('Z mm')
ax.set_title('OpenEQMount V1.6 | NSK 7008AWDB paired DB bearing cartridge',pad=22,fontsize=16,fontweight='bold')
fig.text(.5,.055,'40 x 68 x 30 mm matched DB set | CN clearance, NOT selected preload | NO camera / NO power',ha='center',color='#a94432',fontsize=11)
fig.savefig(out/'OpenEQMount_V16_7008_DB_cartridge_preview.png',dpi=155,bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(12,7),facecolor='#f5f8fc')
ax.set_facecolor('#f9fbff')
def block(r0,r1,z0,z1,fill,text='',xplus=False):
    x=r0 if xplus else -r1
    w=r1-r0
    p=Rectangle((x,z0),w,z1-z0,fc=fill,edgecolor='#30465a',linewidth=1.0,alpha=.88)
    ax.add_patch(p)
    if text and xplus:ax.annotate(text,(r1+1,(z0+z1)/2),fontsize=10,va='center',color='#223449')
# Mirror cross-section about centerline; radially positive x used for annotations.
for side in (False,True):
    block(34.1,45,0,30,'#638cb9','Stator reference bore Ø68.2' if side else '',side)
    block(30,44.5,-5,0,'#8ebbaa','Lower removable metal cap' if side else '',side)
    block(30,44.5,30,35,'#8ebbaa','Upper removable metal cap' if side else '',side)
    block(20,34,0,15,'#e7b65c','7008AWDB ring 1 / 15 mm' if side else '',side)
    block(20,34,15,30,'#e7b65c','7008AWDB ring 2 / 15 mm' if side else '',side)
    block(15,20,-7,40,'#91bfcd','Ø40 hollow metal spindle' if side else '',side)
    block(20,24,-7,0,'#91bfcd','48 mm metal shaft shoulder' if side else '',side)
    block(20.1,26,30,32,'#d9936e','Washer only, no keyed lock' if side else '',side)
    block(20.1,25,32,38,'#d9936e','Locknut envelope; NO THREAD' if side else '',side)
    block(16.5,51,40,45,'#bba7d7','Camera interface stock only' if side else '',side)
ax.axvline(0,c='#51687d',ls='--',lw=1)
ax.plot([0,0],[-8,45],alpha=.0)
ax.annotate('Physical bearing pair: z=0..30 mm',(-46,-13),fontsize=11,color='#233648')
ax.annotate('NSK load centres: -8.1 and +38.1 mm (a0 = 46.2)',(-46,-18),fontsize=10,color='#a94b36')
for z in (-8.1,38.1):ax.axhline(z,xmin=.02,xmax=.42,ls=':',c='#b96043',lw=1)
ax.set_xlim(-55,98);ax.set_ylim(-23,53);ax.set_xlabel('Radial coordinate / section X (mm)');ax.set_ylabel('ROT axis Z (mm)')
ax.set_title('V1.6 | Bearing stack section: representative external boundaries, not a fit/preload drawing',fontsize=14,fontweight='bold',pad=18)
ax.grid(alpha=.12)
fig.text(.5,.035,'NO OEM contact raceway model  |  NO clamp force / shaft tolerance / approved retaining nut  |  Gate A ONLY',ha='center',fontsize=10,color='#a94432')
fig.savefig(out/'OpenEQMount_V16_DB_pair_section.png',dpi=160,bbox_inches='tight');plt.close(fig)
print('V1.6 CAD and bearing-stack preview images rendered')
