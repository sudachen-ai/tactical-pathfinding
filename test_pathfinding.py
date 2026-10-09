import math
import random
import unittest
import pathfinding as pf
from grid_world import GRID, ROWS, COLS, is_blocked
from metrics import path_length, path_threat

class SearchTests(unittest.TestCase):
    def test_first_segment_is_counted(self):
        self.assertAlmostEqual(path_length([(1, 1), (2, 1)], (0, 0)), math.sqrt(2)+1)

    def test_same_snapshot_cost_matches(self):
        rng = random.Random(5150)
        cells = [(c,r) for r in range(ROWS) for c in range(COLS) if not is_blocked(c,r)]
        old = pf.LAMBDA
        try:
            for weight in (0, 1, 4, 20):
                pf.LAMBDA = weight
                for _ in range(30):
                    start, goal, diver = rng.sample(cells, 3)
                    tm = pf.build_threat_map(*diver)
                    a = pf.astar(start, goal, tm, True)
                    d = pf.dijkstra(start, goal, tm, True)
                    self.assertTrue(a and d)
                    for path in (a,d):
                        self.assertEqual(path[-1], goal)
                        prev = start
                        for cell in path:
                            self.assertFalse(is_blocked(*cell))
                            self.assertLessEqual(max(abs(cell[0]-prev[0]),abs(cell[1]-prev[1])), 1)
                            prev = cell
                    self.assertAlmostEqual(path_length(a,start)+weight*path_threat(a,tm),
                                           path_length(d,start)+weight*path_threat(d,tm), places=8)
        finally:
            pf.LAMBDA = old

    def test_blocked_goal(self):
        tm=pf.build_threat_map(10,7)
        self.assertEqual(pf.astar((0,0),(2,1),tm), [])
        self.assertEqual(pf.dijkstra((0,0),(2,1),tm), [])

if __name__ == '__main__':
    unittest.main()
