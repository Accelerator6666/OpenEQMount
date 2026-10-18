"""OpenEQMount V0.2 parametric concept envelope. Millimetres, kg, Nm.

NOTE: Nominal supplier dimensions are VISUAL ENVELOPES, not mounting interfaces.
Obtain manufacturer's verified STEP / confirmation drawings before cutting metal.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class MountParams:
    # Adjustable by regenerating the concept CAD; V0.2 wedge is NOT a moving adjuster.
    latitude_deg: float = 35.0
    base_width: float = 126.0
    base_depth: float = 114.0
    base_thickness: float = 12.0
    wedge_width: float = 74.0
    wedge_half_depth: float = 19.0
    wedge_origin_y: float = -10.0
    wedge_top_z_center: float = 61.0
    # Gearbox nominal body envelopes (official CSF-2UH PDF dimensions)
    ra_gear_diameter: float = 79.0
    ra_gear_length: float = 45.0
    dec_gear_diameter: float = 73.0
    dec_gear_length: float = 41.0
    # Empty gearbox interface space is indicative, not fitted bearing seat.
    ra_housing_od: float = 96.0
    ra_housing_id: float = 80.5
    ra_housing_length: float = 52.0
    dec_housing_od: float = 91.0
    dec_housing_id: float = 74.5
    dec_housing_length: float = 49.0
    dec_axis_z_local: float = 125.0
    # No clamp geometry is assumed: saddle is an adapter blank.
    saddle_width: float = 65.0
    saddle_length: float = 100.0

    def validate(self) -> None:
        if not 25.0 <= self.latitude_deg <= 60.0:
            raise ValueError('V0.2 fixed wedge is defined only for latitude 25–60 deg.')
        if self.ra_housing_id <= self.ra_gear_diameter:
            raise ValueError('RA envelope has no diametral clearance')
        if self.dec_housing_id <= self.dec_gear_diameter:
            raise ValueError('DEC envelope has no diametral clearance')
        if self.wedge_top_z_center - (self.wedge_half_depth / __import__('math').tan(__import__('math').radians(self.latitude_deg))) <= self.base_thickness + 3:
            raise ValueError('Wedge geometry intersects the base')

PARAMS = MountParams()
