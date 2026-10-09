import pygame
import math
import random
from grid_world import is_blocked, TILE, COLS, ROWS
from pathfinding import astar, dijkstra
from metrics import path_length, path_threat

DIVER_RADIUS = 0.28
FLEE_RADIUS  = 6

def collides(c, r):
    for dc in [-DIVER_RADIUS, DIVER_RADIUS]:
        for dr in [-DIVER_RADIUS, DIVER_RADIUS]:
            if is_blocked(int(c + dc), int(r + dr)):
                return True
    return False

def blit_centered(surf, img, cx, cy):
    surf.blit(img, (cx - img.get_width() // 2, cy - img.get_height() // 2))

def find_flee_target(diver_c, diver_r):
    best, best_dist = None, -1
    for _ in range(40):
        nc = random.randint(0, COLS - 1)
        nr = random.randint(0, ROWS - 1)
        if is_blocked(nc, nr):
            continue
        d = math.hypot(nc - diver_c, nr - diver_r)
        if d > best_dist:
            best_dist = d
            best = (nc, nr)
    return best

class Fish:
    def __init__(self, idx, c, r, emoji):
        self.c = float(c); self.r = float(r)
        self.speed   = 0.06 + random.uniform(0, 0.02)
        self.timer   = random.randint(0, 60)
        self.emoji   = emoji
        self.facing  = 1
        self.target  = None
        self.fleeing = False

        # 三条路径
        self.path_normal  = []  # 普通 A*
        self.path_threat  = []  # Threat-Cost A*（鱼实际走这条）
        self.path_dijkstra = [] # Dijkstra

        # 统计数据
        self.stats = {}

    def _plan_all(self, tmap):
        if not self.target:
            return
        start = (self.c, self.r)
        self.path_normal   = astar(start, self.target, tmap, use_threat=False)
        self.path_threat   = astar(start, self.target, tmap, use_threat=True)
        self.path_dijkstra = dijkstra(start, self.target, tmap, use_threat=True)

        # 算统计数据
        self.stats = {
            "normal_len":    round(path_length(self.path_normal, start),   2),
            "threat_len":    round(path_length(self.path_threat, start),    2),
            "dijkstra_len":  round(path_length(self.path_dijkstra, start),  2),
            "normal_threat": round(path_threat(self.path_normal,  tmap), 2),
            "threat_threat": round(path_threat(self.path_threat,  tmap), 2),
            "dijkstra_threat": round(path_threat(self.path_dijkstra, tmap), 2),
        }

    def _pick_wander(self):
        for _ in range(30):
            nc = int(self.c) + random.randint(-6, 6)
            nr = int(self.r) + random.randint(-6, 6)
            if not is_blocked(nc, nr):
                self.target = (nc, nr)
                return

    def update(self, tmap, diver_c, diver_r):
        dist_to_diver = math.hypot(self.c - diver_c, self.r - diver_r)
        is_near = dist_to_diver < FLEE_RADIUS

        self.timer += 1

        if is_near and not self.fleeing:
            self.fleeing = True
            self.path_threat = []
            self.timer = 999
        if not is_near and self.fleeing:
            self.fleeing = False
            self.path_threat = []
            self.timer = 999

        if not self.path_threat or self.timer >= 80:
            self.timer = 0
            if self.fleeing:
                self.target = find_flee_target(diver_c, diver_r)
            else:
                self._pick_wander()
            self._plan_all(tmap)

        # 鱼实际跟着 Threat-Cost A* 走
        if self.path_threat:
            nc, nr = self.path_threat[0]
            dc = nc - self.c
            dr = nr - self.r
            dist = math.hypot(dc, dr)
            if dist < 0.1:
                self.path_threat.pop(0)
            else:
                if abs(dc) > 0.05:
                    self.facing = 1 if dc > 0 else -1
                speed = self.speed * (1.5 if self.fleeing else 1.0)
                self.c += (dc / dist) * speed
                self.r += (dr / dist) * speed

    def draw(self, surf):
        px = int(self.c * TILE + TILE // 2)
        py = int(self.r * TILE + TILE // 2)
        img = self.emoji
        if self.facing == -1:
            img = pygame.transform.flip(img, True, False)
        blit_centered(surf, img, px, py)

    def draw_paths(self, surf, show_paths):
        if not show_paths:
            return
        for path, color, width in [
            (self.path_normal,   (80,  80, 200), 2),  # 蓝
            (self.path_threat,   (80, 200,  80), 2),  # 绿
            (self.path_dijkstra, (220,180,   0), 2),  # 黄
        ]:
            if len(path) >= 2:
                pts = [(c * TILE + TILE // 2, r * TILE + TILE // 2) for c, r in path]
                pygame.draw.lines(surf, color, False, pts, width)


class Diver:
    def __init__(self, c, r, emoji):
        self.c = float(c); self.r = float(r)
        self.speed = 0.15
        self.emoji = emoji

    def update(self, keys):
        dc = dr = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dc = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dc =  1
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dr = -1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dr =  1
        nc = self.c + dc * self.speed
        nr = self.r + dr * self.speed
        if not collides(nc, self.r):
            self.c = max(DIVER_RADIUS, min(COLS - 1 - DIVER_RADIUS, nc))
        if not collides(self.c, nr):
            self.r = max(DIVER_RADIUS, min(ROWS - 1 - DIVER_RADIUS, nr))

    def draw(self, surf):
        px = int(self.c * TILE + TILE // 2)
        py = int(self.r * TILE + TILE // 2)
        blit_centered(surf, self.emoji, px, py)
