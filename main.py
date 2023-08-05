# Modules
import pygame, sys, time
from pygame.constants import *
from dataclasses import dataclass

# Scripts
from scripts.framework import Animation, Controller, Keyboard, load_images, load_animations, controller_check, blit_center, control_deadzone
from scripts.entities import Player
from scripts.camera import Camera, CameraObject
from scripts.user_interface import Button, Menu, UIElement, Text
from scripts.settings import Settings
from scripts.weapons import Weapon

MENU = 0
PLAYING = 1
PAUSED = 2

BASE_IMG_PATH = "data/images/"

JUMP_STRENGTH = -7

class Game:
    def __init__(self):
        # Initialisation
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.joystick.init()
        
         # Main Settings
        self.clock = pygame.time.Clock()
        self.settings = Settings.load_from_file("data/settings.dat")

        # Joystick        
        self.inputDevices = []
        self.detect_inputs()
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
        self.assets = load_animations(BASE_IMG_PATH)

        # Entities
        self.players = []
        self.create_player([0, 0], Weapon(self, [0, 0], [8, 8], "gun", (4, -3), 90), 0)
        self.create_player([0, 0], Weapon(self, [0, 0], [8, 8], "gun", (4, -3), 90), 1)
        

        # Map
        self.floor = pygame.Rect(0, 100, 3000, 20)

        #self.camera.set_target(self.player, (0, -50))
        self.camera.set_targets(self.players, (0, -50))
        self.camera.toggle_panning()

        self.prev_time = time.time()
        self.dt = 0

        self.cameraObjects = []

    def create_player(self, pos, weapon, input=0):
        player = Player(self, pos, [8, 13], "player")
        player.weapon = weapon
        self.inputDevices[input].player = player
        self.inputDevices[input].game = self
        player.input = self.inputDevices[input]
        self.players.append(player)

    def detect_inputs(self):
        self.inputDevices = []
        self.inputDevices.append(Keyboard(self.settings.keyboard))

        try:
            self.joysticks = controller_check()
            for controller in self.joysticks:
                self.inputDevices.append(Controller(self.settings.controller, controller)) 
        except:
            print("no controllers detected")

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
            
            for player in self.players:
                player.input.update(event)

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
        for player in self.players:
            player.update([self.floor])
            player.update_animation()
        self.camera.update(self.dt)

    def render(self):
        self.cameraObjects = []
        self.camera.screen.fill((100, 100, 150))
        self.add_camera_object(self.floor, (0, 255, 0), True)
        for player in self.players:
            player.render()
    
        self.camera.render(*self.cameraObjects)

        for player in self.players:
            self.camera.display.blit(player.cursor.current_image, player.cursor.pos)

        self.tester.render(self.camera.display)
        pygame.display.update()

    def run(self):
        while True:
            pygame.mouse.set_visible(False)
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
