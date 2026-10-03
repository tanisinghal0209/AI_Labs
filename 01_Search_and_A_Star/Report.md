# Search and A* Laboratory Report

## Search problem specification

| Component | Specification |
|---|---|
| State | A free grid coordinate `(row, column)`. The map is fixed, so the coordinate is sufficient to identify a state. |
| Actions | Move one cell Up, Down, Left, or Right. |
| Transition | Add the chosen row/column offset when the resulting cell is inside the grid and is not `#`. |
| Initial state | `S` at `(1, 1)` using zero-based coordinates. |
| Goal | Reach `G` at `(7, 15)`. |
| Cost | 1 for every move. |

The problem is deterministic: each legal action has one known result. An action is invalid if it leaves the grid or enters an obstacle. A solution is a sequence of valid moves that starts at `S` and ends at `G`; its cost is its number of moves.

## Agent design

The grid is a tuple of strings. The search frontier holds coordinates, a parent mapping reconstructs the route, and a `g_score` mapping stores the best known start-to-state cost. A* uses a `heapq` priority queue ordered by `f(n) = g(n) + h(n)`. Stale heap entries are skipped when a lower-cost route to a state has since been found. The program reports whether it found a path, the coordinates in that path, its length, and the count of expanded states. The count includes states whose neighbours were considered and excludes the goal state when it is popped.

## Prompt used for the implementation

This is the task-specific prompt used to guide this implementation; no earlier Search-lab prompt transcript was present in the workspace.

```text
Implement A* search in Python for the following warehouse grid. Positions are row-column pairs. The robot starts at S and must reach G. It may move one cell Up, Down, Left, or Right; each move costs 1 and cells marked # are blocked. Use Manhattan distance as the heuristic. Maintain g, h, and f values, avoid unnecessary repeated expansion, reconstruct and print the path and length, and report the number of expanded states. Include tests for the given map, an adjacent goal, an inaccessible goal, and a map with alternative paths. Also provide a BFS implementation for comparison and let the heuristic be selected as zero, Manhattan, Euclidean, or twice Manhattan for the experiments.

#################
#S....#.........#
#.###.#.#######.#
#...#.#.......#.#
###.#.#######.#.#
#...#.........#.#
#.###########.#.#
#.............#G#
#################
```

## Generated program and tests

- `search_agent.py` implements BFS, A*, grid validation, path reconstruction, and expanded-state reporting.
- `run_experiments.py` runs the requested BFS/A* and heuristic comparisons.
- `test_search_agent.py` tests the supplied map, dimensions, path validity, shortest path, a one-move case, an inaccessible goal, alternative paths, heuristic values, and malformed input.
- The test run passed all 7 tests. See `test_output.txt` and `experiment_output.txt`.

## Original map and BFS/A* comparison

Both algorithms found a 40-move path. With the stated expanded-state counting rule, both expanded 63 states. The route can be written compactly as:

```text
Right × 4, Down × 4, Right × 8, Up × 2,
Left × 6, Up × 2, Right × 8, Down × 6
```

It ends at `(7, 15)`. BFS and Manhattan A* returned the same shortest length. A* did not expand fewer states on this particular maze. This is a measured result for this map, not a claim that A* always expands the same number as BFS.

Thus both found a solution, their path lengths were equal, and neither expanded fewer states on this map. A* can expand fewer states when an informative heuristic directs the search toward the goal and away from irrelevant parts of the map; the corridors and tie ordering in this maze did not produce that reduction.

## Heuristic investigation

| A* heuristic | Solution | Path length | States expanded |
|---|---:|---:|---:|
| `h(n) = 0` | Yes | 40 | 63 |
| Euclidean distance | Yes | 40 | 63 |
| `2 × Manhattan` | Yes | 40 | 66 |

With `h = 0`, A* orders states by accumulated cost only, so it behaves like uniform-cost search; with unit-cost moves this gives the same shortest-path guarantee as BFS. Euclidean distance is also a lower bound for a four-direction grid, but it did not reduce the expanded count on this maze. Doubling Manhattan can overestimate the remaining cost, so A* with that heuristic is no longer guaranteed to return an optimal path. It still found a 40-move shortest path here, verified against BFS, and expanded three more states than the other runs.

## Where A* concepts appear

| Concept | Implementation |
|---|---|
| State | `(row, column)` tuple |
| Action and transition | The four offsets in `MOVES`; bounds and obstacle checks in each search function |
| Goal test | Compare the popped coordinate with `G` |
| `g(n)` | `g_score` and the `current_g + 1` successor cost |
| `h(n)` | `heuristic()` |
| `f(n)` | `candidate_g + heuristic(...)` when pushing to the heap |
| Frontier | Python `heapq`, ordered by `f`; a sequence number breaks ties consistently |
| Visited/best paths | `g_score`; a state is updated only for a strictly lower cost |
| Path reconstruction | `parent` links followed backward from the goal |

## Tests and validation

The test suite passed these cases:

1. The supplied 9 × 17 map has one `S` and one `G`.
2. BFS and Manhattan A* return legal paths of equal length on the supplied map.
3. An adjacent goal takes one move.
4. A fully inaccessible goal returns no path.
5. On a map with multiple routes, A* returns a shortest path matching BFS.
6. The four heuristic functions return the expected distances.
7. A ragged map is rejected.

The executable transcripts are stored alongside the code. Reproduce them from the project root with:

```bash
python3 01_Search_and_A_Star/search_agent.py
python3 01_Search_and_A_Star/run_experiments.py
python3 01_Search_and_A_Star/test_search_agent.py
```

## Task 7 — Evaluate the LLM-assisted implementation

1. **What was correct in the saved run?** The four-neighbour transition rules, obstacle and boundary checks, route reconstruction, and reported metrics matched the specification; the seven tests and the original-map run passed.
2. **Were bugs or design problems found?** The saved search runs exposed no implementation bug. The deliberately doubled heuristic is a design tradeoff: it can overestimate and therefore does not retain A*'s general shortest-path guarantee.
3. **How were problems checked?** I compared the A* route length with BFS on the original and alternative-path maps, and checked trivial and unreachable cases with known outcomes.
4. **Were terms or data structures unclear?** The important structures are an ordered heap frontier, `g_score`, and parent links. The report defines how each supports the algorithm rather than treating their names as evidence of correctness.
5. **Was the implementation modified?** The saved implementation includes the required BFS baseline and switchable heuristic experiments. No corrective code edit was needed after its seven-test run.
6. **Which tests were most useful?** The adjacent-goal and inaccessible-goal cases have unambiguous expected results; the alternative-path case independently checks shortest-path behaviour against BFS.
7. **Could the program be trusted without testing?** No. A program can print a plausible route while crossing a wall, mishandling a disconnected goal, or misreporting path cost.
8. **What did implementing A* clarify?** The `g` term measures cost already paid, `h` estimates cost remaining, and their sum determines which frontier entry is considered next. The quality and admissibility of `h` affect both work and guarantees.

## Final reflection

1. **Why formulate the problem first?** It gives a clear contract for states, actions, transitions, goal testing, and cost before those ideas are encoded in data structures.
2. **In what sense is A* informed?** It uses a goal-directed heuristic estimate in addition to the cost from the start when prioritizing states.
3. **Why does the heuristic matter?** It changes search order; an admissible heuristic preserves optimality, while an overestimate can lose that guarantee.
4. **What did the LLM contribute?** It helped translate the design into implementation and test scaffolding, which were then validated against the PDF's map and test cases.
5. **What could go wrong without testing?** Incorrect transitions, an invalid route, a false no-path result, or an unsupported claim of shortest-path optimality could go unnoticed.
