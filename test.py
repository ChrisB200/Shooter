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