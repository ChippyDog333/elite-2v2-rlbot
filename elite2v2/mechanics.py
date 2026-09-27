from __future__ import annotations
from enum import Enum
from math import atan2, degrees
from rlbot.utils.structures.controller_input import ControllerState
from .world import V3, World

class Action(str, Enum):
    ROTATE = "rotate"; SUPPORT = "support"; SHOOT = "shoot"; PASS = "pass"; DRIBBLE = "dribble"; FAKE = "fake"; CHALLENGE = "challenge"; SHADOW = "shadow"; CLEAR = "clear"; DEMO = "demo"; AERIAL = "aerial"; DOUBLE_TAP = "double_tap"

def steer_toward(car: V3, target: V3, yaw: float) -> float:
    desired = atan2(target.y-car.y, target.x-car.x)
    err = (desired-yaw+3.14159)%(2*3.14159)-3.14159
    return max(-1.0, min(1.0, err * 3.0))

def drive(car, target: V3, yaw: float, boost=False, brake=False):
    c = ControllerState()
    c.steer = steer_toward(car.pos, target, yaw)
    c.throttle = -1.0 if brake else 1.0
    c.boost = bool(boost and not brake and abs(c.steer) < .35)
    c.handbrake = bool(abs(c.steer) > .8)
    return c

def recovery(car, target):
    return drive(car, target, 0.0, boost=True)

def execute(action: Action, world: World, yaw: float, pitch: float, roll: float):
    """Safe first-layer controls. Advanced actions retain possession/rotation fallbacks."""
    m = world.me
    if action in (Action.ROTATE, Action.SUPPORT, Action.SHADOW):
        target = world.our_goal if action == Action.SHADOW else V3(world.ball.x * .35, world.ball.y * .35, 0)
        return drive(m, target, yaw, boost=m.boost > 20)
    if action in (Action.CLEAR, Action.CHALLENGE, Action.SHOOT, Action.PASS, Action.DRIBBLE, Action.FAKE):
        target = world.ball + world.ball_vel * .12
        return drive(m, target, yaw, boost=m.boost > 15)
    if action == Action.DEMO:
        enemy = world.nearest_opponent(world.ball)
        return drive(m, enemy.pos if enemy else world.ball, yaw, boost=m.boost > 30)
    if action in (Action.AERIAL, Action.DOUBLE_TAP):
        # Ground fallback until aerial intercept confidence is high.
        return drive(m, world.ball, yaw, boost=m.boost > 25)
    return drive(m, world.ball, yaw)
