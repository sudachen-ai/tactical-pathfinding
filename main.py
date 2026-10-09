import pygame
import random
from grid_world import TILE, COLS, ROWS, W, H, GRID
from pathfinding import build_threat_map
from sprites import Fish, Diver, blit_centered

FPS = 30
OCEAN_A = (255, 255, 255)
OCEAN_B = (235, 245, 255)

def load_all_emojis():
    """Draw simple original placeholders; no external image pack is required."""
    images = {"fish_count": 3}
    for i, color in enumerate([(255, 130, 70), (80, 170, 240), (170, 110, 220)], 1):
        sprite = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.ellipse(sprite, color, (10, 12, 30, 20))
        pygame.draw.polygon(sprite, color, [(14, 22), (1, 10), (1, 34)])
        pygame.draw.circle(sprite, (20, 30, 40), (33, 19), 3)
        images[f"fish{i}"] = sprite
    diver = pygame.Surface((44, 44), pygame.SRCALPHA)
    pygame.draw.circle(diver, (35, 70, 95), (22, 22), 16)
    pygame.draw.rect(diver, (130, 220, 245), (10, 14, 24, 12), border_radius=4)
    images["diver"] = diver
    coral = pygame.Surface((44, 44), pygame.SRCALPHA)
    pygame.draw.rect(coral, (225, 115, 140), (8, 8, 28, 32), border_radius=8)
    images["coral"] = coral
    return images

def draw_threat(surf, tmap):
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(ROWS):
        for c in range(COLS):
            v = tmap[r][c]
            if v > 0.05:
                pygame.draw.rect(overlay, (255, 40, 40, int(v * 110)),
                                 (c * TILE, r * TILE, TILE, TILE))
    surf.blit(overlay, (0, 0))

def draw_stats(surf, fishes, font):
    import pathfinding
    f = fishes[0]
    panel = [f" Path Stats (λ={pathfinding.LAMBDA:.1f}) "]
    if f.stats:
        s = f.stats
        panel += [
            f"[blue] Normal A*   len={s['normal_len']:.1f}  threat={s['normal_threat']:.1f}",
            f"[green] Threat A*   len={s['threat_len']:.1f}  threat={s['threat_threat']:.1f}",
            f"[yellow] Dijkstra    len={s['dijkstra_len']:.1f}  threat={s['dijkstra_threat']:.1f}",
        ]
    colors = [(60,60,60), (80,80,200), (80,180,80), (180,140,0)]
    pygame.draw.rect(surf, (240,240,240), (W-340, 10, 330, 90), border_radius=6)
    for i, (line, col) in enumerate(zip(panel, colors)):
        surf.blit(font.render(line, True, col), (W-330, 15 + i*20))

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Diver & Fish")
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont(None, 20)

    emojis    = load_all_emojis()
    fish_keys = [f"fish{i}" for i in range(1, emojis["fish_count"] + 1)]

    diver = Diver(10, 7, emojis["diver"])

    fishes = []
    free_cells = [(c, r) for r in range(1, ROWS-1) for c in range(2, COLS-2) if GRID[r][c] == 0]
    for i, (c, r) in enumerate(random.sample(free_cells, 3)):
        emoji = emojis[fish_keys[i % len(fish_keys)]]
        fishes.append(Fish(i, c, r, emoji))

    coral_cells = [(c, r) for r in range(ROWS) for c in range(COLS) if GRID[r][c] == 1]

    show_threat = True
    show_paths  = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:      show_threat = not show_threat
                if event.key == pygame.K_p:      show_paths  = not show_paths
                if event.key == pygame.K_EQUALS:
                    import pathfinding
                    pathfinding.LAMBDA = min(pathfinding.LAMBDA + 1.0, 20.0)
                    for f in fishes: f.path_threat = []  # 强制重新规划
                if event.key == pygame.K_MINUS:
                    import pathfinding
                    pathfinding.LAMBDA = max(pathfinding.LAMBDA - 1.0, 0.0)
                    for f in fishes: f.path_threat = []
                if event.key == pygame.K_ESCAPE: return

        keys = pygame.key.get_pressed()
        diver.update(keys)
        tmap = build_threat_map(diver.c, diver.r)
        for f in fishes:
            f.update(tmap, diver.c, diver.r)

        # 背景
        for r in range(ROWS):
            for c in range(COLS):
                col = OCEAN_A if (c + r) % 2 == 0 else OCEAN_B
                pygame.draw.rect(screen, col, (c * TILE, r * TILE, TILE, TILE))

        # 珊瑚
        for c, r in coral_cells:
            blit_centered(screen, emojis["coral"], c * TILE + TILE // 2, r * TILE + TILE // 2)

        # 威胁热力图
        if show_threat:
            draw_threat(screen, tmap)

        # 路径和角色
        for f in fishes:
            f.draw_paths(screen, show_paths)
        for f in fishes:
            f.draw(screen)
        diver.draw(screen)

        # 统计面板
        draw_stats(screen, fishes, font)

        # UI
        msg = "WASD:move  T:threat  P:paths  +/-:weight  blue=A*  green=ThreatA*  yellow=Dijkstra  ESC:quit"
        pygame.draw.rect(screen, (240, 240, 240), (0, H - 26, W, 26))
        screen.blit(font.render(msg, True, (60, 60, 60)), (10, H - 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
