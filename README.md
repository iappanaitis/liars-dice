# Liar's Dice League

A Python engine for running Liar's Dice games between algorithmic players. Players compete in a tiered league — submit a PR to join, and a weekly scheduled run plays the games and updates standings (extra runs trigger automatically when a player file changes).

_This project is based on the foundational work and initial implementation by [Zach Austin](https://github.com/zachaustin01)._

Interested in competing? **[Visit the Wiki](https://github.com/after2400/liars-dice/wiki)** — rules, player API, and how to submit a bot. For local dev setup see [CONTRIBUTING.md](CONTRIBUTING.md).

## Current Standings

<!-- prettier-ignore-start -->
<!-- leaderboard-start -->
### Premier
| Player | Season W% | Wins in PRM | Win % Total | Total Wins | Games |
|--------|-----------|----------------|-------------|------------|-------|
| The Merovingian | 19.0 | 656 | 29.2 | 1458 | 5000 |
| The Oracle | 17.3 | 173 | 32.9 | 986 | 3000 |
| EvilStewie | 15.3 | 2347 | 17.8 | 2668 | 15000 |
| Deep Thought | 14.3 | 2006 | 15.4 | 2006 | 13000 |
| Sloane | 7.6 | 4056 | 17.6 | 7737 | 44000 |
| Peter Beter | 7.0 | 2243 | 15.8 | 2534 | 16000 |
| Peter Griffin | 6.7 | 2241 | 14.0 | 2241 | 16000 |
| Nuke LaLoosh | 6.7 | 3148 | 16.2 | 4221 | 26000 |

### Championship
| Player | Season W% | Wins in CH | Win % Total | Total Wins | Games |
|--------|-----------|----------------|-------------|------------|-------|
| Stewie | Relegated | 365 | 17.8 | 4994 | 28000 |
| Columbo | 12.9 | 891 | 15.6 | 1400 | 9000 |
| Cal Culatid | 10.2 | 2570 | 17.2 | 4134 | 24000 |
| Zara | 9.9 | 4018 | 18.4 | 6433 | 35000 |
| Eva | 9.3 | 5404 | 18.8 | 6782 | 36000 |
| Diego | 8.4 | 2622 | 17.3 | 6304 | 36350 |
| Honest Abe | 7.9 | 2576 | 13.9 | 3049 | 22000 |
| Remy | 4.5 | 3651 | 16.9 | 8304 | 49000 |

### Level 1
| Player | Season W% | Wins in L1 | Win % Total | Total Wins | Games |
|--------|-----------|----------------|-------------|------------|-------|
| Finn | 12.7 | 3857 | 16.8 | 6597 | 39250 |
| Rick Sanchez | 12.0 | 3488 | 16.6 | 3488 | 21000 |
| Alice | 9.9 | 4244 | 15.5 | 5337 | 34450 |
| Bruno | 8.1 | 3204 | 12.4 | 4159 | 33450 |
| Meg Griffin | 7.4 | 524 | 10.5 | 524 | 5000 |
| Liar², Pants on Fire | 2.4 | 1000 | 4.0 | 1000 | 25000 |
| Topper | 2.2 | 2364 | 7.9 | 2364 | 30000 |
| Cleo | 0.9 | 1695 | 5.0 | 1712 | 34450 |

### Quarter Leaderboard

| Player | Tier | PRM W% | CH W% | L1 W% | Total W% | Games |
|--------|------|--------|-------|-------|----------|-------|
| The Merovingian | Premier | 21.9 | 33.4 | 46.8 | 29.2 | 5000 |
| Zara | Championship | 20.1 | 17.5 | — | 18.4 | 35000 |
| Diego | Championship | 18.1 | 16.4 | — | 17.3 | 36350 |
| The Oracle | Premier | 17.3 | 36.9 | 44.4 | 32.9 | 3000 |
| Eva | Championship | 17.2 | 19.3 | — | 18.8 | 36000 |
| EvilStewie | Premier | 16.8 | 32.1 | — | 17.8 | 15000 |
| Stewie | Championship | 16.7 | 36.5 | 28.8 | 17.8 | 28000 |
| Deep Thought | Premier | 15.4 | — | — | 15.4 | 13000 |
| Peter Beter | Premier | 15.0 | 29.1 | — | 15.8 | 16000 |
| Alice | Level 1 | 14.8 | 12.6 | 16.3 | 15.5 | 34450 |
| Sloane | Premier | 14.5 | 23.0 | — | 17.6 | 44000 |
| Finn | Level 1 | 14.0 | 12.7 | 21.4 | 16.8 | 39250 |
| Peter Griffin | Premier | 14.0 | — | — | 14.0 | 16000 |
| Nuke LaLoosh | Premier | 13.7 | 27.6 | 52.1 | 16.2 | 26000 |
| Cal Culatid | Championship | 12.8 | 17.1 | 26.5 | 17.2 | 24000 |
| Bruno | Level 1 | 10.9 | 13.8 | 12.3 | 12.4 | 33450 |
| Remy | Championship | 10.6 | 13.5 | 22.2 | 16.9 | 49000 |
| Columbo | Championship | 7.2 | 17.8 | 29.3 | 15.6 | 9000 |
| Cleo | Level 1 | 1.1 | 0.3 | 5.7 | 5.0 | 34450 |
| Honest Abe | Championship | — | 12.9 | 23.6 | 13.9 | 22000 |
| Rick Sanchez | Level 1 | — | — | 16.6 | 16.6 | 21000 |
| Meg Griffin | Level 1 | — | — | 10.5 | 10.5 | 5000 |
| Topper | Level 1 | — | — | 7.9 | 7.9 | 30000 |
| Liar², Pants on Fire | Level 1 | — | — | 4.0 | 4.0 | 25000 |

<!-- leaderboard-end -->
<!-- prettier-ignore-end -->

_Updated weekly (Mondays at 9am UTC) or whenever a player file is added/modified. Full history in the [season tracking issue](https://github.com/after2400/liars-dice/issues/4)._

---

## How It Works

Two workflows replace the old per-PR game model:

**`register-player.yml`** — triggered when a PR touches `players/`

- Validates the player file (class name matches filename, display name ≤ 25 chars)
- Registers the player in `leaderboard.yaml` at the appropriate entry tier
- Commits the leaderboard update and auto-merges the PR
- No games run immediately

**`run-season.yml`** — cron fires daily at 9am UTC; a guard job decides whether to actually run

- Runs on Mondays (weekly cadence) or when any `players/*.py` file was added/modified in the last 24h; `workflow_dispatch` always runs
- Plays `N_GAMES` (default 1000) games in each active tier, bottom-up: `inactive → L1 → CH → PRM`
- Promotions and relegations are applied between tiers (so a player promoted from L1 can compete in CH the same day)
- Commits the updated leaderboard and posts a summary to the season tracking issue

A tier is skipped if it has fewer than 2 players.

---

## Tier Structure

Capacities scale with `TOP_N` (repo variable, default 4, max 8):

| Tier     | Capacity    | Notes                                 |
| -------- | ----------- | ------------------------------------- |
| PRM      | `TOP_N`     | Premier Division — top of the table   |
| CH       | `TOP_N`     | Championship                          |
| L1       | `2 × TOP_N` | League One                            |
| inactive | unlimited   | Plays separately; top player promotes |

**Entry tier:** new players enter the lowest active tier that has capacity (L1 if possible, else CH, else PRM). A player registered mid-day plays in the next scheduled run.

**Promotion / relegation (per season run):**

- Top player in each tier promotes to the tier above
- Bottom player(s) relegate to the tier below
- `times_inactive` increments each time a player is relegated to inactive

---

## Project Structure

```
game/
  __main__.py          # entry point, logging, player selection, --tier filter
  validate.py          # player file validator (python -m game.validate <file>)
  components/
    script.py          # game loop and round orchestration
    bets.py            # Bet class, bet_validator, bet_grader
    series.py          # series runner and results formatter
    leaderboard.py     # leaderboard read/write, apply_season_results
    stats.py           # GameStats incremental stats (optional algo arg, opt-in by name)
    utils.py           # player loader
  season/
    utils.py           # shared helpers: _load_lb, _save_lb, date/quarter utilities
  simulation/
    quarter.py         # simulate a full quarter locally (uv run python -m game.simulation.quarter)

players/               # one .py file per player — see full list on GitHub
  ...                  # https://github.com/after2400/liars-dice/tree/main/players

.github/
  workflows/
    register-player.yml      # PR validation, registration, auto-merge
    run-monday.yml           # weekly/conditional season runner (guard + run jobs)
    update-leaderboard.yml   # updates README standings on player file changes
    guard-non-player-prs.yml # blocks non-admin non-player PRs from auto-merge
    release.yml              # PSR — bumps version, regenerates CHANGELOG, creates GitHub Release
    lint.yml                 # ruff + commitlint on push/PR
  scripts/
    register_player.py   # validates player file, writes leaderboard entry
    run_season.py        # bottom-up tier runner, writes season summary
    reset_season.py      # quarterly tournament reset and pool runner
    lb_owner.py          # looks up github_username by class name
    lb_has_player.py     # checks whether a class name is registered
    lb_delete.py         # removes players from leaderboard by file path
    lb_update_name.py    # validates and updates display_name on modification

.Justfile                # local dev recipes (just develop / pytest / lint / simulate-*)
leaderboard.yaml         # source of truth — tier, stats, github_username per player
```
