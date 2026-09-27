from __future__ import annotations
import time
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from .world import CarState, V3, World
from .strategy import Strategist
from .mechanics import execute

class Elite2v2(BaseAgent):
    def initialize_agent(self):
        self.strategy = Strategist(); self.last_decision = 0.0; self.plan = None; self.last_score = (0, 0)

    def _car(self, packet, index):
        c = packet.game_cars[index]; p = c.physics
        return CarState(index, c.team, V3(p.location.x,p.location.y,p.location.z), V3(p.velocity.x,p.velocity.y,p.velocity.z), c.boost, c.has_wheel_contact, c.is_demolished, self.get_player_name(index))

    def _world(self, packet):
        me = self._car(packet, self.index)
        allies = [self._car(packet,i) for i in range(packet.num_cars) if i != self.index and packet.game_cars[i].team == self.team]
        foes = tuple(self._car(packet,i) for i in range(packet.num_cars) if packet.game_cars[i].team != self.team)
        b = packet.game_ball.physics; ball = V3(b.location.x,b.location.y,b.location.z); bv = V3(b.velocity.x,b.velocity.y,b.velocity.z)
        return World(packet.game_info.seconds_elapsed, packet.game_info.game_time_remaining, packet.teams[self.team].score, packet.teams[1-self.team].score, me, allies[0] if allies else None, foes, ball, bv, tuple(), packet.game_info.is_kickoff_pause)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        if packet.num_cars <= self.index: return SimpleControllerState()
        w = self._world(packet); now = time.monotonic()
        score = (w.score_for, w.score_against)
        if score != self.last_score:
            self.strategy.learner.finish(1.0 if score[0] > self.last_score[0] else -1.0); self.last_score = score
        if self.plan is None or now - self.last_decision >= .08:
            self.plan = self.strategy.choose(w); self.last_decision = now
        car = packet.game_cars[self.index]; r = car.physics.rotation
        control = execute(self.plan.action, w, r.yaw, r.pitch, r.roll)
        return control

    def retire(self):
        if hasattr(self, "strategy"): self.strategy.learner.finish(0.0)
