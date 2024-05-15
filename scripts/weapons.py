# Modules
import pygame, math

# Scripts
from scripts.entities import Entity
from scripts.camera import CameraObject
from scripts.framework import get_center, blit_rotate

class Weapon(Entity):
    def __init__(self, pos, size, tag, assets, pivot=(0, 0), offset=0):
        super().__init__(pos, size, tag, assets)
        self.pivot = pivot
        self.offset = offset
        self.rotation = 0
        self.bullets = []

    # Shoots a bullet in the direction of the mouse cursor
    def shoot(self, cursor):
        bullet = Bullet(self.pos, cursor.pos, (5, 5), "bullet1", self.assets, self.rotation, 5, 30)
        self.bullets.append(bullet)

    def rotate_at_cursor(self, cursor, camera):
        # Adjust weapon position by considering camera scrolling
        weapon_x = self.pos[0] - camera.scroll[0]
        weapon_y = self.pos[1] - camera.scroll[1]

        # Flip weapon position based on x axis
        if cursor.location[0] > weapon_x:
            self.flip = False
        else:
            self.flip = True

        self.rotation = self.get_point_angle((cursor.location[0], cursor.location[1]), camera.scroll, self.offset, False)
        
    def update(self, entity, camera):
        self.pos = get_center(entity.pos, entity.size)
        self.rotate_at_cursor(entity.cursor, camera)

        for bullet in self.bullets:
            bullet.update()
            self.check_bullets()

    def render(self):
        img = blit_rotate(self.current_image, self.pos, self.pivot, self.rotation)
        weaponCameraObject = CameraObject(img[0], (img[1].x, img[1].y), 2)
        cameraObjects = [weaponCameraObject]
        
        for bullet in self.bullets:
            cameraObjects.append(bullet.render())

        return cameraObjects
    
    def check_bullets(self):
        for bullet in self.bullets:
            if bullet.remove:
                self.bullets.remove(bullet)

class Bullet(Entity):
    def __init__(self, pos, targetPos, size, tag, assets, rotation, speed, damage, rotationOffset=-90):
        super().__init__(pos, size, tag, assets)
        self.pos = pos
        self.targetPos = targetPos
        self.rotation = rotation
        self.rotationOffset = rotationOffset
        self.speed = speed
        self.damage = damage
        self.remove = False

    def update(self):
        dx = math.cos(math.radians(self.rotation + self.rotationOffset)) * self.speed
        dy = -math.sin(math.radians(self.rotation + self.rotationOffset)) * self.speed
        self.pos[0] += dx
        self.pos[1] += dy

    def render(self):
        img = pygame.transform.rotate(self.current_image, self.rotation)
        return CameraObject(img, (self.pos[0] + self.anim_offset[0], self.pos[1] + self.anim_offset[1]), 1)
    
    # Checks for collisions on an entity, it can take a colliding function which runs when a collision occurs, and a checking function
    def check_collision_on_entity(self, entity, collidedFunc, checkingFunc=None):
        if checkingFunc != None:
            if checkingFunc(entity):
                collidedFunc(entity)
        else:
            if self.rect.colliderect(entity.rect):
                collidedFunc(entity)
            