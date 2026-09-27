from __future__ import annotations
import json, os, time
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Dict
from .config import CONFIG

@dataclass
class DecisionRecord:
    timestamp: float
    action: str
    features: Dict[str, float]
    reward: float = 0.0

class Learner:
    """Small online contextual bandit. It changes priors, never blocks gameplay."""
    def __init__(self):
        self.records = []
        self.weights = defaultdict(float)
        self.counts = defaultdict(int)
        os.makedirs(CONFIG.data_dir, exist_ok=True)
        self.path = os.path.join(CONFIG.data_dir, "weights.json")
        self.episode_path = os.path.join(CONFIG.data_dir, "episodes.jsonl")
        try:
            with open(self.path, encoding="utf8") as f: self.weights.update(json.load(f))
        except (OSError, ValueError): pass

    def prior(self, action: str, features: Dict[str, float]) -> float:
        key = action + "|" + self.bucket(features)
        return float(self.weights.get(key, 0.0))

    def remember(self, action, features):
        self.records.append(DecisionRecord(time.time(), action, dict(features)))
        if len(self.records) > 80: self.records.pop(0)

    def bucket(self, f):
        return ":".join(["lead" if f.get("lead", 0) > 0 else "trail", "safe" if f.get("last_man", 0) else "free", "near" if f.get("ball_dist", 9) < 1800 else "far"])

    def finish(self, reward: float):
        try:
            with open(self.episode_path, "a", encoding="utf8") as out:
                for r in self.records:
                    r.reward = reward
                    out.write(json.dumps(asdict(r), separators=(",", ":")) + "\n")
                    key = r.action + "|" + self.bucket(r.features)
                    n = self.counts[key] + 1
                    self.counts[key] = n
                    self.weights[key] += CONFIG.learning_rate * (reward - self.weights[key])
            with open(self.path + ".tmp", "w", encoding="utf8") as f: json.dump(dict(self.weights), f, indent=2)
            os.replace(self.path + ".tmp", self.path)
        except OSError: pass
        self.records.clear()
