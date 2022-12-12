import pygame
from pygame.locals import *
import sys
sys.path.append("../Backend/Library")


class JunctionVisualiser:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Junction Visualiser')
        self._fps = 60
        self._window_clock = pygame.time.Clock()
        self._window_width, self._window_height = 1920, 1080
        self.window = pygame.display.set_mode((self._window_width, self._window_height))

    def run(self):
        self.window.fill((0, 0, 0))
        self.check_for_close()

    def update(self):
        pygame.display.flip()
        self._window_clock.tick(self._fps)

    def check_for_close(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    def draw_lanes(self, lanes):
        for _lane in lanes:
            pygame.draw.circle(self.window, (255, 255, 255), (_lane.x, _lane.y), 5)

