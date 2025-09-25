import pygame as pg
import random
import math
import time


WIDTH, HEIGHT = 960, 540
FPS = 120
SESSION_TIME = 60 
TARGET_MIN_R, TARGET_MAX_R = 18, 38
SPAWN_MARGIN = 50 
HIT_SHRINK = 0.85  
MISS_PENALTY = 0  

BG_COLOR = (20, 22, 28)
FG_COLOR = (240, 240, 240)

class Target:
    def __init__(self):
        self.r = random.randint(TARGET_MIN_R, TARGET_MAX_R)
        self.x = random.randint(SPAWN_MARGIN, WIDTH - SPAWN_MARGIN)
        self.y = random.randint(SPAWN_MARGIN, HEIGHT - SPAWN_MARGIN)
        self.color = (random.randint(120, 255), 50, 70)

    def draw(self, surf):
        pg.draw.circle(surf, self.color, (self.x, self.y), self.r)
        pg.draw.circle(surf, (255, 255, 255), (self.x, self.y), max(2, self.r // 6)) 

    def contains(self, mx, my):
        return (mx - self.x) ** 2 + (my - self.y) ** 2 <= self.r ** 2

    def respawn(self):
        self.__init__()


def format_time(seconds):
    return time.strftime("%M:%S", time.gmtime(max(0, int(seconds))))

def main():
    pg.init()
    pg.display.set_caption("Aim Trainer (Pygame)")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.SysFont("consolas", 22)

    targets = [Target() for _ in range(4)]
    running = True

    start_ts = time.time()
    end_ts = start_ts + SESSION_TIME
    shots = 0
    hits = 0
    hit_times = [] 

    target_spawn_ts = {id(t): time.time() for t in targets}

    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()
        remaining = end_ts - now

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and remaining > 0:
                mx, my = pg.mouse.get_pos()
                shots += 1
                hit_idx = None
                min_dist = 1e9
                for i, t in enumerate(targets):
                    if t.contains(mx, my):
                        d = math.hypot(mx - t.x, my - t.y)
                        if d < min_dist:
                            min_dist = d
                            hit_idx = i

                if hit_idx is not None:
                    hits += 1
                    t = targets[hit_idx]
                    spawn_ts = target_spawn_ts.get(id(t), now)
                    hit_times.append(max(0.0, now - spawn_ts))
                    t.r = max(TARGET_MIN_R, int(t.r * HIT_SHRINK))
                    t.respawn()
                    target_spawn_ts[id(t)] = time.time()
                else:
                    if MISS_PENALTY:
                        hits = max(0, hits + MISS_PENALTY)

        screen.fill(BG_COLOR)
        for t in targets:
            t.draw(screen)

        acc = (hits / shots * 100.0) if shots > 0 else 0.0
        avg_react = (sum(hit_times) / len(hit_times)) if hit_times else 0.0

        hud_lines = [
            f"Time: {format_time(remaining)}",
            f"Hits: {hits}  Shots: {shots}  Acc: {acc:.1f}%",
            f"Avg React: {avg_react*1000:.0f} ms",
            f"Targets: {len(targets)}  FPS: {clock.get_fps():.0f}",
            "ESC to quit",
        ]
        y = 8
        for line in hud_lines:
            surf = font.render(line, True, FG_COLOR)
            screen.blit(surf, (10, y))
            y += 24

        if remaining <= 0:
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            end_lines = [
                "Session finished",
                f"Shots: {shots}  Hits: {hits}",
                f"Accuracy: {acc:.1f}%",
                f"Avg Reaction: {avg_react*1000:.0f} ms",
                "Press ESC to exit",
            ]
            y = HEIGHT // 2 - 60
            for line in end_lines:
                surf = font.render(line, True, (230, 230, 230))
                screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
                y += 28

        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    main()
