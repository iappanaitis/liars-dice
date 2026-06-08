"""
Current (pre-relegation) leaderboard evaluator.
Called by the run-game workflow job after the game runs.
Reads CHALLENGER env var and game_output.txt, writes comment.md and GITHUB_OUTPUT.
"""
import os
import yaml

challenger = os.environ["CHALLENGER"]

with open("leaderboard.yaml") as f:
    lb = yaml.safe_load(f) or {}
players = lb.get("players", {})
made_it = challenger in players and players[challenger].get("is_active", False)

with open(os.environ["GITHUB_OUTPUT"], "a") as out:
    out.write(f"made_it={'true' if made_it else 'false'}\n")

with open("game_output.txt") as f:
    game_output = f.read().strip()

rows = []
for name, p in players.items():
    status = "✅" if p.get("is_active") else "❌"
    bold = "**" if name == challenger else ""
    rows.append(f"| {bold}{name}{bold} | {p['win_pct']}% | {p['total_wins']}/{p['total_games']} | {status} |")
table = "| Player | Win % | Record | Active |\n|--------|-------|--------|--------|\n" + "\n".join(rows)

fence = "```"
if made_it:
    body = f"""## 🎲 {challenger} made the leaderboard!

<details><summary>Game results</summary>

{fence}
{game_output}
{fence}
</details>

### Current Leaderboard
{table}

This PR will be merged automatically."""
else:
    p_data = players.get(challenger)
    if p_data:
        detail = f"**{challenger}** finished with **{p_data['win_pct']}%** win rate ({p_data['total_wins']}/{p_data['total_games']} games)."
    else:
        detail = f"**{challenger}** did not beat the minimum win rate to qualify."
    body = f"""## 🎲 {challenger} did not make the leaderboard

{detail} To qualify, a challenger must beat the current lowest win rate among active players.

<details><summary>Game results</summary>

{fence}
{game_output}
{fence}
</details>

### Current Leaderboard
{table}

This PR has been left open — improve your strategy and push a new commit to try again."""

with open("comment.md", "w") as f:
    f.write(body)
