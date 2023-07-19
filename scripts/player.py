# Modules
import pygame

# Scripts
import scripts.framework as f

class Player(f.Entity):
    def __init__(self, game, pos, size, tag):
        super().__init__(game, pos, size, tag)
        self.momentum = [0, 0] # [momentumX, momentumY]
        self.strength = [1, 0.5] # [strengthX, strengthY]
        self.cap = [6, 7] # [capX, capY]
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

        self.draw_pos = self.pos

    @property
    def get_pos(self):
        return self.pos

    def update(self, tiles, axesx=1):
        dt = self.game.clock.get_time() / 1000.0
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
                self.flip = False
            elif self.directions["left"]:
                self.momentum[0] += self.strength[0] * -axesx
                self.momentum[0] = f.numCap(self.momentum[0], -self.cap[0])
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

        self.movement[0] = self.momentum[0]
        self.movement[1] = self.momentum[1]

        self.physics.move(self.movement, tiles)
        self.pos[0] = self.physics.pos[0]
        self.pos[1] = self.physics.pos[1]

        self.game.tester.text = str(self.momentum[1])

        # Animations
        if self.airTimer > 12:
            self.set_action("jump")  
        elif ((self.directions["left"] == True) or (self.directions["right"] == True)):
            self.set_action("run")
        else:
            self.set_action("idle")
            