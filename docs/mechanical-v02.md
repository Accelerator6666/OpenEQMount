# OpenEQMount V0.2 — Mechanical Concept & Sizing (2026-10-18)

> **STATUS: geometry/layout proof of concept, not an assembly drawing, CNC production dataset or approved bill of materials.** Existing CAD includes intentional overlap between gearbox **envelopes** and adapter/housing concepts, but **no gear-mating bolt patterns, bearing fits, working drive path, running clearance test, load analysis or validated polar adjuster**. Do not build a loaded mount from these solids unchanged.

## Use case

- Imaging payload **3–5 kg**, total including camera, lens/telescope, rail, guiding and cables; no demonstrated real payload rating.
- Longest intended focal length **≤500 mm**; star tracking/guide performance will require real astrophotography testing.
- GEM / RA+DEC dual driven strain-wave reducer; photographic carry-on/field use is a design aspiration, not an achieved mass rating.
- V0.2 concept uses **reprintable fixed latitude wedge, default 35°**, adjustable in CAD within **25–60°**. Final version must use a **mechanical hinge, lead screw and azimuth adjuster**: do not call the wedge an operable adjustable mount.

## Reducer selection from manufacturer

| Parameter | RA | DEC |
|--|--:|--:|
| Model | CSF-17-100-2UH | CSF-14-100-2UH |
| Harmonic ratio | 100 | 100 |
| Rated output torque (L10), Nm | 24.0 | 7.8 |
| Repeated peak output torque, Nm | 54 | 28 |
| Built-in bearing allowable tilting moment, Nm | 64 | 41 |
| Standard mass, kg | 0.68 | 0.52 |
| Outline max diameter, mm | 79 | 73 |
| Outline overall axial length, mm | 45 | 41 |
| Official model drawing | https://www.harmonicdrive.net/_hd/Content/caddownloads/dxf/csf-2uh_gearheads/csf-17-xx-2uh.pdf | https://www.harmonicdrive.net/_hd/Content/caddownloads/dxf/csf-2uh_gearheads/csf-14-xx-2uh.pdf |
| Data table | https://www.harmonicdrive.net/products/gear-units/gear-units/csf-2uh | https://www.harmonicdrive.net/products/gear-units/gear-units/csf-2uh |

Use those sketches only as procurement references. Some manufacturers substitute reducer models and change input bore/output bolt pattern; **validate an exact delivered part number and supplier confirmation drawing**. No vendor CAD or other party's artwork is redistributed here.

## Preliminary separate load checks

Assumptions illustrate mass-center effect; they are NOT a substitute for calculating actual complete-axis free-body diagrams, shock and dynamic loads.

1. **DEC drive static worst orientation**: 5 kg x 9.80665 m/s² x 50 mm net imbalance = **2.45 N·m** vs **7.8 N·m** rated (**3.18x** ratio). With **150 mm net imbalance**, moment rises to **7.35 N·m** (only **1.06x** ratio). **Balance DEC**; do not install a 5-kg payload cantilevered 150 mm away from the DEC axis without reconsidering the drive size and safety.
2. **RA drive static worst orientation**: assume 6.5 kg effective axis load at 100 mm net gravity torque arm = **6.37 N·m** vs **24 N·m** rated (**3.76x** ratio). The figure depends on entire RA-moving assembly and its actual CG, not merely camera weight.
3. **Output bearing tilting moment**: illustrative **RA 6.5 kg x 200 mm = 12.75 N·m** vs **64 N·m allowable**, and **DEC 5 kg x 180 mm = 8.83 N·m** vs **41 N·m allowable**. Only one simplified moment component is shown; net 3-D applied moment, axial/radial loads, structural compliance and bearing-life requirements must be verified.
4. Torsional stiffness, cable drag, power-loss backdrive, gust and shock loads, thermal changes and tracking error are not modeled. Gearbox nominal positioning accuracy of **1.5 arcminutes** is **not** sub-arcsecond tracking accuracy. Need encoder and PHD2 real-sky measurements.
5. If loading can exceed assumed offsets, redesign (e.g. more balancing, counterweight / larger reducer / brake). Do not count on a strain-wave reducer as a failsafe brake.

## Motor and belts (unverified packaging)

- Initial drivetrain for BOTH axes: 1.8° stepper, **20-tooth GT2 motor pulley**, **60-tooth GT2 reducer-input pulley**, **100:1 strain wave**, total **300:1**. Pulley radius and rear input hardware must be checked against delivered shaft geometry; CAD currently contains motors **only** as block envelopes and **does not model belts**.
- Nominal shaft-to-shaft layout distance **76 mm RA, 69 mm DEC**. Ideal open-belt length from pulley pitch diameters approximately **234 mm RA, 220 mm DEC**. Select a commercially offered closed belt only after measuring actual motor placement and achieving ±3–5 mm practical tensioning slots; those distances in the current solids are layout points, not validated output geometry.
- Baseline **200 full steps/rev x 64 microsteps x 300 gear = 3,840,000 command increments/axis rev**. Ideal command increment **0.3375 arcsec** and RA sidereal command frequency **44.566 microsteps/sec**; physical microstep linearity and gearbox error are not included.
- NEMA17 is a **frame pattern**, not a sufficient torque/current specification. Test selected motors under thermal load at the chosen voltage and slew speed; no motor torque approval at this stage.

## Geometry deliverables and limits

| Model element | V0.2 content | Must add before manufacture |
|--|--|--|
| Base | 126 x 114 x 12 mm plate, four generic Ø6.6 clearance holes | exact tripod 3/8-16 / M10 adapter, clamping stack, anti-rotation feature |
| Latitude | Fixed CAD-parametric 35° wedge (25–60° can be regenerated) | worm/lead screw latitude hinge with positive retention, altitude limit, azimuth fine adjust |
| RA unit | 79 x 45 mm reducer envelope inside Ø96 mm housing ring | exact drawing-dependent flange seats, fasteners, register tolerances, tool access |
| RA output | simplified output disk and 132 mm crosshead | real output flange attachment and RA-balance/optional counterweight feature |
| DEC unit | 73 x 41 mm reducer envelope inside Ø91 mm housing ring | true fastening, collision-free motor mount and support-to-reducer load path |
| Camera | 65 x 100 mm plain adapter plate with provisional clearance holes | off-the-shelf Vixen saddle or selected direct Arca clamp with rated positive safety stop |
| Electromech | two orange motor block envelopes | real stepper mounting, belt/guard, cable exits, home/hard limits, flex relief |

**Important:** The CAD files **are not watertight assembled hardware in the engineering sense** (they include coincident / overlapping conceptual parts); exported printable STLs are *prototype shapes*, not release-to-production units. The vendor reducers shown as gray solid cylinders do not represent internal shafts. CAD does not establish rotation of either axis or independent motion in an assembly solver.

## Mechanical design next gates

1. Acquire supplier PDF + *native STEP* for the exact reducer variant; check output mounting screw location and shaft bore at incoming inspection.
2. Choose **physical camera clamp standard** (Vixen or Arca-Swiss), retaining/safety stops and exact bolt pattern. For a 500 mm imaging setup, a proper Vixen rail may be preferable to a simple ballhead.
3. Select fabrication: recommend 6061-T6 CNC for reducer seats / RA-to-DEC structural join; PETG-CF or PA-CF printed prototype **for fit checking only**, not load-bearing flight parts without destructive validation.
4. Implement the **real** latitude hinge/azimuth adjuster, wire routing and hard collision limits; measure polar height range and telescope pier collision in CAD.
5. Full FEA or hand calcs for fasteners, rail retention, stacked gravity force and shock factors; verify counterweight / parking strategy and fail-safe retention in case of loss of power.
6. Assemble motor test rig with reduction and instrument guide tracking; pursue under-500 mm real-sky exposures only after safe bench loading.
