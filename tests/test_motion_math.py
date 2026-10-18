import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
from motion_math import AxisModel, SIDEREAL_DAY_SECONDS


class MountKinematicsTests(unittest.TestCase):
    def test_reduction(self):
        axis = AxisModel()
        self.assertEqual(axis.gear_ratio, 300.0)
        self.assertEqual(axis.commanded_steps_per_axis_rev, 3_840_000)

    def test_resolution(self):
        self.assertAlmostEqual(AxisModel().ideal_arcsec_per_step, 0.3375, places=7)

    def test_sidereal_one_revolution(self):
        axis = AxisModel()
        self.assertAlmostEqual(axis.sidereal_steps_per_second() * SIDEREAL_DAY_SECONDS,
                               axis.commanded_steps_per_axis_rev, places=4)

    def test_degree_slew(self):
        axis = AxisModel()
        self.assertAlmostEqual(axis.slew_steps_per_second(1.0), axis.steps_per_degree)

    def test_reject_zero_gear_ratio(self):
        with self.assertRaises(ValueError):
            AxisModel(harmonic_ratio=0)


if __name__ == '__main__':
    unittest.main()
