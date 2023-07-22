# Modules
import pygame
from pygame.constants import *

# Scripts

# An object which can be used in a camera class
class CameraObject():
    def __init__(self, entity, pos=[0, 0], layer=0, colour=(255, 255, 255)):
        self.entity = entity
        if isinstance(entity, pygame.Rect):
            self.pos = [entity.x, entity.y]
            self.type = "rect"
        elif isinstance(entity, pygame.Surface):
            self.pos = pos
            self.type = "surface"
        self.layer = layer
        self.colour = colour

# Camera System
class Camera:
    def __init__(self, resolution, scale, fullscreen=FULLSCREEN):
        # Display Data
        self.resolution = resolution
        self.scale = scale
        self.display = pygame.display.set_mode(resolution, fullscreen)
        # Scroll Data
        self.trueScroll = [0, 0]
        # Tracking Data
        self.isFollowing = None  # [target, [offsetX, offsetY]]
        self.isPanning = False
        self.panStrength = 5
        self.offset = (0, 0)
        # Other
        self.renderOrder = {"x": False, "y": False, "layer": True}
        self.screen = pygame.Surface((self.resolution[0] / self.scale, self.resolution[1] / self.scale))

    # Returns a screen size
    @property
    def screenSize(self):
        return self.screen.get_size()[0], self.screen.get_size()[1]

    # Returns an integer scroll value
    @property
    def scroll(self):
        return [int(self.trueScroll[0]), int(self.trueScroll[1])]

    # Sets the render order
    def set_renderOrder(self, order):
        if order == "x":
            return {"x": True, "y": False, "layer": False}
        elif order == "y":
            return {"x": False, "y": True, "layer": False}
        else:
            return {"x": False, "y": False, "layer": True}

    # Sets a camera target
    def set_target(self, target, offset=(0, 0)):
        self.isFollowing = target
        self.offset = offset

    # Toggles panning
    def toggle_panning(self):
        self.isPanning = not self.isPanning

    # Sorts camera objects via layer, x position, or y position
    def sortCameraObjects(self, cameraObjects):
        if self.renderOrder["x"] == True:
            return sorted(cameraObjects, key=lambda camObj: camObj.entity.x)
        elif self.renderOrder["y"] == True:
            return sorted(cameraObjects, key=lambda camObj: camObj.entity.y)
        else:
            return sorted(cameraObjects, key=lambda camObj: camObj.layer)

    
    # Allows for zooming functionality
    def zoom(self, amount:int):
        self.scale += amount
        tempScreen = pygame.transform.scale(self.screen.copy(), (self.resolution[0] / self.scale, self.resolution[1] / self.scale))
        self.screen = tempScreen

    def update(self, dt):
        if abs(dt) > 1e-6:
            pan_strength = self.panStrength / dt
        else:
            pan_strength = self.panStrength
        if self.isFollowing is not None:
            if self.isPanning:
                target_center_x = (self.isFollowing.pos[0] + self.isFollowing.size[0] // 2) + self.offset[0]
                target_center_y = (self.isFollowing.pos[1] + self.isFollowing.size[1] // 2) + self.offset[1]
                self.trueScroll[0] += ((target_center_x - self.trueScroll[0]) - self.screenSize[0] / 2) / pan_strength
                self.trueScroll[1] += ((target_center_y - self.trueScroll[1]) - self.screenSize[1] / 2) / pan_strength
            else:
                target_center_x = (self.isFollowing.pos[0] + self.isFollowing.size[0] // 2)
                target_center_y = (self.isFollowing.pos[1] + self.isFollowing.size[1] // 2)
                self.trueScroll[0] += ((target_center_x - self.trueScroll[0]) - self.screenSize[0] / 2) / pan_strength
                self.trueScroll[1] += ((target_center_y - self.trueScroll[1]) - self.screenSize[1] / 2) / pan_strength
    
    # Renders camera objects and controls scrolling
    def render(self, *camObjects):
        sorted_camObjects = self.sortCameraObjects(camObjects[0])

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

