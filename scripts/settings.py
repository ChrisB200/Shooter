# Modules
import pygame
from pygame.constants import *
from dataclasses import dataclass

@dataclass
class Controls:
    moveR: int
    moveL: int
    dash: int
    jump: int
    pause: int

class Settings:
    def __init__(self):
        self.resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.targetFPS = 120
        self.keyboard = Controls(K_d, K_a, K_LSHIFT, K_SPACE, K_ESCAPE)
        self.controller = Controls(0, 0, 1, 0, 7)

    @property
    def width(self):
        return self.resolution[0]
    
    @property
    def height(self):
        return self.resolution[1]