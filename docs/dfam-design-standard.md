# OpenEQMount DfAM Design Standard — FDM/FFF (binding)

**Revision:** DFAM-001 / 2026-10-18  
**Scope:** Every part supplied as a 3D-printable STL / 3MF or described as a printed load-carrying part, in every future release. Historic V0.2 concept meshes are **NOT printable production files**. V0.3 parts are **bench-fit-only**, and all 3–5 kg payload claims remain unverified.

## Mandatory design-first rules

| ID | Requirement | Design action | What may be checked automatically |
| --- | --- | --- | --- |
| D-01 | **Print orientation and anisotropy come first** | Each part has a specified bed-contact surface, +Z layer direction, load vector(s), and interlayer-peel risks. Optimize placement so dominant stresses flow in the XY plane; never assume Z tension is equivalent to XY strength. | Explicit orientation recorded; STL placed at Z=0. Stress directions remain **manual**. |
| D-02 | **Self-supporting geometry by default** | Redesign >45°-from-vertical-overhang risk cases using slopes, arches, chamfers, split components, or properly designed removable supports. Never assume a nominal angle guarantees support-free printing. | Slicer review status mandatory; actual overhang/bridging must be checked in slicer. |
| D-03 | **Smooth, continuous load paths** | Avoid sharp re-entrant corners and long, thin overhanging ears. Use root fillets, generous XY-plane gussets, ribs aligned with expected force vectors, local shell thickness. Avoid uniform solid infill as a substitute for stiffness design. | CAD unit tests cover some fillets, gussets, nonintersections; structural simulation / measurements remain manual. |
| D-04 | **Metal load-bearing joints** | Use factory metal threads, full-depth through-bolts with metal washers/nuts or engineered metal load-spreading plates. Do not use printed plastic threads or untested heat-set inserts in tensile/peel/cyclic primary load paths. Provide tool access and measured screw engagement. | Required fastener strategy recorded; physical access/torque/creep is **manual**. |
| D-05 | **Layer-aware tolerances** | All mating holes and fits get *material/printer-specific* calibration coupons; avoid interference fit on expensive reducers; distinguish diametral from radial clearance and nominal CAD vs as-printed dimensions. | Parametric fit gauge geometry exists; slicer/material calibration is **manual**. |
| D-06 | **Printability before light-weighting** | Minimize unnecessary mass where it does not support load; reinforce interfaces rather than indiscriminately increasing infill. No fragile isolated pillars, inaccessible support cavities, or overlong bridges. | Connected watertight meshes + envelope dimensions are checked; wall thickness / supports remain manual. |
| D-07 | **Environmental/creep resistance** | PLA is not a permitted structural field material. PETG may be used for bench fit only until stiffness/creep/UV/cold/hot qualification. Consider ASA, PC, PA-CF after controlled printing and actual tests; dry filament and use hardened nozzle for filled polymer. | Material + validation stage recorded, not physically tested. |
| D-08 | **Mechanical fail-safe** | 3D prints must not be the *only* means of preventing payload fall, loss of restraint, or uncontrolled shaft motion. Incorporate independent metal retention, safe stow, hard limits, and safe load handling. | Not automatable by mesh checks. Must have field-test evidence. |
| D-09 | **Assembly/service accessibility** | Ensure realistic screwdriver, nut/washer, bearing removal, belt tensioning, cable routing, inspection, and replacement clearances; avoid glued-up non-serviceable gear interfaces. | CAD assembly review + physical trial fit required. |
| D-10 | **Build reproducibility** | Every printable model must have editable source, named revision, machine-readable DfAM record, STEP and bed-oriented STL, and a test/build workflow. | CI blocks missing records, STL mismatches, non-manifold parts, and oversized build envelopes. |

## Preliminary FDM profile (NOT mechanical acceptance criteria)

- Trial profile: 0.4–0.6 mm nozzle, layer 0.20 mm, **at least 6 perimeters** for fastening regions, **at least 7 solid top/bottom layers**; locally increase material near bolt paths. These are *trial slicer settings*, not a substitute for local feature-thickness calculation.
- Size each minimum wall/rib/fillet against the **actual extrusion width, layer direction, joining load and printer calibration**. Avoid universal declarations such as "all walls ≥2mm = strong enough"; minimum nominal web dimensions should be measured from CAD and documented per part.
- Use real clearance and shrinkage coupons; remember X/Y dimensional accuracy and vertical (Z) fit can differ.
- Avoid assuming support-free prints solely from a 45° rule or the CAD's watertightness. The final slicer preview and printed results are decisive.

## Current V0.3 axis interface changes under DfAM

1. Rear-housing motor lugs have **rounded vertical corners and integral XY-plane gussets** to distribute force into the ring body. Their strength remains untested.
2. Optional bearing-bridge and motor-lug pilot locations are **Ø4.5 mm through-clearances** for metal M4 through-bolts/nuts/washers, **not** heat-set insert blind sockets. Engineering must separately confirm feasible fastener access and stack length.
3. NEMA17 carrier external XY corners are rounded to reduce stress concentration and layer start discontinuities.
4. Every V0.3 STL is emitted with its **bottom face on Z=0** while the STEP model retains the original assembly coordinates. All parts have JSON DfAM metadata describing orientation, manual audit and safety state.
5. V0.2 legacy STL exports are disabled by default; it remains a **spatial concept** without a DfAM-verified load path.

## Three gates: only the first is automated

- **Gate A: digital model (automated)** — CAD script/tests pass, all parts have DfAM metadata, STL is manifold/single-body, aligned with Z=0 and within target 220×220 mm bed. Run `python tools/dfam_gate.py`. **No certification of support-free slicing or mechanical strength.**
- **Gate B: slicer and fit audit (human, required)** — inspect every layer around supports, bridges, top/bottom closure, screw pockets, seam positions and interlayer forces; print tolerance gauges; record calibrated measurements; verify fastener and assembly access. Mark record per part, attach slicer screenshots/print photos.
- **Gate C: mechanical acceptance (human/test rig, required)** — physical static/dynamic testing, creep and thermal cycling, repeated motor acceleration, vibration, fastener loosening and failure mode review, independent restraint and safety stop checks. Only then may a part be called suitable for the declared payload and environmental envelope.

`python tools/dfam_gate.py --require-qualified` **must fail** until each model receives supporting Gate B/C evidence. Passing CI indicates only Gate A.

## Per-part required review template

See [`dfam-review-template.md`](dfam-review-template.md). Store evidence in `hardware/cad/reviews/<part_name>.md` or attach the controlled photo/test report in a GitHub issue. Never mark a model structurally verified based only on a geometry test or finite-element estimate.

### References

- [Prusa: Modeling with 3D printing in mind](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135) — layer direction, printer clearances, overhangs and manifold meshes.
- [Prusa: Poor bridging](https://help.prusa3d.com/article/poor-bridging_1802) — short spans, bridge cooling and orientation.
- [Harmonic Drive: CSF-2UH](https://www.harmonicdrive.net/products/gear-units/gear-units/csf-2uh) — integrated output cross-roller bearing, not printable bearing substitute.
