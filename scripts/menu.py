import pygame
from pygame.constants import *
        
class Style:
    def __init__(self, font=None, font_size=12, colour=(0, 0, 0), background=(255, 255, 255, 0), opacity=255):
        pygame.init()
        self.font = pygame.font.Font(font, font_size) # intialises font style
        self.font_size = font_size # intialises font size style
        self.colour = colour # intialises colour style
        self.background = background # intialises bg style || could add different background to main menu/GUI 
        self.opacity = opacity # opacity value
    
class Root: # for the tower defence side menu GUI, root is the basis of UI elements and their functionality
    def __init__(self, window, x=0, y=0, width=1920, height=1080): # all of these are optional parameters for game other than the SCREEN
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.window = window
        self.children = [] # contains the store of all elements on screen (is the parent node like a DIV in CSS)
        
    def update(self, window): # updates the root window
        self.window = window
        self.width = self.window.get_width()
        self.height = self.window.get_height()
        
        for child in self.children: # for loop which updates the children of that root in the main root || calls func from the child class
            child.update() 
            
    def handle_event(self, event):
        for child in reversed(self.children):
            if child.handle_event(event):
                break

    def render(self, surf):
        for child in self.children: # renders each child on the surf (game window)
            child.render(surf)

    def add_children(self, *args):
        for element in args:
            self.children.append(element)
            element.parent = self

class UIElement:
    def __init__(self, parent, x=0, y=0, width=10, height=10, text="", defaultStyle=Style(), hoverStyle=None, activeStyle=None, callback=None, canAlert=False, alertTimer=30):
        # Parent-child relationship
        self.parent = parent
        self.children = []
        
        # Transform
        self.local_x = x
        self.local_y = y
        self.width = width
        self.height = height
        self.offset = {"x": 0, "y": 0, "width": 0, "height": 0}
        
        # Styling
        self.text = text
        self.style = defaultStyle
        self.defaultStyle = defaultStyle
        self.visible = True
        self.disabled = False
        
        # Hovering
        if hoverStyle is not None:
            self.hoverStyle = hoverStyle
        else:
            self.hoverStyle = defaultStyle
        self.hover = False
        
        # Active
        if activeStyle is not None:
            self.activeStyle = activeStyle
        else:
            if hoverStyle is not None:
                self.activeStyle = hoverStyle
            else:
                self.activeStyle = defaultStyle

        # Alert
        self.maxAlertTimer = alertTimer
        self.alertTimer = self.maxAlertTimer
        self.canAlert = canAlert
        self.isAlerting = False

        if self.canAlert:
            self.visible = False

        # Docking
        self.dockTypeX = "none"
        self.dockTypeY = "none"

        self.active = False
        self.callback = callback
        
        parent.add_children(self)

    def change_parent(self, parent):
        self.parent.remove_children(self)
        self.parent = parent
    
    @property
    def x(self):
        if self.dockTypeX == "center":
            return self.parent.x + (self.parent.width // 2) - (self.width // 2) + self.offset["x"]
        if self.dockTypeX == "left":
            return self.parent.x + self.offset["x"]
        return self.local_x + + self.offset["x"] + (self.parent.x if self.parent else 0)
    
    @property
    def y(self):
        return self.local_y + + self.offset["y"] + (self.parent.y if self.parent else 0)

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def size(self):
        return (self.width, self.height)
    
    def children_render(self, surf):
        for child in self.children:
            child.render(surf)
            
    def children_update(self):
        for child in reversed(self.children):
            if child.update():
                break

    def children_handle_event(self, event):  
        for child in reversed(self.children):
            if child.handle_event(event):
                break

    def set_alert(self, isAlerting):
        self.isAlerting = isAlerting

    def set_visibility(self, visible):
        self.visible = visible

    def handle_alert(self):
        if self.isAlerting == True:
            self.visible = True
            if self.alertTimer <= 0:
                self.isAlerting = False
                self.visible = False
                self.alertTimer = self.maxAlertTimer
            else:
                self.alertTimer -= 1
            print(self.alertTimer)

    def dock_x(self, dockType):
        if dockType == "center":
            self.dockTypeX = "center"

    def handle_docking(self):
        #if self.dockTypeX == "center":
        #    self.local_x = self.parent.x + (self.parent.width // 2) - (self.width // 2) + self.offset["x"]
        #if self.dockTypeX == "left":
        #    self.local_x = self.parent.x + self.offset["x"]
        pass
    
    def handle_text(self, elementSurface):
        # Creates the text
        textSurface = self.style.font.render(self.text, True, self.style.colour)
        elementSurface.blit(textSurface, (self.width // 2 - (textSurface.get_width() // 2), self.height // 2 - (textSurface.get_height() // 2)))
    
    def handle_background(self, elementSurface):
        elementSurface.fill(self.style.background)
        
    def handle_opacity(self, elementSurface):
        elementSurface.set_alpha(self.style.opacity)

    def render(self, surf):
        if self.visible:
            # Creates a surface
            elementSurface = pygame.Surface(self.size)
            
            # Handles the drawing of the elements
            self.handle_background(elementSurface)
            self.handle_text(elementSurface)
            self.handle_opacity(elementSurface)
            self.handle_alert()
            self.handle_docking()
            
            surf.blit(elementSurface, self.pos)
            
            self.children_render(surf)
        
    def add_children(self, *args):
        for element in args:
            self.children.append(element)
            element.parent = self
            
    def check_hover(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
            return True
        else:
            return False
            
    def change_style(self, event):
        if event == "hover":
            self.style = self.hoverStyle
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif event == "active":
            self.style = self.activeStyle
        elif event == "default":
            self.style = self.defaultStyle

    def handle_event(self, event):
        if self.visible or not self.disabled:
            if self.callback is not None:
                if self.hover:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.active = True
                        self.change_style("active")
                        return True
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.callback()
                        self.active = False
                        return True

            self.children_handle_event(event)
        return False
    
    def update(self):
        if self.visible or not self.disabled:
            if self.callback != None:
                if self.check_hover() == True:
                    if self.active != True:
                        self.hover = True
                        self.change_style("hover")
                else:
                    self.hover = False
                    
                if self.active != True and self.hover != True:
                    self.change_style("default")
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
            self.children_update()
            
class Text(UIElement):
    def __init__(self, parent, x=0, y=0, width=10, height=10, text="", defaultStyle=Style(), hoverStyle=Style(), activeStyle=Style(), callback=None, dropshadow=False, shadow_offset=2, canAlert=False, alertTimer=30):
        super().__init__(parent, x, y, width, height, text, defaultStyle, hoverStyle, activeStyle, callback, canAlert, alertTimer)
        self.dropshadow = dropshadow
        self.shadow_offset = shadow_offset

    def handle_text(self):
        text_surface = self.style.font.render(self.text, True, self.style.colour)
        shadow_surface = self.handle_dropshadow()

        if shadow_surface:
            text_surface.blit(shadow_surface, (self.x + self.shadow_offset, self.y + self.shadow_offset))
            
        return text_surface

    def handle_dropshadow(self):
        if self.dropshadow:
            shadow_surface = self.style.font.render(self.text, True, (0, 0, 0))
            return shadow_surface
        else:
            return None

    def render(self, surf):
        if self.visible:
            text_surface = self.handle_text()
            self.width = text_surface.get_width()
            self.height = text_surface.get_height()

            # Handle drop shadow
            shadow_surface = self.handle_dropshadow()
            if shadow_surface:
                shadow_offset = 2  # Adjust this value based on your preference
                surf.blit(shadow_surface, (self.x + shadow_offset, self.y + shadow_offset))

            self.handle_opacity(text_surface)
            self.handle_docking()
            surf.blit(text_surface, self.pos)
            

            self.children_render(surf)
        self.handle_alert()
        
class Img(UIElement):
    def __init__(self, parent, image, x=0, y=0, width=10, height=10, text="", defaultStyle=Style(), hoverStyle=None, activeStyle=None, callback=None, dropshadow=False, canAlert=False, alertTimer=30):
        super().__init__(parent, x, y, width, height, text, defaultStyle, hoverStyle, activeStyle, callback, canAlert, alertTimer)
        self.image = image
        self.imageSize = (self.image.get_width(), self.image.get_height())
        self.objectFit = "fill"

    def reset_image(self):
        self.image = pygame.transform.scale(self.image, self.imageSize)

    def change_object_fit(self, objectFit, size=(0, 0)):
        if objectFit in ["none", "contain", "fill", "cover"]:
            self.objectFit = objectFit

    def handle_background(self, elementSurface):
        if self.objectFit == "none":
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            elementSurface.blit(self.image, (0, 0))
        elif self.objectFit == "fill":
            elementSurface.blit(pygame.transform.scale(self.image, (self.width + self.offset["width"], self.height + self.offset["height"])), (0, 0))
        
        return elementSurface