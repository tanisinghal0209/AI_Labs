import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from search_agent import (
    WAREHOUSE_MAP,
    a_star_search,
    breadth_first_search,
    find_marker,
    heuristic,
    validate_grid,
)


class SearchAgentTests(unittest.TestCase):
    def assert_valid_path(self, rows, result):
        self.assertIsNotNone(result.path)
        path = result.path
        assert path is not None
        grid = validate_grid(rows)
        self.assertEqual(path[0], find_marker(grid, "S"))
        self.assertEqual(path[-1], find_marker(grid, "G"))
        for (r1, c1), (r2, c2) in zip(path, path[1:]):
            self.assertEqual(abs(r1 - r2) + abs(c1 - c2), 1)
            self.assertNotEqual(grid[r2][c2], "#")

    def test_original_map_dimensions_and_markers(self):
        self.assertEqual(len(WAREHOUSE_MAP), 9)
        self.assertTrue(all(len(row) == 17 for row in WAREHOUSE_MAP))
        self.assertEqual(sum(row.count("S") for row in WAREHOUSE_MAP), 1)
        self.assertEqual(sum(row.count("G") for row in WAREHOUSE_MAP), 1)

    def test_original_map_astar_and_bfs_find_shortest_paths(self):
        bfs = breadth_first_search(WAREHOUSE_MAP)
        astar = a_star_search(WAREHOUSE_MAP, "manhattan")
        self.assert_valid_path(WAREHOUSE_MAP, bfs)
        self.assert_valid_path(WAREHOUSE_MAP, astar)
        self.assertEqual(astar.path_length, bfs.path_length)

    def test_trivial_adjacent_goal_is_one_move(self):
        grid = ("#####", "#SG##", "#####")
        result = a_star_search(grid)
        self.assert_valid_path(grid, result)
        self.assertEqual(result.path_length, 1)

    def test_inaccessible_goal_returns_no_solution(self):
        grid = ("#######", "#S....#", "###.###", "#...#G#", "#######")
        self.assertIsNone(a_star_search(grid).path)

    def test_alternative_paths_still_return_a_shortest_route(self):
        grid = ("#######", "#S...G#", "#.....#", "#######")
        bfs = breadth_first_search(grid)
        astar = a_star_search(grid, "manhattan")
        self.assert_valid_path(grid, astar)
        self.assertEqual(astar.path_length, bfs.path_length)

    def test_heuristics_are_nonnegative_and_zero_is_zero(self):
        position, goal = (1, 2), (4, 6)
        self.assertEqual(heuristic(position, goal, "zero"), 0)
        self.assertEqual(heuristic(position, goal, "manhattan"), 7)
        self.assertAlmostEqual(heuristic(position, goal, "euclidean"), 5.0)
        self.assertEqual(heuristic(position, goal, "double_manhattan"), 14)

    def test_malformed_map_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "rectangular"):
            validate_grid(("#####", "#S.G", "#####"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
