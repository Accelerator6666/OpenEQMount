import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from three_axis_motion import (JointPose,MotionRefused,AXES,plan_synchronized_move,
    requested_rot_mechanical_angle,SIDEREAL_RATE_DEG_PER_S,normalize_position_angle,optical_axis_mount_vector,dec_axis_mount_vector)

def test_sidereal_rate():
    assert 0.00417 < SIDEREAL_RATE_DEG_PER_S < 0.00419

def test_three_axis_moves_synchronously():
    p=plan_synchronized_move(JointPose(0,0,0),JointPose(20,-30,90),homed=True,enabled=True)
    assert p.duration_s == 45.0
    assert p.sample(p.duration_s/2)==JointPose(10,-15,45)
    assert p.sample(1e8)==p.target

def test_cable_wrap_not_hidden_by_modulo():
    with pytest.raises(MotionRefused):
        plan_synchronized_move(JointPose(0,0,140),JointPose(0,0,200),homed=True,enabled=True)
    assert normalize_position_angle(400)==40

def test_unhomed_or_disabled_rejected():
    for kw in ({},{'homed':True},{'enabled':True}):
        with pytest.raises(MotionRefused):
            plan_synchronized_move(JointPose(0,0,0),JointPose(1,1,1),**kw)

def test_unbounded_and_nan_rejected():
    with pytest.raises(MotionRefused):
        plan_synchronized_move(JointPose(0,0,0),JointPose(float('nan'),1,1),homed=True,enabled=True)
    with pytest.raises(MotionRefused):
        plan_synchronized_move(JointPose(0,0,0),JointPose(170,1,1),homed=True,enabled=True)

def test_camera_angle_calibration_without_wrap():
    assert requested_rot_mechanical_angle(90,zero_pa_deg=0,zero_mechanical_deg=10,sign=-1)==-80
    with pytest.raises(MotionRefused):
        requested_rot_mechanical_angle(359,zero_pa_deg=0,zero_mechanical_deg=0)

def test_zero_move_safe():
    q=JointPose(10,-10,30)
    p=plan_synchronized_move(q,q,homed=True,enabled=True)
    assert p.duration_s==0 and p.sample(0)==q


def test_rotator_optical_axis_remains_perpendicular_to_dec_axis():
    for ra in (-90,0,45,130):
        for dec in (-60,0,25,80):
            optical=optical_axis_mount_vector(ra,dec)
            decaxis=dec_axis_mount_vector(ra)
            assert sum(a*b for a,b in zip(optical,decaxis))==pytest.approx(0,abs=1e-12)
