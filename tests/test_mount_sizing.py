import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from mount_sizing import RA,DEC,gravity_torque,margin,arcsec_per_microstep,open_belt_length_mm

class TestSizing(unittest.TestCase):
    def test_ra_margin(self): self.assertGreater(margin(RA.rated_torque_nm,gravity_torque(6.5,.1)),3.5)
    def test_dec_margin(self): self.assertGreater(margin(DEC.rated_torque_nm,gravity_torque(5,.05)),3)
    def test_unbalanced_dec(self): self.assertLess(margin(DEC.rated_torque_nm,gravity_torque(5,.15)),1.1)
    def test_belt(self):
        self.assertTrue(230<open_belt_length_mm(76)<240)
        self.assertTrue(215<open_belt_length_mm(69)<225)
    def test_angular_quantization(self):self.assertTrue(math.isclose(arcsec_per_microstep(),0.3375,rel_tol=1e-9))
    def test_bad_input(self):
        with self.assertRaises(ValueError):gravity_torque(-5,0.1)

if __name__=='__main__': unittest.main()
