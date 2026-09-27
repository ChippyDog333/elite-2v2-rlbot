# Elite 2v2 RLBot

A Python RLBot 2v2 bot foundation focused on decision quality, teamplay, possession, safe rotations, and persistent gameplay data. It is intentionally layered: reliable control and strategic evaluation come before advanced mechanics.

## Requirements

- Windows
- Rocket League with RLBot-compatible offline/bot support
- Python 3.8–3.11 (use the version supported by your installed RLBot release)
- RLBot Python package

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Install and run

1. Clone this repository into a folder known to RLBot.
2. Install dependencies.
3. Open the RLBot GUI.
4. Add/import `bot.cfg` from this repository.
5. Add two instances of `Elite2v2` to the same team and two opponents; select Soccar/2v2.
6. Start an offline match.

The bot's runtime data is written to `data/episodes.jsonl` and compact learned weights to `data/weights.json`. These files are ignored by git.

## Architecture

- `bot.py`: RLBot adapter and frame loop.
- `elite2v2/world.py`: immutable, normalized game-state snapshot and geometry helpers.
- `elite2v2/strategy.py`: role assignment and scored action selection.
- `elite2v2/mechanics.py`: reusable driving, aerial, shot, dribble, recovery, and demo controls.
- `elite2v2/learning.py`: low-overhead episodic event logging and outcome-conditioned action weights.
- `elite2v2/config.py`: tunable strategy constants.

The strategy scores alternatives rather than using one ball-chasing rule. It explicitly penalizes double commits and last-man failures, values teammate predicted position, and changes risk with score/time. Fakes, demos, passes, double taps, and aerials are gated by opportunity checks; the initial implementation uses safe control fallbacks when a high-level mechanic cannot be executed reliably.

## Learning

Every decision records a compact feature vector, chosen action, and later outcome. At episode end, positive/negative events update action weights using a bounded online average. Learning is deliberately synchronous and tiny: no model training occurs on the gameplay thread. Delete `data/weights.json` to reset learned behavior. Future training tools can consume `episodes.jsonl` for offline analysis.

This is a playable foundation, not a claim of elite performance. The next high-value work is a proper intercept planner, reliable aerial controller, wall/backboard planning, kickoff roles, and replay-based evaluation.
