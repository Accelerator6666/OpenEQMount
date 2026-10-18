#!/usr/bin/env python3
"""Preliminary worst-orientation gravity sizing, NOT FEA or safety certification."""
from dataclasses import dataclass
from math import pi
G=9.80665
SIDEREAL_DAY=86164.0905

@dataclass(frozen=True)
class Reducer:
    model: str
    rated_torque_nm: float
    allowed_moment_nm: float
    mass_kg: float
    diameter_mm: float
    length_mm: float
    ratio: float = 100

RA=Reducer('CSF-17-100-2UH',24,64,0.68,79,45)
DEC=Reducer('CSF-14-100-2UH',7.8,41,0.52,73,41)

def gravity_torque(mass_kg:float, offset_m:float)->float:
    if mass_kg<0 or offset_m<0: raise ValueError('Nonnegative values required')
    return mass_kg*G*offset_m

def margin(limit_nm:float,actual_nm:float)->float:
    return float('inf') if actual_nm==0 else limit_nm/actual_nm

def belt_pitch_diameter_mm(tooth_count:int,pitch_mm:float=2.0)->float:
    if tooth_count<=0 or pitch_mm<=0:raise ValueError('Invalid timing pulley')
    return tooth_count*pitch_mm/pi

def open_belt_length_mm(center_mm:float,small_teeth:int=20,large_teeth:int=60,pitch_mm:float=2.0)->float:
    # Approximation, not a vendor belt selector.
    if center_mm<=0:raise ValueError('Invalid center distance')
    d=belt_pitch_diameter_mm(small_teeth,pitch_mm)
    D=belt_pitch_diameter_mm(large_teeth,pitch_mm)
    if 2*center_mm<=D-d:raise ValueError('Pulley center distance too small')
    return 2*center_mm + pi*(D+d)/2 + (D-d)**2/(4*center_mm)

def arcsec_per_microstep(stepper_full_steps=200,microsteps=64,reduction=300):
    return 1296000.0/(stepper_full_steps*microsteps*reduction)

def main():
    ra_t=gravity_torque(6.5,0.10)  # camera + part DEC mass, net RA offset
    de_t=gravity_torque(5,0.05)  # after balancing camera on DEC axis
    ra_m=gravity_torque(6.5,0.20) # load's overhung distance, output bearing
    de_m=gravity_torque(5,0.18)
    print(f'RA worst gravity drive torque (assumed): {ra_t:.2f} N*m / {RA.rated_torque_nm} Nm, ratio={margin(RA.rated_torque_nm,ra_t):.2f}')
    print(f'DEC worst gravity drive torque (assumed): {de_t:.2f} N*m / {DEC.rated_torque_nm} Nm, ratio={margin(DEC.rated_torque_nm,de_t):.2f}')
    print(f'RA output bearing moment (assumed): {ra_m:.2f} N*m / {RA.allowed_moment_nm} Nm, ratio={margin(RA.allowed_moment_nm,ra_m):.2f}')
    print(f'DEC output bearing moment (assumed): {de_m:.2f} N*m / {DEC.allowed_moment_nm} Nm, ratio={margin(DEC.allowed_moment_nm,de_m):.2f}')
    print(f'DEC 5kg at 150mm off axis: {gravity_torque(5,0.15):.2f} N*m -> only {margin(DEC.rated_torque_nm,gravity_torque(5,0.15)):.2f}x rated; UNACCEPTABLE margin')
    print(f'Belt length nominal estimate RA 76mm: {open_belt_length_mm(76):.1f} mm; DEC 69mm: {open_belt_length_mm(69):.1f} mm')
    print(f'Theoretical resolution: {arcsec_per_microstep():.4f} arcsec per 1/64 commanded microstep')
    print('NOTE: static gravity examples are not validated load cases; cross-axis moments and shocks require full analysis.')

if __name__=='__main__':main()
