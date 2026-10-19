#!/usr/bin/env python3
"""Render REAL V0.6 CadQuery solids through VTK; display only, not load evidence."""
from pathlib import Path
import sys
import vtk
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
import generate_v06 as v


def actor(shape,rgb):
    verts,faces=shape.val().tessellate(.50,.24)
    points=vtk.vtkPoints()
    for p in verts:points.InsertNextPoint(p.x,p.y,p.z)
    cells=vtk.vtkCellArray()
    for tri in faces:
        face=vtk.vtkTriangle()
        for i,k in enumerate(tri):face.GetPointIds().SetId(i,k)
        cells.InsertNextCell(face)
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    n=vtk.vtkPolyDataNormals();n.SetInputData(poly);n.ConsistencyOn();n.AutoOrientNormalsOn()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(n.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mapper)
    prop=a.GetProperty();prop.SetColor(*rgb);prop.SetDiffuse(.72)
    prop.SetAmbient(.2);prop.SetSpecular(.25);prop.SetSpecularPower(17)
    return a


def label(renderer,txt,xy,size,col=(.15,.19,.26)):
    t=vtk.vtkTextActor();t.SetInput(txt);t.SetPosition(*xy)
    t.GetTextProperty().SetFontSize(size)
    t.GetTextProperty().SetBold(True)
    t.GetTextProperty().SetColor(*col)
    renderer.AddActor2D(t)


def render(path,prints=False):
    r=vtk.vtkRenderer();r.GradientBackgroundOn()
    r.SetBackground(.98,.985,1);r.SetBackground2(.82,.87,.93)
    if prints:
        layout=[(-100,55),(-20,55),(-105,-45),(40,-45)]
        for (name,shape),(x,y) in zip(v.printed_parts().items(),layout):
            a=actor(shape,(.13,.41,.64));a.SetPosition(x,y,0);r.AddActor(a)
        cam=r.GetActiveCamera();cam.SetPosition(0,0,500);cam.SetViewUp(0,1,0)
        cam.SetFocalPoint(-20,0,0);cam.ParallelProjectionOn();cam.SetParallelScale(170)
        label(r,'V0.6 | DfAM PRINTABLE NONSTRUCTURAL PARTS',(35,855),28)
        label(r,'2 GUARDS  /  1 FIT GAUGE  /  1 UNQUALIFIED TAG',(35,815),18)
    else:
        original=v.v05.metals(35)
        for name,shape in original.items():
            if 'tripod_anchor_BASE' in name or 'azimuth_slew_DECK' in name:continue
            if 'PIN' in name or 'JACK' in name or 'screw' in name:c=(.83,.62,.26)
            else:c=(.68,.72,.76)
            r.AddActor(actor(shape,c))
        r.AddActor(actor(v.v05.fixed_triad_base(),(.48,.54,.59)))
        for name,shape in v.metal_parts(35).items():
            if 'OPTION' in name:continue
            if 'lock_sector_' in name:c=(.20,.43,.65)
            elif 'upper_lock_lug_' in name:c=(.89,.52,.21)
            elif 'pin_' in name:c=(.82,.27,.19)
            else:c=(.45,.61,.66)
            r.AddActor(actor(shape,c))
        cam=r.GetActiveCamera();cam.SetPosition(350,-385,275);cam.SetFocalPoint(-2,0,63)
        cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(172)
        label(r,'OpenEQMount  V0.6  |  METAL LATITUDE LOCK + STOP',(35,855),28)
        label(r,'Two independent slot/pin pairs   /   25-45 deg trial range',(35,820),18)
    label(r,'GATE A ONLY - DO NOT INSTALL CAMERA - NO VALIDATED FAIL-SAFE',(35,35),17,(.70,.16,.17))
    w=vtk.vtkRenderWindow();w.SetSize(1500,920);w.SetOffScreenRendering(1);w.AddRenderer(r)
    r.ResetCameraClippingRange();w.Render()
    f=vtk.vtkWindowToImageFilter();f.SetInput(w);f.Update()
    out=vtk.vtkPNGWriter();out.SetFileName(str(path));out.SetInputConnection(f.GetOutputPort());out.Write();w.Finalize()
    print('Rendered',path)

if __name__=='__main__':
    output=ROOT/'hardware/cad/v06_generated';output.mkdir(exist_ok=True,parents=True)
    render(output/'OpenEQMount_V06_lock_assembly.png')
    render(output/'OpenEQMount_V06_printable_set.png',True)
