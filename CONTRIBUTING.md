# Contributing

Before submitting changes, open an issue describing the module and hardware revision. Attach clear before/after photos or schematics for hardware changes, and test logs for firmware changes. Do not present untested load ratings or mechanical drawings as certified. All moving-axis safety changes require a documented failure-mode review.

## DfAM is mandatory for all 3D-printed parts

All PRs adding or changing printable geometries MUST satisfy [`docs/dfam-design-standard.md`](docs/dfam-design-standard.md). Include print orientation, expected layer-load path, overhang/slicer review, actual wall/rib measurements, metal fastening scheme, calibration coupon, STEP/STL, generated manifest and the automated `tools/dfam_gate.py` report. A passed mesh test NEVER represents field safety certification. V0.2 concept STLs must not be reintroduced as printable artefacts.
