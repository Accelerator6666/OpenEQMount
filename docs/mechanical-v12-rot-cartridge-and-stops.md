# OpenEQMount V1.2 — serviceable ROT bearing cartridge and contact-stop CAD (Gate A)

**This is a mechanical layout investigation. NOT a manufacturing drawing, bearing-life approval, 3–5 kg payload rating, proven fall restraint, or authorization to energize motors.** The project remains research-level until Gates B/C are completed.

## Why V1.2 was necessary — an actual V1.0 assembly error

The V1.0 one-piece proposed stator (`v10.bearing_seat_housing`) had a **50 mm-diameter opening** through most of its axial length, with **52 mm counterbores** only at `Z=7–14` and `Z=37–44`. A **6808-2RS, Ø52 mm** bearing cannot enter either buried counterbore from either face: the CAD could be viewed but **the bearing could not be assembled**.

V1.2 replaces **only that stator body in the complete V1.1 viewing assembly** with a Ø52.2 mm nominal axial *through-bore* and **separate** metal outer-ring contact spacers and removable end caps. The 52.2 mm number is a provisional CAD clearance — **it is not a specified ISO bore tolerance or running fit**.

The JTEKT/Koyo [6808 2RS product page](https://koyo.jtekt.co.jp/en/products/detail/print.php?pno=6808+2RS) gives `d=40, D=52, B=7 mm`, and refers to mounting shoulder dimensions such as `da(max)=42` and `Da(max)=50` mm. Such small ring-face margins make the V1.2 **Ø42/Ø40 inner spacer** and **Ø52/Ø50 outer spacers** narrow (1 mm radial walls). **These dimensions are only diagnostic CAD reference faces, NOT machinist-approved retaining sleeves.** Ring-face contact, axial preload, fit, heat expansion and pressing sequence must be verified from the selected bearing manufacturer and revisited; a **different bearing family** may be preferable after stiffness calculation.

### ROT nominal stack (local optical +Z, mm)

| Axial zone | Digital part/reference | Mechanical gate |
|---|---|---|
| −4 to 0 | Ø108 metal lower removable cap, 4 × Ø4.5 PCD90 | Bolts/thread engagement/strength unknown |
| 0 to 7 | Ø52/Ø50 outer-ring contact spacer | Narrow, unqualified section |
| 7 to 14 | 6808-2RS bearing #1, Ø40/Ø52/7 | Fits and ring shoulders unknown |
| 14 to 37 | Outer spacer Ø52/Ø50; inner reference Ø42/Ø40 | 23 mm separation; neither spacer approved |
| 37 to 44 | 6808-2RS bearing #2, Ø40/Ø52/7 | Bending/tilt and fatigue not evaluated |
| 44 to 54 | Ø52/Ø50 outer-ring spacer | Unqualified |
| 54 to 58 | Ø108 upper removable metal cap, 4 × Ø4.5 PCD90 | Actual cap-to-stator thread scheme TBD |

All dimensions nominal. A real bearing shaft requires a properly specified **shoulder and end lock**, preload/clearance method and lock against loosening. These are **NOT PRESENT**; the earlier V1.0 hollow sleeve and loose capture collar remain digital placeholders. Correcting bearing insertion alone has **not** solved axial load retention. An unverified motor, camera, or lens must not be mounted or energized.

## ROT positive contact model — stronger than a decorative arc, not strength proof

Two fixed metal stop blocks are shown at local azimuth **−166° and +166°**, extending from the stator envelope. A moving metal dog attached in concept to the camera output flange has a separate model. In the reference 3D boolean interference sweep, the moving dog remains clear at angles `−150°, 0°, +150°` and intersects a stop block at `−160°` and `+160°` (~620.8 mm³ Boolean overlap at each endpoint).

**Interpretation:** this geometrically establishes a contact opportunity between the software ±150° envelope and the beyond-range 160° check; it is not an exactly ±160° hard-stop. Elastic deflection, contact onset angle, bolt anchorage, inertia, deflection, dynamic motor torque and impact loads are still unknown. Critically, a CAD solid penetrating another at 160° represents an impossible physical pose, **not** a demonstrated certified arrest position. A motor-interrupt switch, end-stop wiring, electronic watchdog and E-stop are **not implemented**.

The moving tether lug is angularly offset from the stop dog by 90° to avoid two separate conceptual parts occupying identical space. A fixed lug exists on the stator. **No fall-arrest cable, attachment chain, routing-length calculation or independent retention proof exists**. Two drilled tabs do not constitute a safe tether.

## V1.1 integrated model retained, safety restrictions increased

The V1.1 DEC-to-ROT metal design-intent bridge remains based on **unverified** DEC OEM output PCD23 and unspecified metal fabrication. The ROT/output path still contains intersecting concept fastener/hub envelopes, which are not exploded, toleranced manufacturing instructions. V1.2 has NOT certified all part-to-part interferences, real motor pulleys/GT2 teeth, lens collar, power-off retention or cable motion during meridian flip.

The latest **one-file FreeCAD combined STEP** is

`hardware/cad/v12_generated/OpenEQMount_V12_THREE_AXIS_SERVICEABLE_CARTRIDGE_CONCEPT_UNQUALIFIED.step`

It contains **64 separate named bodies**. The local detail image highlights the outer retainers (blue), bearings/spacers (gold), fixed and moving stops (orange), and disconnected safety-lug proposals (green). For Windows FreeCAD, open the STEP, press `V` then `F` to fit, expand the model tree and toggle a part with Space. The `v12_*` loose STEP parts are usable for fit assessment, but are not cleared for machining.

## DfAM and test gates

- **Gate A (completed digitally):** 10 added unit/geometry tests; through-bore insertion check; 4-hole upper/lower cap pattern alignment; local ±150/±160 numerical stop-contact check; STEP export/reimport of 64 bodies; 2 non-load PETG gauge STLs watertight, single connected mesh, XY bed-flat with Z=0; GitHub Actions reproducible generation.
- **Gate B (pending):** selected bearing OEM ring face drawing and fit class; machinable and assemblable axial shoulders/retainers; physical DEC-ROT OEM bolt patterns; camera and lens-specific metal clamp; FDM coupons, slicer clearance and physical gauge measurements.
- **Gate C (pending):** static, dynamic and thermal/creep tests; measured system centre of mass; stiffness, deflection, ring loading/preload and load lifetime; actual stop impact and motor cutout; fastener torque/locking; fall-arrest independent tether; RA/DEC/ROT collision sweep including camera envelope, cable, tripod and meridian flips. NO authorized camera payload or powered testing before independent safety controls and hazards assessment.

## Source and reproduction

```bash
python -m pip install 'cadquery>=2.5,<3' pytest trimesh matplotlib
python -m pytest -q tests/test_v12_rot_cartridge.py
python hardware/cad/generate_v12_rot_cartridge.py --latitude 35 --dec-preview 25 --rot-preview 0 --out hardware/cad/v12_generated
python tools/dfam_gate_v12.py --dir hardware/cad/v12_generated --report hardware/cad/v12_generated/dfam-gate-report.json
python tools/render_v12.py
```

Related historical context: [V1.1 DEC–ROT metal bridge](mechanical-v11-dec-rot-integration.md), [V1.0 bearing bench](mechanical-v10-rotator-bearing-bench.md) and [DfAM standard](dfam-design-standard.md).
