"""BFS and A* search for the warehouse map in the Search laboratory brief."""

from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import hypot

Position = tuple[int, int]
Grid = tuple[str, ...]

WAREHOUSE_MAP = (
    "#################",
    "#S....#.........#",
    "#.###.#.#######.#",
    "#...#.#.......#.#",
    "###.#.#######.#.#",
    "#...#.........#.#",
    "#.###########.#.#",
    "#.............#G#",
    "#################",
)

MOVES: tuple[tuple[str, int, int], ...] = (
    ("Up", -1, 0),
    ("Down", 1, 0),
    ("Left", 0, -1),
    ("Right", 0, 1),
)


@dataclass(frozen=True)
class SearchResult:
    path: tuple[Position, ...] | None
    states_expanded: int

    @property
    def path_length(self) -> int | None:
        return None if self.path is None else len(self.path) - 1


def validate_grid(rows: Sequence[str]) -> Grid:
    grid = tuple(row.strip() for row in rows)
    if not grid or not grid[0] or any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("The warehouse must be a non-empty rectangular grid.")
    allowed = {"#", ".", "S", "G"}
    invalid = sorted({cell for row in grid for cell in row if cell not in allowed})
    if invalid:
        raise ValueError(f"Unsupported map characters: {invalid}")
    for marker in ("S", "G"):
        count_found = sum(row.count(marker) for row in grid)
        if count_found != 1:
            raise ValueError(f"The grid must contain exactly one {marker}; found {count_found}.")
    return grid


def find_marker(grid: Grid, marker: str) -> Position:
    for row, line in enumerate(grid):
        column = line.find(marker)
        if column >= 0:
            return row, column
    raise ValueError(f"Missing map marker {marker!r}.")


def heuristic(position: Position, goal: Position, name: str) -> float:
    row_distance = abs(position[0] - goal[0])
    column_distance = abs(position[1] - goal[1])
    if name == "manhattan":
        return float(row_distance + column_distance)
    if name == "euclidean":
        return hypot(row_distance, column_distance)
    if name == "zero":
        return 0.0
    if name == "double_manhattan":
        return float(2 * (row_distance + column_distance))
    raise ValueError(f"Unknown heuristic: {name}")


def _reconstruct_path(
    parent: dict[Position, Position | None], goal: Position
) -> tuple[Position, ...]:
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])  # type: ignore[arg-type]
    path.reverse()
    return tuple(path)


def breadth_first_search(rows: Sequence[str]) -> SearchResult:
    grid = validate_grid(rows)
    start, goal = find_marker(grid, "S"), find_marker(grid, "G")
    height, width = len(grid), len(grid[0])

    def is_open(position: Position) -> bool:
        row, column = position
        return 0 <= row < height and 0 <= column < width and grid[row][column] != "#"

    frontier = deque([start])
    parent: dict[Position, Position | None] = {start: None}
    expanded = 0
    while frontier:
        current = frontier.popleft()
        if current == goal:
            return SearchResult(_reconstruct_path(parent, goal), expanded)
        expanded += 1
        row, column = current
        for _action, dr, dc in MOVES:
            neighbor = row + dr, column + dc
            if is_open(neighbor) and neighbor not in parent:
                parent[neighbor] = current
                frontier.append(neighbor)
    return SearchResult(None, expanded)


def a_star_search(rows: Sequence[str], heuristic_name: str = "manhattan") -> SearchResult:
    grid = validate_grid(rows)
    start, goal = find_marker(grid, "S"), find_marker(grid, "G")
    height, width = len(grid), len(grid[0])

    def is_open(position: Position) -> bool:
        row, column = position
        return 0 <= row < height and 0 <= column < width and grid[row][column] != "#"

    sequence = count()
    frontier: list[tuple[float, int, float, Position]] = []
    initial_h = heuristic(start, goal, heuristic_name)
    heappush(frontier, (initial_h, next(sequence), 0.0, start))
    g_score = {start: 0.0}
    parent: dict[Position, Position | None] = {start: None}
    expanded = 0

    while frontier:
        _f_score, _order, current_g, current = heappop(frontier)
        if current_g != g_score.get(current):
            continue  # Ignore an outdated heap entry after a better route was found.
        if current == goal:
            return SearchResult(_reconstruct_path(parent, goal), expanded)
        expanded += 1

        row, column = current
        for _action, dr, dc in MOVES:
            neighbor = row + dr, column + dc
            if not is_open(neighbor):
                continue
            candidate_g = current_g + 1
            if candidate_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = candidate_g
                parent[neighbor] = current
                score = candidate_g + heuristic(neighbor, goal, heuristic_name)
                heappush(frontier, (score, next(sequence), candidate_g, neighbor))

    return SearchResult(None, expanded)


def print_result(name: str, result: SearchResult) -> None:
    print(f"{name}: solution={'yes' if result.path is not None else 'no'}")
    print(f"  path length: {result.path_length}")
    print(f"  states expanded: {result.states_expanded}")
    if result.path is not None:
        print(f"  path: {list(result.path)}")


def main() -> None:
    print("Warehouse map:")
    print("\n".join(WAREHOUSE_MAP))
    print("\nState: (row, column); actions: Up, Down, Left, Right; each costs 1.")
    print("Manhattan heuristic: |row-row_goal| + |column-column_goal|.")
    print_result("A* with Manhattan heuristic", a_star_search(WAREHOUSE_MAP))


if __name__ == "__main__":
    main()
