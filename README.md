# Liar's Dice League

A Python engine for running Liar's Dice games between algorithmic players. Players compete in a tiered league — submit a PR to join, and a weekly scheduled run plays the games and updates standings (extra runs trigger automatically when a player file changes).

_This project is based on the foundational work and initial implementation by [Zach Austin](https://github.com/zachaustin01)._

Interested in competing? **[Visit the Wiki](https://github.com/after2400/liars-dice/wiki)** — rules, player API, and how to submit a bot. For local dev setup see [CONTRIBUTING.md](CONTRIBUTING.md).

## Current Standings

<!-- prettier-ignore-start -->
<!-- leaderboard-start -->
### Premier
| Player | Win % in PRM | Wins in PRM | Win % Total | Total Wins | Games |
|--------|----------------|----------------|-------------|------------|-------|
| Stewie | 18.4 | 3689 | 19.7 | 4342 | 22000 |
| Peter Beter | 17.0 | 1699 | 18.1 | 1990 | 11000 |
| EvilStewie | 16.6 | 1325 | 18.3 | 1646 | 9000 |
| Deep Thought | 16.4 | 1310 | 16.4 | 1310 | 8000 |
| Peter Griffin | 16.1 | 1770 | 16.1 | 1770 | 11000 |
| Sloane | 15.9 | 3492 | 18.9 | 7173 | 38000 |
| Nuke LaLoosh | 15.3 | 2746 | 18.2 | 3819 | 21000 |

### Championship
| Player | Win % in CH | Wins in CH | Win % Total | Total Wins | Games |
|--------|----------------|----------------|-------------|------------|-------|
| Eva | 21.2 | 4655 | 20.1 | 6033 | 30000 |
| Cal Culatid | 19.4 | 1945 | 18.5 | 3509 | 19000 |
| Zara | 18.8 | 3193 | 19.3 | 5608 | 29000 |
| Diego | 18.1 | 1805 | 18.3 | 5375 | 29350 |
| Remy | 14.7 | 3385 | 17.7 | 7247 | 41000 |
| Honest Abe | 13.9 | 2084 | 15.0 | 2557 | 17000 |

### Level 1
| Player | Win % in L1 | Wins in L1 | Win % Total | Total Wins | Games |
|--------|----------------|----------------|-------------|------------|-------|
| Finn | 22.1 | 3534 | 18.4 | 5929 | 32250 |
| Rick Sanchez | 17.4 | 2779 | 17.4 | 2779 | 16000 |
| Alice | 17.1 | 3424 | 15.9 | 4517 | 28450 |
| Bruno | 12.6 | 2525 | 12.7 | 3480 | 27450 |
| Topper | 8.7 | 2099 | 8.7 | 2099 | 24000 |
| Cleo | 6.6 | 1582 | 5.6 | 1599 | 28450 |
| Liar², Pants on Fire | 4.1 | 829 | 4.1 | 829 | 20000 |
| Meg Griffin | 0.0 | 0 | 0.0 | 0 | 0 |

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
