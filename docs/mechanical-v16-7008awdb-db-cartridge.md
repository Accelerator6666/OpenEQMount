# OpenEQMount V1.6 — 7008AWDB DB matched bearing cartridge (Gate A ONLY)

> **NOT a release for manufacture. No payload, no camera and no energized motors.** No friction, preload, bearing life, retention strength, camera anti-fall or fitted shaft dimensions have been verified. Gate B and Gate C remain PENDING. This is a standalone ROT bearing study, **not** a replacement for the V1.4 three-axis installed ROT cartridge. All FDM files are nonstructural PETG dimensional coupons, complying with `docs/dfam-design-standard.md`.

## 1. Selected dimensional reference; not yet a procurement-approved bearing

The official [NSK 7008AWDB matched angular-contact DB product page](https://www.nsk.com/engineering/products/bearings/ball-bearings/angular-contact-ball-bearings/matched-angular-contact-ball-bearings/7008awdb-apn.html) lists:

| Design variable | NSK 7008AWDB value | Used in CAD? |
|---|---:|---|
| Bore `d` | **40 mm** | Yes (external envelope) |
| Outside diameter `D` | **68 mm** | Yes (external envelope) |
| Pair total width `2B` | **30 mm** (two adjacent 15 mm rings) | Yes |
| DB arrangement | Back-to-back | Yes (arrangement name; race geometry not reconstructed) |
| Contact angle `A` | 30° | Report only |
| `a0` load-center spacing | **46.2 mm** | Arithmetic report only |
| Shaft abutment `da min` | **46 mm** | Nominal 48 mm shoulder passes diameter-only check |
| Housing abutment `Db max` | **63 mm** | Nominal 60 mm cap bore passes diameter-only check |
| Axial internal clearance | **CN** | **Does NOT identify required application preload** |
| Catalogue radial ratings C / C0 | 35 / 31 kN | Recorded only; **not ROT moment capacity** |

**V1.5 correction:** 50 mm was an arbitrary **hypothetical support separation**, not the nominal physical bearing width of a matched 7008AWDB pair. The manufacturer `a0=46.2 mm` describes load-center geometry. These numbers are deliberately distinct in the V1.6 CAD and tests. For a symmetric reference datum with physical faces z=0/30 mm, virtual load centers are z=-8.1/+38.1 mm. Virtual equilibrium reactions are not actual rolling-element/raceway contact forces.

## 2. Cartridge mechanical architecture — reference only

- **Two directly adjacent factory-matched 7008AWDB rings:** z=0 to15 and z=15 to30 mm. No homemade intermediate shims/spacers that change OEM controlled axial clearance or preload.
- **Metal stator:** Ø90 external reference, Ø68.2 straight-through bore across 30 mm. The **68.2 is a deliberately loose visualization/installation envelope** and **not** the manufacturing bore fit. This prevents repeating the V1.2 issue of a bearing too large to pass its housing entry. Actual housing fit must be replaced from NSK application guidance.
- **Two removable metal outer-ring caps:** Ø89 x5, nominal Ø60 central openings. The nominal diameter-only `Db(max)` rule is checked but contact face extent, axial interference, screw preload, seal and cap accessibility are not.
- **One-piece hollow spindle reference:** 40 mm nominal journal, Ø30 central bore, Ø48 lower **integral** metal shoulder ending at bearing z=0; upper washer and nut are **space reservation only**.
- **Six Ø4.5 nominal clearance holes, PCD80**: arbitrary metal cap-to-shell bolt concept, **not an OEM approved pattern**. They are not populated with modeled, rated or torque-qualified bolts.
- **Separate metal camera clamp plate blank**: not an actual clamp. The V1.3 independent safety tether and V1.4 load-envelope issues remain unresolved.
- **One assembled, one axial-exploded STEP**: both intentionally show reference solid outlines, no NSK proprietary internal bearing or seal details. All STEP labels contain unqualified status.

**Important qualification blocker:** axial clamp contact geometry, real journal tolerance, shaft fillet radius and finish, housing concentricity, locknut female thread, locking washer tabs, anti-loosening design, matched-pair face order, safe axial clamp force and differential thermal expansion are **not** resolved. Do not manufacture from the CAD, no interference- or press-fit assumptions.

## 3. Comparison of hypothetical external radial reactions

V1.6 retains the *illustrative* transverse load assumption with load plane z=`75mm + CG distance from fixture face` and **virtual** NSK load centers z=-8.1/38.1. Under mass 4 kg, CG 80 mm from an assumed fixture face, 20 mm radial eccentricity:

- Transverse force `F=m*g≈39.23N`.
- `a0=46.2mm`; virtual near and far reactions ≈**99.3 N / 138.5 N** in opposite directions, not physical bearing loads.
- ROT gravity-roll torque `F × 0.020m≈0.785 N·m` (no gearbox efficiency, backlash, dynamic accelerations or orientation-dependent component analysis).
- Sweep: 3/4/5 kg × 40/80/120 mm CG distance × 0/20/40 mm eccentricity = **27 illustrative cases**.

NSK `C` or `C0` are basic **radial** catalogue ratings and **must not** be treated as combined-axis/tilting-moment ratings for the built ROT. No moment stiffness, axial preload, thermal stack, runout, tracking RMS, allowable acceleration or life has been established.

## 4. Gate A/B/C checklist

**Gate A (digital checks, implemented)**

- 14 parametric/datum tests: correct OEM dimensions, pair faces 0/15/30 mm, a0 distinct from 2B, shoulder-reference limits, relative forces, invalid cases, assembly part count and export.
- 9 body STEP import, 2 bed-oriented nonload STL coupons watertight and base z=0, manifest and reference report.
- `tools/dfam_gate_v16.py` rejects unqualified status being silently promoted to approved.

**Gate B (PENDING)**

- Order/verify a specific approved manufacturer paired set (exact suffix and axial clearance/preload grade); review manufacturer engineering application guidance.
- Determine actual bearing housing/journal fits, axial locating shoulder, face contact, fillets, preload and locking method; inspect full exploded maintenance process.
- Print PETG coupons flat XY; measure with calipers, record material, layer height, shrinkage, sliding/fit, supports, thermal/environment effects; **coupons are never structural pieces**.
- Inspect actual sample rotation clearance, free torque, axial/endplay, runout, thermal expansion and service tools.

**Gate C (PENDING)**

- Independent metallurgical load path and independent tether with camera vendor retention hardware; camera CG survey, FEA/stiffness/fastener/fatigue/life and physical load tests.
- Verify ROT physical stops, motor stalls, power-off drop, meridian-flip cable clearance, emergency release, actual rotation precision and repeated thermal cycling.
- Only then assess 3–5 kg as a **goal**, not current rated payload.

## 5. Windows FreeCAD workflow

After download from `hardware/cad/v16_generated/`, use **FreeCAD → File → Open**:

1. `OpenEQMount_V16_NSK7008AWDB_DB_SERVICE_CARTRIDGE_UNQUALIFIED.step` — **assembled 9-body bearing study**.
2. `OpenEQMount_V16_DB7008_INSTALLATION_SEQUENCE_UNQUALIFIED.step` — axial *exploded* ordering, not assembly fits.
3. Individual `V16_*.step` references for dimensions; `V16_NONLOAD_*.stl` files only for OrcaSlicer calibration.
4. `OpenEQMount_V16_DB_pair_section.png` for axial reference and `v16_db7008_engineering_report.json` for arithmetic assumptions.

Regenerate (Python 3.11; CadQuery in a dedicated Python environment):

```bash
python -m pip install 'cadquery>=2.5,<3' pytest trimesh matplotlib
python -m pytest -q tests/test_v16_db7008_cartridge.py
python hardware/cad/generate_v16_db7008_cartridge.py --out hardware/cad/v16_generated
python tools/dfam_gate_v16.py --dir hardware/cad/v16_generated --report hardware/cad/v16_generated/dfam-gate-report.json
python tools/render_v16_db.py
```

Open tracking: [ROT mechanical qualification Issue #4](https://github.com/Accelerator6666/OpenEQMount/issues/4).
