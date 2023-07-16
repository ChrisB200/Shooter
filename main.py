# Modules
import pygame, sys, math
from pygame.constants import *
from dataclasses import dataclass

# Scripts
import data.scripts.framework as f
from data.scripts.player import Player
from data.scripts.camera import Camera
from data.scripts.user_interface import Button, Menu, UIElement

# Constants
WIDTH, HEIGHT = 1920, 1080
SCALE = 3

@dataclass
class Controls:
    moveR: int
    moveL: int
    dash: int
    jump: int
    pause: int

KEYBOARD = Controls(K_d, K_a, K_LSHIFT, K_SPACE, K_ESCAPE)
CONTROLLER = Controls(0, 0, 1, 0, 7)

MENU = 0
PLAYING = 1
PAUSED = 2

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.joystick.init()
        
         # Main Settings + Scaling
        self.clock = pygame.time.Clock()

        # Entities
        self.player = Player([0, 0], [50, 50], "player")

        # Map
        self.floor = pygame.Rect(0, 340, 1200, 20)

        # Camera
        self.camera = Camera((WIDTH, HEIGHT), 1)
        self.camera.set_target(self.player, (0, -150))
        self.camera.toggle_panning()

        # Joystick
        self.isUsingJoystick = True
        try:
            self.joysticks = f.controller_check()
            self.selectedJoystick = self.joysticks[0]
        except:
            self.selectedJoystick = None
        self.axesx = 1

        # States
        self.currentState = PLAYING

        # Menus
        self.pauseMenu = Menu(0, 0, WIDTH, HEIGHT)
        bg = UIElement(WIDTH//2-250, HEIGHT//2-250, 500, 500, {"bgColour": (255, 255, 255), "opacity": 5})
        end = Button(bg.x+bg.width//2-50, bg.y+bg.height//2-50, 100, 100, {"bgColour": (255, 0, 0), "text": "END"}, lambda: pygame.quit())
        self.pauseMenu.add_elements(bg, end)

    def convert_cam(self, **kwargs):
        camObjects = []
        camObjects.append(kwargs.get("player").render())
        camObjects.append(f.CameraObject(kwargs.get("floor"), colour=(0, 255, 0)))
        return camObjects
    
    def keyboard_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                pygame.quit()
            if event.key == KEYBOARD.pause:
                if self.currentState == PAUSED:
                    self.currentState = PLAYING
                else:
                    self.currentState = PAUSED
            if event.key == KEYBOARD.moveL:
               self.player.directions["left"] = True
            if event.key == KEYBOARD.moveR:
               self.player.directions["right"] = True
            if event.key == KEYBOARD.jump:
                if self.player.airTimer < self.player.maxAirTimer:
                    self.player.momentum[1] = -5
                if self.player.currentJumps < self.player.totalJumps:
                    self.player.momentum[1] = -5
                    self.player.currentJumps += 1
            if event.key == KEYBOARD.dash and self.player.isDashing == False and self.player.canDash == True and self.player.dashCooldown[2] != True:
                self.player.momentum[0] = self.player.momentum[0] *self.player.dashStrength
                self.player.isDashing = True
                self.player.canDash = False
                self.player.dashCooldown[2] = True
        if event.type == pygame.KEYUP:
            if event.key == KEYBOARD.moveL:
               self.player.directions["left"] = False
            if event.key == KEYBOARD.moveR:
               self.player.directions["right"] = False

    # a:0, b:1, x:2, y:3
    def joystick_events(self, event):
        axes_x = self.selectedJoystick.get_axis(0)
        
        # Apply deadzone to filter out small joystick movements
        deadzone = 0.1  # Adjust the deadzone threshold as needed
        if abs(axes_x) < deadzone:
            axes_x = 0

        if axes_x > 0:
            self.player.directions["right"] = True
            self.player.directions["left"] = False
        elif axes_x < 0:
            self.player.directions["left"] = True
            self.player.directions["right"] = False
        else:
            self.player.directions["left"] = False
            self.player.directions["right"] = False

        if (event.type == pygame.JOYBUTTONDOWN):
            if event.button == CONTROLLER.jump:
                if self.player.airTimer < self.player.maxAirTimer:
                    self.player.momentum[1] = -5
                if self.player.currentJumps < self.player.totalJumps:
                    self.player.momentum[1] = -5
                    self.player.currentJumps += 1
            if event.button == CONTROLLER.dash and self.player.isDashing == False and self.player.canDash == True and self.player.dashCooldown[2] != True:
                self.player.momentum[0] = self.player.momentum[0] *self.player.dashStrength
                self.player.isDashing = True
                self.player.canDash = False
                self.player.dashCooldown[2] = True
            if event.button == CONTROLLER.pause:
                if self.currentState == PAUSED:
                    self.currentState = PLAYING
                else:
                    self.currentState = PAUSED

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if self.isUsingJoystick != False:
                try:
                    self.joystick_events(event)
                except:
                    self.isUsingJoystick = False
            else:
                self.keyboard_events(event)

    def paused_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == KEYBOARD.pause:
                    if self.currentState == PAUSED:
                        self.currentState = PLAYING
                    else:
                        self.currentState = PAUSED
            self.pauseMenu.handle(event)

    def update(self):
        self.player.update([self.floor], self.axesx)

    def render(self):
        self.camera.screen.fill((100, 100, 150))
        self.camera.render(self.convert_cam(player=self.player, floor=self.floor))
        pygame.display.update()

    def run(self):
        while True:
            if self.currentState == MENU:
                pass
            elif self.currentState == PAUSED:
                self.paused_events()
                self.pauseMenu.render(self.camera.display)
                pygame.display.update()
            elif self.currentState == PLAYING:
                self.update()
                self.render()
                self.playing_events()

game = Game()
game.run()



