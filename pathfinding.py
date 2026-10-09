import math
import heapq
from grid_world import is_blocked, COLS, ROWS

THREAT_RADIUS = 4
LAMBDA = 4.0

def build_threat_map(dc, dr):
    tmap = [[0.0] * COLS for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            d = math.hypot(c - dc, r - dr)
            if d < THREAT_RADIUS:
                tmap[r][c] = 1.0 - d / THREAT_RADIUS
    return tmap

def heuristic(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def astar(start, goal, tmap, use_threat=False):
    """A* 寻路，use_threat=True 时启用威胁代价"""
    sc, sr = int(start[0]), int(start[1])
    gc, gr = int(goal[0]),  int(goal[1])
    if is_blocked(gc, gr):
        return []

    open_heap = []
    heapq.heappush(open_heap, (0, (sc, sr)))
    came_from = {}
    g_score = {(sc, sr): 0.0}

    while open_heap:
        _, cur = heapq.heappop(open_heap)
        if cur == (gc, gr):
            path = []
            while cur in came_from:
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
            return path

        for dc, dr in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nc, nr = cur[0]+dc, cur[1]+dr
            if is_blocked(nc, nr):
                continue
            move_cost   = math.hypot(dc, dr)
            threat_cost = LAMBDA * tmap[nr][nc] if use_threat else 0.0
            ng = g_score[cur] + move_cost + threat_cost
            if ng < g_score.get((nc, nr), float('inf')):
                g_score[(nc, nr)] = ng
                came_from[(nc, nr)] = cur
                f = ng + heuristic((nc, nr), (gc, gr))
                heapq.heappush(open_heap, (f, (nc, nr)))
    return []

def dijkstra(start, goal, tmap, use_threat=False):
    """威胁加权 Dijkstra，没有启发式，保证找到真正最优路径"""
    sc, sr = int(start[0]), int(start[1])
    gc, gr = int(goal[0]),  int(goal[1])
    if is_blocked(gc, gr):
        return []

    open_heap = []
    heapq.heappush(open_heap, (0, (sc, sr)))
    came_from = {}
    g_score = {(sc, sr): 0.0}

    while open_heap:
        _, cur = heapq.heappop(open_heap)
        if cur == (gc, gr):
            path = []
            while cur in came_from:
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
            return path

        for dc, dr in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nc, nr = cur[0]+dc, cur[1]+dr
            if is_blocked(nc, nr):
                continue
            move_cost   = math.hypot(dc, dr)
            threat_cost = LAMBDA * tmap[nr][nc] if use_threat else 0.0
            ng = g_score[cur] + move_cost + threat_cost
            if ng < g_score.get((nc, nr), float('inf')):
                g_score[(nc, nr)] = ng
                came_from[(nc, nr)] = cur
                heapq.heappush(open_heap, (ng, (nc, nr)))
    return []
