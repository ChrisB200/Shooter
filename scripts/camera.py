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
        # Scaling Data
        self.desired_scale = scale
        self.min_scale = 1.5  # Set your desired minimum scale value here
        self.max_scale = 2  # Set your desired maximum scale value here
        self.zoom_speed = 1  # Set the zoom speed, adjust as needed
        # Other
        self.renderOrder = {"x": False, "y": False, "layer": True}
        self.screen = pygame.Surface((self.resolution[0] / self.scale, self.resolution[1] / self.scale))
        self.targets = ()

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

    def set_targets(self, targets, offset=(0, 0)):
        self.targets = targets
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
    def zoom(self, amount: float):
        # Incrementally update the desired scale
        self.desired_scale += amount

        # Clamp the desired scale to the defined range
        self.desired_scale = max(self.min_scale, min(self.max_scale, self.desired_scale))

        # Smoothly transition the current scale towards the desired scale
        self.scale += (self.desired_scale - self.scale) * self.zoom_speed

        tempScreen = pygame.transform.scale(self.screen.copy(), (self.resolution[0] / self.scale, self.resolution[1] / self.scale))
        self.screen = tempScreen

    def followATarget(self, panStrength):
        if self.isPanning:
            target_center_x = (self.isFollowing.pos[0] + self.isFollowing.size[0] // 2) + self.offset[0]
            target_center_y = (self.isFollowing.pos[1] + self.isFollowing.size[1] // 2) + self.offset[1]
            self.trueScroll[0] += ((target_center_x - self.trueScroll[0]) - self.screenSize[0] / 2) / panStrength
            self.trueScroll[1] += ((target_center_y - self.trueScroll[1]) - self.screenSize[1] / 2) / panStrength
        else:
            target_center_x = (self.isFollowing.pos[0] + self.isFollowing.size[0] // 2)
            target_center_y = (self.isFollowing.pos[1] + self.isFollowing.size[1] // 2)
            self.trueScroll[0] += ((target_center_x - self.trueScroll[0]) - self.screenSize[0] / 2) / panStrength
            self.trueScroll[1] += ((target_center_y - self.trueScroll[1]) - self.screenSize[1] / 2) / panStrength

    def followMultipleTargets(self, panStrength):
        # Calculate the bounding box of all targets
        min_x = min(target.pos[0] for target in self.targets) - 100
        max_x = max(target.pos[0] + target.size[0] for target in self.targets) + 100
        min_y = min(target.pos[1] for target in self.targets) - 100
        max_y = max(target.pos[1] + target.size[1] for target in self.targets) + 100

        # Calculate the size of the bounding box
        box_width = max_x - min_x
        box_height = max_y - min_y

        
        # Calculate the required scale to fit the bounding box on the screen
        required_scale_x = self.resolution[0] / box_width
        required_scale_y = self.resolution[1] / box_height
        required_scale = min(required_scale_x, required_scale_y)

        # Calculate the current distance between players (targets)
        current_distance_x = max_x - min_x
        current_distance_y = max_y - min_y

        print(box_width, box_height, current_distance_x)


        # Check if players are moving away from each other
        if current_distance_x > box_width // required_scale_x or current_distance_y > box_height // required_scale_y:
            # Update the camera scale to fit the bounding box
            self.zoom(required_scale - self.scale)
        else:
            # Zoom back in towards the initial scale
            self.zoom(self.scale - self.scale)  # Equivalent to self.zoom(0)

        # Center the camera on the center of the bounding box
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        target_center_x = center_x + self.offset[0]
        target_center_y = center_y + self.offset[1]
        self.trueScroll[0] += ((target_center_x - self.trueScroll[0]) - self.screenSize[0] / 2) / panStrength
        self.trueScroll[1] += ((target_center_y - self.trueScroll[1]) - self.screenSize[1] / 2) / panStrength

    def update(self, dt):
        if abs(dt) > 1e-6:
            panStrength = self.panStrength / dt
        else:
            panStrength = self.panStrength
            
        if self.targets:
            self.followMultipleTargets(panStrength)
        elif self.isFollowing is not None:
            self.followATarget(panStrength)
    
    # Renders camera objects and controls scrolling
    def render(self, *camObjects):
        sorted_camObjects = self.sortCameraObjects(camObjects)

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

