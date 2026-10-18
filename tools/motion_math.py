"""Idealized mount kinematics used for early system sizing, NOT live motion control."""
from dataclasses import dataclass

SIDEREAL_DAY_SECONDS = 86164.0905  # approximate mean sidereal day, s

@dataclass(frozen=True)
class AxisModel:
    full_steps_per_rev: int = 200
    microsteps: int = 64
    harmonic_ratio: float = 100.0
    belt_ratio: float = 3.0

    def __post_init__(self):
        if (self.full_steps_per_rev <= 0 or self.microsteps <= 0
                or self.harmonic_ratio <= 0 or self.belt_ratio <= 0):
            raise ValueError('All parameters must be positive')

    @property
    def gear_ratio(self) -> float:
        return self.harmonic_ratio * self.belt_ratio

    @property
    def commanded_steps_per_axis_rev(self) -> float:
        return self.full_steps_per_rev * self.microsteps * self.gear_ratio

    @property
    def steps_per_degree(self) -> float:
        return self.commanded_steps_per_axis_rev / 360.0

    @property
    def ideal_arcsec_per_step(self) -> float:
        return 360.0 * 3600.0 / self.commanded_steps_per_axis_rev

    def sidereal_steps_per_second(self) -> float:
        return self.commanded_steps_per_axis_rev / SIDEREAL_DAY_SECONDS

    def slew_steps_per_second(self, deg_per_second: float) -> float:
        return self.steps_per_degree * deg_per_second


def main():
    axis = AxisModel()
    print(f'Total reduction: {axis.gear_ratio:.1f}:1')
    print(f'Commanded steps / axis revolution: {axis.commanded_steps_per_axis_rev:.0f}')
    print(f'Steps / degree: {axis.steps_per_degree:.6f}')
    print(f'Sidereal tracking steps / second: {axis.sidereal_steps_per_second():.6f}')
    print(f'Ideal arcsec / commanded step: {axis.ideal_arcsec_per_step:.6f}')
    print('NOTE: Mathematical command resolution is NOT real-world tracking accuracy.')


if __name__ == '__main__':
    main()
