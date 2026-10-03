# Task 3 — Prompt Engineering

## Prompt used for this completion pass

The following task-specific prompt was prepared from the laboratory handout and used to guide the implementation in this folder. It records this completion pass; it is not a reconstruction of an earlier chat transcript.

```text
Write a clear, documented Python 3 program for the goal-based warehouse navigation task. Use this exact map, where S is the start, G is the goal, # is blocked, and . is open:

#####################
#S....#............G#
#.##....##########..#
#....##.............#
#.######.###.#.###..#
#........#..........#
#####################

Allow only one-cell Up, Down, Left, and Right moves. Find a collision-free route from S to G, print the route or a clear no-route message, and explain the search algorithm and why it fits this problem. Reject malformed maps clearly. Keep this grid-navigation program separate from the supplied symbolic package-transfer planner. Include tests for the supplied route, obstacle avoidance, unreachable goals, and basic map validation.
```

## Generated program

The resulting implementation is [warehouse_agent.py](warehouse_agent.py). It parses and validates the map, uses breadth-first search, reconstructs the route from parent links, and prints the directions with zero-based `(row, column)` coordinates.

## Execution and iteration record

- **Did it work on the first attempt?** Yes. The first run of the generated program found a route from `(1, 1)` to `(1, 19)` in 20 moves and printed every action.
- **What was tested?** Six unit tests check the handout map dimensions and markers, the supplied map route and obstacle avoidance, an unreachable goal, a start already at the goal, a ragged map, and missing or duplicate markers. The first test run found an incorrect duplicate-marker fixture; I corrected the fixture and the tests passed on rerun. Results are saved in [warehouse_agent_test_output.txt](Results/warehouse_agent_test_output.txt). The program's run is saved in [warehouse_agent_run_output.txt](Results/warehouse_agent_run_output.txt).
- **What algorithm did it choose?** Breadth-first search (BFS).
- **Why is BFS appropriate?** The warehouse is a finite, unweighted grid: each legal move costs one step. BFS explores positions by increasing path length, is complete for this finite map, and returns a shortest route. With `V` traversable cells and `E` legal neighbour links, its time and memory use are `O(V + E)`.
- **Were prompt improvements needed after execution?** No corrective prompt iteration was needed. The first program run produced the expected route; the test-suite correction was to the test fixture, not the generated program. The task-specific prompt states the exact map, movement rules, output, and validation needs so the implementation target is unambiguous.

## Reproduce

From the project root:

```bash
python3 04_Goal_Based_Agents/warehouse_agent.py
python3 04_Goal_Based_Agents/test_warehouse_agent.py
```

The symbolic package-transfer planner is filed separately under **Logical Planning**; it is not the grid-navigation solution.
