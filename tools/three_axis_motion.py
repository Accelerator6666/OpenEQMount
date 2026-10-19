"""OpenEQMount V0.9 3-axis *simulation*, no IO or motor drive.

Coordinates are continuous mount joint angles, not RA/Dec celestial coordinates.
Never identify this output as firmware, tracking accuracy or a safety interlock.
A real controller needs absolute/reference homing, watchdog, measured end stops,
independent power removal, and verified pier/rotator cable paths.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

SIDEREAL_DAY_SECONDS = 86164.0905
SIDEREAL_RATE_DEG_PER_S = 360.0 / SIDEREAL_DAY_SECONDS

class MotionRefused(ValueError):
    """An intentionally refused simulated command."""

@dataclass(frozen=True)
class Axis:
    name: str
    minimum_deg: float
    maximum_deg: float
    max_speed_deg_s: float

    def validate(self, value: float) -> None:
        if not isfinite(value) or not self.minimum_deg <= value <= self.maximum_deg:
            raise MotionRefused(f'{self.name} target {value} outside [{self.minimum_deg},{self.maximum_deg}]')

# Prototype *software* soft boundaries, not verified physical travel limits.
AXES = (
    Axis('RA', -160.0, 160.0, 2.0),
    Axis('DEC', -85.0, 85.0, 2.0),
    Axis('ROT', -160.0, 160.0, 3.0),
)

@dataclass(frozen=True)
class JointPose:
    ra_deg: float
    dec_deg: float
    rot_deg: float

    @property
    def angles(self):
        return (self.ra_deg, self.dec_deg, self.rot_deg)

    def validate(self):
        for axis, value in zip(AXES, self.angles):
            axis.validate(value)

@dataclass(frozen=True)
class ThreeAxisPlan:
    origin: JointPose
    target: JointPose
    duration_s: float

    def sample(self, elapsed_s: float) -> JointPose:
        if not isfinite(elapsed_s):
            raise MotionRefused('Invalid sampling time')
        t = max(0.0, min(elapsed_s / self.duration_s, 1.0)) if self.duration_s else 1.0
        easing = t*t*(3.0 - 2.0*t)  # bounded smoothstep; zero speed at ends
        a=self.origin.angles
        b=self.target.angles
        return JointPose(*(start+(end-start)*easing for start,end in zip(a,b)))


def plan_synchronized_move(origin: JointPose, target: JointPose, *,
                           homed: bool=False, enabled: bool=False) -> ThreeAxisPlan:
    """Plan a virtual coordinated point-to-point move; NEVER issue motor pulses.

    Deliberately does not wrap ROT by 360: cable envelope is physically bounded.
    Does not calculate celestial RA/Dec, meridian flip or field derotation.
    Peak smoothstep derivative is 1.5, used for minimum travel time.
    """
    if not homed or not enabled:
        raise MotionRefused('Digital interlock: all axes require homed + explicitly enabled')
    origin.validate()
    target.validate()
    durations=[1.5 * abs(b-a)/axis.max_speed_deg_s
               for axis,a,b in zip(AXES,origin.angles,target.angles)]
    duration=max(durations, default=0.0)
    return ThreeAxisPlan(origin,target,duration)


def normalize_position_angle(angle_deg: float) -> float:
    """Only for sky PA UI, never mechanical travel or cable rotation limits."""
    if not isfinite(angle_deg):
        raise MotionRefused('Invalid position angle')
    return angle_deg % 360.0


def requested_rot_mechanical_angle(pa_deg: float, *,
                                    zero_pa_deg: float, zero_mechanical_deg: float,
                                    sign: int=1) -> float:
    """Calibration-dependent PA conversion, no pier-flip assumptions.

    Caller must separately determine parity/pier orientation and reject unresolved
    360-degree aliases; *no* modulo is applied to the mechanical axis.
    """
    if sign not in (-1,1) or not all(map(isfinite, (pa_deg,zero_pa_deg,zero_mechanical_deg))):
        raise MotionRefused('Invalid rotator calibration')
    target=zero_mechanical_deg + sign*(pa_deg-zero_pa_deg)
    AXES[2].validate(target)
    return target


def optical_axis_mount_vector(ra_deg: float, dec_deg: float) -> tuple[float,float,float]:
    """Toy orientation: DEC rotation about local X, then RA about Z.

    Used for axis-orthogonality verification, not pointing calibration.
    """
    from math import radians, sin, cos
    if not isfinite(ra_deg) or not isfinite(dec_deg):
        raise MotionRefused('Non-finite optical axis angle')
    ra,dec=radians(ra_deg),radians(dec_deg)
    return (sin(ra)*sin(dec), -cos(ra)*sin(dec), cos(dec))


def dec_axis_mount_vector(ra_deg: float) -> tuple[float,float,float]:
    """Toy orientation of DEC axis after RA rotation."""
    from math import radians, sin, cos
    if not isfinite(ra_deg): raise MotionRefused('Non-finite RA angle')
    a=radians(ra_deg)
    return (cos(a),sin(a),0.)
