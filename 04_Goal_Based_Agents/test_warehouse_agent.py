import unittest
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

from warehouse_agent import (
    WAREHOUSE_MAP,
    WarehouseAgent,
    action_between,
    breadth_first_search,
    find_marker,
    validate_grid,
)


class WarehouseAgentTests(unittest.TestCase):
    def test_handout_map_dimensions_and_markers(self):
        self.assertEqual(len(WAREHOUSE_MAP), 7)
        self.assertTrue(all(len(row) == 21 for row in WAREHOUSE_MAP))
        self.assertEqual(sum(row.count("S") for row in WAREHOUSE_MAP), 1)
        self.assertEqual(sum(row.count("G") for row in WAREHOUSE_MAP), 1)

    def test_supplied_map_has_collision_free_shortest_path(self):
        agent = WarehouseAgent()
        path = agent.plan()

        self.assertIsNotNone(path)
        assert path is not None
        self.assertEqual(path[0], find_marker(WAREHOUSE_MAP, "S"))
        self.assertEqual(path[-1], find_marker(WAREHOUSE_MAP, "G"))

        for source, destination in zip(path, path[1:]):
            self.assertEqual(
                abs(source[0] - destination[0]) + abs(source[1] - destination[1]),
                1,
            )
            self.assertNotEqual(WAREHOUSE_MAP[destination[0]][destination[1]], "#")
            self.assertIn(action_between(source, destination), {"Up", "Down", "Left", "Right"})

        # The known shortest distance for the handout map is 20 moves.
        self.assertEqual(len(path) - 1, 20)

    def test_unreachable_goal_returns_none(self):
        enclosed_goal = (
            "#####",
            "#S#G#",
            "#####",
        )
        self.assertIsNone(breadth_first_search(enclosed_goal, (1, 1), (1, 3)))

    def test_start_equal_to_goal_returns_single_position_path(self):
        one_row = ("S.G",)
        self.assertEqual(breadth_first_search(one_row, (0, 0), (0, 0)), [(0, 0)])

    def test_ragged_grid_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "rectangular"):
            validate_grid(("####", "#S.G", "###"))

    def test_missing_or_duplicate_markers_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly one S"):
            validate_grid(("###", "#..", "#G#"))
        with self.assertRaisesRegex(ValueError, "exactly one G"):
            validate_grid(("#####", "#SGG#", "#####"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
