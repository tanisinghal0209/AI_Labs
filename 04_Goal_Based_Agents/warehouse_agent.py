"""Goal-based agent for the warehouse map in the laboratory handout."""

from collections import deque
from collections.abc import Sequence

Position = tuple[int, int]

WAREHOUSE_MAP = (
    "#####################",
    "#S....#............G#",
    "#.##....##########..#",
    "#....##.............#",
    "#.######.###.#.###..#",
    "#........#..........#",
    "#####################",
)

MOVES: tuple[tuple[str, int, int], ...] = (
    ("Up", -1, 0),
    ("Down", 1, 0),
    ("Left", 0, -1),
    ("Right", 0, 1),
)


def validate_grid(rows: Sequence[str]) -> tuple[str, ...]:
    """Return a normalized grid, rejecting malformed maps."""
    grid = tuple(row.strip() for row in rows)
    if not grid:
        raise ValueError("The warehouse map must contain at least one row.")

    width = len(grid[0])
    if width == 0 or any(len(row) != width for row in grid):
        raise ValueError("The warehouse map must be rectangular and non-empty.")

    allowed = {"#", ".", "S", "G"}
    invalid = sorted({cell for row in grid for cell in row if cell not in allowed})
    if invalid:
        raise ValueError(f"The map contains unsupported characters: {invalid}")

    for marker in ("S", "G"):
        count = sum(row.count(marker) for row in grid)
        if count != 1:
            raise ValueError(f"The map must contain exactly one {marker}; found {count}.")

    return grid


def find_marker(grid: Sequence[str], marker: str) -> Position:
    """Find the row and column of a marker in a validated grid."""
    for row_index, row in enumerate(grid):
        column_index = row.find(marker)
        if column_index != -1:
            return row_index, column_index
    raise ValueError(f"The map does not contain {marker!r}.")


def breadth_first_search(
    grid_rows: Sequence[str], start: Position, goal: Position
) -> list[Position] | None:
    """Return a shortest path from start to goal, or None if unreachable.

    Each legal move has equal cost, so breadth-first search explores positions
    in order of path length. The returned path includes both endpoints.
    """
    grid = validate_grid(grid_rows)
    height, width = len(grid), len(grid[0])

    def is_open(position: Position) -> bool:
        row, column = position
        return (
            0 <= row < height
            and 0 <= column < width
            and grid[row][column] != "#"
        )

    if not is_open(start) or not is_open(goal):
        return None

    frontier = deque([start])
    parent: dict[Position, Position | None] = {start: None}

    while frontier:
        current = frontier.popleft()
        if current == goal:
            break

        row, column = current
        for _action, row_change, column_change in MOVES:
            neighbor = row + row_change, column + column_change
            if is_open(neighbor) and neighbor not in parent:
                parent[neighbor] = current
                frontier.append(neighbor)

    if goal not in parent:
        return None

    path = [goal]
    while path[-1] != start:
        previous = parent[path[-1]]
        assert previous is not None
        path.append(previous)
    path.reverse()
    return path


def action_between(source: Position, destination: Position) -> str:
    """Return the cardinal action that moves between adjacent positions."""
    change = destination[0] - source[0], destination[1] - source[1]
    for action, row_change, column_change in MOVES:
        if change == (row_change, column_change):
            return action
    raise ValueError(f"Positions are not adjacent: {source} -> {destination}")


class WarehouseAgent:
    """A goal-based agent that plans a route through a known static map."""

    def __init__(self, grid_rows: Sequence[str] = WAREHOUSE_MAP) -> None:
        self.grid = validate_grid(grid_rows)
        self.start = find_marker(self.grid, "S")
        self.goal = find_marker(self.grid, "G")

    def plan(self) -> list[Position] | None:
        """Plan a shortest route from S to G using breadth-first search."""
        return breadth_first_search(self.grid, self.start, self.goal)


def main() -> None:
    agent = WarehouseAgent()
    path = agent.plan()

    print("Warehouse map:")
    print("\n".join(agent.grid))
    print("\nSearch algorithm: Breadth-First Search (BFS)")
    print("BFS is complete and finds a shortest path because every move has equal cost.")

    if path is None:
        print("\nNo collision-free path exists from S to G.")
        return

    print(f"\nPath found: {len(path) - 1} moves")
    print(f"Start (row, column): {path[0]}")
    for source, destination in zip(path, path[1:]):
        print(f"{action_between(source, destination)} -> {destination}")
    print(f"Goal reached at (row, column): {path[-1]}")


if __name__ == "__main__":
    main()
