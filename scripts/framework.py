# Modules
import pygame, os
from pygame.constants import *

BASE_IMG_PATH = "data/images/"

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
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

# Loads a group of images in a alocation
def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

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