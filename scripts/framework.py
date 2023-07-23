# Modules
import pygame, os, json
from pygame.constants import *
from dataclasses import dataclass

BASE_IMG_PATH = "data/images/"

MENU = 0
PLAYING = 1
PAUSED = 2
JUMP_STRENGTH = -7

# Animation System
class Animation:
    def __init__(self, images, img_dur=0.2, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
        self.time_elapsed = 0
    
    # Returns a copy of itself
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    # Updates the current frame (uses deltatime)
    def update(self, dt):
        self.time_elapsed += dt
        while self.time_elapsed >= self.img_duration:
            self.time_elapsed -= self.img_duration
            if self.loop:
                self.frame = (self.frame + 1) % len(self.images)
            else:
                self.frame = min(self.frame + 1, len(self.images) - 1)
                if self.frame == len(self.images) - 1:
                    self.done = True
    
    # Returns the current frame
    def img(self):
        return self.images[self.frame]
    
@dataclass
class Controls:
    moveR: int
    moveL: int
    dash: int
    jump: int
    pause: int

class Controller:
    def __init__(self, controls:Controls, joystick):
        self.player = None
        self.game = None
        self.controls = controls
        self.joystick = joystick
        self.leftStick = [0, 0]
        self.rightStick = [0, 0]
    
    def update(self, event):
        self.leftStick = control_deadzone(0.1, self.joystick.get_axis(0), self.joystick.get_axis(1))
        self.rightStick = control_deadzone(0.1, self.joystick.get_axis(2), self.joystick.get_axis(3))

        if self.leftStick[0] > 0:
            self.player.directions["right"] = True
            self.player.directions["left"] = False
        elif self.leftStick[0] < 0:
            self.player.directions["left"] = True
            self.player.directions["right"] = False
        else:
            self.player.directions["left"] = False
            self.player.directions["right"] = False

        if (event.type == pygame.JOYBUTTONDOWN):
            if event.button == self.controls.jump:
                if self.player.airTimer < self.player.maxAirTimer:
                    self.player.momentum[1] = JUMP_STRENGTH
                if self.player.currentJumps < self.player.totalJumps:
                    self.player.momentum[1] = JUMP_STRENGTH
                    self.player.currentJumps += 1
            if event.button == self.controls.dash and self.player.isDashing == False and self.player.canDash == True and self.player.dashCooldown[2] != True:
                self.player.momentum[0] = self.player.momentum[0] * self.player.dashStrength
                self.player.isDashing = True
                self.player.canDash = False
                self.player.dashCooldown[2] = True
            if event.button == self.controls.pause:
                if self.currentState == PAUSED:
                    self.currentState = PLAYING
                else:
                    self.currentState = PAUSED
class Keyboard:
    def __init__(self, controls:Controls):
        self.player = None
        self.game = None
        self.controls = controls

    def update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls.pause:
                if self.currentState == PAUSED:
                    self.currentState = PLAYING
                else:
                    self.currentState = PAUSED
            if event.key == self.controls.moveL:
                self.player.directions["left"] = True
            if event.key == self.controls.moveR:
                self.player.directions["right"] = True
            if event.key == self.controls.jump:
                if self.player.airTimer < self.player.maxAirTimer:
                    self.player.momentum[1] = JUMP_STRENGTH
                if self.player.currentJumps < self.player.totalJumps:
                    self.player.momentum[1] = JUMP_STRENGTH
                    self.player.currentJumps += 1
            if event.key == self.controls.dash and self.player.isDashing == False and self.player.canDash == True and self.player.dashCooldown[2] != True:
                self.player.momentum[0] = self.player.momentum[0] * self.player.dashStrength
                self.player.isDashing = True
                self.player.canDash = False
                self.player.dashCooldown[2] = True
        if event.type == pygame.KEYUP:
            if event.key == self.controls.moveL:
               self.player.directions["left"] = False
            if event.key == self.controls.moveR:
               self.player.directions["right"] = False

# Returns a crop of a selected surface
def clip(surf, x1, y1, x2, y2):
    clip = pygame.Rect(x1, y1, x2, y2)
    img = surf.subsurface(clip)
    return img

def blit_rotate(image, pos, originPos, angle):
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    return (rotated_image, rotated_image_rect)

# Removes case sensitivity from string comparisons
def convertBool(val):
    return True if val.lower() == "true" else False

# Returns centered coordinates of surface
def blit_center(display ,pos):
    x = int(display.get_width() / 2)
    y = int(display.get_height() / 2)
    return (pos[0] - x, pos[1] - y)

# returns center of something
def get_center(pos, size):
    x = pos[0] + int(size[0] / 2)
    y = pos[1] + int(size[1] / 2)
    return [x,y]

def control_deadzone(deadzone, *axes):
    newAxes = []
    for axis in axes:
        if abs(axis) < deadzone:
            axis = 0
        newAxes.append(axis)

    return newAxes

# Flips an image
def flip_img(img,boolean=True, boolean_2=False):
    return pygame.transform.flip(img,boolean,boolean_2)

# Caps a number to be below a target
def numCap(number, target):
    if target >= 0:
        if number > target:
            return target
        else:
            return number
    else:
        if number < target:
            return target
        else:
            return number

# Checks for collisions between 2 objects   
def collision_test(object_1,object_list):
    collision_list = []
    for obj in object_list:
        if obj.colliderect(object_1):
            collision_list.append(obj)
    return collision_list

# Checks for controllers and initialises them
def controller_check():
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
    return joysticks

# Sets an objects position to another position
def setPos(object, pos):
    object.pos[0] = pos[0]
    object.pos[1] = pos[1]

# Loads an image using its location   
def load_image(path):
    img = pygame.image.load(path).convert()
    img.set_colorkey((0, 0, 0))
    return img

# Loads a group of images in a alocation
def load_images(path):
    images = []
    for img_name in sorted(os.listdir(path)):
        images.append(load_image(path + '/' + img_name))
    return images

def load_animations(base_path, data="data/animation_data.json"):
    assets = {}
    with open(data, "rb") as file:
        data = json.load(file)

    for group in os.listdir(base_path):
        for folder in os.listdir(base_path+group):
            for animation in os.listdir(base_path+group+"/"+folder):
                name = f"{folder}/{animation}"
                if name in data:
                    assets[name] = Animation(load_images(f"{base_path}{group}/{folder}/{animation}"), data[name]["img_dur"], data[name]["loop"])
                else:
                    assets[name] = Animation(load_images(f"{base_path}{group}/{folder}/{animation}"))

    return assets

# Splits a .csv file into a 2D array
def load_map(filename):
    grid = []
    with open(filename) as map:
        for row in map:
            rows = row.split(",")
            grid.append(rows)
    for count, row in enumerate(grid):
        temp = grid[count][len(row)-1].split("\n")
        grid[count][len(row)-1] = temp[0]
    return grid