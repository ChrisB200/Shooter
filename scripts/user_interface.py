import pygame

def tryExcept(dict, key, default=None):
    try:
        return dict[key]
    except:
        return default

class UIElement:
    def __init__(self, x, y, width, height, style):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = tryExcept(style, "image")
        self.text = tryExcept(style, "text", "")
        self.font = tryExcept(style, "font")
        self.fontSize = tryExcept(style, "fontSize", 12)
        self.fontColour = tryExcept(style, "fontColour", (0, 0, 0))
        self.bgColour = tryExcept(style, "bgColour", (255, 255, 255))
        self.opacity = tryExcept(style, "opacity", 255)
        
    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def size(self):
        return (self.width, self.height)

    def render(self, surf):
        # Creates the text
        font = pygame.font.Font(None, self.fontSize)
        textSurface = font.render(self.text, True, self.fontColour)

        # Creates a surface
        uiElement = pygame.Surface(self.size)
        uiElement.fill(self.bgColour)
        uiElement.blit(textSurface, (self.width // 2 - (textSurface.get_width() // 2), self.height // 2 - (textSurface.get_height() // 2)))
        uiElement.set_alpha(self.opacity)
        surf.blit(uiElement, self.pos)

    def follow(self, entity):
        self.x = entity[0] - (self.width // 2)
        self.y = entity[1] - (self.height // 2)

    def set_pos(self, x, y):
        self.x = x - (self.width // 2)
        self.y = y - (self.height // 2)

    def handle_event(self, event):
        pass

class Button(UIElement):
    def __init__(self, x, y, width, height, style, action=None):
        super().__init__(x, y, width, height, style)
        self.action = action

    def handle_event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.action()
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

class Text(UIElement):
    def __init__(self, x, y, width, height, text, style):
        super().__init__(x, y, width, height, style)
        self.text = text
        self.font = tryExcept(style, "font")
        self.fontSize = tryExcept(style, "fontSize", 12)
        self.fontColour = tryExcept(style, "fontColour", (0, 0, 0))

    def render(self, surf):
        # Creates the text
        font = pygame.font.Font(None, self.fontSize)
        textSurface = font.render(self.text, True, self.fontColour)

        surf.blit(textSurface, self.pos)
            

class Menu():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.uiElements = []

    def add_elements(self, *args):
        for element in args:
            self.uiElements.append(element)

    def render(self, surf):
        for element in self.uiElements:
            element.render(surf)

    def handle(self, event):
        for element in self.uiElements:
            element.handle_event(event)
