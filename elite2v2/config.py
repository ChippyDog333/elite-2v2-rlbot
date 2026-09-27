from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    tick_rate: float = 1 / 60
    decision_period: float = 0.08
    prediction_seconds: float = 2.0
    safe_last_man_distance: float = 1700.0
    teammate_support_distance: float = 2600.0
    shot_min_value: float = 0.45
    risky_action_penalty: float = 0.35
    learning_rate: float = 0.08
    data_dir: str = "data"

CONFIG = Config()
