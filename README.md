# OpenEQMount — 开源双轴摄影赤道仪

**当前版本：V0.3 / FDM 3D 打印 RA/DEC 减速器接口试装原型，尚未经过真实负载与安全验证。**

用途已经确定：**广角星野摄影；目标摄影载荷 3–5 kg；最长焦距 ≤500 mm**。这些属于研发目标，不是量产参数或已确认的安全载荷。项目以德式双轴赤道仪 (GEM) 为基础，拟使用 RA/DEC 独立谐波减速器 + 3:1 同步带传动，第一阶段优先兼容 OnStepX 生态。

## V0.2 机械选型

| Axis | Candidate reducer | Rated output torque | Output bearing moment | Nominal outline |
|--|--|--:|--:|--|
| RA | CSF-17-100-2UH | 24 Nm | 64 Nm | Ø79 x 45 mm |
| DEC | CSF-14-100-2UH | 7.8 Nm | 41 Nm | Ø73 x 41 mm |

Both have 100:1 ratios and integrated crossed-roller output bearings. Official source [CSF reducer catalogue](https://www.harmonicdrive.net/products/gear-units/gear-units/csf-2uh). Actual drive/bracket interfaces **are NOT yet in CAD**.

## V0.2 CAD preview

![CAD concept](hardware/cad/generated/OpenEQMount_V02_iso.png)

The `hardware/cad/` folder contains **editable CadQuery Python source**, separate STEP components, a combined STEP conceptual assembly, STL shape-prototype files, and three PNG previews. V0.2 shows a **fixed** parametric latitude wedge at 35°, reconfigurable at generation to 25–60°; a functional, continuously adjustable polar wedge remains to be designed.

## Quick start

```bash
python -m unittest discover -s tests -v
python tools/mount_sizing.py
python tools/motion_math.py
pip install 'cadquery>=2.5,<3'
python hardware/cad/generate_v02.py --latitude 35 --out hardware/cad/generated
```

`cad-build.yml` rebuilds concept STEP/STL and uploads them as **GitHub Actions artifacts**, not as machining-ready parts. For rendered local previews, install VTK and run `xvfb-run -a python tools/render_cad_preview.py` on Linux.

### Engineering files

- [V0.2 calculations, reducer choice, and design gates](docs/mechanical-v02.md)
- [Parametric CAD source](hardware/cad/generate_v02.py) / [editable dimensions](hardware/cad/params.py)
- [V0.2 initial bill of materials](hardware/bom/bom-v02.csv)
- [V0.1 project architecture](docs/architecture.md) / [test plan](docs/test-plan.md) / [roadmap](docs/roadmap.md)
- [Motor ratio / angular-step calculator](tools/motion_math.py)

## Safety and design status

This is **NOT a functional mount**. There are no verified fastener patterns or tolerance fits, belt routing and tensioner geometry, lat/az moving adjuster, collisions, camera clamp, counterweight/brake, power-loss retention, or real tracking-error measurements. Do **not** use CAD output to mount valuable camera equipment without redesign, analysis and bench testing. The strain-wave gear cannot be assumed to self-lock. A 0.3375 arcsec commanded microstep is NOT physical tracking accuracy.

No vendor CAD or third-party source is included. Hardware/software open-source license selection is pending and should be completed before third-party redistribution.

## V0.3 — 3D printed reducer interface prototypes (2026-10-18)

> ⚠️ These are **bench-fit prototypes ONLY**. The RA–DEC load-carrying joint, wave-generator input shafts, adjustable polar wedge and tripod clamp are **not implemented or safety/load-verified**. Do not attach an optical payload or run powered GoTo.

For 3–5 kg target starfield cameras <=500 mm focal length, V0.3 designs individual
printable RA CSF-17 and DEC CSF-14 OEM 2UH interfaces:

- rear mounting housing with factory bolt patterns (RA PCD71, DEC PCD65, 6×M4 each), clearance sleeve
- output bolt adapters (RA PCD27 6×M5, DEC PCD23 6×M4) with counterbored screw pockets
- NEMA17 slotted motor carriages with 31×31mm mounting holes and ±5mm belt adjustment
- optional input shaft bearing bridge (for verified input shaft design **only**)
- printer tolerance coupons for reducer bores and 608/626 auxiliary bearing fits

**START HERE:** [`docs/mechanical-v03-3dprint.md`](docs/mechanical-v03-3dprint.md).

```bash
python -m pip install 'cadquery>=2.5,<3' pytest
python -m pytest -q tests/test_v03_mechanics.py
python hardware/cad/generate_v03.py --out hardware/cad/v03_generated
```

BOM: [`hardware/bom/bom-v03-print.csv`](hardware/bom/bom-v03-print.csv).
CAD: [`hardware/cad/generate_v03.py`](hardware/cad/generate_v03.py).
Automation: [`.github/workflows/cad-v03.yml`](.github/workflows/cad-v03.yml).
