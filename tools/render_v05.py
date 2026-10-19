#!/usr/bin/env python3
"""Actual V0.5 CAD solids preview. Illustrative only; no certified load capacity."""
from pathlib import Path
import sys
import vtk
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
import generate_v05 as v


def actor(shape,rgb,opacity=1.0):
    verts,faces=shape.val().tessellate(.52,.28)
    points=vtk.vtkPoints()
    for pt in verts:points.InsertNextPoint(pt.x,pt.y,pt.z)
    cells=vtk.vtkCellArray()
    for tri in faces:
        face=vtk.vtkTriangle()
        for j,k in enumerate(tri):face.GetPointIds().SetId(j,k)
        cells.InsertNextCell(face)
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    n=vtk.vtkPolyDataNormals();n.SetInputData(poly);n.ConsistencyOn();n.AutoOrientNormalsOn()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(n.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mapper)
    prop=a.GetProperty();prop.SetColor(*rgb);prop.SetAmbient(.22);prop.SetDiffuse(.7);prop.SetSpecular(.24);prop.SetSpecularPower(16)
    prop.SetOpacity(opacity)
    return a


def t(scene,label,x,y,size=24,color=(.18,.23,.30)):
    o=vtk.vtkTextActor();o.SetInput(label);o.SetPosition(x,y)
    o.GetTextProperty().SetFontSize(size);o.GetTextProperty().SetBold(True)
    o.GetTextProperty().SetColor(*color);scene.AddActor2D(o)


def render(outfile,prints=False):
    ren=vtk.vtkRenderer();ren.GradientBackgroundOn();ren.SetBackground(.98,.985,1);ren.SetBackground2(.84,.88,.92)
    if not prints:
        for name,part in v.metals(35).items():
            if 'tripod' in name:color=(.36,.44,.51)
            elif 'DECK' in name or 'INTERFACE' in name:color=(.59,.67,.73)
            elif 'JACK' in name or 'PIN' in name or 'screw' in name:color=(.93,.60,.22)
            else:color=(.78,.80,.83)
            ren.AddActor(actor(part,color))
        camera=ren.GetActiveCamera();camera.SetPosition(325,-340,250);camera.SetFocalPoint(0,0,50)
        camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();camera.SetParallelScale(160)
        t(ren,'OpenEQMount  V0.5  |  ADJUSTABLE POLAR WEDGE',35,865,28)
        t(ren,'25-45 deg LATITUDE  /  +/-5 deg AZIMUTH  /  METAL LOAD PATH CONCEPT',35,830,16)
    else:
        centers=[(-155,80),(15,80),(175,80),(-110,-95),(100,-95)]
        for (name,part),(x,y) in zip(v.prints().items(),centers):
            a=actor(part,(.13,.46,.68));a.SetPosition(x,y,0);ren.AddActor(a)
        camera=ren.GetActiveCamera();camera.SetPosition(0,0,610);camera.SetFocalPoint(5,0,0)
        camera.SetViewUp(0,1,0);camera.ParallelProjectionOn();camera.SetParallelScale(300)
        t(ren,'V0.5   DfAM  /  5 NONSTRUCTURAL PRINTED PARTS',35,865,27)
        t(ren,'Flat bed-oriented covers, reference scales and clearance coupon',35,828,18)
    t(ren,'GATE A ONLY  /  NOT FOR CAMERA PAYLOAD  /  LATCH AND FAIL-SAFE NOT DESIGNED',35,43,19,(.71,.21,.17))
    win=vtk.vtkRenderWindow();win.SetSize(1500,920);win.SetOffScreenRendering(1);win.AddRenderer(ren)
    ren.ResetCameraClippingRange();win.Render()
    out=vtk.vtkWindowToImageFilter();out.SetInput(win);out.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(outfile));writer.SetInputConnection(out.GetOutputPort());writer.Write()
    win.Finalize()
    print('rendered',outfile)

if __name__=='__main__':
    dst=ROOT/'hardware/cad/v05_generated'
    dst.mkdir(exist_ok=True,parents=True)
    render(dst/'OpenEQMount_V05_wedge_assembly.png')
    render(dst/'OpenEQMount_V05_printable_set.png',True)
