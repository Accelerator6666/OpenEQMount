# OpenEQMount V0.2 — Editable layout CAD

**THIS IS NOT A MANUFACTURING RELEASE.** The generated STEP and STL show external envelope concepts only. Real gearbox shaft and attachment geometry, latitude hinge, azimuth fine adjustment, belt path, fastener design, electrical routing, mechanical limits, collision testing, finite-element load checking and camera clamp are *not modeled/validated*. Gearbox envelopes are geometrically superposed with rings, not machined fitted units.

Source: `params.py`, `generate_v02.py` (CadQuery ≥2.5). Default fixed-wedge polar altitude is `35°`; the CAD script can rebuild another angle in **25–60°**. This angle is *not mechanically adjustable* in V0.2. Official reducers drawings must be obtained before machining: https://www.harmonicdrive.net/downloads/pdf-drawings/csf-gear-units

```bash
pip install 'cadquery>=2.5,<3'
python hardware/cad/generate_v02.py --latitude 35 --out hardware/cad/generated
```

Optional preview (requires VTK and X display / `xvfb-run`):

```bash
pip install vtk
xvfb-run -a python tools/render_cad_preview.py
```

- `generated/OpenEQMount_V02_assembly.step`: separate conceptual bodies (use FreeCAD or Fusion 360 to inspect).
- `generated/{part}.step`: individual bodies with placeholder interfaces.
- `generated/{part}.stl`: **legacy concept meshes removed from default generator / released repository**, as they are not DfAM-controlled printable parts.
- `generated/manifest.json`: all modeled elements and approximate bounding boxes.
- `generated/OpenEQMount_V02_{iso,side,front}.png`: scene previews.

See [mechanical-v02.md](../../docs/mechanical-v02.md) for actual load assumptions and release-to-production gates.

### V0.3 FDM reducer interfaces

See `generate_v03.py` and `../../docs/mechanical-v03-3dprint.md`.

```bash
python hardware/cad/generate_v03.py --out hardware/cad/v03_generated
```

Generated STEP and STL are geometrically checked *bench-fit prototypes*, not
rated mechanical components. Reducer rear M4 threaded-hole angular phase is
provisional and must be checked against purchased OEM hardware.

### Mandatory DfAM gate for V0.3+

Every printable part must follow [`docs/dfam-design-standard.md`](../../docs/dfam-design-standard.md) and have a complete per-part record in the generated manifest. STL output is print-plane normalized; STEP remains assembly-positioned.

```bash
python -m pip install 'cadquery>=2.5,<3' pytest trimesh
python hardware/cad/generate_v03.py --out hardware/cad/v03_generated
python tools/dfam_gate.py --report hardware/cad/v03_generated/dfam-gate-report.json
```

The automated **digital Gate A** checks watertight single-body STL meshes, metadata, file inventory and 220 mm bed size; this does not demonstrate absence of supports, field durability or payload safety. Each design requires human slicer/fit **Gate B** and mechanical **Gate C** before use.


### V0.4 DfAM metal-reinforced RA/DEC frame
Run `python hardware/cad/generate_v04.py --out hardware/cad/v04_generated`, then `python tools/dfam_gate_v04.py --dir hardware/cad/v04_generated --report hardware/cad/v04_generated/dfam-gate-report.json`. The 5 printable prototypes are nonstructural. Metal STEP proposals are not cutting-ready engineering drawings. See [V0.4 mechanical note](../../docs/mechanical-v04-frame.md). GitHub Action `cad-v04.yml` regenerates these files on main.
