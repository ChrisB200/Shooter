# Modules
import pygame, math, sys, os
from pygame.constants import *

BASE_IMG_PATH = "data/images/"

# Scripts
class Physics2D:
    def __init__(self, pos, size):
        self.pos = pos # [x, y]
        self.size = size # [width, height]
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.collisions = {'bottom': False, 'top': False, 'left': False, 'right': False}

    def move(self, movement, tiles): # Checks collisions based on movement direction
        # x-axis
        self.pos[0] += movement[0]
        self.rect.x = int(self.pos[0])
        tileCollisions = collision_test(self.rect, tiles)
        objectCollisions = {'bottom': False, 'top': False, 'left': False, 'right': False}
        for tile in tileCollisions:
            if movement[0] > 0:
                self.rect.right = tile.left
                objectCollisions["right"] = True
            elif movement[0] < 0:
                self.rect.left = tile.right
                objectCollisions["left"] = True
        self.pos[0] = self.rect.x

        # y-axis
        self.pos[1] += movement[1]
        self.rect.y = int(self.pos[1])
        tileCollisions = collision_test(self.rect, tiles)
        for tile in tileCollisions:
            if movement[1] > 0:
                self.rect.bottom = tile.top
                objectCollisions["bottom"] = True
            elif movement[1] < 0:
                self.rect.top = tile.bottom
                objectCollisions["top"] = True
        self.pos[1] = self.rect.y
        self.collisions = objectCollisions

class Object:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.rotation = 0
        self.flip = False
        self.physics = Physics2D(self.pos, self.size)

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

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
    
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]

class Entity:
    def __init__(self, game, pos, size, tag):
        self.game = game
        self.pos = pos
        self.size = size
        self.tag = tag
        self.physics = Physics2D(self.pos, self.size)
        self.flip = False
        self.directions = {"left" : False, "right": False, "up": False, "down": False}
        self.movement = [0, 0] # [x, y]

        self.action = ""
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action("idle")

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.tag + "/" + self.action].copy()

    def get_entity_angle(self, entity_2):
        x1 = self.pos[0] + int(self.size[0] / 2)
        y1 = self.pos[1] + int(self.size[1] / 2)
        x2 = entity_2.pos[0] + int(entity_2.size[0] / 2)
        y2 = entity_2.pos[1] + int(entity_2.size[1] / 2)
        angle = math.atan((y2-y1) / (x2-x1))
        if x2 < x1:
            angle += math.pi
        return angle

    def get_point_angle(self, point):
        centerPos = get_center(self.pos, self.size)
        return math.atan2(point[1] - centerPos[1], point[0] - centerPos[0])

    def get_distance(self, point):
        dis_x = point[0] - self.get_center()[0]
        dis_y = point[1] - self.get_center()[1]
        return math.sqrt(dis_x ** 2 + dis_y ** 2)
    
    def render(self):
        img = pygame.transform.flip(self.animation.img(), self.flip, False)
        return CameraObject(img, (self.pos[0] + self.anim_offset[0], self.pos[1] + self.anim_offset[1]), 1)
    
    def update_animation(self):
        self.animation.update()

def clip(surf, x1, y1, x2, y2):
    clip = pygame.Rect(x1, y1, x2, y2)
    img = surf.subsurface(clip)
    return img

def convertBool(val):
    return True if val.lower() == "true" else False

def blit_center(surf, display ,pos):
    x = int(display.get_width() / 2)
    y = int(display.get_height() / 2)
    surf.blit(display, (pos[0] - x, pos[1] - y))

def get_center(pos, size):
    x = pos[0] + int(size[0] / 2)
    y = pos[1] + int(size[1] / 2)
    return [x,y]

def flip_img(img,boolean=True, boolean_2=False):
    return pygame.transform.flip(img,boolean,boolean_2)

def load_img(path, colorkey):
    img = pygame.image.load(path).convert()
    img.set_colorkey(colorkey)
    return img

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
            
def collision_test(object_1,object_list):
    collision_list = []
    for obj in object_list:
        if obj.colliderect(object_1):
            collision_list.append(obj)
    return collision_list

def controller_check():
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
    return joysticks

def setPos(object, pos):
    object.pos[0] = pos[0]
    object.pos[1] = pos[1]

def scale_object(obj, scale):
    if isinstance(obj, pygame.Surface):
        width = int(obj.get_width() * scale)
        height = int(obj.get_height() * scale)
        scaled_obj = pygame.transform.scale(obj, (width, height))
        return scaled_obj
    elif isinstance(obj, pygame.Rect):
        x = int(obj.x * scale)
        y = int(obj.y * scale)
        width = int(obj.width * scale)
        height = int(obj.height * scale)
        scaled_obj = pygame.Rect(x, y, width, height)
        return scaled_obj
    else:
        raise ValueError("Unsupported object type. Expected pygame.Surface or pygame.Rect.")
    
def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

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

def find_screen_resolution(settings):
    monitor_w = pygame.display.Info().current_w
    monitor_h = pygame.display.Info().current_h
    for i in range(len(settings.resolutions)):
        # This checks if the monitors resolution matches any of the
        # avaliable ones.
        if settings.resolutions[i][0] == monitor_w and \
           settings.resolutions[i][1] == monitor_h:
            settings.respointer = i

    if settings.respointer is None:
        # If a match resolutoin can't be found it will try to find one with
        # the same aspect ratio.
        settings.respointer = 1
        for i in range(len(settings.resolutions)):
            if (monitor_w // monitor_h ==
               settings.resolutions[i][0] // settings.resolutions[i][1]):
                respointer = i