# OpenEQMount V1.0 — Camera ROT bearing / drive mechanical bench concept

**Status: CAD / DfAM Gate A only — NOT approved to carry a camera, NOT safe to energize.**

This revision adds a genuinely editable *metal bearing carrier / motor prototype* to the V0.9 optical-axis rotator. It does **not** close the DEC-saddle-to-camera gap in the V0.9 full mount, and is **not** a production assembly drawing. RA and DEC are unchanged.

## Candidate hardware and load path

| Unit | Proposed digital fit | Status |
|---|---|---|
| Bearings | 2× 6808-2RS, **40×52×7 mm**, 30 mm nominal bearing plane spacing | Boundary dimensions supported by [JTEKT/Koyo 6808](https://koyo.jtekt.co.jp/en/products/detail/?pno=6808+2RS); combined bending moment, preload, stiffness and deflection **unqualified** |
| Stator | Machined **metal** housing OD128, pilot bore Ø50 and two Ø52 nominal bearing pockets, z=7 & z=37 mm | Needs toleranced drawing, metal shoulders and true bearing seats; CAD geometry is not a prescribed interference/clearance fit |
| Rotor | Hollow metal sleeve nominal Ø40 outside / Ø32 through opening | Needs shoulders, axial location, preload and appropriate metal hub retention |
| Camera output | Metal plate Ø108, 6×Ø4.5 at PCD88 candidate | **Not** a universal camera thread, Arca or lens collar connector; no optical payload connection |
| Axial retention | Independent **metal** collar reference Ø65 | Needs load path, independent restraint, fastening and failure-mode test |
| Drive | **GT2 nominal 80T:20T = 4:1**, NEMA17, centre distance 105 ±5 mm | Pitch math only: **NO real teeth, hubs, belts, shafts or motor torque verification** |
| Stops | metal stop arc spatial reference at ±160°, proposed software travel ±150° | Not mechanically actuated or force-tested; no switches installed |
| FDM | Scale bezel, M4 clearance coupon, cable slot coupon | **NONLOAD** samples only, flat on XY; printer-specific Gate B pending |

The 6808 is a *deep groove ball bearing*, not a substitute for a qualified crossed-roller bearing. For scale, 5 kg at 100 mm eccentricity creates about 4.9 N·m static moment; a simplistic 30 mm bearing separation produces an approximate 164 N force couple before shocks. This is **not** an approved load calculation. Two 6808s must not be selected for a **3–5 kg** off-axis camera rig without bending stiffness, equivalent loads, fatigue, tilt/runout and retention analysis using the real centre-of-mass offset and camera-to-optical-axis dimensions.

## Engineering risks and unimplemented features

- **DEC-to-ROT mechanical attachment is absent**. Do not assemble the rotor with an imagined plate to the DEC reduction output; factory thread phasing, remaining clearances and collision envelope are unverified.
- **Camera/lens connection is absent**. Provide a *metal* lens collar, dovetail/camera-plate adapter and independent steel safety tether before field testing; printed bezels/threads cannot support a payload.
- Metal stator screws/shoulders and rotor axial preload are only preliminary CAD. Specific inner/outer race clamping and thermal expansion must be reviewed.
- Output pulley is **not** a toothed component. `belt_estimated_length_mm` is approximate belt *pitch line* length; source equation assumes open two-pulley belt and ignores tooth engagement, wrap and tension.
- Cable controls: no >360° wrap, no slip ring. Home and limits must be physically independent and validated; a software ±150° range is not a safety device.
- Motor carrier is a **metal proposal** and may need an actual stand-off bracket to attach to the stator; the STEP is not machining-approved.
- The stop plate is not a closed engineering stop mechanism; actual rotating lug contacts, pin shear and crash loads are missing.

## DfAM release gates

Gate **A**: Python unit tests + CAD generation + watertight single-solid STL + Z=0 + manifest/metadata in CI. Passing it only means geometry and inventory checks passed. Gate **B**: print coupons, physical bearing fit, slicer support/interlayer/clearance and fastener access. Gate **C**: static/dynamic camera-load tests, structural safety, creepage, cable/stop, torque and bearing durability, and independent retaining hardware.

**Never print the metal references as substitute structural plastic parts**. There is no field payload approval, motor-drive firmware or ASCOM/INDI rotator driver in V1.0.

## Windows FreeCAD

Open `hardware/cad/v10_generated/OpenEQMount_V10_ROTATOR_BENCH_UNQUALIFIED.step` to see all candidate parts in one bench STEP. For previous whole-mount conceptual layout continue using `v09_generated/OpenEQMount_V09_THREE_AXIS_MOUNT_CONCEPT_UNQUALIFIED.step` (the new bearing unit is **not** mechanically integrated into that full mount).

## Rebuild

```bash
python -m pip install 'cadquery>=2.5,<3' pytest trimesh
python -m pytest -q tests/test_v10_rotator_bench.py
python hardware/cad/generate_v10_rotator_bench.py --out hardware/cad/v10_generated
python tools/dfam_gate_v10.py --dir hardware/cad/v10_generated --report hardware/cad/v10_generated/dfam-gate-report.json
```
