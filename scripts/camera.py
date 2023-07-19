import pygame
from pygame.constants import *

import scripts.framework as f
from scripts.player import Player

class Camera:
    def __init__(self, resolution, scale, fullscreen=FULLSCREEN):
        self.resolution = resolution
        self.scale = scale

        self.display = pygame.display.set_mode(resolution, fullscreen)
        self.trueScroll = [0, 0]
        self.panStrength = 10

        self.renderOrder = {"x": False, "y": False, "layer": True}
        self.isFollowing = None  # [target, [offsetX, offsetY]]
        self.isPanning = False

        self.screen = pygame.Surface((self.resolution[0] / self.scale, self.resolution[1] / self.scale))

        self.offset = (0, 0)

    @property
    def screenSize(self):
        return self.screen.get_size()[0], self.screen.get_size()[1]

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
        
    def zoom(self, amount:int):
        self.scale += amount
        tempScreen = pygame.transform.scale(self.screen.copy(), (self.resolution[0] / self.scale, self.resolution[1] / self.scale))
        self.screen = tempScreen
        
        
    def render(self, *camObjects):
        if self.isFollowing is not None:
            if self.isPanning:
                target_center_x = (self.isFollowing.pos[0] + self.isFollowing.size[0] // 2) + self.offset[0]
                target_center_y = (self.isFollowing.pos[1] + self.isFollowing.size[1] // 2) + self.offset[1]
                self.trueScroll[0] += ((target_center_x - self.trueScroll[0]) - self.screenSize[0] / 2) / self.panStrength
                self.trueScroll[1] += ((target_center_y - self.trueScroll[1]) - self.screenSize[1] / 2) / self.panStrength
            else:
                target_center_x = (self.isFollowing.pos[0] + self.isFollowing.size[0] // 2)
                target_center_y = (self.isFollowing.pos[1] + self.isFollowing.size[1] // 2)
                self.trueScroll[0] += ((target_center_x - self.trueScroll[0]) - self.screenSize[0] / 2) / self.panStrength
                self.trueScroll[1] += ((target_center_y - self.trueScroll[1]) - self.screenSize[1] / 2) / self.panStrength


        sorted_camObjects = sorted(camObjects, key=self.sort_cameraObjects)[0]

        for camObj in sorted_camObjects:
            if camObj.type == "rect":
                tempRect = pygame.Rect(camObj.entity.x - self.scroll[0], camObj.entity.y - self.scroll[1], camObj.entity.width, camObj.entity.height) 
                pygame.draw.rect(self.screen, camObj.colour, tempRect)
            elif camObj.type == "surface":
                self.screen.blit(camObj.entity, ((camObj.pos[0] - self.trueScroll[0]), (camObj.pos[1] - self.trueScroll[1])))
            else:
                raise ValueError("Unsupported entity type.")

         # Apply zoom factor to the screen
        self.display.blit(pygame.transform.scale(self.screen, self.resolution), (0, 0))

