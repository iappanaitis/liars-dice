# Relegation League System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single-tier admission model with a three-tier promotion/relegation pyramid (Premier Division, Championship, League One) driven entirely by PR-triggered game runs.

**Architecture:** The game engine (`__main__.py`, `leaderboard.py`) handles player selection by tier and stat updates. A new `evaluate.py` script (run by the workflow's evaluate job) owns all cascade logic — it reads game results, decides promotions/relegations, and writes the final leaderboard. The GitHub Actions workflow is restructured into four jobs: `setup`, `run-entry`, `run-prm`, `run-l1`, `evaluate`.

**Tech Stack:** Python 3.11, PyYAML, pytest, uv, GitHub Actions

> ⚠️ **Prerequisite:** One design item from the brainstorming session was not captured. Review with the project owner before beginning implementation.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `leaderboard.yaml` | Modify | Schema migration: `is_active` → `tier`, add `tier_since`, `times_last_in_l1`, `pending_relegation` |
| `game/components/leaderboard.py` | Rewrite | Helper functions + updated `update_leaderboard` signature |
| `game/__main__.py` | Modify | Add `--tier`, `--results-file` args; remove `update_leaderboard` call |
| `.github/scripts/evaluate.py` | Create | Cascade decision logic, leaderboard update orchestration, PR comment |
| `.github/workflows/liars-dice.yml` | Rewrite | 4-job structure: setup → run-entry → (run-prm ‖ run-l1) → evaluate |
| `pyproject.toml` | Modify | Add pytest dev dependency |
| `tests/__init__.py` | Create | Test package marker |
| `tests/conftest.py` | Create | Shared leaderboard fixtures |
| `tests/test_leaderboard.py` | Create | Tests for all leaderboard.py functions |
| `tests/test_main.py` | Create | Tests for --tier player selection and --results-file output |

---

## Task 1: Migrate leaderboard.yaml Schema

**Files:**
- Modify: `leaderboard.yaml`

The current `is_active: bool` field is replaced by `tier: str`. All four existing players go into `PRM` (the system currently has 4 players; with TOP_N=6 this is Phase 1 — everyone in PRM). A `pending_relegation: []` key is added at the top level.

- [ ] **Step 1: Update leaderboard.yaml**

Replace the file contents with the migrated schema. Preserve all existing stats exactly:

```yaml
total_runs: 2
last_updated: '2026-05-22T16:10:13Z'
pending_relegation: []
players:
  Diego:
    date_added: '2026-05-22T16:10:13Z'
    total_wins: 60
    total_games: 100
    win_pct: 60.0
    tier: PRM
    tier_since: '2026-05-22T16:10:13Z'
    times_last_in_l1: 0
  Alice:
    date_added: '2026-05-22T15:47:31Z'
    total_wins: 88
    total_games: 200
    win_pct: 44.0
    tier: PRM
    tier_since: '2026-05-22T15:47:31Z'
    times_last_in_l1: 0
  Bruno:
    date_added: '2026-05-22T15:47:31Z'
    total_wins: 48
    total_games: 200
    win_pct: 24.0
    tier: PRM
    tier_since: '2026-05-22T15:47:31Z'
    times_last_in_l1: 0
  Cleo:
    date_added: '2026-05-22T15:47:31Z'
    total_wins: 4
    total_games: 200
    win_pct: 2.0
    tier: PRM
    tier_since: '2026-05-22T15:47:31Z'
    times_last_in_l1: 0
```

- [ ] **Step 2: Commit**

```bash
git add leaderboard.yaml
git commit -m "feat: migrate leaderboard schema to tier-based model"
```

---

## Task 2: Add pytest to pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add dev dependency group**

```toml
[project]
name = "liars-dice"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["pandas", "pyyaml"]

[dependency-groups]
dev = ["pytest>=8.0"]
```

- [ ] **Step 2: Sync and verify pytest is available**

```bash
uv sync
uv run pytest --version
```

Expected output: `pytest 8.x.x`

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add pytest dev dependency"
```

---

## Task 3: Test Fixtures

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create test package marker**

`tests/__init__.py` — empty file.

- [ ] **Step 2: Create conftest.py with fixtures**

```python
import pytest


@pytest.fixture
def minimal_lb():
    """Two players, both in PRM. Phase 1 with TOP_N=4."""
    return {
        "total_runs": 2,
        "last_updated": "2026-01-01T00:00:00Z",
        "pending_relegation": [],
        "players": {
            "Alice": {
                "date_added": "2026-01-01T00:00:00Z",
                "total_wins": 40,
                "total_games": 100,
                "win_pct": 40.0,
                "tier": "PRM",
                "tier_since": "2026-01-01T00:00:00Z",
                "times_last_in_l1": 0,
            },
            "Bruno": {
                "date_added": "2026-01-01T00:00:00Z",
                "total_wins": 30,
                "total_games": 100,
                "win_pct": 30.0,
                "tier": "PRM",
                "tier_since": "2026-01-01T00:00:00Z",
                "times_last_in_l1": 0,
            },
        },
    }


@pytest.fixture
def full_two_tier_lb():
    """Four players: 2 PRM, 2 CH. Phase 2 with TOP_N=2."""
    return {
        "total_runs": 5,
        "last_updated": "2026-01-01T00:00:00Z",
        "pending_relegation": [],
        "players": {
            "Alice": {"date_added": "2026-01-01T00:00:00Z", "total_wins": 40,
                      "total_games": 100, "win_pct": 40.0, "tier": "PRM",
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
            "Bruno": {"date_added": "2026-01-01T00:00:00Z", "total_wins": 30,
                      "total_games": 100, "win_pct": 30.0, "tier": "PRM",
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
            "Cleo": {"date_added": "2026-01-01T00:00:00Z", "total_wins": 20,
                     "total_games": 100, "win_pct": 20.0, "tier": "CH",
                     "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
            "Diego": {"date_added": "2026-01-01T00:00:00Z", "total_wins": 10,
                      "total_games": 100, "win_pct": 10.0, "tier": "CH",
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
        },
    }


@pytest.fixture
def lb_with_pending():
    """Leaderboard with a pending PRM→CH relegation."""
    return {
        "total_runs": 3,
        "last_updated": "2026-01-01T00:00:00Z",
        "pending_relegation": [
            {"player": "Alice", "from_tier": "PRM", "to_tier": "CH"}
        ],
        "players": {
            "Alice": {"date_added": "2026-01-01T00:00:00Z", "total_wins": 40,
                      "total_games": 100, "win_pct": 40.0, "tier": "PRM",
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
            "Bruno": {"date_added": "2026-01-01T00:00:00Z", "total_wins": 30,
                      "total_games": 100, "win_pct": 30.0, "tier": "PRM",
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
        },
    }


@pytest.fixture
def lb_file(tmp_path, minimal_lb):
    """Write minimal_lb to a temp file and return its path."""
    import yaml
    path = tmp_path / "leaderboard.yaml"
    path.write_text(yaml.dump(minimal_lb, default_flow_style=False, sort_keys=False))
    return str(path)
```

- [ ] **Step 3: Commit**

```bash
git add tests/
git commit -m "test: add test infrastructure and fixtures"
```

---

## Task 4: Rewrite leaderboard.py (TDD)

**Files:**
- Create: `tests/test_leaderboard.py`
- Rewrite: `game/components/leaderboard.py`

### Step A — Write failing tests first

- [ ] **Step 1: Write tests/test_leaderboard.py**

```python
import yaml
import pytest
from game.components.leaderboard import (
    apply_pending_relegation,
    detect_phase,
    get_tier_players,
    update_leaderboard,
)


# --- apply_pending_relegation ---

def test_apply_pending_moves_player_to_new_tier(lb_with_pending):
    result = apply_pending_relegation(lb_with_pending)
    assert result["players"]["Alice"]["tier"] == "CH"

def test_apply_pending_updates_tier_since(lb_with_pending):
    result = apply_pending_relegation(lb_with_pending)
    assert result["players"]["Alice"]["tier_since"] != "2026-01-01T00:00:00Z"

def test_apply_pending_clears_list(lb_with_pending):
    result = apply_pending_relegation(lb_with_pending)
    assert result["pending_relegation"] == []

def test_apply_pending_empty_list_is_noop(minimal_lb):
    result = apply_pending_relegation(minimal_lb)
    assert result["players"]["Alice"]["tier"] == "PRM"
    assert result["pending_relegation"] == []


# --- detect_phase ---

def test_detect_phase_1_when_below_top_n(minimal_lb):
    assert detect_phase(minimal_lb, top_n=4) == 1

def test_detect_phase_2_when_between(full_two_tier_lb):
    # 4 total players, TOP_N=2: 4 > 2 and 4 <= 4 → phase 2
    assert detect_phase(full_two_tier_lb, top_n=2) == 2

def test_detect_phase_3_when_above_double(full_two_tier_lb):
    # 4 total players, TOP_N=1: 4 > 2 → phase 3
    assert detect_phase(full_two_tier_lb, top_n=1) == 3

def test_detect_phase_counts_inactive():
    data = {
        "players": {
            "A": {"tier": "PRM"},
            "B": {"tier": "inactive"},
        }
    }
    assert detect_phase(data, top_n=1) == 3  # 2 > 2*1


# --- get_tier_players ---

def test_get_tier_players_returns_correct_names(full_two_tier_lb):
    prm = get_tier_players(full_two_tier_lb, "PRM")
    assert set(prm) == {"Alice", "Bruno"}

def test_get_tier_players_empty_when_none(minimal_lb):
    assert get_tier_players(minimal_lb, "CH") == []

def test_get_tier_players_includes_inactive():
    data = {"players": {"X": {"tier": "inactive"}, "Y": {"tier": "PRM"}}}
    assert get_tier_players(data, "inactive") == ["X"]


# --- update_leaderboard ---

def test_update_stats_for_competing_players(lb_file):
    update_leaderboard(
        wins={"Alice": 60, "Bruno": 40},
        n_games=100,
        tier="PRM",
        path=lb_file,
    )
    with open(lb_file) as f:
        result = yaml.safe_load(f)
    assert result["players"]["Alice"]["total_wins"] == 100   # 40 + 60
    assert result["players"]["Alice"]["total_games"] == 200  # 100 + 100
    assert result["players"]["Alice"]["win_pct"] == 50.0

def test_update_does_not_touch_non_competing_players(lb_file, tmp_path, full_two_tier_lb):
    import yaml as _yaml
    path = str(tmp_path / "lb2.yaml")
    (tmp_path / "lb2.yaml").write_text(
        _yaml.dump(full_two_tier_lb, default_flow_style=False, sort_keys=False)
    )
    update_leaderboard(
        wins={"Cleo": 70, "Diego": 30},
        n_games=100,
        tier="CH",
        path=path,
    )
    with open(path) as f:
        result = _yaml.safe_load(f)
    assert result["players"]["Alice"]["total_games"] == 100  # unchanged

def test_promotions_change_tier_immediately(lb_file):
    update_leaderboard(
        wins={"Alice": 60, "Bruno": 40},
        n_games=100,
        tier="PRM",
        promotions={"Bruno": "CH"},
        path=lb_file,
    )
    with open(lb_file) as f:
        result = yaml.safe_load(f)
    assert result["players"]["Bruno"]["tier"] == "CH"

def test_pending_relegation_added_to_list(lb_file):
    update_leaderboard(
        wins={"Alice": 60, "Bruno": 40},
        n_games=100,
        tier="PRM",
        pending_relegations=[{"player": "Bruno", "from_tier": "PRM", "to_tier": "CH"}],
        path=lb_file,
    )
    with open(lb_file) as f:
        result = yaml.safe_load(f)
    assert len(result["pending_relegation"]) == 1
    assert result["pending_relegation"][0]["player"] == "Bruno"

def test_times_last_in_l1_incremented(lb_file):
    update_leaderboard(
        wins={"Alice": 60, "Bruno": 40},
        n_games=100,
        tier="L1",
        last_place="Bruno",
        path=lb_file,
    )
    with open(lb_file) as f:
        result = yaml.safe_load(f)
    assert result["players"]["Bruno"]["times_last_in_l1"] == 1

def test_times_last_in_l1_not_incremented_for_other_tiers(lb_file):
    update_leaderboard(
        wins={"Alice": 60, "Bruno": 40},
        n_games=100,
        tier="PRM",
        last_place="Bruno",
        path=lb_file,
    )
    with open(lb_file) as f:
        result = yaml.safe_load(f)
    assert result["players"]["Bruno"]["times_last_in_l1"] == 0

def test_total_runs_incremented(lb_file):
    update_leaderboard(
        wins={"Alice": 60, "Bruno": 40},
        n_games=100,
        tier="PRM",
        path=lb_file,
    )
    with open(lb_file) as f:
        result = yaml.safe_load(f)
    assert result["total_runs"] == 3  # was 2
```

- [ ] **Step 2: Run tests — verify they all fail**

```bash
cd ~/Dropbox/Projects/Python/liars-dice
uv run pytest tests/test_leaderboard.py -v 2>&1 | head -40
```

Expected: import errors or `AttributeError` — functions don't exist yet.

### Step B — Implement leaderboard.py

- [ ] **Step 3: Rewrite game/components/leaderboard.py**

```python
import os
import yaml
from datetime import datetime, timezone

_LEADERBOARD_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "leaderboard.yaml")
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def apply_pending_relegation(data: dict) -> dict:
    """Apply all pending_relegation entries and clear the list. Returns updated data."""
    now = _now()
    for entry in data.get("pending_relegation", []):
        player = entry["player"]
        new_tier = entry["to_tier"]
        if player in data.get("players", {}):
            data["players"][player]["tier"] = new_tier
            data["players"][player]["tier_since"] = now
    data["pending_relegation"] = []
    return data


def detect_phase(data: dict, top_n: int) -> int:
    """Return 1, 2, or 3 based on total player count relative to TOP_N."""
    total = len(data.get("players", {}))
    if total < top_n:
        return 1
    if total <= top_n * 2:
        return 2
    return 3


def get_tier_players(data: dict, tier: str) -> list[str]:
    """Return player names whose tier matches the given value."""
    return [
        name
        for name, p in data.get("players", {}).items()
        if p.get("tier") == tier
    ]


def update_leaderboard(
    wins: dict[str, int],
    n_games: int,
    tier: str,
    promotions: dict[str, str] | None = None,
    pending_relegations: list[dict] | None = None,
    last_place: str | None = None,
    path: str = _LEADERBOARD_PATH,
) -> None:
    """
    Update cumulative stats for players who competed, apply tier changes,
    append deferred relegations, and write leaderboard.yaml.

    Args:
        wins: {player_name: win_count} for this run only.
        n_games: games played this run.
        tier: which league ran ('PRM', 'CH', 'L1').
        promotions: {player_name: new_tier} — applied immediately.
        pending_relegations: list of {player, from_tier, to_tier} — deferred.
        last_place: player who finished last (increments times_last_in_l1 if tier=='L1').
        path: path to leaderboard.yaml.
    """
    promotions = promotions or {}
    pending_relegations = pending_relegations or []

    if os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    now = _now()
    data.setdefault("total_runs", 0)
    data["total_runs"] += 1
    data["last_updated"] = now
    data.setdefault("players", {})
    data.setdefault("pending_relegation", [])

    # Update stats for competing players; create entry for new players
    for name, win_count in wins.items():
        player = data["players"].setdefault(name, {
            "date_added": now,
            "total_wins": 0,
            "total_games": 0,
            "win_pct": 0.0,
            "tier": promotions.get(name, tier),
            "tier_since": now,
            "times_last_in_l1": 0,
        })
        player["total_wins"] += win_count
        player["total_games"] += n_games
        player["win_pct"] = round(player["total_wins"] / player["total_games"] * 100, 1)

    # Apply immediate promotions (tier changes now)
    for name, new_tier in promotions.items():
        if name in data["players"]:
            if data["players"][name]["tier"] != new_tier:
                data["players"][name]["tier"] = new_tier
                data["players"][name]["tier_since"] = now

    # Append deferred relegations
    data["pending_relegation"].extend(pending_relegations)

    # Increment times_last_in_l1 for last place in L1 runs
    if tier == "L1" and last_place and last_place in data["players"]:
        data["players"][last_place]["times_last_in_l1"] = (
            data["players"][last_place].get("times_last_in_l1", 0) + 1
        )

    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

- [ ] **Step 4: Run tests — verify they all pass**

```bash
uv run pytest tests/test_leaderboard.py -v
```

Expected: all green.

- [ ] **Step 5: Commit**

```bash
git add game/components/leaderboard.py tests/test_leaderboard.py
git commit -m "feat: rewrite leaderboard.py with tier model and helpers"
```

---

## Task 5: Update `__main__.py` (TDD)

**Files:**
- Create: `tests/test_main.py`
- Modify: `game/__main__.py`

### Step A — Write failing tests first

- [ ] **Step 1: Write tests/test_main.py**

```python
import json
import subprocess
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def run_game(args: list[str], leaderboard: dict, tmp_path: Path) -> dict:
    """Run `python -m game` with a temp leaderboard, return parsed results JSON."""
    lb_path = tmp_path / "leaderboard.yaml"
    lb_path.write_text(yaml.dump(leaderboard, default_flow_style=False, sort_keys=False))

    results_path = tmp_path / "results.json"
    cmd = [
        "uv", "run", "python", "-m", "game",
        *args,
        "--results-file", str(results_path),
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr

    if results_path.exists():
        return json.loads(results_path.read_text())
    return {}


def test_tier_prm_selects_only_prm_players(tmp_path):
    """--tier PRM runs only PRM players."""
    lb = {
        "total_runs": 1,
        "pending_relegation": [],
        "players": {
            "Alice": {"tier": "PRM", "date_added": "2026-01-01T00:00:00Z",
                      "total_wins": 40, "total_games": 100, "win_pct": 40.0,
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
            "Bruno": {"tier": "CH", "date_added": "2026-01-01T00:00:00Z",
                      "total_wins": 30, "total_games": 100, "win_pct": 30.0,
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
        },
    }
    results = run_game(["--tier", "PRM", "10", "4"], lb, tmp_path)
    assert "Alice" in results
    assert "Bruno" not in results


def test_tier_l1_includes_inactive_players(tmp_path):
    """--tier L1 runs L1 and inactive players together."""
    lb = {
        "total_runs": 1,
        "pending_relegation": [],
        "players": {
            "Alice": {"tier": "L1", "date_added": "2026-01-01T00:00:00Z",
                      "total_wins": 40, "total_games": 100, "win_pct": 40.0,
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
            "Bruno": {"tier": "inactive", "date_added": "2026-01-01T00:00:00Z",
                      "total_wins": 30, "total_games": 100, "win_pct": 30.0,
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 2},
            "Cleo": {"tier": "PRM", "date_added": "2026-01-01T00:00:00Z",
                     "total_wins": 50, "total_games": 100, "win_pct": 50.0,
                     "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
        },
    }
    results = run_game(["--tier", "L1", "10", "4"], lb, tmp_path)
    assert "Alice" in results
    assert "Bruno" in results
    assert "Cleo" not in results


def test_results_file_written(tmp_path):
    """--results-file writes a JSON dict of {player: wins}."""
    lb = {
        "total_runs": 1,
        "pending_relegation": [],
        "players": {
            "Alice": {"tier": "PRM", "date_added": "2026-01-01T00:00:00Z",
                      "total_wins": 40, "total_games": 100, "win_pct": 40.0,
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
            "Bruno": {"tier": "PRM", "date_added": "2026-01-01T00:00:00Z",
                      "total_wins": 30, "total_games": 100, "win_pct": 30.0,
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
        },
    }
    results = run_game(["--tier", "PRM", "5", "4"], lb, tmp_path)
    total = sum(results.values())
    assert total == 5  # exactly N_GAMES wins distributed

def test_no_leaderboard_update_written(tmp_path):
    """Running the game must NOT modify leaderboard.yaml."""
    lb = {
        "total_runs": 1,
        "pending_relegation": [],
        "players": {
            "Alice": {"tier": "PRM", "date_added": "2026-01-01T00:00:00Z",
                      "total_wins": 40, "total_games": 100, "win_pct": 40.0,
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
            "Bruno": {"tier": "PRM", "date_added": "2026-01-01T00:00:00Z",
                      "total_wins": 30, "total_games": 100, "win_pct": 30.0,
                      "tier_since": "2026-01-01T00:00:00Z", "times_last_in_l1": 0},
        },
    }
    lb_path = tmp_path / "leaderboard.yaml"
    lb_path.write_text(yaml.dump(lb, default_flow_style=False, sort_keys=False))
    original_content = lb_path.read_text()

    results_path = tmp_path / "results.json"
    subprocess.run(
        ["uv", "run", "python", "-m", "game", "--tier", "PRM",
         "--results-file", str(results_path), "5", "4"],
        cwd=REPO_ROOT, capture_output=True, check=True,
    )
    assert lb_path.read_text() == original_content
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
uv run pytest tests/test_main.py -v 2>&1 | head -30
```

Expected: failures because `--tier` is not a valid argument yet.

### Step B — Implement __main__.py changes

- [ ] **Step 3: Rewrite game/__main__.py**

Replace the file entirely with this version. Key changes: argparse for `--tier` and `--results-file`, tier-based player selection, removed `update_leaderboard` call.

```python
import argparse
import json
import logging
import os
import yaml
from pathlib import Path

project_root = Path(__file__).parent.parent


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--tier", choices=["PRM", "CH", "L1"], default=None,
                   help="Run only players in this tier (L1 also includes inactive)")
    p.add_argument("--results-file", default=None,
                   help="Write wins dict as JSON to this path")
    p.add_argument("n_games", type=int, nargs="?", default=1)
    p.add_argument("top_n", type=int, nargs="?", default=4)
    return p.parse_args()


# --- Logging setup ---

file_handler = logging.FileHandler("gamelog.log", mode="w")
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_fmt = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_fmt)


class _GameFormatter(logging.Formatter):
    def format(self, record):
        msg = record.getMessage()
        if not msg:
            return ""
        if record.levelno >= logging.WARNING:
            return f"[{record.levelname}] {msg}"
        return msg


class _SeriesConsoleFilter(logging.Filter):
    def filter(self, record):
        return record.name == "game.components.series"


console_handler.setFormatter(_GameFormatter())
console_handler.addFilter(_SeriesConsoleFilter())
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])

# --- Imports after logging setup ---

from game.components.series import run_series, format_results  # noqa: E402
from game.components.utils import import_player_classes_from_dir  # noqa: E402

# --- Main ---

args = _parse_args()
N_GAMES = args.n_games
TOP_N = args.top_n

_lb_path = project_root / "leaderboard.yaml"
_lb_data = yaml.safe_load(open(_lb_path)) if _lb_path.exists() else {}
_lb_players = _lb_data.get("players", {})

all_players = import_player_classes_from_dir(str(project_root / "players"))

if args.tier:
    include_tiers = {args.tier}
    if args.tier == "L1":
        include_tiers.add("inactive")

    if args.tier in ("PRM", "CH"):
        # Registered tier players + unregistered challengers (not yet in leaderboard)
        players = [p for p in all_players
                   if _lb_players.get(p.name, {}).get("tier") in include_tiers
                   or p.name not in _lb_players]
    else:
        # L1: registered L1/inactive only — challengers never enter L1 directly
        players = [p for p in all_players
                   if _lb_players.get(p.name, {}).get("tier") in include_tiers]
else:
    # Local run with no tier filter: include all known players
    players = [p for p in all_players if p.name in _lb_players] or all_players

print(f"Playing: {[p.name for p in players]}")

wins = run_series(players, N_GAMES)
print(format_results(wins, N_GAMES))

if args.results_file:
    with open(args.results_file, "w") as f:
        json.dump(wins, f)
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
uv run pytest tests/test_main.py -v
```

Expected: all green.

- [ ] **Step 5: Run full test suite to confirm no regressions**

```bash
uv run pytest tests/ -v
```

Expected: all green.

- [ ] **Step 6: Commit**

```bash
git add game/__main__.py tests/test_main.py
git commit -m "feat: add --tier and --results-file to game runner; remove leaderboard update from game"
```

---

## Task 6: Write evaluate.py

**Files:**
- Create: `.github/scripts/evaluate.py`

This script is called by the workflow's `evaluate` job. It reads game result JSON files, applies cascade logic, updates the leaderboard, and writes `comment.md`.

- [ ] **Step 1: Create .github/scripts/ directory and evaluate.py**

```python
#!/usr/bin/env python3
"""
Evaluate game results, apply cascade logic, update leaderboard, write PR comment.

Required environment variables:
  CHALLENGER        player name from the PR
  CHALLENGER_TIER   tier they entered (PRM or CH)
  PHASE             1, 2, or 3
  N_GAMES           games per run (int)
  TOP_N             league size cap (int)
"""
import json
import os
import yaml
from game.components.leaderboard import (
    apply_pending_relegation,
    get_tier_players,
    update_leaderboard,
)

TIER_LABELS = {
    "PRM": "Premier Division",
    "CH": "Championship",
    "L1": "League One",
    "inactive": "Inactive",
}


def load_results(prefix: str) -> dict[str, int] | None:
    path = f"{prefix}_results.json"
    return json.loads(open(path).read()) if os.path.exists(path) else None


def load_output(prefix: str) -> str:
    path = f"{prefix}_output.txt"
    return open(path).read().strip() if os.path.exists(path) else ""


def ranked(results: dict[str, int], lb_data: dict | None = None) -> list[tuple[str, int]]:
    """Sort by wins desc; tiebreak on total_games desc then tier_since asc."""
    players = (lb_data or {}).get("players", {})
    def _key(item: tuple[str, int]):
        name, wins = item
        p = players.get(name, {})
        return (-wins, -p.get("total_games", 0), p.get("tier_since", ""))
    return sorted(results.items(), key=_key)


def main():
    challenger = os.environ["CHALLENGER"]
    challenger_tier = os.environ["CHALLENGER_TIER"]
    phase = int(os.environ["PHASE"])
    n_games = int(os.environ["N_GAMES"])

    with open("leaderboard.yaml") as f:
        lb = yaml.safe_load(f) or {}
    lb = apply_pending_relegation(lb)

    entry_prefix = challenger_tier.lower()
    entry_results = load_results(entry_prefix)
    prm_results = load_results("prm") if challenger_tier == "CH" else None
    l1_results = load_results("l1")

    # Per-tier promotion/relegation decisions
    entry_promotions: dict[str, str] = {}
    entry_pending: list[dict] = []
    prm_pending: list[dict] = []
    l1_promotions: dict[str, str] = {}
    l1_pending: list[dict] = []
    last_in_l1: str | None = None

    # --- Entry league cascade ---
    if entry_results:
        r = ranked(entry_results, lb)
        winner, last = r[0][0], r[-1][0]
        existing = set(get_tier_players(lb, challenger_tier))

        if challenger_tier == "CH":
            # Winner → PRM
            entry_promotions[winner] = "PRM"

            # Challenger placement
            if challenger == winner:
                pass  # promoted to PRM, not admitted to CH
            elif phase == 3 and challenger == last:
                entry_promotions[challenger] = "L1"
            else:
                entry_promotions[challenger] = "CH"

            # Existing CH bottom → pending to L1 (Phase 3 only, not winner)
            if phase == 3 and existing:
                existing_results = {k: v for k, v in entry_results.items()
                                    if k in existing}
                if existing_results:
                    ch_bottom = min(existing_results, key=existing_results.get)
                    if ch_bottom != winner:
                        entry_pending.append({
                            "player": ch_bottom,
                            "from_tier": "CH",
                            "to_tier": "L1",
                        })

        else:  # Phase 1: challenger enters PRM
            entry_promotions[challenger] = "PRM"

    # --- PRM cascade ---
    if prm_results:
        r = ranked(prm_results, lb)
        prm_last = r[-1][0]
        prm_pending.append({
            "player": prm_last,
            "from_tier": "PRM",
            "to_tier": "CH",
        })

    # --- L1 cascade ---
    if l1_results:
        r = ranked(l1_results, lb)
        l1_winner, last_in_l1 = r[0][0], r[-1][0]
        l1_promotions[l1_winner] = "CH"
        # Determine if last place is L1 or inactive
        l1_roster = set(get_tier_players(lb, "L1"))
        from_tier = "L1" if last_in_l1 in l1_roster else "inactive"
        l1_pending.append({
            "player": last_in_l1,
            "from_tier": from_tier,
            "to_tier": "inactive",
        })

    # --- Write leaderboard updates ---
    if entry_results:
        update_leaderboard(
            wins=entry_results,
            n_games=n_games,
            tier=challenger_tier,
            promotions=entry_promotions,
            pending_relegations=entry_pending,
        )
    if prm_results:
        update_leaderboard(
            wins=prm_results,
            n_games=n_games,
            tier="PRM",
            promotions={},
            pending_relegations=prm_pending,
        )
    if l1_results:
        update_leaderboard(
            wins=l1_results,
            n_games=n_games,
            tier="L1",
            promotions=l1_promotions,
            pending_relegations=l1_pending,
            last_place=last_in_l1,
        )

    _write_comment(
        challenger=challenger,
        challenger_tier=challenger_tier,
        entry_promotions=entry_promotions,
        entry_pending=entry_pending,
        prm_pending=prm_pending,
        l1_promotions=l1_promotions,
        l1_pending=l1_pending,
        entry_prefix=entry_prefix,
        prm_results=prm_results,
        l1_results=l1_results,
    )


def _write_comment(
    challenger, challenger_tier, entry_promotions, entry_pending,
    prm_pending, l1_promotions, l1_pending,
    entry_prefix, prm_results, l1_results,
):
    with open("leaderboard.yaml") as f:
        lb = yaml.safe_load(f) or {}
    players = lb.get("players", {})

    challenger_dest = entry_promotions.get(challenger, challenger_tier)
    summary = f"**{challenger}** → {TIER_LABELS[challenger_dest]}"

    all_pending = entry_pending + prm_pending + l1_pending
    pending_notes = [
        f"- {p['player']}: {TIER_LABELS[p['from_tier']]} → "
        f"{TIER_LABELS[p['to_tier']]} *(takes effect next PR)*"
        for p in all_pending
    ]

    # Full leaderboard table
    table = ["| Player | Tier | Win % | Games | Tier Since |",
             "|--------|------|-------|-------|------------|"]
    for tier_key in ("PRM", "CH", "L1", "inactive"):
        tier_players = sorted(
            [(n, p) for n, p in players.items() if p.get("tier") == tier_key],
            key=lambda x: x[1].get("win_pct", 0), reverse=True,
        )
        for name, p in tier_players:
            bold = "**" if name == challenger else ""
            table.append(
                f"| {bold}{name}{bold} | {TIER_LABELS[tier_key]} | "
                f"{p.get('win_pct', 0)}% | {p.get('total_games', 0)} | "
                f"{str(p.get('tier_since', ''))[:10]} |"
            )

    fence = "```"
    sections = [f"## 🎲 {summary}\n"]

    if all_pending:
        sections.append("**Pending next PR:**\n" + "\n".join(pending_notes) + "\n")

    for prefix, label in [
        (entry_prefix, TIER_LABELS[challenger_tier]),
        ("prm", "Premier Division"),
        ("l1", "League One"),
    ]:
        output = load_output(prefix)
        if output:
            sections.append(
                f"<details><summary>{label} results</summary>\n\n"
                f"{fence}\n{output}\n{fence}\n</details>\n"
            )

    sections.append("### Full Leaderboard\n\n" + "\n".join(table))

    with open("comment.md", "w") as f:
        f.write("\n".join(sections))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the script is importable**

```bash
cd ~/Dropbox/Projects/Python/liars-dice
uv run python -c "import sys; sys.path.insert(0, '.'); import importlib.util; \
  spec = importlib.util.spec_from_file_location('evaluate', '.github/scripts/evaluate.py'); \
  m = importlib.util.module_from_spec(spec); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add .github/scripts/evaluate.py
git commit -m "feat: add evaluate.py for cascade logic and leaderboard orchestration"
```

---

## Task 7: Rewrite the GitHub Actions Workflow

**Files:**
- Rewrite: `.github/workflows/liars-dice.yml`

Replace the entire workflow with the 4-job structure. Jobs: `setup` → `run-entry` → (`run-prm` ‖ `run-l1`) → `evaluate`.

- [ ] **Step 1: Rewrite .github/workflows/liars-dice.yml**

```yaml
name: Liars Dice

on:
  pull_request:
    branches: [main]
    paths:
      - 'players/*'

jobs:
  setup:
    if: github.actor != 'github-actions[bot]'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    outputs:
      challenger: ${{ steps.detect.outputs.challenger }}
      challenger_tier: ${{ steps.detect.outputs.challenger_tier }}
      phase: ${{ steps.detect.outputs.phase }}
      pending_l1_relegation: ${{ steps.detect.outputs.pending_l1_relegation }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
          fetch-depth: 0
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: uv sync --no-install-project
      - name: Validate PR and detect phase
        id: detect
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TOP_N: ${{ vars.TOP_N || '6' }}
        run: |
          git fetch origin main
          new_files=$(git diff --name-only origin/main HEAD -- players/ | grep '\.py$' || true)
          count=$(echo "$new_files" | grep -c '.' || true)
          if [ "$count" -ne 1 ]; then
            gh pr comment ${{ github.event.pull_request.number }} \
              --body "❌ Each PR must add exactly one player file in \`players/\`. Found: $count"
            exit 1
          fi
          player=$(basename "$(echo "$new_files")" .py)
          echo "challenger=$player" >> "$GITHUB_OUTPUT"
          python3 - <<'EOF'
import yaml, os
with open("leaderboard.yaml") as f:
    lb = yaml.safe_load(f) or {}
top_n = int(os.environ["TOP_N"])
total = len(lb.get("players", {}))
phase = 1 if total < top_n else (2 if total <= top_n * 2 else 3)
challenger_tier = "PRM" if phase == 1 else "CH"
pending = lb.get("pending_relegation", [])
pending_l1 = any(p.get("to_tier") == "L1" for p in pending)
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"phase={phase}\n")
    f.write(f"challenger_tier={challenger_tier}\n")
    f.write(f"pending_l1_relegation={'true' if pending_l1 else 'false'}\n")
EOF

  run-entry:
    needs: setup
    runs-on: ubuntu-latest
    permissions:
      contents: read
    outputs:
      ch_promoted: ${{ steps.run.outputs.ch_promoted }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
          fetch-depth: 0
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: uv sync --no-install-project
      - name: Apply pending relegation to workspace leaderboard
        run: |
          python3 - <<'EOF'
import yaml
from game.components.leaderboard import apply_pending_relegation
with open("leaderboard.yaml") as f:
    data = yaml.safe_load(f) or {}
data = apply_pending_relegation(data)
with open("leaderboard.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
EOF
      - name: Run entry league game
        id: run
        env:
          CHALLENGER_TIER: ${{ needs.setup.outputs.challenger_tier }}
          TOP_N: ${{ vars.TOP_N || '6' }}
        run: |
          tier="${CHALLENGER_TIER}"
          prefix=$(echo "$tier" | tr '[:upper:]' '[:lower:]')
          uv run python -m game \
            --tier "$tier" \
            --results-file "${prefix}_results.json" \
            ${{ vars.N_GAMES || '500' }} ${{ vars.TOP_N || '6' }} \
            2>&1 | tee "${prefix}_output.txt"

          python3 - <<'EOF'
import json, yaml, os
tier = os.environ["CHALLENGER_TIER"]
prefix = tier.lower()
with open(f"{prefix}_results.json") as f:
    results = json.load(f)
with open("leaderboard.yaml") as f:
    lb = yaml.safe_load(f) or {}
top_n = int(os.environ["TOP_N"])
tier_players = [n for n, p in lb.get("players", {}).items() if p.get("tier") == tier]
# CH promoted if at least one existing CH player competed (winner goes to PRM)
ch_promoted = tier == "CH" and len(tier_players) >= 1
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"ch_promoted={'true' if ch_promoted else 'false'}\n")
EOF
      - name: Upload entry results
        uses: actions/upload-artifact@v4
        with:
          name: entry-results
          path: |
            *_results.json
            *_output.txt

  run-prm:
    needs: [setup, run-entry]
    if: |
      needs.setup.outputs.challenger_tier == 'CH' &&
      needs.run-entry.outputs.ch_promoted == 'true'
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
          fetch-depth: 0
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: uv sync --no-install-project
      - name: Apply pending relegation to workspace leaderboard
        run: |
          python3 - <<'EOF'
import yaml
from game.components.leaderboard import apply_pending_relegation
with open("leaderboard.yaml") as f:
    data = yaml.safe_load(f) or {}
data = apply_pending_relegation(data)
with open("leaderboard.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
EOF
      - name: Run PRM game
        run: |
          uv run python -m game \
            --tier PRM \
            --results-file prm_results.json \
            ${{ vars.N_GAMES || '500' }} ${{ vars.TOP_N || '6' }} \
            2>&1 | tee prm_output.txt
      - name: Upload PRM results
        uses: actions/upload-artifact@v4
        with:
          name: prm-results
          path: |
            prm_results.json
            prm_output.txt

  run-l1:
    needs: setup
    if: |
      needs.setup.outputs.phase == '3' &&
      needs.setup.outputs.pending_l1_relegation == 'true'
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
          fetch-depth: 0
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: uv sync --no-install-project
      - name: Apply pending relegation to workspace leaderboard
        run: |
          python3 - <<'EOF'
import yaml
from game.components.leaderboard import apply_pending_relegation
with open("leaderboard.yaml") as f:
    data = yaml.safe_load(f) or {}
data = apply_pending_relegation(data)
with open("leaderboard.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
EOF
      - name: Run L1 game (includes inactive)
        run: |
          uv run python -m game \
            --tier L1 \
            --results-file l1_results.json \
            ${{ vars.N_GAMES || '500' }} ${{ vars.TOP_N || '6' }} \
            2>&1 | tee l1_output.txt
      - name: Upload L1 results
        uses: actions/upload-artifact@v4
        with:
          name: l1-results
          path: |
            l1_results.json
            l1_output.txt

  evaluate:
    needs: [setup, run-entry, run-prm, run-l1]
    if: always() && needs.run-entry.result == 'success'
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
          fetch-depth: 0
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: uv sync --no-install-project
      - name: Download all game results
        uses: actions/download-artifact@v4
        with:
          merge-multiple: true
      - name: Evaluate results and update leaderboard
        env:
          CHALLENGER: ${{ needs.setup.outputs.challenger }}
          CHALLENGER_TIER: ${{ needs.setup.outputs.challenger_tier }}
          PHASE: ${{ needs.setup.outputs.phase }}
          N_GAMES: ${{ vars.N_GAMES || '500' }}
          TOP_N: ${{ vars.TOP_N || '6' }}
        run: python .github/scripts/evaluate.py
      - name: Commit leaderboard
        run: |
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git config user.name "github-actions[bot]"
          git add leaderboard.yaml
          if ! git diff --cached --quiet; then
            git commit -m "ci: update leaderboard [skip ci]"
            git push
          fi
      - name: Post comment
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: gh pr comment ${{ github.event.pull_request.number }} --body-file comment.md
      - name: Enable auto-merge
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: gh pr merge ${{ github.event.pull_request.number }} --auto --squash
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/liars-dice.yml
git commit -m "feat: restructure workflow into 4-job relegation cascade"
```

---

## Task 8: Push and Seed the Required Status Check

- [ ] **Step 1: Push all commits**

```bash
git push
```

- [ ] **Step 2: Open a test PR to seed the `run-entry` status check**

Create a new branch, add a player file to `players/`, open a PR against `main`. This triggers the workflow and registers `run-entry`, `evaluate`, etc. as known status check names in GitHub.

```bash
git checkout -b test/seed-workflow
# copy any existing player file as a new name, e.g.:
cp players/alice.py players/eve.py
# Edit players/eve.py — change the class name and self.name to "Eve"
git add players/eve.py
git commit -m "test: seed workflow status checks"
git push -u origin test/seed-workflow
# Open PR via GitHub UI or:
gh pr create --title "test: seed workflow" --body "Seeding required status checks."
```

- [ ] **Step 3: After workflow completes, add required status checks in GitHub**

Go to **Settings → Branches → branch protection rule for `main`**:
- Add `run-entry` as a required status check
- Add `evaluate` as a required status check

- [ ] **Step 4: Verify PR auto-merged or close manually if not merging**

If Eve's player wins or is admitted to PRM (Phase 1 at this point), the PR will auto-merge. Review the PR comment to confirm the leaderboard comment format looks correct.

---

## Open Question

One design item from the brainstorming session was not captured before this plan was written. **Resolve with the project owner before merging any implementation work.** Document the resolution in the spec (`docs/specs/2026-06-08-relegation-league-system-design.md`) and update this plan accordingly.
