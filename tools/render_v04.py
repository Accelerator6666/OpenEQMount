#!/usr/bin/env python3
"""VTK preview of actual V0.4 CAD solids (not a photograph or load-qualified mount)."""
from pathlib import Path
import sys
import vtk
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware'/'cad'))
import generate_v04 as v


def actor(shape,rgb,opacity=1.0):
    verts,faces=shape.val().tessellate(.55,.24)
    p=vtk.vtkPoints()
    for q in verts:p.InsertNextPoint(q.x,q.y,q.z)
    polys=vtk.vtkCellArray()
    for tri in faces:
        t=vtk.vtkTriangle()
        for j,n in enumerate(tri):t.GetPointIds().SetId(j,n)
        polys.InsertNextCell(t)
    mesh=vtk.vtkPolyData();mesh.SetPoints(p);mesh.SetPolys(polys)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(mesh);normals.ConsistencyOn();normals.AutoOrientNormalsOn()
    m=vtk.vtkPolyDataMapper();m.SetInputConnection(normals.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(m)
    a.GetProperty().SetColor(*rgb);a.GetProperty().SetAmbient(.21);a.GetProperty().SetDiffuse(.7);a.GetProperty().SetSpecular(.19)
    a.GetProperty().SetOpacity(opacity)
    return a


def text(scene,label,x,y,size=24,col=(.17,.22,.29)):
    t=vtk.vtkTextActor();t.SetInput(label);t.SetPosition(x,y)
    t.GetTextProperty().SetBold(True);t.GetTextProperty().SetFontSize(size)
    t.GetTextProperty().SetColor(*col);scene.AddActor2D(t)


def make_render(path,show_print=False):
    w,h=1500,920
    s=vtk.vtkRenderer();s.GradientBackgroundOn();s.SetBackground(.98,.99,1);s.SetBackground2(.83,.88,.91)
    if not show_print:
        for name,part in v.metal_parts().items():
            col=(.58,.63,.67) if 'plate' in name else (.76,.78,.81)
            s.AddActor(actor(part,col))
        for right in [False,True]:
            part=v.in_global_side(v.side_shape(8,True),right,True)
            s.AddActor(actor(part,(.18,.48,.67),.9))
        cam=s.GetActiveCamera();cam.SetPosition(350,-370,300);cam.SetFocalPoint(26,0,90);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(165)
        text(s,'OpenEQMount  /  V0.4  ORTHOGONAL FRAME CAD',35,862,28)
        text(s,'Metal load path concept + printed nonstructural DfAM covers',35,823,18)
    else:
        for name,part in v.printable_parts().items():
            x=-225 if 'cheek_left' in name else (0 if 'cheek_right' in name else 230)
            y=0 if 'cheek_' in name else (0 if 'ra_' in name else (160 if 'dec_' in name else -80))
            a=actor(part,(.14,.46,.66));a.SetPosition(x,y,0);s.AddActor(a)
        cam=s.GetActiveCamera();cam.SetPosition(0,-200,710);cam.SetFocalPoint(40,90,0);cam.SetViewUp(0,1,0);cam.ParallelProjectionOn();cam.SetParallelScale(390)
        text(s,'OpenEQMount V0.4  /  PRINTABLE FLAT-ON-BED PARTS',35,862,26)
        text(s,'2 side covers + RA/DEC drill jigs + M4/M5 calibration coupon',35,823,18)
    text(s,'BENCH FIT ONLY  /  NO QUALIFIED CAMERA PAYLOAD',35,45,23,(.62,.19,.15))
    win=vtk.vtkRenderWindow();win.SetSize(w,h);win.SetOffScreenRendering(1);win.AddRenderer(s)
    s.ResetCameraClippingRange();win.Render()
    snap=vtk.vtkWindowToImageFilter();snap.SetInput(win);snap.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(path));writer.SetInputConnection(snap.GetOutputPort());writer.Write();win.Finalize()
    print(str(path))

if __name__=='__main__':
    dst=ROOT/'hardware/cad/v04_generated'
    dst.mkdir(exist_ok=True,parents=True)
    make_render(dst/'OpenEQMount_V04_assembly.png',False)
    make_render(dst/'OpenEQMount_V04_printable_set.png',True)
