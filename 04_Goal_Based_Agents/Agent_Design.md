# Task 2 — Designing the Agent

## Agent components

- **Environment:** the supplied 7 × 21 warehouse grid; shelves are blocked and open cells are traversable.
- **Current state:** the vehicle's `(row, column)` position. At planning start this is the location marked `S`.
- **Goal:** the location marked `G`.
- **Actions:** move one cell Up, Down, Left, or Right, provided the destination is open and inside the grid.
- **Decision-making component:** breadth-first search (BFS). It stores discovered positions and parent links, then returns a shortest route. The next action is the direction from the current route position to the following position.

## Block diagram

```text
 Known warehouse map ───────┐
 Current position (row,col) ├──> [State and goal input]
 Goal position G ───────────┘             │
                                          v
                              [BFS planner: queue,
                               visited, parent links]
                                          │
                                          v
                               [Shortest path / next
                                    direction]
                                          │
                                          v
                              [Warehouse vehicle]
                                          │
                                          └── updated position
                                              fed back as state
```

The program supplied here plans against a fully known, static map. The feedback arrow represents how the same design would be used by a real vehicle: after each move, its observed position becomes the current state for the next decision.
