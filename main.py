# Modules
import pygame, sys, time
from pygame.constants import *
from dataclasses import dataclass

# Scripts
from scripts.framework import Animation, Controller, Keyboard, load_images, controller_check, blit_center, control_deadzone
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
        self.player.input = Keyboard(self.player, self.settings.keyboard)

        self.player2 = Player(self, [0, 0], [8, 13], "player")
        self.player2.weapon = Weapon(self, blit_center(self.player2.current_image, self.player2.pos), [8, 8], "weapons", (4, -3), 90)
        self.player2.input = Controller(self.player2, self.settings.controller, 0)

        self.players = [self.player, self.player2]

        # Map
        self.floor = pygame.Rect(0, 100, 3000, 20)

        #self.camera.set_target(self.player, (0, -50))
        self.camera.set_targets([self.player, self.player2], (0, -50))
        self.camera.toggle_panning()

        self.prev_time = time.time()
        self.dt = 0

        self.cameraObjects = []

    def add_camera_object(self, object, colour=(255, 255, 255), isRect=False, layer=1):
        if isRect:
            self.cameraObjects.append(CameraObject(object, colour=colour, layer=layer))
        else:
            self.cameraObjects.append(object)

    def remove_camera_object(self, cameraObject):
        self.cameraObjects.remove(cameraObject)

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            self.player.input.update(event)
            self.player2.input.update(event)

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
        self.player.update([self.floor])
        self.player.update_animation()
        self.player2.update([self.floor])
        self.player2.update_animation()
        self.camera.update(self.dt)

    def render(self):
        self.cameraObjects = []
        self.camera.screen.fill((100, 100, 150))
        self.add_camera_object(self.floor, (0, 255, 0), True)
        self.player.render()
        self.player2.render()
        self.camera.render(*self.cameraObjects)
        self.camera.display.blit(self.player.cursor.current_image, self.player.cursor.pos)
        self.camera.display.blit(self.player2.cursor.current_image, self.player2.cursor.pos)
        self.tester.render(self.camera.display)
        pygame.display.update()

    def run(self):
        while True:
            pygame.mouse.set_visible = False
            self.clock.tick(self.settings.targetFPS)
            now = time.time()
            self.dt = (now - self.prev_time) * self.settings.targetFPS
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



