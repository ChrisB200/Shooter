import pygame
from pygame.constants import *

import data.scripts.framework as f
from data.scripts.player import Player

class Camera:
    def __init__(self, resolution, pixelSize):
        self.resolution = resolution
        self.pixelSize = pixelSize

        self.display = pygame.display.set_mode(resolution, FULLSCREEN)
        self.trueScroll = [0, 0]
        self.panStrength = 10

        self.renderOrder = {"x": False, "y": False, "layer": True}
        self.isFollowing = None  # [target, [offsetX, offsetY]]
        self.isPanning = False
        self.zoom = 1

        self.screen = pygame.Surface((self.resolution[0] / self.pixelSize / self.zoom, self.resolution[1] / self.pixelSize / self.zoom))

        self.offset = (0, 0)

    @property
    def screenSize(self):
        return self.screen.get_size()[0] * self.zoom, self.screen.get_size()[1] * self.zoom

    @property
    def scroll(self):
        return [int(self.trueScroll[0]), int(self.trueScroll[1])]

    def set_renderOrder(self, order):
        if order == "x":
            return {"x": True, "y": False, "layer": False}
        elif order == "y":
            return {"x": False, "y": True, "layer": False}
        else:
            return {"x": False, "y": False, "layer": True}

    def set_target(self, target, offset=(0, 0)):
        self.isFollowing = target
        self.offset = offset

    def toggle_panning(self):
        self.isPanning = not self.isPanning

    def sort_cameraObjects(self, cameraObj):
        if self.renderOrder["x"] == True:
            return cameraObj.pos[0]
        elif self.renderOrder["y"] == True:
            return cameraObj.pos[1]
        else:
            return 0
        
    def render(self, *camObjects):
        if self.isFollowing is not None:
            if self.isPanning:
                target_center_x = (self.isFollowing.pos[0] + self.isFollowing.size[0] // 2) * self.zoom + self.offset[0]
                target_center_y = (self.isFollowing.pos[1] + self.isFollowing.size[1] // 2) * self.zoom + self.offset[1]
                self.trueScroll[0] += ((target_center_x - self.trueScroll[0]) - self.screenSize[0] / 2) / self.panStrength
                self.trueScroll[1] += ((target_center_y - self.trueScroll[1]) - self.screenSize[1] / 2) / self.panStrength
            else:
                target_center_x = (self.isFollowing.pos[0] + self.isFollowing.size[0] // 2) * self.zoom
                target_center_y = (self.isFollowing.pos[1] + self.isFollowing.size[1] // 2) * self.zoom
                self.trueScroll[0] = target_center_x - self.resolution[0] / (self.pixelSize * self.zoom) / 2
                self.trueScroll[1] = target_center_y - self.resolution[1] / (self.pixelSize * self.zoom) / 2

        sorted_camObjects = sorted(camObjects, key=self.sort_cameraObjects)[0]

        for camObj in sorted_camObjects:
            if camObj.type == "rect":
                tempRect = pygame.Rect(camObj.entity.x * self.zoom - self.scroll[0], camObj.entity.y * self.zoom - self.scroll[1], camObj.entity.width * self.zoom, camObj.entity.height * self.zoom) 
                pygame.draw.rect(self.screen, camObj.colour, tempRect)
            elif camObj.type == "surface":
                self.screen.blit(camObj.entity, ((camObj.pos[0] - self.trueScroll[0]) * self.pixelSize * self.zoom, (camObj.pos[1] - self.trueScroll[1]) * self.pixelSize * self.zoom))
            else:
                raise ValueError("Unsupported entity type.")

        self.display.blit(pygame.transform.scale(self.screen, self.resolution), (0, 0))

