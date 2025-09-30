import pygame
from PIL import Image, ImageDraw
import math


class ToolbarButton:
    def __init__(self, x, y, size, icon_path):
        self.rect = pygame.Rect(x, y, size, size)
        self.icon = pygame.image.load(icon_path).convert_alpha()
        self.icon = pygame.transform.smoothscale(self.icon, (size - 10, size - 10))  # Иконка с отступами
        self.is_pressed = False

    def draw(self, surface):
        color = (200, 200, 200) if not self.is_pressed else (150, 150, 150)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)  # Скругленные края
        icon_pos = (self.rect.x + 5, self.rect.y + 5)
        surface.blit(self.icon, icon_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
            if self.rect.collidepoint(event.pos):
                self.is_pressed = not self.is_pressed
                return True
        return False


class Toolbar:
    def __init__(self, x, y, cell_size, button_icons):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.button_size = int(cell_size * 0.9)
        self.spacing = 10
        self.buttons = []

        for i, icon_path in enumerate(button_icons):
            button_x = x + i * (self.button_size + self.spacing)
            button_y = y
            self.buttons.append(ToolbarButton(button_x, button_y, self.button_size, icon_path))

    def draw(self, surface):
        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False


class EntityWidget:
    def __init__(self, entity, diameter, initial_x, initial_y, cell_size):
        self.entity = entity
        self.diameter = diameter
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.x = initial_x
        self.y = initial_y
        self.cell_size = cell_size
        self.toolbar = None

        # Загружаем аватар и обрезаем его в круг
        avatar_image = Image.open(self.entity.avatar).resize((diameter, diameter))
        self.avatar_surface = self._create_circular_avatar(avatar_image)

    def _create_circular_avatar(self, image):
        size = image.size
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)

        circular_image = Image.new("RGBA", size)
        circular_image.paste(image, (0, 0), mask)

        return pygame.image.fromstring(circular_image.tobytes(), circular_image.size, circular_image.mode)

    def draw(self, surface):
        surface.blit(self.avatar_surface, (self.x, self.y))

        # HP квадрат
        square_side = self.diameter / 4
        hp_x = self.x + self.diameter + 10
        hp_y = self.y

        hp_rect = pygame.Rect(hp_x, hp_y, square_side, square_side)
        pygame.draw.rect(surface, (107, 142, 35), hp_rect)
        pygame.draw.rect(surface, (85, 107, 47), hp_rect, width=2)

        font = pygame.font.Font(None, int(square_side * 0.8))
        hp_text = font.render(str(self.entity.hp), True, (0, 0, 0))
        text_rect = hp_text.get_rect(center=hp_rect.center)
        surface.blit(hp_text, text_rect)

        if self.toolbar:
            self.toolbar.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self._is_mouse_over(event.pos):
                self.is_dragging = True
                self.offset_x = self.x - event.pos[0]
                self.offset_y = self.y - event.pos[1]
            elif event.button == 3 and self._is_mouse_over(event.pos):
                self.open_toolbar(event.pos[0], event.pos[1])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self.x = event.pos[0] + self.offset_x
            self.y = event.pos[1] + self.offset_y

        if self.toolbar:
            self.toolbar.handle_event(event)

    def _is_mouse_over(self, pos):
        return self.x <= pos[0] <= self.x + self.diameter and self.y <= pos[1] <= self.y + self.diameter

    def open_toolbar(self, mouse_x, mouse_y):
        button_icons = ["steps.png", "sword.png", "bow.png", "magic.png"]
        self.toolbar = Toolbar(mouse_x, mouse_y, self.cell_size, button_icons)


# Тестовый код
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Entity Widget Test")

    class Entity:
        def __init__(self, name, hp, armor_class, avatar, entity_type):
            self.name = name
            self.hp = hp
            self.armor_class = armor_class
            self.avatar = avatar
            self.entity_type = entity_type

    test_entity = Entity(name="Hero", hp=12, armor_class=15, avatar="gnome.png", entity_type="Player")
    widget = EntityWidget(test_entity, 100, 100, 100, 100)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            widget.handle_event(event)

        screen.fill((30, 30, 30))
        widget.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
