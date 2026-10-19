# OpenEQMount V0.4 — RA/DEC orthogonal frame (DfAM structural-architecture prototype)

**Release state: ENGINEERING BENCH-FIT ONLY, NOT LOAD RATED.** A 3–5 kg photographic payload and ≤500 mm focal length are design *targets*, not permitted operating loads. **No telescope, camera, or payload may be mounted using these prototype components before Gate B/C and a dedicated retention design are completed.**

## What V0.4 actually delivers

- Parametric `hardware/cad/generate_v04.py`, 5 bed-oriented FDM bench pieces (2 identical removable side covers, RA/DEC bolt-pattern drill templates, hole-size calibration coupon), their editable STEP and STL files.
- 8 **metal-only** STEP models: one RA metal output plate, one DEC metal rear plate, two XZ plane side webs, two RA L-angle cleats, two DEC L-angle cleats; overall layout STEP.
- Separate machine-readable DfAM manifest and digital Gate A (`tools/dfam_gate_v04.py`), verification tests and build workflow.
- Metal profiles are indicative; **not production-ready machining drawings**. Bolt clocking, fits, manufacturer screw engagement and plate/angle section dimensions must be reviewed after physical hardware arrives.

## Coordinate, envelope and interfaces

Coordinates in millimetres: global RA output plane Z=0; RA rotates about +Z. DEC reducer rear flange plane X=117; DEC turns about +X; DEC center `(Y=0, Z=112)`. This is a **90° orthogonal concept**, not a complete equatorial mount with collision swept volumes, shaft drive, latitude wedge, cabling or counterweight.

| Model item | Nominal interface | Caution |
|---|---|---|
| RA output plate | 150×150×5 mm AL; 6 × Ø5.5 PCD Ø27 M5 to OEM flange; Ø12 cable pilot | Axial clearance/cable routing and screw head/washer seating require physical inspection |
| DEC rear plate | 150×150×5 mm AL; Ø54 wave-generator opening; 6 × Ø4.5 PCD Ø65 M4 to OEM | Radial ligament between the Ø54 aperture and threaded-hole circle is only approx 3.25 mm to the edge of a Ø4.5 hole; **engineering review required** |
| Two metal side webs | 5 mm AL sheet, side print-profile projection 167×145 mm; M5 at `(-25,10),(35,10),(102,55),(102,117)` in print coordinates; assemble with +10 mm Z offset in XZ | Plate/angle outboard connector load path is preliminary |
| Printed side covers | 8 mm flat-on-bed XY profile, 167×145×8 mm; Ø11 bolt-head windows | Do NOT clamp plastic in the metal structural bolt path |
| RA angle cleats | 4 mm preliminary section; M5 connection to metal plate and side web | 2 mm shim gaps are *nominal* and must be checked with actual metal lengths |
| DEC angle cleats | 5 mm preliminary section; M5 connection to DEC metal plate and side web | Off-the-shelf angle section may require redesign; no claimed fitting standard |

**Critical conceptual metal force path:** rotating RA metal factory output → 150 mm RA metal plate → M5 metal-to-metal RA cleats → 5 mm metal side webs → M5 metal DEC cleats → metal DEC plate → DEC factory threads. FDM covers and printed drill templates are explicitly *outside* the primary load path. The real retaining/torque path within DEC and both gear units is still unverified. Compressive contact/bending and hardware classes also require review.

## DfAM fabrication approach

1. **Orientation:** print both cheek covers laying flat on the XY bed, Z thickness=8 mm. The 167×145 mm outline fits 220×220 beds. The printed XY hoop and triangulated ribs are only alignment and cover features, not structural credentials.
2. **Material:** PETG only for bench fits and coupons. PLA is not permitted for field structural brackets. Final material choice requires temperature, UV, creep, fiber orientation, nozzle and printer qualification.
3. **Support & relief:** broad lower face, through-bores perpendicular to bed, open triangular relief to limit mass. Check islands, slopes and extrusion continuity in the actual slicer; no automatic support-free claim.
4. **Bolt and layer strategy:** structural bolts clamp **metal to metal**; cheek covers have Ø11 cutouts around M5 hardware, fasten only with two independently serviced M3 screws per cover into metal. Never use hot-insert nuts in primary lift/fall-restraint joints.
5. **Print calibration:** gauges for Ø4.4, Ø4.6, Ø5.4, Ø5.6 mm; record measured bore diameters and deviation by printer/filament batch; no universal tolerance assumed.
6. **Assembly:** verify full tool and fastener access with real fasteners; check 2 mm outboard rail shims before clamping. Plastic may not prevent metal hardware service access or take tightening preload.

## Factory hole pattern pending verification

- RA CSF-17-100-2UH output uses nominal 6 × M5 on PCD Ø27 from earlier design data; DEC CSF-14-100-2UH rear uses 6 × M4 on PCD Ø65; **thread/clearance phase, allowable screw engagement and true rear input bore must be compared to the purchased units and latest supplier drawings before drilling metal**.
- The DEC Ø54 through opening and rear M4 hole ligament require a serious plate-specific bending/tear-out/fastener-bearing review. An OEM-matched steel backer or revised rear plate may be necessary.
- No motor pulley, harmonic wave-generator drive, RA polar wedge, counterweight, cable slip/strain management, anti-tip or independent safety harness is designed or approved in V0.4.

## Minimum sign-off sequence

- **Gate A:** CAD watertight, bed aligned, part inventory and DfAM metadata; automated CI PASS means *geometrically consistent only*.
- **Gate B:** printer+material-specific slice review, gauges, physical hole clocks/bolts and plate-to-angle shim verification, assembly tooling access. Attach photographs and measured results to GitHub issue #1.
- **Gate C:** metal section/source certificate; joint/bolt preload and fatigue analysis; FEA with actual optical payload and orientation; static and dynamic bench rig; thermal creep, vibration and fall-retention tests. Signed field safety acceptance required *before* any live equipment use.

### Build commands

```bash
python -m pip install 'cadquery>=2.5,<3' trimesh pytest
python hardware/cad/generate_v04.py --out hardware/cad/v04_generated
python tools/dfam_gate_v04.py --dir hardware/cad/v04_generated --report hardware/cad/v04_generated/dfam-gate-report.json
python -m pytest -q tests/test_v04_frame.py
```
