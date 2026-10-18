# OpenEQMount V0.3 — 3D-printable RA / DEC reducer interface prototypes

**Status: bench-fit prototypes only; NOT a working, load-rated equatorial mount.** 

**Scope:** 3–5 kg target payload / <=500 mm optics, predominantly printed components. This build contains actual hole patterns and removable interface solids; the RA–DEC cross-axis load-bearing yoke, altitude/azimuth polar adjuster, approved telescope saddle, wave-generator INPUT SHAFT, drive couplings, safety restraint, physical torque/load testing and cable routing are **not finished**. Do not attach a telescope, operate overhead, or run GoTo while these components remain unvalidated.

## 1. Supplier drawings / part revision is decisive

- CSF-17-100-2UH: https://www.harmonicdrive.net/_hd/Content/caddownloads/dxf/csf-2uh_gearheads/csf-17-xx-2uh.pdf
- CSF-14-100-2UH: https://www.harmonicdrive.net/_hd/Content/caddownloads/dxf/csf-2uh_gearheads/csf-14-xx-2uh.pdf
- CSF drawing catalogue: https://www.harmonicdrive.net/downloads/pdf-drawings/csf-gear-units
- Official CSF standard product sizes: https://legacy.harmonicdrive.net/products/gearheads/csf-unit/

| Mechanical dimension | RA (CSF-17-100-2UH) | DEC (CSF-14-100-2UH) | Status |
|---|---:|---:|---|
| Housing OD / axial envelope | Ø79 × 45 mm | Ø73 × 41 mm | Supplier nominal |
| Output face bolt pattern | 6 × M5, PCD 27 mm, thread max indicated 10 mm | 6 × M4, PCD 23 mm, thread max indicated 8 mm | Supplier nominal, verify actual part |
| Housing rear side | 6 × M4 threaded + 6 × Ø4.5 clearance, PCD 71 mm | 6 × M4 threaded + 6 × Ø4.5 clearance, PCD 65 mm | Supplier nominal, threaded-hole rotation must be checked |
| Housing rear bolt phase used for CAD | 30° provisional | 30° provisional | **MANDATORY FIT-TEST before bolts** |
| Main output bearing | Built-in cross-roller bearing | Built-in cross-roller bearing | Do NOT replace with small printed shaft + 608 |
| Auxiliary input shaft bearing candidate | 608-2RS, 8×22×7 mm | 626-2RS, 6×19×6 mm | NOT proven compatible with actual input couplings |

**Warning:** 2UH rear face has both threaded and clearance holes on the same PCD, staggered by 30°. The printed rear cap assumes six threaded holes with a *provisional* phase. It must be checked against the actual reducer and orientation before assembly. Metal replacement/clone "17/14 harmonic reducers" may have entirely different dimensions.

## 2. Output adapters and bolt engagement

- `ra_output_bolt_adapter`: 6 × Ø5.5 clearance holes on PCD27, six Ø10 × 5.5-deep cap-screw pockets, outer Ø76×12. Adapter centre relief Ø12. Four Ø5.6 *insert pilot* holes PCD58 for a future metal-spreader-backed yoke interface.
- `dec_output_bolt_adapter`: 6 × Ø4.5 clearance holes PCD23, six Ø8.5 × 4.5-deep head pockets, Ø70×11 adapter, centre relief Ø10; four Ø5.0 insert pilot holes PCD54.
- Example screw starting points (**not guaranteed final fastener lengths**): RA M5×12 (printed material under head nominal 6.5 mm → 5.5 mm OEM engagement). DEC M4×12 (printed 6.5 mm → 5.5 mm OEM engagement). Check installed head/washers, engagement and blind-hole bottoming; do not exceed OEM thread depth. Use thread-locking only as allowed by gearbox supplier, and never contaminate bearing or strain wave generator.
- A printed output flange with insert holes does NOT establish the telescope payload rating. Reinforcing metallic interface plates and physical mechanical testing are required.

## 3. Printed reducer rear shells

- `ra_rear_mount_housing`: cap Ø108×9 mm (z -9..0), sleeve bore Ø80.5 (Ø79 reducer +1.5 diametral), sleeve outer Ø100.5, length 43 mm; six Ø4.5 rear screw clearance holes PCD71; four Ø4.5 through holes at PCD92 for optional bridge; rounded and gusseted motor mounting ears with Ø4.5 through holes at (x,y)=(57,±25) mm.
- `dec_rear_mount_housing`: cap Ø104×9 mm, bore Ø74.5, sleeve outer Ø94.5, length 39 mm; six Ø4.5 rear holes PCD65; same optional bridge interface, rounded/gusseted motor ears and through holes.

- **The reducers are retained axially by their metal rear threaded pattern**, not by clamping on the gearbox OD. On assembly, insert the reducer from the output side, face side out, and place the M4 bolts through the printed cap from behind; use substantial washers/metal backing washers. Example M4×14 with a 9mm cap may give 5mm theoretical engagement, but the supplied thread depth is not specified on that face: **measure before buying or tightening screws**.
- **DfAM revision:** bridge/motor ear connections use Ø4.5 **through clearances** with metal M4 bolts, metal washers/spacers and metal nuts. Verify head/washer access, nut retention and actual length before any powered test. The original Ø5.5 heat-set insert blind sockets are superseded; heat-set inserts are **not permitted as untested primary tensile joints**.

## 4. NEMA17 motor carriers / timing belts

- `*_nema17_slider` is a **separate flat motor carriage**. NEMA17 standard pattern: 4 M3 tapped motor holes at 31×31 mm; CAD clearance slots 3.6 mm wide ×13.5 mm long, with ±5mm travel along x. Pilot is a 34×24mm elongated centre slot to clear a nominal Ø22 motor register with motion.
- Two M4 mounting locations on the carriage are at (x,y)=(57,±25) mm. 9mm metal standoffs nominal join the motor carriage top z=-18 to rear cap z=-9. **A third brace is necessary before moving a payload**: this two-standoff bench layout is not torsionally qualified.
- Motor centre x≈85mm. Assuming a **20T / 60T GT2 2mm-pitch pulley pair** and C=85mm centres, calculated approximate pitch belt length L=251.9mm; **GT2 252mm is only a provisional fit sample**, not a verified belt. Actual pulleys, flange width, hub placement, printed deflection and tension range must be measured.
- Example M3×12 with a 7mm printed plate + ~1mm washer gives ~4mm thread reach into motor; verify actual tapped depth, don't bottom out on the motor winding.
- Both motor and driven pulleys must be genuine aluminium/metal with metal shaft coupling. Printed friction-coupled pulley or printed wave-generator input hub is NOT in the load-rated path.

## 5. Bearing bridge — OPTION ONLY

- `*_input_bearing_bridge_OPTIONAL`: 608 / 626 bench test seats with nominal OD+0.15mm; four M4 through holes on PCD92; sculpted +X relief to clear moving motor slider.
- It is for a *future supported metal input shaft design*. Cannot install until wave-generator bore geometry, shaft length, shaft preload/axial location and pulley spacing are measured.
- Never insert a mismatched shaft or load an internal bearing from a bridge that cannot be coaxially aligned. Printed radial bearing seats cannot guarantee machining-level concentricity.

## 6. Binding DfAM policy and printer guidance

Every printable part now follows [DfAM design controls](dfam-design-standard.md). Exported V0.3 STL Z-min is 0 with XY bed plane. **Digital checks cannot verify stresses, overhang support, layer adhesion or manufacturer fit**. The Gate B slicer/print review and Gate C physical load validation are still pending. All V0.3 parts are labelled `prototype_unqualified` in the CAD manifest.

Run the reproducible Gate A:

```bash
python hardware/cad/generate_v03.py --out hardware/cad/v03_generated
python tools/dfam_gate.py --report hardware/cad/v03_generated/dfam-gate-report.json
```

## 6.1 Printer guidance and fit strategy

| Parameter | Initial value (adjust by coupon) |
|---|---|
| Material | PETG or PETG-CF for first bench iteration; PA12-CF for later stiffness/thermal trials after drying and printer qualification |
| Layer height | 0.20 mm; small layer height for hole print trials |
| Walls | >= 6 perimeters for structural interfaces |
| Top/bottom | >= 7 solid layers |
| Infill | 45–60% gyroid or cubic, increase locally around bolt bosses |
| Nozzle | 0.4/0.6 mm; hardened for abrasive CF |
| Orientation | Rear housings: rear cap underside z=-9 on print bed; output adapters: lower face on bed; sliders: large planar side on bed |
| Supports | Designed around axial printable bores; support settings remain slicer-dependent |
| Load joint fasteners | Ø4.5 through clearances plus accessible metal washers and nuts; not plastic threads or untested heat-set inserts |

**Tolerance gauges (print first):** `*_fit_gauge_diam_plus_0p6/1p2/1p8` = reducer OD plus 0.6, 1.2, 1.8 mm of *diametral* clearance; `*_bearing_gauge_bore_plus_0p10/0p20/0p30` = bearing OD plus hole clearance 0.10/0.20/0.30 mm. They are calibration rings; a clear slip fit is desirable for gearbox OD, while bearing pilot fits must avoid overconstraint. The full CAD housing uses +1.5mm diameter, not a press fit. **Measure supplier ODs and print actual ring tests.**

## 7. Recommended mechanical assembly checks

1. Measure gearbox OD, bolt PCD, front/rear face designation, and the threaded-vs-clearance stagger with calipers and manufacturer drawing. Photograph each face.
2. Print **only** tolerance coupons; record measured dimensions and select parameters.
3. Trial-fit housing on UNPOWERED reducer. If bolt holes don't align by hand, STOP and regenerate phase / PCD parameters; NEVER force mounting bolts.
4. Verify cap-screw engagement with depth gauge, flat washers and manual torque limits applicable to printed interfaces. Do not directly apply factory metal-to-metal torque to plastic.
5. Fit an output adapter, inspect head clearance and flatness; use temporary dummy loads, not a telescope.
6. Trial-fit NEMA slider and check free travel and pulley/cable access; do not connect an unfinished input coupler to the harmonic drive.
7. Fit the optional bearing bridge only after independent, verified concentric input-shaft design.
8. Before field operation, design RA–DEC yoke and polar wedge, metal reinforcement, tripod interface, retention stops, counterbalance path, safety cable and full-direction collision envelope; test 2× rated load in controlled conditions with no valuable equipment.

## 8. Generation, output status and caveats

```bash
python -m pip install 'cadquery>=2.5,<3' pytest
python hardware/cad/generate_v03.py --out hardware/cad/v03_generated
python -m pytest -q
```

- Every component gets independent STEP and STL. `OpenEQMount_V03_interface_layout.step` is a **spatial interface preview** of two independent modules, **not** a functioning assembly or 5kg-ready hardware.
- All geometric parts are original. Neither vendor STEP, vendor schematics, 3D-printed gearbox internals, a proprietary saddle, nor unlicensed OEM CAD assets are distributed.

## 9. Major unresolved engineering decisions before a production-like V0.4

1. Physical CSF17/CSF14 revision and actual purchase; if using non-Harmonic-Drive clones the drawing is not portable.
2. Input adapter type (flex spline / wave generator), precision metal shaft, coupling eccentricity, bearing preload and belt-plane stack-up.
3. A two-sided RA–DEC joint with load-rated mechanical reinforcement (critical on printed mounts).
4. Camera saddle interface (verified Vixen/Arca hardware), tripod clamp, adjustable altitude/azimuth wedge and safety retention.
5. Exposure-relevant periodic error/backlash/creep and payload tests before using expensive optics.
