# OpenEQMount V1.8 — ROT shaft-to-camera positive-drive interface (Gate A only)

**Status: prototype_unqualified; NO camera / NO motor power / NO manufacture released.**

## Objective and change from V1.7

V1.7 mated a candidate NSK 7008AWDB bearing cartridge to the DEC bridge with provisional PCD110-to-PCD80 metal adapter. The camera end of the V1.6 cartridge remained an *unconnected floating blank*: merely rotating it in CAD did not create a physical torque or axial-force path. V1.8 replaces the floating blank and previous spindle (without overlapping them) with the following **conceptual metal** interface.

- Single continuous **metal spindle**: Ø40 journal over the two adjacent 7008AWDB envelopes, Ø30 through bore, integral Ø48 bearing shoulder, plus an **integral Ø110 × 8 mm output flange** at local ROT z=45–53 mm.
- Removable Ø122 × 8 mm **metal camera-side mounting blank** at z=53–61 mm, with nominal Ø36 central opening. This is **not a camera clamp**, Arca compatible saddle, or verified camera/lens cage mount.
- Two nominal Ø6 metal dowels at **PCD68**, diametrically opposed. Reference Ø6.2 holes are deliberately just visual clearance placeholders — they are **not** a permissible dowel fit recommendation. Dowel retained length/lead-in, exact holes, pressing method, material, shock/fretting/bearing and shear design remain pending.
- Six nominal **M6 through-bolt / nut envelope** stacks at **PCD90**, clocked 30° away from the two dowels. Models show cylindrical bolts/round nut envelopes, **not actual threads, metric hex nuts, hardened washers, torque specifications or lock hardware**. The bolts are intended to transfer axial retention force through metal and clamp the face; the pins add a prospective positive torque path. Structural adequacy and mutual load share are entirely unproven.

This configuration keeps 7008 bearing faces at local z=0–30 mm and the V1.6 provisional locknut region z=32–38 mm. The new flange begins at z=45 mm, leaving 7 mm nominal **axial** clearance to the *reference locknut envelope*; this is not a tool-access certification. A real locknut/washer/thread stack must be engineered, including preload and axial play. Manufacturer 7008AWDB (CN) is **not confirmed to have the required installed preload**.

### Reference dimensions (mm; NOT machining tolerances)

| Feature | Nominal |
| --- | ---: |
| Spindle OD / through ID | 40 / 30 |
| Integral hub flange OD / axial thickness | 110 / 8 |
| Removable camera blank OD / bore / thickness | 122 / 36 / 8 |
| Bolt count / nominal diameter / pitch circle | 6 / M6 / PCD90 |
| Bolt clearance hole | Ø6.6 (provisional) |
| Dowel count / nominal diameter / pitch circle | 2 / Ø6 / PCD68 |
| Dowel hole reference | Ø6.2 **NOT a fit specification** |
| Nominal minimum outer radial ligament of hub near bolt hole | 6.7 |
| Local z flange / camera blank | 45–53 / 53–61 |
| NSK 7008AWDB pair envelope | 40×68×30; a0=46.2 (load center distance, not physical spacing) |

The physical width of the matched pair is 30 mm and NSK lists normal axial internal clearance (CN); verify the *specific supplied designation* and preload before an engineered assembly. Manufacturer: https://www.nsk.com/engineering/products/bearings/ball-bearings/angular-contact-ball-bearings/matched-angular-contact-ball-bearings/7008awdb-apn.html

### Load path interpretation — IMPORTANT

```
[Camera + real independent metal clamp NOT DESIGNED]
   -> [removable metal camera blank]
        -> 2 pin contacts (positive torque concept; fit unqualified)
        -> 6 through-bolts/nuts (axial primary hold + face clamp, unqualified)
   -> [single continuous metal spindle + output flange]
   -> [matched DB bearing envelopes + existing provisional shoulder/locknut]
   -> [metal ROT stator] -> [V1.7 adapter] -> [DEC bridge]
```

**Independent payload fall arrest is still missing.** Failure of bolts, camera clamp, mounting interface, bearing housing or DEC bridge must NOT cause the camera/lens to fall. The dowel pins do not prevent axial separation on their own. Fit a separate engineered, rated, retained metal tether **from a verified camera cage/lens-collar strongpoint to an independent fixed support** with safe slack/routing throughout RA/DEC/ROT motion and meridian flip. Merely adding a metal eyelet does not qualify a catch system.

### Simplified torque example — not an engineering rating

With equal share across two pins at pitch radius r=34 mm, each pin sees an *illustrative tangential force*

\[F_{\rm pin}=T/(2r), \quad \tau_{\rm nominal}=F_{\rm pin}/(\pi d^2/4).\]

- T=0.785 N·m => ~11.5 N nominal/pin.
- T=2.4525 N·m => ~36.1 N nominal/pin.

This **excludes** pin clearance impact, one-pin-first loading, hole bearing stress, fretting, bending, fatigue, motor torque, shock from stops, camera off-axis acceleration, and the dynamic loads of a fall. Neither shear stress nor the manufacturer bearing rating establishes safe payload capacity.

## CAD reproducibility

```bash
python -m pip install 'cadquery>=2.5,<3' pytest trimesh matplotlib
python -m pytest -p no:cacheprovider -q tests/test_v18_positive_drive.py
python hardware/cad/generate_v18_positive_drive.py --out hardware/cad/v18_generated
python tools/dfam_gate_v18.py --dir hardware/cad/v18_generated --report hardware/cad/v18_generated/dfam-gate-report.json
python tools/render_v18.py
```

Files:
- `OpenEQMount_V18_THREE_AXIS_POSITIVE_DRIVE_CONCEPT_UNQUALIFIED.step` — 66 separated metal/reference solids in one **FreeCAD** assembly STEP.
- `OpenEQMount_V18_DEC_ROT_SHAFT_TO_CAMERA_JOINT_UNQUALIFIED.step` — 24 subassembly solids.
- `OpenEQMount_V18_LOCAL_SHAFT_TO_CAMERA_INTERFACE_UNQUALIFIED.step` — 16 conceptual coupling solids in local ROT coordinates.
- Dedicated shaft and camera blank STEP, axial/torsional `manifest.json`, three torque illustration cases, preview PNGs.
- **One nonstructural PETG calibration STL**: `v18_NONLOAD_DOWEL_PCD68_TRANSFER_COUPON_PRINT_FLAT.stl` (horizontal bed XY/Z0, 3 mm thick, through holes, no field load, no metal preload). After slicing, record as-printed hole XY sizes and keep off the operational mount.

**DfAM Gate A is only an automated CAD/STL/data check**; Gate B printed fit, assembly path, tool access and Gate C physical stiffness, bearing thermal/preload, bolt fatigue, vibration, stop impact, drop-retention/line routing and tracking error are **PENDING**.

## Blocking work for V1.9 / physical prototype

1. Confirm reducer OEM output clocking/holes and purchased NSK bearing pairing, contact angle, internal clearance/preload and abutment geometry.
2. Detailed shaft machining design: bearing seats/shoulder radii, stress concentration, flange fillets and access to the lower locknut; GD&T, material and surface finishes.
3. Select supplier dowel hardware + interference/slip fit by material, pin retention against migration, appropriate torque margins and assembly service method; validate real fasteners, joint axial load, tightening and prevention of loosening.
4. Choose a **real camera cage/clamp and lens collar**, measure CG and flange-to-cage clearance, implement an independent metal fall-arrest path with safe cable slack at ±150° ROT.
5. Check full three-axis pose sweep and mechanical hard stops, then complete physical Gate B and Gate C with dummy weights, **before any expensive optics/power**.

**Do not treat these CAD nominal coordinates as a manufacturing drawing or an approved 3–5 kg load rating.**
