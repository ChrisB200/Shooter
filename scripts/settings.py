# Modules
import pygame, pickle
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

    def save_to_file(self, filename):
        try:
            with open(filename, 'wb') as file:
                pickle.dump(self, file)
            print("Settings saved successfully.")
        except Exception as e:
            print(f"Error while saving settings: {e}")

    @staticmethod
    def load_from_file(filename):
        try:
            with open(filename, 'rb') as file:
                settings = pickle.load(file)
            print("Settings loaded successfully.")
            return settings
        except Exception as e:
            print(f"Error while loading settings: {e}")
            return Settings()