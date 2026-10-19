# OpenEQMount — Engineering Agent Rules

This file is binding for any person, coding agent, CAD generator, pull request, and automation that creates or changes a 3D-printable part.

## DfAM is mandatory; CAD is not field qualification

- Read `docs/dfam-design-standard.md` before editing any FDM model.
- Specify material, part orientation, XY/Z stress direction, build plate interface, no-support strategy, critical minimum wall and boss dimensions, metal joints, assembly access, service/replacement strategy, fit coupons and documented risks.
- Prefer integrated XY-plane ribs/gussets and radiused transitions to sharp lugs or excessive infill. Do not presume 45-degree overhangs are universally support-free.
- Any part in the mechanical retention path must use appropriately engineered metal fasteners, plates and independent fail-safe retention. Printed threads and untested heat-set inserts must NOT be sole tensile/cyclic retention.
- Every new printable part requires editable parameterized source, STEP, bed-aligned STL, a `manifest.json` DfAM record, unit tests and a passing `tools/dfam_gate.py` Gate A.
- Gate A only means digital geometry/metadata checks; per-part slicer inspection and physical fit (Gate B), structural/creep/thermal/dynamic tests and safety sign-off (Gate C) are separate and mandatory.
- Keep status `prototype_unqualified` until linked Gate B/C evidence supports any other state; never claim a 3–5 kg payload rating or observation readiness without physical testing.
- Do not reintroduce historic V0.2 concept STL files as production print files. Respect reducer vendor-specific hole geometry and supplied drawings; do not substitute a 'similar' unit without dimension verification.
- Any change in load, material, nozzle, print orientation, fastener, bearing interface or motor mount requires review of relevant tests and documentation.

## Before submitting CAD changes

```bash
python -m pip install 'cadquery>=2.5,<3' pytest trimesh
python hardware/cad/generate_v03.py --out hardware/cad/v03_generated
python tools/dfam_gate.py --report hardware/cad/v03_generated/dfam-gate-report.json
python -m pytest -q
```

Track pending slicer and mechanical acceptance in [issue #1](https://github.com/Accelerator6666/OpenEQMount/issues/1).

## V0.4 Gate A additional requirements
- Treat printed V0.4 cheek covers and drill gauges as **nonstructural**. The primary RA-to-DEC path must remain metal-to-metal. Do not trap printed polymer under metal bolt preload.
- Keep source `hardware/cad/generate_v04.py`, Gate A checker `tools/dfam_gate_v04.py`, and tests `tests/test_v04_frame.py` in sync. The metal part STEP files are **provisional**, not machining-release drawings.
- Before merging changes to V0.4: `python hardware/cad/generate_v04.py --out hardware/cad/v04_generated && python tools/dfam_gate_v04.py --dir hardware/cad/v04_generated --report hardware/cad/v04_generated/dfam-gate-report.json && python -m pytest -q tests/test_v04_frame.py`.
- Only Gate A is automated. Do not mark Gate B or C qualified without physical measurements and safety evidence.
