# OpenEQMount V1.7 — DEC–ROT NSK 7008AWDB reference integration (Gate A only)

**Engineering status:** `prototype_unqualified`; **no live camera, no payload, no powered motion, no machining release.** Digital appearance does not qualify the 3–5 kg aspirational payload rating. Independent ASTM/ISO-style certification is **not** claimed.

## Scope and interface design

V1.7 mounts the **V1.6 external-outline NSK 7008AWDB matched DB cartridge** in the **V1.1 DEC-to-ROT metal bridge coordinate system** and regenerates a 52-body complete RA/DEC/ROT reference STEP. The V1.4 6808 bearings, 6808 housing, obsolete output rotor, conjectural stop blocks, old pseudo-locknut and outdated camera plate have been **removed**, not overlaid. The RA and DEC reducer/hardware envelopes, V0.5–0.7 polar mount and V1.1 candidate bridge remain unqualified.

* Fixed bridge: nominal `PCD110`, six Ø5.5 reference clearance holes. This is **not** an OEM bolt standard.
* Cartridge: nominal `PCD80`, six Ø4.5 reference clearance holes matching the V1.6 housing model, not an OEM-certified interface.
* Transfer plate: **Ø136 OD × Ø64 ID × 8 mm thick** candidate machined metal annulus; all 12 holes; nominal minimum radial ligament **5.75 mm** (geometry only). No fastener strength, edge-distance design standard, tensile fatigue, bending or thermal validation.
* Local position: bridge top is ROT local `z=0`; transfer plate z=0..8; lower cartridge end cap z=8..13; paired bearing housing z=13..43, with 7008 pair occupying z=13..43. This is an **exploded positional stack**, not a verified positive bolted assembly. The proposed bolt heads/nuts would need real tool access and plate clamping calculations.
* 7008AWDB: each external ring 40×68×15 mm; paired total physical width 30 mm. **NSK a0=46.2 mm is the nominal load-centre distance, not two bearings physically spaced 46.2 mm apart.** Exact 7008AWDB CN paired set, preload class, raceway/shoulder face geometry, tolerances and appropriate anti-loosening remain pending.
* ROT is nominally optical axis local +Z and remains perpendicular to DEC local +X; the complete assembly transforms these axes by the same DEC and wedge angles.

## Explicit unresolved mechanical safety defects

1. **Camera interface is floating.** The V1.6 camera interface blank touches the spindle datum only in a reference plane; no OEM mating holes, metal keyed torque transfer, clamp strength or certified spindle axial clamp exists. Rotating the blank for rendering **does not mean it is mechanically driven**.
2. **Positive axial retention and preload not engineered.** The current nut model has no specified thread/torque/locking tab; actual matched-bearing preload and outer-ring retainer fastening have not been proven.
3. **No independent fall arrest.** No camera/lens collar selected; there is no real metal tether, independent anchors at both ends, verified rated assembly, fall travel or 3-axis cable sweep test.
4. **No qualified limit/stop or powered operation.** V1.2 nominal stop geometry must be re-engineered for the new bearing stack and full ±150°/±160° motion with hard-limit and cable clearance under all RA/DEC poses.
5. **OEM DEC output flange unverified.** V1.1 candidate `PCD23` and gear unit housing datum lack actual part-specific clocking, tolerances, fastener engagement and reduction ratio/torque sign-off.
6. **No bearing structural model.** Joint stiffness, cantilever, contact forces, tilting angle, fatigue, static safety margin, ring clamp, hub stresses, looseness and thermal operation are pending.

## Windows FreeCAD opening

Open `hardware/cad/v17_generated/OpenEQMount_V17_THREE_AXIS_7008AWDB_INTERFACE_STUDY_UNQUALIFIED.step` for all three axes (52 solids). For easier inspection use `OpenEQMount_V17_DEC_ROT_7008_AWDB_INTERFACE_SUBASSEMBLY_UNQUALIFIED.step` (10 solids) and `v17_METAL_PCD110_TO_PCD80_BRIDGE_ADAPTER_UNQUALIFIED.step` (1 solid). FreeCAD STEP files import CAD geometry; parametric design remains in `hardware/cad/generate_v17_integrated_7008.py`.

## Reproducible digital checks

```bash
python -m pip install 'cadquery>=2.5,<3' pytest trimesh matplotlib
python -m pytest -q tests/test_v17_7008_mated_integration.py
python hardware/cad/generate_v17_integrated_7008.py --out hardware/cad/v17_generated
python tools/dfam_gate_v17.py --dir hardware/cad/v17_generated --report hardware/cad/v17_generated/dfam-gate-report.json
python tools/render_v17.py
```

- **Gate A**: CAD topology, STEP reimport, nominal hole dimensions and nonstructural mesh watertightness.
- **Gate B**: proper PETG fit-gauge slicer/orientation and actual hole measurements/real OEM parts **PENDING**.
- **Gate C**: calibrated bearing preload and shaft fits, qualified metal fall arrest, static/dynamic torque and load, full 3-axis collision/limit/cable tests, thermal/lifetime and power-off safety **PENDING**.

## Next design targets (V1.8)

Retrieve measured actual DEC reducer output drawing and the full NSK matched-set fitting instructions; select metal camera lens-collar attachment and independent-rated fall arrest; resolve V1.6 spindle-to-output blank positive torque/axial coupling; then perform stress/deflection and physical Gates B/C. **Do not select manufacturing threads or torque values by guesswork.**

Reference: [NSK 7008AWDB catalogue](https://www.nsk.com/engineering/products/bearings/ball-bearings/angular-contact-ball-bearings/matched-angular-contact-ball-bearings/7008awdb-apn.html) · [V1.6 research](mechanical-v16-7008awdb-db-cartridge.md) · [Open V1.1+ safety backlog, Issue #4](https://github.com/Accelerator6666/OpenEQMount/issues/4).
