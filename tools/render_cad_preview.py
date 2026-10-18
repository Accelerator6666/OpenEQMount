#!/usr/bin/env python3
"""Render conceptual CAD preview. Requires cadquery + vtk + X server/Xvfb."""
import sys
from pathlib import Path
import vtk
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
from generate_v02 import generate,COLORS
from params import MountParams


def actor_from_cq(shape, color):
    pts,tris=shape.val().tessellate(0.7,0.2)
    points=vtk.vtkPoints()
    for p in pts: points.InsertNextPoint(p.x,p.y,p.z)
    cells=vtk.vtkCellArray()
    for t in tris:
        tri=vtk.vtkTriangle()
        for n,i in enumerate(t): tri.GetPointIds().SetId(n,i)
        cells.InsertNextCell(tri)
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    norm=vtk.vtkPolyDataNormals();norm.SetInputData(poly);norm.ConsistencyOn();norm.AutoOrientNormalsOn();norm.SplittingOff();norm.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(norm.GetOutputPort())
    actor=vtk.vtkActor();actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color.toTuple()[:3]);actor.GetProperty().SetAmbient(0.13)
    actor.GetProperty().SetDiffuse(0.8);actor.GetProperty().SetSpecular(0.25)
    actor.GetProperty().SetSpecularPower(22)
    return actor


def render(path,view='iso',latitude=35):
    scene=vtk.vtkRenderer();scene.SetBackground(0.965,0.977,0.985)
    scene.SetBackground2(0.81,0.86,0.91);scene.GradientBackgroundOn()
    for name, part in generate(MountParams(latitude_deg=latitude)).items():
        scene.AddActor(actor_from_cq(part,COLORS[name]))
    window=vtk.vtkRenderWindow();window.SetSize(1540,1120);window.OffScreenRenderingOn();window.AddRenderer(scene)
    camera=scene.GetActiveCamera()
    if view=='iso':
        camera.SetPosition(340,-500,380)
        camera.SetFocalPoint(0,0,132)
        camera.SetViewUp(0,0,1)
    elif view=='side':
        camera.SetPosition(400,0,170)
        camera.SetFocalPoint(0,0,130)
        camera.SetViewUp(0,0,1)
    elif view=='front':
        camera.SetPosition(0,-480,230)
        camera.SetFocalPoint(0,0,115)
        camera.SetViewUp(0,0,1)
    scene.ResetCameraClippingRange()
    scene.GetActiveCamera().ParallelProjectionOn()
    camera.SetParallelScale(195 if view=='iso' else 180)
    banner=vtk.vtkTextActor();banner.SetInput('OpenEQMount  |  V0.2  CONCEPT LAYOUT');banner.SetPosition(55,1055)
    banner.GetTextProperty().SetFontSize(28);banner.GetTextProperty().SetBold(True);banner.GetTextProperty().SetColor(0.13,0.21,0.27)
    scene.AddActor2D(banner)
    sub=vtk.vtkTextActor();sub.SetInput(f'RA CSF-17-100  /  DEC CSF-14-100     |     fixed wedge: {latitude} deg  |  NOT manufacturing-ready')
    sub.SetPosition(55,1012);sub.GetTextProperty().SetFontSize(19);sub.GetTextProperty().SetColor(0.26,0.34,0.38)
    scene.AddActor2D(sub)
    note=vtk.vtkTextActor();note.SetInput('Gearboxes + motors = geometric envelopes. Mount interfaces, belt path and clearance are TBD.')
    note.SetPosition(55,50);note.GetTextProperty().SetFontSize(17);note.GetTextProperty().SetColor(0.30,0.37,0.43)
    scene.AddActor2D(note)
    window.Render()
    image=vtk.vtkWindowToImageFilter();image.SetInput(window);image.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(path));writer.SetInputConnection(image.GetOutputPort());writer.Write()
    window.Finalize()
    print(path)

if __name__=='__main__':
    output=ROOT/'hardware/cad/generated'
    for v in ('iso','side','front'):
        render(output/f'OpenEQMount_V02_{v}.png',v)
