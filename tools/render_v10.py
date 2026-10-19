#!/usr/bin/env python3
"""Deterministic reference rendering of V1.0 ROT bench source, not qualified drawings."""
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'/'cad'))
import generate_v10_rotator_bench as v

out=Path(__file__).resolve().parents[1]/'hardware'/'cad'/'v10_generated'
out.mkdir(parents=True,exist_ok=True)
fig=plt.figure(figsize=(11.8,8.3),facecolor='#f6f8fb')
ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
colors=['#9cb0be','#527eaf','#a8b1b9','#be8561','#71879a','#3c719e','#dbad60','#d9ac60']
for (name,sh),c in zip(v.metal_parts().items(),colors):
    verts,faces=sh.val().tessellate(2.4,.55)
    pts=[(p.x,p.y,p.z) for p in verts]
    polys=[[pts[q] for q in face] for face in faces]
    ax.add_collection3d(Poly3DCollection(polys,facecolor=c,linewidth=.10,edgecolor='#20394d',alpha=.78))
# Preview gauges as an exploded reference, separate from hardware.
scale=v.loose_print_parts()['v10_NONLOAD_ROT_INDEX_BEZEL_PRINT_FLAT'].translate((0,0,74))
verts,faces=scale.val().tessellate(3.5,.6)
pts=[(p.x,p.y,p.z) for p in verts]
ax.add_collection3d(Poly3DCollection([[pts[q] for q in f] for f in faces],facecolor='#2b9c9a',linewidth=.05,edgecolor='#1d676b',alpha=.7))
ax.view_init(elev=24,azim=-60)
ax.set_xlim(-83,156);ax.set_ylim(-90,90);ax.set_zlim(-32,88)
ax.set_box_aspect((1.4,1.1,.9))
ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)');ax.set_zlabel('optical +Z (mm)')
ax.set_title('OpenEQMount V1.0 | Camera Rotator Metal Bearing Bench',fontweight='bold',pad=18)
fig.text(.5,.035,'NOT load rated | DEC saddle/camera coupler missing | FDM only non-load gauges',ha='center',size=10,color='#a34427')
fig.savefig(out/'OpenEQMount_V10_rotator_bench_preview.png',dpi=148,bbox_inches='tight')
plt.close(fig)
print('Rendered V1.0 bench preview')
