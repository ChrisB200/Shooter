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

    def draw(self, surf):
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

class Button(UIElement):
    def __init__(self, x, y, width, height, style, action=None):
        super().__init__(x, y, width, height, style)
        self.action = action

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the mouse position is within the button's bounds
            mouse_x, mouse_y = event.pos
            if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
                # The mouse is within the button, so call the action function
                self.action()
