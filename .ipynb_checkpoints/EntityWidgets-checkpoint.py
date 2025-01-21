import pygame
from PIL import Image, ImageDraw
import math

class EntityWidget:
    def __init__(self, entity, diameter, initial_x, initial_y):
        self.entity = entity
        self.diameter = diameter
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.x = initial_x
        self.y = initial_y

        # Загружаем аватар, обрезаем его в круг и конвертируем в Pygame Surface
        avatar_image = Image.open(self.entity.avatar).resize((diameter, diameter))
        self.avatar_surface = self._create_circular_avatar(avatar_image)

    def _create_circular_avatar(self, image):
        """Обрезает изображение в круг и возвращает Pygame Surface."""
        size = image.size
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)

        circular_image = Image.new("RGBA", size)
        circular_image.paste(image, (0, 0), mask)

        return pygame.image.fromstring(circular_image.tobytes(), circular_image.size, circular_image.mode)

    def draw(self, surface):
        """Рисует виджет на заданной поверхности."""
        # Рисуем круг с аватаром
        surface.blit(self.avatar_surface, (self.x, self.y))
        center_x, center_y = self.x + self.diameter/2, self.y + self.diameter/2
        
        # Сторона квадрата с ХП
        square_side = (math.sqrt(3) / 4) * self.diameter

        # Позиция квадрата с ХП
        hp_x = center_x + self.diameter/4
        hp_y = center_y - square_side

        # Рисуем квадрат с HP
        hp_rect = pygame.Rect(hp_x, hp_y, square_side, square_side)
        if self.entity.entity_type == 'Player':
            square_color = (107, 142, 35)
            border_color = (85, 107, 47)
        else:
            square_color = (130, 0, 0)
            border_color = (200, 0, 0)
        pygame.draw.rect(surface, square_color, hp_rect)  # Основной квадрат
        pygame.draw.rect(surface, border_color, hp_rect, width=2)  # Обводка
        # Рисуем текст HP
        font_size = int(0.95 * square_side)  # Размер шрифта для ХП
        font = pygame.font.Font(None, font_size)
        hp_text = font.render(str(self.entity.hp), True, (0, 0, 0))
        text_rect = hp_text.get_rect(center=hp_rect.center)
        surface.blit(hp_text, text_rect)

        # Пятиугольник для armor_class
        pentagon_height = self.diameter / 2  # Высота пятиугольника равна радиусу
        pentagon_x0 = hp_x + square_side /2  
        pentagon_y0 = center_y
        side = pentagon_height / 1.54

        # Координаты вершин пятиугольника
        pentagon_points = [
            (pentagon_x0 - side/2, pentagon_y0), (pentagon_x0 + side/2, pentagon_y0),
            (pentagon_x0 + 0.81*side, pentagon_y0 + pentagon_height - 0.588 * side), 
            (pentagon_x0, pentagon_y0+pentagon_height),
            (pentagon_x0 - 0.81*side, pentagon_y0 + pentagon_height - 0.588 * side),
        ]
        penta_color = (176, 196, 222)
        penta_border_color = (65, 105, 225)
        # Рисуем пятиугольник
        if self.entity.entity_type != 'Monster':
            pygame.draw.polygon(surface, penta_color, pentagon_points)
            pygame.draw.polygon(surface, penta_border_color, pentagon_points, width = 2)

            # Рисуем текст armor_class по центру пятиугольника
            ac_text = font.render(str(self.entity.armor_class), True, (0, 0, 0))
            ac_rect = ac_text.get_rect(center=(pentagon_x0, pentagon_y0 + pentagon_height / 2))
            surface.blit(ac_text, ac_rect)

    def handle_event(self, event):
        """Обрабатывает события для перетаскивания виджета."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_x, mouse_y = event.pos
                if self.x <= mouse_x <= self.x + self.diameter and self.y <= mouse_y <= self.y + self.diameter:
                    self.is_dragging = True
                    self.offset_x = self.x - mouse_x
                    self.offset_y = self.y - mouse_y

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_x, mouse_y = event.pos
                self.x = mouse_x + self.offset_x
                self.y = mouse_y + self.offset_y

    def snap_to_cell(self, cell):
        #Привязывает виджет к центру заданной клетки.
        self.x = cell.rect.x + (cell.rect.width - self.diameter) / 2
        self.y = cell.rect.y + (cell.rect.height - self.diameter) / 2

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

    test_entity = Entity(name="Hero", hp=12, armor_class=15, avatar="gnome.png", entity_type="player")
    widget = EntityWidget(test_entity, 100)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            widget.handle_event(event)

        screen.fill((30, 30, 30))
        widget.draw(screen)
        pygame.display.flip()

    pygame.quit()