# Modules
import pygame
import sys
import time
from pygame.constants import *

# Scripts
from scripts.framework import blit_center
from scripts.animation import load_images, load_animations
from scripts.input import Controller, Keyboard, Controls, controller_check
from scripts.entities import Player
from scripts.camera import Camera, CameraObject
from scripts.settings import Settings
from scripts.weapons import Weapon

BASE_IMG_PATH = "data/images/"

MENU = 0
PLAYING = 1
PAUSED = 2

class Game:
    def __init__(self):
        # Initialisation
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.joystick.init()

         # Main Settings
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.settings: Settings = Settings.load_from_file("data/settings.dat")

        # Camera
        self.cameraObjects = []
        self.camera = Camera(self.settings.resolution, 2)

        # Joystick        
        self.inputDevices: list[Controller | Keyboard] = []

        # States
        self.currentState = PLAYING

        # Assets
        self.assets = load_animations(BASE_IMG_PATH)

        # Entities
        self.players = []
        self.floor = pygame.Rect(0, 100, 3000, 20)

        # Delta Time Calculations
        self.prev_time = time.time()
        self.dt = 0
        
    def start(self):
        self.detect_inputs()
        self.create_player([0, 0], Weapon([0, 0], [8, 8], "gun", self.assets, (4, -3), 90), 0)
        self.create_player([0, 0], Weapon([0, 0], [8, 8], "gun", self.assets, (4, -3), 90), 1)
        self.camera.set_targets(self.players, (0, -50))
        self.camera.toggle_panning()

    def create_player(self, pos, weapon, input=0):
        player = Player(len(self.players), pos, [8, 13], "player", self.assets)
        player.weapon = weapon
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
            if event.type == pygame.KEYDOWN:
                if event.key == self.settings.keyboard.pause:
                    if self.currentState == PAUSED:
                        self.currentState = PLAYING
                    else:
                        self.currentState = PAUSED
            
            for player in self.players:
                player.input_events(event)

    def update(self):
        player: Player
        for player in self.players:
            player.update([self.floor], self.dt, self.camera)
            player.update_animation(self.dt)
            player.check_entity_collisions(self.players)
        self.camera.update(self.dt)

    def render(self):
        self.cameraObjects = []
        self.camera.screen.fill((100, 100, 150))
        self.add_camera_object(self.floor, (0, 255, 0), True)
        
        player: Player
        for player in self.players:
            tempPlayer = player.render()[0]
            tempWeaponAndBullets = player.render()[1]
            self.add_camera_object(tempPlayer)


            for camObj in tempWeaponAndBullets:
                self.add_camera_object(camObj)
    
        self.camera.render(*self.cameraObjects)

        for player in self.players:
            self.camera.display.blit(player.cursor.current_image, player.cursor.pos)

        pygame.display.update()

    def run(self):
        self.start()
        while True:
            self.clock.tick(self.settings.targetFPS)
            now = time.time()
            self.dt = (now - self.prev_time) * self.settings.targetFPS
            self.prev_time = now
            
            if self.currentState == MENU:
                pass
            elif self.currentState == PLAYING:
                pygame.mouse.set_visible(False)
                self.update()
                self.render()
                self.playing_events()

Game().run()
