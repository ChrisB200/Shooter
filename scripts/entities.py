# Modules
import pygame, math

# Scripts
from scripts.camera import CameraObject
from scripts.framework import get_center, collision_test, numCap

# Entity Class
class Entity:
    def __init__(self, game, pos, size, tag):
        # Parameters
        self.game = game
        self.pos = pos
        self.size = size
        self.tag = tag
        # Movement Logic
        self.flip = False
        self.directions = {"left" : False, "right": False, "up": False, "down": False}
        self.movement = [0, 0] # [x, y]
        # Animation Logic
        self.action = ""
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action("idle")

    # Sets an animation action
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.tag + "/" + self.action].copy()

    # Gets the angle between 2 entities
    def get_entity_angle(self, entity_2):
        x1 = self.pos[0] + int(self.size[0] / 2)
        y1 = self.pos[1] + int(self.size[1] / 2)
        x2 = entity_2.pos[0] + int(entity_2.size[0] / 2)
        y2 = entity_2.pos[1] + int(entity_2.size[1] / 2)
        angle = math.atan((y2-y1) / (x2-x1))
        if x2 < x1:
            angle += math.pi
        return angle

    # Gets the angle between an entity and a point
    def get_point_angle(self, point):
        centerPos = get_center(self.pos, self.size)
        return math.atan2(point[1] - centerPos[1], point[0] - centerPos[0])

    # Gets the distance between an entity and a point
    def get_distance(self, point):
        dis_x = point[0] - self.get_center()[0]
        dis_y = point[1] - self.get_center()[1]
        return math.sqrt(dis_x ** 2 + dis_y ** 2)
    
    # Returns a camera object
    def render(self):
        img = pygame.transform.flip(self.animation.img(), self.flip, False)
        return CameraObject(img, (self.pos[0] + self.anim_offset[0], self.pos[1] + self.anim_offset[1]), 1)
    
    # Updates the current frame of an animation
    def update_animation(self):
        self.animation.update(self.game.dt)

# Physics Entity
class PhysicsEntity(Entity):
    def __init__(self, game, pos, size, tag):
        # Parameters
        super().__init__(game, pos, size, tag)
        # Rects and Collisions
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.collisions = {'bottom': False, 'top': False, 'left': False, 'right': False}

    # Checks for collisions based on movement direction
    def move(self, movement, tiles):
        # x-axis
        self.pos[0] += movement[0] * self.game.dt
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
        self.pos[1] += movement[1] * self.game.dt
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
    
# Player Class
class Player(PhysicsEntity):
    def __init__(self, game, pos, size, tag):
        # Parameters
        super().__init__(game, pos, size, tag)
        # Movement Data
        self.momentum = [0, 0] # [momentumX, momentumY]
        self.strength = [0.5, 0.2] # [strengthX, strengthY]
        self.cap = [4, 5] # [capX, capY]
        # Jump Data
        self.totalJumps = 2
        self.currentJumps = 0
        self.airTimer = 0
        self.maxAirTimer = 2
        self.isGrounded = False
        # Dash Data
        self.isDashing = False
        self.canDash = True
        self.dashStrength = 4.2
        self.dashCooldown = [25, 25, False] # [currentTimer, maxTimer, currentlyCounting]

    # Returns the position
    @property
    def get_pos(self):
        return self.pos

    # Controls player movement and states
    def update(self, tiles, axesx=1):
        if self.airTimer < self.maxAirTimer:
            self.isGrounded = True
        else:
            self.isGrounded = False
        
        # Dash Cooldown
        if self.dashCooldown[2] != True:
            self.dashCooldown[0] = self.dashCooldown[1]
        else:
            if self.dashCooldown[0] == 0:
                self.dashCooldown[2] = False
                self.dashCooldown[0] = self.dashCooldown[1]
            else:
                self.dashCooldown[0] -= 1

        # Resets momentum when top collides
        if self.collisions["top"]:
            self.momentum[1] = 0.1

        # Resets Jumps, momentum and airtimer when grounded
        if self.collisions["bottom"]:
            self.momentum[1] = 0.1
            self.airTimer = 0
            self.currentJumps = 0
            self.isGrounded = True
            if self.dashCooldown[2] != True:
                self.canDash = True
        else:
            # Adds gravity
            self.momentum[1] += self.strength[1]
            self.momentum[1] = numCap(self.momentum[1], self.cap[1]) # caps the gravity
            self.airTimer += 1
            self.isGrounded = False
        
        # x-axis movement
        if self.isDashing == False:
            if self.directions["right"]:
                self.momentum[0] += self.strength[0] * axesx
                self.momentum[0] = numCap(self.momentum[0], self.cap[0])
                self.flip = False
            elif self.directions["left"]:
                self.momentum[0] += self.strength[0] * -axesx
                self.momentum[0] = numCap(self.momentum[0], -self.cap[0])
                self.flip = True
            else:
                if self.momentum[0] < -0.0001:
                    self.momentum[0] = 0

        # Dashing
        if self.isDashing or (not(self.directions["right"]) and not(self.directions["left"])):
            if self.momentum[0] > 0:
                self.momentum[0] -= self.strength[0]
            elif self.momentum[0] < 0:
                self.momentum[0] += self.strength[0]

        if ((self.momentum[0] <= 3) and (self.momentum[0] >= -3)) and self.isDashing:
            self.isDashing = False

        # Checking for collision
        self.movement[0] = self.momentum[0]
        self.movement[1] = self.momentum[1]
        self.move(self.movement, tiles)

        # Animations
        if self.airTimer > 12:
            self.set_action("jump")  
        elif ((self.directions["left"] == True) or (self.directions["right"] == True)):
            self.set_action("run")
        else:
            self.set_action("idle")
            
# Object Class TEMPORARY            
class Object:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.rotation = 0
        self.flip = False