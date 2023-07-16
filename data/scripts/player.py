# Modules
import pygame

# Scripts
import data.scripts.framework as f

class Player(f.Entity):
    def __init__(self, pos, size, tag):
        super().__init__(pos, size, tag)
        self.momentum = [0, 0] # [momentumX, momentumY]
        self.strength = [0.1, 0.1] # [strengthX, strengthY]
        self.cap = [3, 5] # [capX, capY]
        # Jump Data
        self.totalJumps = 2
        self.currentJumps = 0
        self.airTimer = 0
        self.maxAirTimer = 15
        self.isGrounded = False
        # Dash Data
        self.isDashing = False
        self.canDash = True
        self.dashStrength = 3.5
        self.dashCooldown = [25, 25, False] # [currentTimer, maxTimer, currentlyCounting]

        self.draw_pos = self.pos

    @property
    def get_pos(self):
        return self.pos

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
        if self.physics.collisions["top"]:
            self.momentum[1] = 0.1

        # Resets Jumps, momentum and airtimer when grounded
        if self.physics.collisions["bottom"]:
            self.momentum[1] = 0.1
            self.airTimer = 0
            self.currentJumps = 0
            self.isGrounded = True
            if self.dashCooldown[2] != True:
                self.canDash = True
        else:
            # adds gravity
            self.momentum[1] += self.strength[1]
            self.momentum[1] = f.numCap(self.momentum[1], self.cap[1]) # caps the gravity
            self.airTimer += 1
            self.isGrounded = False
        
        # x-axis movement
        if self.isDashing == False:
            if self.directions["right"]:
                self.momentum[0] += self.strength[0] * axesx
                self.momentum[0] = f.numCap(self.momentum[0], self.cap[0])
            elif self.directions["left"]:
                self.momentum[0] -= self.strength[0] * axesx
                self.momentum[0] = f.numCap(self.momentum[0], -self.cap[0])
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

        self.movement[0] = self.momentum[0]
        self.movement[1] = self.momentum[1]

        self.physics.move(self.movement, tiles)

    def render(self,):
        #tempRect = pygame.Rect(self.pos[0] - scroll[0], self.pos[1] - scroll[1], self.size[0], self.size[1])
        return f.CameraObject(self.physics.rect, colour=(255, 255, 0), layer=1)
        
        