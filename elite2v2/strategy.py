from __future__ import annotations
from dataclasses import dataclass
from .config import CONFIG
from .learning import Learner
from .world import World, V3, attack_sign
from .mechanics import Action

@dataclass(frozen=True)
class Plan:
    action: Action
    role: str
    score: float
    features: dict

class Strategist:
    def __init__(self): self.learner = Learner()

    def role(self, w: World):
        mate_dist = w.teammate.pos.distance(w.ball) if w.teammate else 99999
        mine = w.me.pos.distance(w.ball)
        if w.teammate and mate_dist + 250 < mine: return "last_man" if w.me.pos.distance(w.our_goal) > w.teammate.pos.distance(w.our_goal) else "support"
        if w.me.pos.distance(w.our_goal) > 3200 and (not w.teammate or w.teammate.pos.distance(w.our_goal) < w.me.pos.distance(w.our_goal)): return "first_man"
        return "second_man"

    def choose(self, w: World) -> Plan:
        role = self.role(w); nearest = w.nearest_opponent(w.ball)
        last = role == "last_man"
        lead = w.goal_diff > 0 and w.time_remaining < 45
        f = {"lead": float(lead), "last_man": float(last), "ball_dist": w.me.pos.distance(w.ball), "boost": w.me.boost / 100.0}
        candidates = []
        def add(a, value): candidates.append((value + self.learner.prior(a.value, f), a))
        danger = w.ball.distance(w.our_goal) < 3000 and w.ball_vel.y * attack_sign(w.me.team) < -300
        if last:
            add(Action.SHADOW, 1.35 if danger else .8); add(Action.CLEAR, .9 if danger else .35); add(Action.ROTATE, .7)
        else:
            add(Action.SUPPORT, .95); add(Action.SHOOT, .65); add(Action.PASS, .62); add(Action.DRIBBLE, .58); add(Action.FAKE, .52)
            if nearest and nearest.pos.distance(w.ball) < 1300 and w.me.boost > 25: add(Action.DEMO, .55)
            if w.ball.z > 350 and w.me.boost > 35: add(Action.AERIAL, .48)
            if w.ball.z > 700 and abs(w.ball_vel.y) > 500: add(Action.DOUBLE_TAP, .5)
            add(Action.CHALLENGE, .45)
        if lead:
            for a, penalty in ((Action.SHOOT,.25),(Action.CHALLENGE,.3),(Action.DEMO,.2)): candidates = [(v-penalty if x == a else v, x) for v,x in candidates]
        action_score, action = max(candidates, key=lambda p: p[0])
        self.learner.remember(action.value, f)
        return Plan(action, role, action_score, f)
