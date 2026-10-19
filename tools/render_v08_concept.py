#!/usr/bin/env python3
"""VTK rendered engineering view of combined V0.8 concept assembly."""
import sys
from pathlib import Path
import vtk
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
import generate_v08_concept_assembly as mod

def actor(shape,rgb,opacity=1.):
    vs,fs=shape.val().tessellate(1.35,.46)
    points=vtk.vtkPoints()
    for pt in vs:points.InsertNextPoint(pt.x,pt.y,pt.z)
    cells=vtk.vtkCellArray()
    for tri in fs:
        tr=vtk.vtkTriangle()
        for j,k in enumerate(tri):tr.GetPointIds().SetId(j,k)
        cells.InsertNextCell(tr)
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    n=vtk.vtkPolyDataNormals();n.SetInputData(poly);n.ConsistencyOn();n.AutoOrientNormalsOn()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(n.GetOutputPort())
    act=vtk.vtkActor();act.SetMapper(mapper)
    prop=act.GetProperty();prop.SetColor(*rgb);prop.SetAmbient(.26);prop.SetDiffuse(.68);prop.SetSpecular(.21);prop.SetSpecularPower(24);prop.SetOpacity(opacity)
    return act

def text(ren,st,x,y,size,color=(.13,.20,.28)):
    o=vtk.vtkTextActor();o.SetInput(st);o.SetPosition(x,y)
    o.GetTextProperty().SetFontSize(size);o.GetTextProperty().SetBold(True);o.GetTextProperty().SetColor(*color)
    ren.AddActor2D(o)

ren=vtk.vtkRenderer();ren.GradientBackgroundOn();ren.SetBackground(.98,.985,1);ren.SetBackground2(.86,.9,.94)
colors={'metal_wedge':(.68,.72,.76),'metal_base':(.37,.45,.53),'metal_lock':(.31,.56,.7),
 'metal_ra_stator':(.34,.62,.77),'metal_ra_dec_frame':(.77,.79,.82),
 'reference_gearbox':(.94,.61,.27),'printed_nonstructural':(.14,.43,.67)}
for item in mod.make_components(35.):
    ren.AddActor(actor(item['shape'],colors[item['category']],.4 if item['category']=='reference_gearbox' else 1))
cam=ren.GetActiveCamera();cam.SetPosition(425,-490,420);cam.SetFocalPoint(-48,0,180)
cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(270)
text(ren,'OpenEQMount  V0.8  |  COMBINED ASSEMBLY CONCEPT',35,1010,28)
text(ren,'V0.5-0.7 polar wedge + RA stator  /  V0.4 RA-DEC orthogonal frame',35,972,19)
text(ren,'REFERENCE ONLY  /  UNVERIFIED FITS  /  NOT SAFE FOR CAMERA PAYLOAD',35,53,21,(.75,.24,.18))
win=vtk.vtkRenderWindow();win.SetSize(1600,1080);win.SetOffScreenRendering(1);win.AddRenderer(ren)
ren.ResetCameraClippingRange();win.Render()
f=vtk.vtkWindowToImageFilter();f.SetInput(win);f.Update()
out=ROOT/'hardware'/'cad'/'v08_generated'/'OpenEQMount_V08_WHOLE_MOUNT_CONCEPT.png'
w=vtk.vtkPNGWriter();w.SetFileName(str(out));w.SetInputConnection(f.GetOutputPort());w.Write()
win.Finalize();print('rendered',out)
