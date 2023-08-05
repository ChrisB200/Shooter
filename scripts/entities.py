# Modules
import pygame, math

# Scripts
from scripts.camera import CameraObject, Camera
from scripts.framework import Animation, Controller, Keyboard, get_center, collision_test, numCap, control_deadzone

# Entity Class
class Entity:
    def __init__(self, pos:list[int, int], size:list[int, int], tag:str, assets:dict[str, Animation]):
        # Parameters
        self.pos: list[int, int] = pos
        self.size: list[int, int] = size
        self.tag: str = tag
        self.assets: dict[str, Animation] = assets
        # Movement Logic
        self.flip: bool = False
        self.directions: dict[str, bool] = {"left" : False, "right": False, "up": False, "down": False}
        self.movement: list[float, float] = [0, 0] # [x, y]
        # Animation Logic
        self.action: str = ""
        self.anim_offset: tuple[int, int] = (0, 0)
        self.flip: bool = False
        self.set_action("idle")

    @property
    def x(self):
        return self.pos[0]
    
    @property
    def y(self):
        return self.pos[1]

    # Sets an animation action
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.assets[self.tag + "/" + self.action].copy()

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
    def get_point_angle(self, point, scroll=[0, 0], offset=0, centered=True):
        pos = [self.pos[0] - scroll[0], self.pos[1] - scroll[1]]
        if centered:
            pos = get_center(pos, self.size)
        radians = math.atan2(point[1] - pos[1], point[0] - pos[0])
        return -math.degrees(radians) + offset
         

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
    def update_animation(self, dt):
        self.animation.update(dt)

    # Returns the current image
    @property
    def current_image(self):
        return pygame.transform.flip(self.animation.img(), self.flip, False)

# Physics Entity
class PhysicsEntity(Entity):
    def __init__(self, pos:list[int, int], size:list[int, int], tag:str, assets):
        # Parameters
        super().__init__(pos, size, tag, assets)
        # Rects and Collisions
        self.rect: pygame.Rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.collisions: dict[str, bool] = {'bottom': False, 'top': False, 'left': False, 'right': False}

    # Checks for collisions based on movement direction
    def move(self, movement, tiles, dt):
        # x-axis
        self.pos[0] += movement[0] * dt
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
        self.pos[1] += movement[1] * dt
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
    def __init__(self, pos:list[int, int], size:list[int, int], tag:str, assets):
        # Parameters
        super().__init__(pos, size, tag, assets)
        # Movement Data
        self.momentum: list[float, float] = [0, 0] # [momentumX, momentumY]
        self.strength: list[float, float] = [0.5, 0.2] # [strengthX, strengthY]
        self.cap: tuple[int, int] = (4, 5) # [capX, capY]
        # Jump Data
        self.jumpStrength: int = -7
        self.totalJumps: int = 2
        self.currentJumps: int = 0
        self.airTimer: float = 0
        self.maxAirTimer: int = 2
        self.isGrounded: bool = False
        # Dash Data
        self.isDashing: bool = False
        self.canDash: bool = True
        self.dashStrength: float = 6.2
        self.dashCooldown: list[float, float, bool] = [25, 25, False] # [currentTimer, maxTimer, currentlyCounting]
        # Animation Data
        self.anim_offset: tuple[int, int] = (-3, -5)
        # Weapon
        self.cursor: UserCursor = UserCursor([*pygame.mouse.get_pos()], [9, 9], "cursor1", self.assets)
        self.weapon = None
        self.input: Keyboard | Controller = None

    # Returns the position
    @property
    def get_pos(self):
        return self.pos
    
    def render(self):
        retVal = super().render()
        if self.weapon is not None:
            return retVal, self.weapon.render()
        else:
            return retVal
        
    def input_events(self, event):
        if type(self.input) == Controller:
            self.controller_input(event)
        else:
            self.keyboard_input(event)
        
    def keyboard_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.input.controls.moveL:
                self.directions["left"] = True
            if event.key == self.input.controls.moveR:
                self.directions["right"] = True
            if event.key == self.input.controls.jump:
                if self.airTimer < self.maxAirTimer:
                    self.momentum[1] = self.jumpStrength
                if self.currentJumps < self.totalJumps:
                    self.momentum[1] = self.jumpStrength
                    self.currentJumps += 1
            if event.key == self.input.controls.dash and self.isDashing == False and self.canDash == True and self.dashCooldown[2] != True:
                self.momentum[0] = self.momentum[0] * self.dashStrength
                self.isDashing = True
                self.canDash = False
                self.dashCooldown[2] = True
        if event.type == pygame.KEYUP:
            if event.key == self.input.controls.moveL:
                self.directions["left"] = False
            if event.key == self.input.controls.moveR:
                self.directions["right"] = False
        
    def controller_input(self, event):
        self.input.leftStick = control_deadzone(0.1, self.joystick.get_axis(0), self.joystick.get_axis(1))
        self.input.rightStick = control_deadzone(0.1, self.joystick.get_axis(2), self.joystick.get_axis(3))

        if self.input.leftStick[0] > 0:
            self.directions["right"] = True
            self.directions["left"] = False
        elif self.input.leftStick[0] < 0:
            self.directions["left"] = True
            self.directions["right"] = False
        else:
            self.directions["left"] = False
            self.directions["right"] = False

        if (event.type == pygame.JOYBUTTONDOWN):
            if event.button == self.input.controls.jump:
                if self.airTimer < self.maxAirTimer:
                    self.momentum[1] = self.jumpStrength
                if self.currentJumps < self.totalJumps:
                    self.momentum[1] = self.jumpStrength
                    self.currentJumps += 1
            if event.button == self.input.controls.dash and self.isDashing == False and self.canDash == True and self.dashCooldown[2] != True:
                self.momentum[0] = self.momentum[0] * self.dashStrength
                self.isDashing = True
                self.canDash = False
                self.dashCooldown[2] = True
        
    # input player movement and states
    def update(self, tiles, dt, camera):
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
            strength = self.strength[0]
            if self.directions["right"]:   
                if type(self.input) == Controller:
                    strength *= self.input.leftStick[0]
                self.momentum[0] += strength
                self.momentum[0] = numCap(self.momentum[0], self.cap[0])
                self.flip = False
            elif self.directions["left"]:
                if type(self.input) == Controller:
                    strength *= self.input.leftStick[0]
                self.momentum[0] += -self.strength[0]
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
        self.move(self.movement, tiles, dt)

        # Animations
        if self.airTimer > 12:
            self.set_action("jump")  
        elif ((self.directions["left"] == True) or (self.directions["right"] == True)):
            self.set_action("run")
        else:
            self.set_action("idle")

        self.cursor.update(self, camera)
        if self.weapon:
            self.weapon.update(self, camera)

# Object Class TEMPORARY            
class Object:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.rotation = 0
        self.flip = False

# Cursor for users
class UserCursor(Entity):
    def __init__(self, pos, size, tag, assets):
        super().__init__(pos, size, tag, assets)
        self.location = [1, 1]

    def set_pos(self, x, y):
        self.pos[0] = x
        self.pos[1] = y

    def update(self, player:Player, camera:Camera):
        x = self.pos[0]
        y = self.pos[1]
        if type(player.input) == Controller:
            x += round(player.input.rightStick[0] * 5)
            y += round(player.input.rightStick[1] * 5)
            self.pos[0] = self.pos[0]
            self.pos[1] = self.pos[1] 
            self.set_pos(x, y)
        else:
            x, y = pygame.mouse.get_pos()
            self.set_pos(x, y)
        self.cursor_in_space(camera.scale)

    def cursor_in_space(self, camera_scale):
        self.location[0] = self.pos[0] // camera_scale
        self.location[1] = self.pos[1] // camera_scale