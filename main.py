# Modules
import pygame, sys, time
from pygame.constants import *
from dataclasses import dataclass

# Scripts
from scripts.framework import Animation, load_images, controller_check, blit_center, control_deadzone
from scripts.entities import Player
from scripts.camera import Camera, CameraObject
from scripts.user_interface import Button, Menu, UIElement, Text
from scripts.settings import Settings
from scripts.weapons import Weapon

MENU = 0
PLAYING = 1
PAUSED = 2

JUMP_STRENGTH = -7

#1024 768
class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.joystick.init()
        
         # Main Settings + Scaling
        self.clock = pygame.time.Clock()
        self.settings = Settings.load_from_file("data/settings.dat")

        # Joystick
        self.isUsingJoystick = False
        try:
            self.joysticks = controller_check()
            self.selectedJoystick = self.joysticks[0]
        except:
            self.selectedJoystick = None

        self.leftJoy = (1, 1)
        self.rightJoy = (1, 1)
        self.switch_input()

        # States
        self.currentState = PLAYING

        # Camera
        self.camera = Camera(self.settings.resolution, 2)

        # Menus
        self.pauseMenu = Menu(0, 0, self.settings.width, self.settings.height)
        bg = UIElement(self.settings.width//2-250, self.settings.height//2-250, 500, 500, {"bgColour": (255, 255, 255), "opacity": 5})
        end = Button(bg.x+bg.width//2-50, bg.y+bg.height//2-50, 100, 100, {"bgColour": (255, 0, 0), "text": "END"}, lambda: (self.settings.save_to_file("data/settings.dat"), pygame.quit()))
        self.pauseMenu.add_elements(bg, end)

        self.tester = Text(200, 200, 400, 400, "undefined", {"fontColour": (255, 255, 255), "opacity": 0, "fontSize": 40})

        # Assets
        self.assets = {
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=10),
            'player/run': Animation(load_images('entities/player/run'), img_dur=10),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'weapons/idle': Animation(load_images('weapons')),
            'cursor/idle': Animation(load_images('cursor'))
        }

        # Entities
        self.player = Player(self, [0, 0], [8, 13], "player")
        self.player.weapon = Weapon(self, blit_center(self.player.current_image, self.player.pos), [8, 8], "weapons", (4, -3), 90)

        # Map
        self.floor = pygame.Rect(0, 100, 1000, 20)

        self.camera.set_target(self.player, (0, -50))
        self.camera.toggle_panning()

        self.prev_time = time.time()
        self.dt = 0

    def switch_input(self):
        if not self.isUsingJoystick:
            self.isUsingJoystick = True
            self.leftJoy = (0, 0)
            self.rightJoy = (0, 0)
        else:
            self.isUsingJoystick = False
            self.leftJoy = (1, 1)
            self.rightJoy = None
        

    def convert_cam(self, **kwargs):
        camObjects = []
        camObjects.append(kwargs.get("player").render())
        camObjects.append(CameraObject(kwargs.get("floor"), colour=(0, 255, 0)))
        camObjects.append(kwargs.get("weapon").render())
        return camObjects
    
    def keyboard_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                pygame.quit()
            if event.key == self.settings.keyboard.pause:
                if self.currentState == PAUSED:
                    self.currentState = PLAYING
                else:
                    self.currentState = PAUSED
            if event.key == self.settings.keyboard.moveL:
               self.player.directions["left"] = True
            if event.key == self.settings.keyboard.moveR:
               self.player.directions["right"] = True
            if event.key == self.settings.keyboard.jump:
                if self.player.airTimer < self.player.maxAirTimer:
                    self.player.momentum[1] = JUMP_STRENGTH
                if self.player.currentJumps < self.player.totalJumps:
                    self.player.momentum[1] = JUMP_STRENGTH
                    self.player.currentJumps += 1
            if event.key == self.settings.keyboard.dash and self.player.isDashing == False and self.player.canDash == True and self.player.dashCooldown[2] != True:
                self.player.momentum[0] = self.player.momentum[0] * self.player.dashStrength
                self.player.isDashing = True
                self.player.canDash = False
                self.player.dashCooldown[2] = True
        if event.type == pygame.KEYUP:
            if event.key == self.settings.keyboard.moveL:
               self.player.directions["left"] = False
            if event.key == self.settings.keyboard.moveR:
               self.player.directions["right"] = False
        if event.type == pygame.MOUSEWHEEL:
            zoom = event.y/10
            self.camera.zoom(zoom)

    # a:0, b:1, x:2, y:3
    def joystick_events(self, event):
        self.leftJoy = control_deadzone(0.1, self.selectedJoystick.get_axis(0), self.selectedJoystick.get_axis(1))
        self.rightJoy = control_deadzone(0.1, self.selectedJoystick.get_axis(2), self.selectedJoystick.get_axis(3))

        if self.leftJoy[0] > 0:
            self.player.directions["right"] = True
            self.player.directions["left"] = False
        elif self.leftJoy[0] < 0:
            self.player.directions["left"] = True
            self.player.directions["right"] = False
        else:
            self.player.directions["left"] = False
            self.player.directions["right"] = False

        if (event.type == pygame.JOYBUTTONDOWN):
            if event.button == self.settings.controller.jump:
                if self.player.airTimer < self.player.maxAirTimer:
                    self.player.momentum[1] = JUMP_STRENGTH
                if self.player.currentJumps < self.player.totalJumps:
                    self.player.momentum[1] = JUMP_STRENGTH
                    self.player.currentJumps += 1
            if event.button == self.settings.controller.dash and self.player.isDashing == False and self.player.canDash == True and self.player.dashCooldown[2] != True:
                self.player.momentum[0] = self.player.momentum[0] * self.player.dashStrength
                self.player.isDashing = True
                self.player.canDash = False
                self.player.dashCooldown[2] = True
            if event.button == self.settings.controller.pause:
                if self.currentState == PAUSED:
                    self.currentState = PLAYING
                else:
                    self.currentState = PAUSED

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_0:
                    self.switch_input()
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
                if event.key == self.settings.keyboard.pause:
                    if self.currentState == PAUSED:
                        self.currentState = PLAYING
                    else:
                        self.currentState = PAUSED
            self.pauseMenu.handle(event)

    def update(self):
        self.tester.text = str(self.leftJoy)
        self.player.update([self.floor])
        self.player.update_animation()
        self.camera.update(self.dt)

    def render(self):
        self.camera.screen.fill((100, 100, 150))
        self.camera.render(self.convert_cam(player=self.player, floor=self.floor, weapon=self.player.weapon))
        self.camera.display.blit(self.player.cursor.current_image, self.player.cursor.pos)
        self.tester.render(self.camera.display)
        pygame.display.update()

    def run(self):
        while True:
            self.clock.tick(self.settings.targetFPS)
            now = time.time()
            self.dt = 1
            self.prev_time = now
            
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

Game().run()



