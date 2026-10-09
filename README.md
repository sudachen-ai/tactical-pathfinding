# Tactical Pathfinding

An interactive Python/Pygame demo by Shiyu Chen, developed for the Spring 2026 CS 5150 Game AI final project. Fish avoid a player-controlled diver while the interface compares standard A*, threat-weighted A*, and threat-weighted Dijkstra on the same planning snapshot.

## Run

Python 3.10 or later is recommended.

```sh
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

Move with WASD or arrow keys. Press `T` for the threat overlay, `P` for paths, `+`/`=` or `-` to change the threat weight, and `Esc` to quit. Blue is ordinary A*, green is threat-weighted A*, and yellow is threat-weighted Dijkstra. The panel describes the first fish's most recent plan.

## How it works

The world is a 20 by 15 grid. Search considers eight neighboring cells. Each step costs its geometric length plus `weight * threat(destination_cell)` when threat costs are enabled. A* adds a Euclidean heuristic to this accumulated cost; Dijkstra uses the accumulated cost alone. A threat field is centered on the diver, and fish switch between wandering and fleeing.

Each search receives a fixed threat-map snapshot. Moving the diver can make an existing plan stale between replans, but does not change the cost map midway through these synchronous searches. With nonnegative threat weights, the Euclidean heuristic remains admissible. Different equal-cost routes are possible; compare total objective cost, not path shape alone.

## Code map

| File | Responsibility |
| --- | --- |
| `main.py` | Event loop, controls, overlays and self-contained placeholder graphics |
| `grid_world.py` | Grid, obstacles and bounds checks |
| `pathfinding.py` | Threat field and A*/Dijkstra searches |
| `sprites.py` | Fish and diver movement and replanning |
| `metrics.py` | Route distance and threat exposure |
| `test_pathfinding.py` | Search-cost and metric regression checks |

## Validation

```sh
python -m unittest -v test_pathfinding.py
```

The tests compare A* and Dijkstra on 120 identical-snapshot cases and check path accounting. All three test methods passed during the October 2026 cleanup. The graphical loop has not been rerun in that cleanup environment because Pygame was unavailable. The simulation is a small teaching demo: diagonal corner-cutting is allowed, fish are point agents during planning, and replanning is periodic rather than continuous. No production-scale performance claim is made.

## Project history

The four original Python modules come from the course project. The October 2026 portfolio cleanup renamed `map.py`, extracted shared metrics, included the first path segment in displayed distance, avoided spawning fish in blocked cells, separated weight controls from movement, and replaced external emoji files with simple procedural graphics. It also corrected the explanation of snapshot search optimality. These maintenance changes are distinct from the original course submission.

[Original submitted demonstration video](https://youtu.be/5_PjMS6uTUo) shows the course version. The current placeholders look different. Course handouts, grades and private feedback are not included.
