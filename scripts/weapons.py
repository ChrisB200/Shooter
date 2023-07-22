# Modules
import pygame, math

# Scripts
from scripts.entities import Entity
from scripts.camera import CameraObject
from scripts.framework import get_center, blit_rotate

class Weapon(Entity):
    def __init__(self, game, pos, size, tag, pivot=(0, 0), offset=0):
        super().__init__(game, pos, size, tag)
        self.pivot = pivot
        self.offset = offset
        self.rotation = 0
        
    def rotate_at_cursor(self):
        # Mouse Coordinates
        mx, my = pygame.mouse.get_pos()
        mx = mx // self.game.camera.scale
        my = my // self.game.camera.scale

        # Adjust weapon position by considering camera scrolling
        weapon_x = self.pos[0] - self.game.camera.scroll[0]
        weapon_y = self.pos[1] - self.game.camera.scroll[1]

        # Flip weapon position based on x axis
        if mx > weapon_x:
            self.flip = False
        else:
            self.flip = True

        self.rotation = self.get_point_angle((mx, my), self.game.camera.scroll, self.offset, False)

    def update(self, entity):
        self.pos = get_center(entity.pos, entity.size)
        self.rotate_at_cursor()

    def render(self):
        img = blit_rotate(self.current_image, self.pos, self.pivot, self.rotation)
        return CameraObject(img[0], (img[1].x, img[1].y), 2)

