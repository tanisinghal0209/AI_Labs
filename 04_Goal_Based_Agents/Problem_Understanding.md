# Task 1 — Understanding the Problem

## 1. What is the environment?

The environment is a known, static, two-dimensional warehouse grid. The map uses `S` for the vehicle's starting square, `G` for the dispatch destination, `#` for shelving that blocks movement, and `.` for an open square. The supplied map is 7 rows by 21 columns. The agent can observe the whole map and its current grid position.

## 2. What is the goal of the agent?

Reach the square marked `G` from the square marked `S` without entering a shelf square or leaving the map. Since every move has the same cost, the implemented agent returns a route with the fewest moves.

## 3. What actions are available?

The vehicle can move one square Up, Down, Left, or Right. Diagonal moves are not allowed. A move is legal only if its destination is inside the map and is not marked `#`.

## 4. What information must the agent maintain?

The agent needs the warehouse map, its current position as a `(row, column)` pair, and the goal position. During BFS it also maintains a queue of positions to explore and a parent link for each discovered position. The parent links reconstruct the route after the goal is found. The visited positions prevent repeated work. The implementation treats the map as static and plans from the supplied start to the goal; a physical vehicle would also need to track its changing position and replan if observations differed from the map.

## 5. Why is this a goal-based agent?

The agent has an explicit goal position and uses a model of the map to compare possible future states. It chooses actions as part of a route to `G`. A simple reflex agent would choose an action only from the current percept using a fixed rule; it would not search ahead to decide whether a move helps reach the destination or avoids a dead end.

## Think About It — If the Warehouse Becomes Twice as Large

BFS remains appropriate when the enlarged warehouse is a finite grid and every move has equal cost. Its time and memory use grow with the number of reachable squares, approximately `O(V + E)`; in a four-neighbour grid, this is linear in the number of squares. A larger map can therefore require substantially more memory and search time. If the map is very large, A* with Manhattan distance can prioritize positions likely to reach the goal sooner. If moves have different costs, Dijkstra's algorithm or A* with a suitable cost-aware heuristic is more appropriate. Unknown or moving obstacles would also require fresh observations and replanning.
