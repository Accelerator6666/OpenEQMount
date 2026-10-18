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
- `generated/{part}.stl`: **shape prototypes only** (do not rely on as load-bearing components).
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
