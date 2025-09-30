import pygame
from PIL import Image, ImageDraw
import math
import maptools


'''
Надо так: при инициализации Энтити у него по определению уже есть тулбар
и в нем уже по определению уже есть 4 кнопки с соответствующим функционалом. У каждой кнопки есть как минимум название и при нажатии
она будет писать что название+какой_энтити_нажал+clicked
'''




class ToolbarButton:
    def __init__(self, x, y, size, icon_path):
        self.rect = pygame.Rect(x, y, size, size)
        self.icon = pygame.image.load(icon_path)
        padding = 10
        self.icon = pygame.transform.smoothscale(self.icon, (size - padding, size-padding))  # Уменьшаем иконку для отступов
        self.is_pressed = False
        
    def draw(self, surface):
        # Скругленный прямоугольник
        color = (200, 200, 200) if not self.is_pressed else (150, 150, 150)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)  # Скругленные края
        icon_rect = self.icon.get_rect(center=self.rect.center)  # Выравнивание по центру кнопки
        surface.blit(self.icon, icon_rect.topleft)  # Отрисовка иконки
        
    def handle_event(self, event):
        if not self.buttons:  # Если кнопок нет, выходим
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
            mouse_x, mouse_y = event.pos
            if not any(button["rect"].collidepoint(mouse_x, mouse_y) for button in self.buttons):
                return False  # Закрываем тулбар, если клик вне кнопок
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_x, mouse_y):
                    button["clicked"] = True
                    print("Button clicked!")
                    return True
        return True
        
button_icons = ["steps.png", "sword.png", "bow.png", "magic.png"]      


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
            button = ToolbarButton(button_x, button_y, self.button_size, icon_path)
            self.buttons.append(button)

    def draw(self, surface):
        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    button.is_pressed = True
                    # Здесь можно вызвать действие, привязанное к кнопке
                    print(f"Button {self.buttons.index(button)} clicked!")
                    return True
        return False

class EntityWidget:
    def __init__(self, entity, diameter, initial_x, initial_y, cell_size, map_manager):
        self.entity = entity
        self.diameter = diameter
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.x = initial_x
        self.y = initial_y
        self.cell_size = cell_size
        self.initial_position = (initial_x, initial_y)
        self.rect = pygame.Rect(self.initial_position[0], self.initial_position[1], cell_size, cell_size)

        # Сохраняем map_manager
        self.map_manager = map_manager

        # Загружаем аватар, обрезаем его в круг и конвертируем в Pygame Surface
        avatar_image = Image.open(self.entity.avatar).resize((diameter, diameter))
        self.avatar_surface = self._create_circular_avatar(avatar_image)
        self.toolbar = None

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
        surface.blit(self.avatar_surface, (self.x, self.y))
        center_x, center_y = self.x + self.diameter / 2, self.y + self.diameter / 2
        
        if self.entity.entity_type == 'Player':
            self._draw_hp_and_armor(surface, center_x, center_y)


    def _draw_hp_and_armor(self, surface, center_x, center_y):
        """Отдельный метод для отрисовки HP и Armor."""
        square_side = (math.sqrt(3) / 4) * self.diameter
        hp_x = center_x + self.diameter / 4
        hp_y = center_y - square_side
        hp_rect = pygame.Rect(hp_x, hp_y, square_side, square_side)
        
        if self.entity.entity_type == 'Player':
            square_color = (107, 142, 35)
            border_color = (85, 107, 47)
        else:
            square_color = (130, 0, 0)
            border_color = (200, 0, 0)
        
        pygame.draw.rect(surface, square_color, hp_rect)  # Основной квадрат
        pygame.draw.rect(surface, border_color, hp_rect, width=2)  # Обводка
        
        font = pygame.font.Font(None, int(0.95 * square_side))  # Размер шрифта для ХП
        hp_text = font.render(str(self.entity.hp), True, (0, 0, 0))
        text_rect = hp_text.get_rect(center=hp_rect.center)
        surface.blit(hp_text, text_rect)

        # Рисуем броню в пятиугольнике (аналогично)
        self._draw_armor(surface, center_x, center_y)

    def _draw_armor(self, surface, center_x, center_y):
        """Метод для отрисовки armor_class в пятиугольнике."""
        pentagon_height = self.diameter / 2
        pentagon_x0 = center_x + (math.sqrt(3) / 4) * self.diameter
        pentagon_y0 = center_y
        side = pentagon_height / 1.54

        pentagon_points = [
            (pentagon_x0 - side / 2, pentagon_y0), (pentagon_x0 + side / 2, pentagon_y0),
            (pentagon_x0 + 0.81 * side, pentagon_y0 + pentagon_height - 0.588 * side), 
            (pentagon_x0, pentagon_y0 + pentagon_height),
            (pentagon_x0 - 0.81 * side, pentagon_y0 + pentagon_height - 0.588 * side),
        ]
        penta_color = (176, 196, 222)
        penta_border_color = (65, 105, 225)
        
        pygame.draw.polygon(surface, penta_color, pentagon_points)
        pygame.draw.polygon(surface, penta_border_color, pentagon_points, width=2)

        # Рисуем текст armor_class
        font = pygame.font.Font(None, int(0.5 * self.diameter))  # Меньший шрифт
        ac_text = font.render(str(self.entity.armor_class), True, (0, 0, 0))
        ac_rect = ac_text.get_rect(center=(pentagon_x0, pentagon_y0 + pentagon_height / 2))
        surface.blit(ac_text, ac_rect)

    def handle_event(self, event):
        if self.toolbar:
            # Если есть тулбар, обработаем события, связанные с ним
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    # Обрабатываем событие тулбара и прерываем обработку, если тулбар не захватил событие
                    if not self.toolbar.handle_event(event):
                        self.toolbar = None
                elif event.button == 3:  # ПКМ
                    # Закрыть тулбар при ПКМ
                    self.toolbar = None
                return  # Прерываем обработку, так как при наличии тулбара больше ничего не нужно делать
                
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # ПКМ
            if self.toolbar:
                self.toolbar = None  # Скрыть тулбар
            else:
                self.toolbar = self.toolbar.draw(surface)  # Нарисовать тулбар
        return
        self._handle_dragging(event)


    def _handle_dragging(self, event):
        """Обработка перетаскивания."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
            mouse_x, mouse_y = event.pos
            if self.x <= mouse_x <= self.x + self.diameter and self.y <= mouse_y <= self.y + self.diameter:
                self.is_dragging = True
                self.offset_x = self.x - mouse_x
                self.offset_y = self.y - mouse_y
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # ЛКМ
            self.is_dragging = False

            self.snap_to_cell()                      ########### Начинаем с нуля отсюда! 

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_x, mouse_y = event.pos
                self.x = mouse_x + self.offset_x
                self.y = mouse_y + self.offset_y

