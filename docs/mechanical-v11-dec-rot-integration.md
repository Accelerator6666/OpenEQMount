# OpenEQMount V1.1 — DEC-to-ROT metal bridge and one-file FreeCAD three-axis view

> **Gate A: digital geometry only. NOT a structural manufacturing drawing, 3–5 kg payload certification or powered-motion authorization.**

This version answers a specific missing interface from V0.9/V1.0: **the previously floating ROT camera rotator now has a continuously connected metal design-intent load path to the provisional DEC rotating output face**, and a full coloured STEP assembly for Windows FreeCAD.

## Motion axes / coordinates

- Wedge / RA polar angle nominal 35° (V0.5 allowed 25°–45°), RA rotates around the wedge-defined inclined +Z reference frame.
- In the V0.4 rotating-RA subassembly, DEC rotates around **+X** about `(x=158, y=0, z=112)` mm. The DEC rear stator is at x=117; the **rotating DEC output**, not the fixed rear housing, must mount the new saddle at **x=158**.
- ROT is a *different and perpendicular* optical-axis roll around local **+Z**, centred at `(x=194, y=0, z=165)` in that DEC subassembly. It is physically offset from the DEC +X axis by the metal bracket. It is not the DEC axis and not a third alt-az pointing axis.
- View preset: latitude 35°, DEC 25°, ROT 0°. DEC preview input is limited to ±65°; this is **not** certified mechanical operating travel. ROT software preview ±150° is still software-only; **no independently functional mechanical travel stop is installed**.

## Proposed assembly stack (metal primary pathway)

| Stage | Nominal proposed CAD reference | Verification still required |
|---|---|---|
| DEC output-to-bridge hub | Ø68 × 8 mm disk, provisional 6 × Ø4.5 on PCD23 | Real CSF14 output face, OEM angular clock, seating and fastener engagement **unknown** |
| Monolithic metal bridge envelope | Two nominal 6-mm webs joining DEC hub and a 146 × 146 × 6 mm upper metal deck | **CAD is a fused shape only**, not proof of machinable billet or qualified weld, structural strength, or load safety |
| ROT fixed stator-to-deck | Reused V1.0 Ø128 metal bearing housing; six nominal Ø5.5 at PCD110 in deck, Ø72 cable/collar opening | Real shoulder fit, fastening, manufacturing tolerances, screw torque, service access not verified |
| Motor plate support | Three nominal 14-mm metal spacers at PCD146, revised **metal** motor carrier with added clearance holes | Bolt grades, grip length, motor vibration, motor clearance and motor power not verified |
| ROT rotating output | V1.0 nominal hollow metal spindle Ø40 × Ø32, proposed 2 × 6808-2RS deep groove ball bearings 30 mm apart | Major unresolved issue: axial metal retention and preload, bearing bending-moment stiffness and life |
| Camera-end blank | Ø108 × 6 mm annular metal adapter matching conceptual V1.0 output flange PCD88 | **Not** a camera/lens collar, Arca clamp or qualified camera attachment |
| Safety retention | NONE verified | **Independent metal fall-arrest, verified brake/fail-safe retention and positive stop/switch** must be engineered before mounting any camera |

**Do not infer manufacturing safety from a single fused STEP body.** In reality the proposed bridge needs a defined stock alloy, machining process or welding procedure, grain/directional stiffness, independent positive fasteners or verified weld seams and fatigue/deflection testing. A STEP union can conceal mechanical impossibilities.

## Approximate load illustration (NOT a stress certification)

For a **hypothetical** 5 kg payload with 100 mm transverse centre-of-mass offset, a gravity-only moment scale is `5 × 9.81 × 0.10 = 4.905 N·m` before the optical stack, accelerations, dew heaters, winds, cables and any dynamic slewing. Actual moment magnitude and direction depend on articulated pose and measured system mass properties. Neither the 6808 paired bearings nor the bridge can be declared sufficient from this number. The full telescope rig may have a materially different centre of mass.

## FreeCAD on Windows

Download the repository ZIP or [V1.1 generated file folder](../hardware/cad/v11_generated/) then open

`hardware/cad/v11_generated/OpenEQMount_V11_THREE_AXIS_MATED_CONCEPT_UNQUALIFIED.step`

This opens **one 53-solid integrated assembly document** in FreeCAD. Use `V`, `F` to fit to view; expand the left model tree; toggle individual components with `Space`. A separate `OpenEQMount_V11_DEC_ROT_connection_preview.png` explains the bridge/housing geometry. This is a viewable STEP assembly, **not** a fully constrained FreeCAD `.FCStd` PartDesign assembly with joints.

CAD source: `hardware/cad/generate_v11_three_axis_mated_concept.py`. Change parameters and regenerate rather than editing a STEP import with no original feature history.

## FDM policy and gates

The sole new printable file is `v11_NONLOAD_DEC_OUTPUT_PCD23_FIT_GAUGE_PRINT_FLAT.stl`. It is a **fit/drill gauge only** and must never form part of the actual load path. No hub, deck, bearing carrier, motor stand-off or camera capture piece is released as load-bearing FDM STL. The coupon is oriented XY flat Z=0, PETG fit specimen; actual printer/slicer review is Gate B and physical assembly/torque/load/cable/worst-case motion qualification is Gate C.

- Gate **A**: 10 new source tests, geometry generator, watertight FDM mesh, BOM and manifest checks, full STEP export and reimport smoke test, GitHub Actions.
- Gate **B**: measure actual DEC, bearings, camera adapter; print coupon with controlled horizontal/vertical clearance; physically fit the assembly.
- Gate **C**: structurally analyze and then physically load-test metal bridge, bearings, fasteners and independent tether; prove limits under E-stop and cable handling; thermal creep, impact, counterbalance, RA/DEC/ROT sweep and meridian-flip clearance. **Pending.**

## Intentionally excluded / known gaps

1. Accurate OEM input/output connection and angular bolt clocking, camera or lens ring clamp, independent retention tether and proven metal bearing capture.
2. V1.0 stop reference was excluded from assembled V1.1 because it **does not contact** the output rotor; simply placing it in the viewer would imply a safety stop that does not exist.
3. The 60T/20T RA/DEC drive cassettes remain isolated bench fixtures and are not presented as installed. The ROT 80T/20T pulley teeth, belt wraps/hubs, motor bearing load and sensor stack remain missing.
4. Kinematic transformations in this viewer are mathematical poses, not an exhaustive solid-interference sweep; camera/lens envelope, cables, tripod, polar adjusters and counterweights lack measured models.
5. High reliability stop switches, stall detection, watchdog, safe homing, ASCOM Alpaca/INDI rotator service and actual motor firmware are **NOT implemented**.

## Rebuild locally

```bash
python -m pip install 'cadquery>=2.5,<3' pytest trimesh matplotlib
python -m pytest -q tests/test_v11_three_axis_mated.py
python hardware/cad/generate_v11_three_axis_mated_concept.py --out hardware/cad/v11_generated --latitude 35 --dec-preview 25 --rot-preview 0
python tools/dfam_gate_v11.py --dir hardware/cad/v11_generated --report hardware/cad/v11_generated/dfam-gate-report.json
python tools/render_v11.py
```
