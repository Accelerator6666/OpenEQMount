# OpenEQMount V0.7 — RA Fixed Stator + Dual-Axis Belt Bench

**Status: engineering prototype, DfAM Gate A only. Strictly NO payload / powered-operation approval.**

## Purpose and major interface correction

V0.6 built a prototype independent polar-altitude metal lock. This revision adds a **metal, stationary CSF-17-2UH rear housing adapter**, and two **separate unpowered flat-belt layout fixtures** for RA and DEC. The rotating output from RA is **not** fastened to the polar wedge. The 2UH already incorporates its own precision output bearing; no printed bearing should carry its moment load. Manufacturer context: https://www.harmonicdrive.net/products/gear-units/gear-units/csf-2uh ; download the **exact** selected reducer drawing at https://www.harmonicdrive.net/downloads/pdf-drawings/csf-gear-units .

**Important retrofit:** V0.6's moving lock lugs occupy the *original* V0.5 top deck's `x=45, y=±45` threaded/access locations. The V0.7 adapter **does not reuse or drill through those lugs**. Instead, `v07_WEDGE_REPLACEMENT_TOP_DECK_METAL` has four **additional** candidate M6 through-bores at `x=(-43,65)`, `y=(-27,27)` in the pre-tilt V0.5 local XY datum. Fabricate a **replacement verified metal deck**; the original V0.5/V0.6 upper plate should not be assumed drop-in compatible.

## Assembly and local datums

Top-deck local frame: wedge top surface at local `z=30 mm`, hinge axis = `(-61,0,29)`. All RA stator parts undergo the **same** rotation about that hinge for test latitudes 25°–45°; this is **not** a complete collision simulation against all lower wedge bolts, tripod parts, motors or cables.

| Component | Nominal local Z / dimensions | Role |
|---|---|---|
| Modified V0.5 wedge top | top at z=30 mm | metal, contains old V0.6 lock bolts plus new V0.7 attach bores |
| Four lower tubular stand-offs | z=30..56, Ø16 / Ø6.6 | 26 mm **metal only**, keep above locking ears |
| Wedge/stator intermediate adapter | z=56..64, 172 × 110 mm, center x=10 | 8 mm metal, 4 M6 thru plus Ø58 central opening |
| Four upper stand-offs | z=64..85, Ø16 / Ø6.6 | 21 mm **metal only**; set stator ring above adapter |
| RA stationary gearbox rear flange | z=85..93, 172 × 110 mm | 8 mm metal, Ø58 opening; M4 PCD71 **angular phase provisional** |
| RA gearbox volume reference | z=93..138, Ø79 mm | volume envelope **not real mounting CAD** |

The metallic bolts, bolt stretch/preload, washers, engagement length, countersinks, anti-loosening, drive pulley interference, jack reach, fatigue and capacity remain unspecified. One unqualified printed part, metal-as-STL substitution, or stand-off fastener loosening may cause loss of load retention; design a completely independent restraint before a payload is used. All drawings are dimensional bench references only.

## Dual-axis transmission bench fixtures (NOT installed in mount)

The independent RA and DEC metal-only bench plates use two GT2 **pitch-diameter only** pulley cylinders (60T and 20T). No keyway, pulley tooth profile, input bore, input bearing constraint, wave-generator hub fixation, belt tension force, flange interference or motor torque calculations have been checked.

| Item | Reference value |
|---|---:|
| Reducer ratio, provisional | 100:1 |
| Belt tooth-count ratio | 60T:20T (3:1) |
| Nominal combined ratio | 300:1 |
| GT2 tooth pitch | 2.0 mm |
| Motor shaft center | X=115 mm from input reference |
| Mounting hole pattern | NEMA17 31 × 31 mm, four Ø3.6 mm full-length slots |
| Nominal ± motor movement | ±5 mm (10 mm total) |
| Central clearance | RA Ø58; DEC Ø54 (not physical input hub fit) |
| Approx open-belt pitch length | 301.4 to 321.4 mm over 110–120 mm center range |

The belt length is a **geometry estimate**, not a purchased-belt SKU. A separately machined input spindle/appropriate bearings and correctly selected 2UH wave-generator connection need their own drawings and validation. The current kit has NO mechanically coupled drive shaft.

### DfAM: all 3 FDM parts

- Flat XY orientation, single watertight STL, within 220 × 220 mm; exposed loose covers and hole-coupon only.
- PETG is allowed only for alignment and test coupons, not primary mechanical service.
- Do not install the FDM identifier lids over *powered* moving belts; they are not safety guards and have **no fasteners, safety rating or tool access proof**.
- For every printed part, record slicer overhang/bridging, perimeters and actual hole fit as Gate B. Print direction, minimum wall and thermal creep are **not validated by the Gate A mesh gate**.
- FDM must never become the torque path from wave generator to reducer, RA casing to wedge or camera to tripod.

## Verification

```sh
python -m pip install 'cadquery>=2.5,<3' pytest trimesh
python -m pytest -q tests/test_v07_ra_input_interface.py
python hardware/cad/generate_v07.py --latitude 35 --out hardware/cad/v07_generated
python tools/dfam_gate_v07.py --dir hardware/cad/v07_generated --report hardware/cad/v07_generated/dfam-gate-report.json
```

**Gate A:** CAD, single-body mesh, bed orientation, dimensions, intended use safety metadata (automated). **Gate B:** actual slicer, print fit, OEM phase/inputs and all fastener access (pending). **Gate C:** load path calculations, FEA (supplementary), retention, fatigue, thermal creep, physical vibration and safely controlled payload trials (pending). Do not energize or carry a camera until an independent responsible engineer signs off both B and C.

## Blocking measurements / V0.8

1. Obtain **exact vendor revision** CSF-17 and CSF-14 rear-face, wave-generator input/bore, depth, runout, bearing-preload drawing. The code's 30° rear-hole pattern is *provisional*.
2. Validate combined V0.6+V0.7 latitude and azimuth travel, including mechanical fastener stacks, the wedge jack and finger clearance; build a complete assembly.
3. Design real metal **input shaft, bearing carrier, coupler and pulley**, confirm interference at 25/35/45°, and measure static belt tracking/tension on a stand **without payload**.
4. Finalize a real tripod (manufacturer and model), actual screw dimensions, stops and independent fall-restraint.
5. Keep all V0.7 FDM outputs marked unqualified until Gate B/C evidence exists.
