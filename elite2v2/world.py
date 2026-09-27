from __future__ import annotations
from dataclasses import dataclass
from math import hypot
from typing import Iterable, Optional

BLUE_GOAL = (0.0, -5120.0, 320.0)
ORANGE_GOAL = (0.0, 5120.0, 320.0)
FIELD_X = 4096.0
FIELD_Y = 5120.0

@dataclass(frozen=True)
class V3:
    x: float
    y: float
    z: float = 0.0
    def __add__(self, o): return V3(self.x + o.x, self.y + o.y, self.z + o.z)
    def __sub__(self, o): return V3(self.x - o.x, self.y - o.y, self.z - o.z)
    def __mul__(self, s): return V3(self.x * s, self.y * s, self.z * s)
    def flat(self): return V3(self.x, self.y, 0)
    def norm(self): return (self.x*self.x + self.y*self.y + self.z*self.z) ** 0.5
    def flat_norm(self): return hypot(self.x, self.y)
    def distance(self, o): return (self-o).norm()

@dataclass(frozen=True)
class CarState:
    index: int
    team: int
    pos: V3
    vel: V3
    boost: float
    on_ground: bool
    demolished: bool
    name: str = ""

@dataclass(frozen=True)
class World:
    time: float
    match_time: float
    score_for: int
    score_against: int
    me: CarState
    teammate: Optional[CarState]
    opponents: tuple[CarState, ...]
    ball: V3
    ball_vel: V3
    ball_prediction: tuple[V3, ...]
    kickoff: bool = False

    @property
    def our_goal(self): return BLUE_GOAL if self.me.team == 0 else ORANGE_GOAL
    @property
    def their_goal(self): return ORANGE_GOAL if self.me.team == 0 else BLUE_GOAL
    @property
    def time_remaining(self): return max(0.0, 300.0 - self.match_time)
    @property
    def goal_diff(self): return self.score_for - self.score_against
    def nearest_opponent(self, point: V3) -> Optional[CarState]:
        return min(self.opponents, key=lambda c: c.pos.distance(point), default=None)
    def nearest_teammate_to_ball(self):
        return self.teammate if self.teammate and self.teammate.pos.distance(self.ball) < self.me.pos.distance(self.ball) else self.me

def predict_linear(pos: V3, vel: V3, seconds: float) -> V3:
    return pos + vel * seconds

def attack_sign(team: int) -> float: return 1.0 if team == 0 else -1.0
