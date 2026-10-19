# OpenEQMount V0.6 — Independent metal latitude locking and hard-stop bench CAD

**Revision:** V0.6, **safety status:** `prototype_unqualified_Gate_A_only`.

> **NOT FOR FIELD USE OR CAMERA LOADS.** STEP files are dimensional proposals, not released fabrication drawings. This version does not include a qualified primary latitude lock, independent fall-arrest, tested fastener stack, load analysis or a verified RA stator/tripod interface.

## Scope

The previous V0.5 wedge established a geometric north-facing polar altitude range of 25°–45°, with ±5° azimuth adjustment. It lacked a separate locking clamp, positive latitude limits, and a confirmed tripod attachment. V0.6 adds **independent paths in reference geometry**, both made exclusively of metal:

1. Two 6 mm reference metal sector plates fixed to the **metal azimuth deck** by two Ø6.6 mm through-holes per side, x = −12/+15 mm, y = ±63 mm; fastener grade, clamp stack, slot edge distance and contact stresses remain unqualified.
2. Two metal lugs bolted to existing **upper deck x = 45, y = ±45 mm provisional holes**. Separate transverse M8 clamping pin and M6 mechanical travel-stop pin positions are defined.
3. A long **Ø9.0 mm locking slot** and a different **Ø7.0 mm stop-pin slot**, each swept on an exact circular arc around the Y-axis hinge center x = −61, z = 29 mm. End-stop function is geometric **only if pins are independently retained**; no retention design has been qualified.
4. Replaceable **METAL tripod plates**, Ø146 × 6 mm and three Ø6.6 holes at PCD124 on angular pattern 30°,150°,270°; center-hole options Ø10.5 mm (M10 clearance candidate) and Ø10.0 mm (3/8-inch clearance candidate). Neither implies compatibility with a real tripod. Only ONE adapter option may be installed.
5. Four **non-load-bearing FDM** pieces: two loose slot/bolt guards, one clearance-gauge coupon and one unqualified-status tag. They cannot restrain motion, support payload or hold preloads.

### Reference interface table (millimetres)

| Mechanical interface | Definition | Confirmation still required |
|---|---|---|
| RA stator connection | Unchanged V0.5 top deck provisional M6 pitch | OEM-specific stator flange drawing and RA axis bearing loads |
| Lock-sector metal plate | t=6 mm; y=±63 mm | Real alloy, yield, stress, fastener edge distance |
| Deck fastening | 2×Ø6.6 per side, x−12/+15, y±63 | Tool access, washer bearing, bolt engagement, preload & vibration |
| Upper lug attachment | x45, y±45 via Ø6.6 in V0.5 top metal deck | Bolt countersink and physical access / clamp fit |
| M8 clamp-slot | r = √(92² + 13²) ≈ 92.91, nominal Ø9 slot | Shoulder diameter, clamping washers, friction, creep, torque |
| M6 independent stop-slot | r = √(78² + 13²) ≈ 79.08, Ø7 slot | Positive retention, end-stop loads, energy dissipation |
| Side-lug nominal clearance | ≥ 2 mm in nominal 35° assembly | Actual washers, spacer stack and tolerances |
| Tripod adapter | Ø146 × 6, candidate center Ø10.5 / Ø10.0 | Actual tripod stud, central clamping, base anti-rotation |
| Longitude/latitude | Generic wedge; altitude 25–45° | Range cannot be confirmed until hinge/bolt stack assembled |

**Kinematics:** a local upper-deck point `(x,0,z)` describes a circle about `(-61,0,29)` as the upper plate rotates about Y by `-(90°−latitude)`. Both slots are built from that same hinge reference, *not* an approximated segmented linear slot. CAD numerical tests check open clearance at five latitudes and hard metal interference at overtravel angles.

### Load-path and DfAM decisions

- Latitude torque: upper **metal** deck → upper **metal** lugs → clamping fastener → **metal** lock-sector plates → **metal** deck → **metal** tripod adapter. Printed guards do not contact fastener preloads.
- Dedicated **metal** M6 stop pins use separate tracks so loosening the M8 clamp does not remove the slot geometry. Neither independent **pin retention** nor safe arrest has been proven. Wedge must remain unloaded.
- Fastener washer bearing area and bolt length must be calculated and measured before any mechanical demonstration.
- All printed STL meshes are flat on XY at Z=0 with DfAM metadata. Nonstructural trial PETG only. Their light planar forms are intended to require minimal supports; manual slicer review remains mandatory.
- No metal-designated STEP part may be treated as a printable structural STL; the CAD gate rejects any corresponding metal STL.

### Unresolved engineering tasks (do not close until evidence exists)

1. **Tripod interface:** select exact tripod brand, stud and anti-rotation geometry; check clamped metal stack and choose ONE adapter.
2. **Latitudinal locking:** choose locking stud, washers, steel backing plates, clamp torque, proof-load and vibration loosening test; quantify required torque under all scope conditions.
3. **Positive stops & independent fall arrest:** select retained M6 shoulder pins, separate independent retention system, check stop energy/stresses and possible user misassembly.
4. **Geometric mate:** cross-section and tool-clearance review with real bearings and OEM reducer housing. Never couple the stationary wedge to a **rotating** RA output flange.
5. **Full DfAM B/C acceptance:** slicer, calibrated hole coupons, printed fit tests, temperature/humidity aging, metal-plate fatigue, torque and controlled no-payload failure trials.
6. **Safety margin:** all 3–5 kg target claims require an explicit calculation with real camera+telephoto center of gravity and signed physical test report.

### Commands

```bash
python -m pip install 'cadquery>=2.5,<3' pytest trimesh
python -m pytest -q tests/test_v06_latitude_lock.py
python hardware/cad/generate_v06.py --latitude 35 --out hardware/cad/v06_generated
python tools/dfam_gate_v06.py --dir hardware/cad/v06_generated --report hardware/cad/v06_generated/dfam-gate-report.json
```

Automated Gate A is **not** a certification of mechanical safety. The assembly STEP uses one tripod insert (M10 reference); the optional alternative is separately exported and not assembled simultaneously.
