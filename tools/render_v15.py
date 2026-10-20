#!/usr/bin/env python3
"""Render comparative CAD geometry concept diagrams, never a bearing performance claim."""
from pathlib import Path
import json,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.rotator_bearing_tradeoff import CANDIDATES,case
OUT=ROOT/'hardware/cad/v15_generated'
OUT.mkdir(parents=True,exist_ok=True)
fig,axes=plt.subplots(1,3,figsize=(13.4,5.2),sharey=True)
for ax,c in zip(axes,CANDIDATES):
    # Drawing is section through candidate's cylindrical solids in local X/Z.
    ax.set_facecolor('#f7f9fb')
    shell_od=76 if c.key=='6808_pair' else (90 if c.key=='7008_db_pair' else 113)
    housing_rect=Rectangle((-shell_od/2,-3),shell_od,69,facecolor='#708293',alpha=.36,edgecolor='#37506b')
    ax.add_patch(housing_rect)
    ax.add_patch(Rectangle((-c.bore_mm/2,0),c.bore_mm,69,facecolor='#f7f9fb',edgecolor='none'))
    if c.count==2:
        for z in c.theoretical_support_centers_mm:
            zz=z-c.width_mm/2
            ax.add_patch(Rectangle((-c.od_mm/2,zz),c.od_mm,c.width_mm,facecolor='#e4a445',edgecolor='#885824',lw=1.4))
            ax.add_patch(Rectangle((-c.bore_mm/2,zz-.3),c.bore_mm,c.width_mm+.6,facecolor='#f7f9fb',edgecolor='none'))
        for z in c.theoretical_support_centers_mm:
            ax.axhline(z,color='#b65747',ls='--',lw=.75,alpha=.7)
    else:
        ax.add_patch(Rectangle((-47.5,20),95,15,facecolor='#e4a445',edgecolor='#885824',lw=1.5))
        ax.add_patch(Rectangle((-17.5,19.5),35,16,facecolor='#f7f9fb',edgecolor='none'))
    ax.plot([-c.bore_mm/2,-c.bore_mm/2],[0,68],color='#5187af',lw=2)
    ax.plot([c.bore_mm/2,c.bore_mm/2],[0,68],color='#5187af',lw=2)
    ax.set_xlim(-63,63);ax.set_ylim(-18,83);ax.set_aspect('equal')
    ax.set_title(c.product+f'\n{int(c.bore_mm)}×{int(c.od_mm)}×{int(c.width_mm)} mm ×{c.count}',size=10.5,weight='bold')
    ax.set_xlabel('radial section X (mm)',fontsize=9);ax.grid(alpha=.12)
    ax.text(0,-11,'40mm shaft: YES' if c.previous_40mm_spindle_compatible else '40mm shaft: NO / redesign',
            fontsize=9,ha='center',color='#9a4a2e' if not c.previous_40mm_spindle_compatible else '#34516d')
axes[0].set_ylabel('axial Z (mm)',fontsize=9)
fig.suptitle('OpenEQMount V1.5 | Three DETACHED bearing architecture candidates',size=16,weight='bold',y=.99)
fig.text(.5,.012,'Reference boundary dimensions only; bore fits, preload, mounting holes and camera retention NOT engineered.',ha='center',fontsize=9,color='#9e4b29')
fig.savefig(OUT/'OpenEQMount_V15_bearing_architecture_comparison.png',dpi=165,bbox_inches='tight')
plt.close(fig)

res=case(4,80,20)['results']
fig,ax=plt.subplots(figsize=(9.5,5.2))
labels=['2×6808 / 30mm\nold proposal','2×7008 / 50mm\nhypothetical span']
vals=[res[0]['far_support_same_direction_abs_N'],res[1]['far_support_same_direction_abs_N']]
ax.bar(labels,vals,width=.52,edgecolor='#203042',linewidth=.8,color=['#759bc4','#5f9f93'])
ax.set_ylabel('Far simple-support radial reaction (N)')
ax.set_ylim(0,220)
for i,v in enumerate(vals):ax.text(i,v+5,f'{v:.1f} N',ha='center',weight='bold')
ax.text(.5,.92,'RU66 excluded: single cross-roller ring requires OEM moment calculation',
        transform=ax.transAxes,ha='center',color='#9d4d26',fontsize=9)
ax.grid(axis='y',alpha=.2)
ax.set_axisbelow(True)
fig.suptitle('4 kg | CG 80mm from camera mounting face | transverse gravity example',fontsize=13,weight='bold')
fig.text(.5,.018,'Geometry-driven arithmetic only. NOT real bearing contact forces, accuracy, moment limit, fatigue or payload approval.',ha='center',fontsize=9,color='#9e4b29')
fig.savefig(OUT/'OpenEQMount_V15_illustrative_support_reactions.png',dpi=160,bbox_inches='tight')
plt.close(fig)
print('V1.5 static comparison previews rendered')
