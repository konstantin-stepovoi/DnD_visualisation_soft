import pygame
from PIL import Image, ImageDraw
import math
import maptools

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


    def snap_to_cell(self, mouse_x, mouse_y):
        '''
        автоцентровка по клетке
        '''
        # Проверяем, что координаты внутри границ карты
        if not (self.map_manager.start_x <= mouse_x <= self.map_manager.start_x + self.map_manager.cols * self.map_manager.cell_width and
                self.map_manager.start_y <= mouse_y <= self.map_manager.start_y + self.map_manager.rows * self.map_manager.cell_height):
            return  # Если координаты вне поля, ничего не делаем
                
        if self.map_manager.get_entity(mouse_x, mouse_y) == None:
            cell_indices = self.map_manager._get_cell_indices(mouse_x, mouse_y)
            row, col = cell_indices
            #так, ну row, col он считает правильно, окей
            
            # Вычисляем координаты центра клетки
            cell_corner_x = self.map_manager.start_x + (col * self.map_manager.cell_width) 
            cell_corner_y = self.map_manager.start_y + (row * self.map_manager.cell_height)
            '''print(f'sx = {self.map_manager.cell_width, self.map_manager.cell_height}')
            print(f'start_corner: {self.map_manager.start_x, self.map_manager.start_y}')
            print(f'corner_x = {cell_corner_x}, corner_y = {cell_corner_y}')'''
            # Устанавливаем виджет в центр этой клетки
            self.x = cell_corner_x
            self.y = cell_corner_y
            self.rect.topleft = (self.x, self.y)
            self.map_manager.set_entity(mouse_x, mouse_y, self.entity)
        else:
            self.snap_to_cell(mouse_x + self.diameter, mouse_y)
                


#######################################################################################

    
    def handle_event(self, event):
        """Обрабатывает события мыши для перетаскивания или клика правой кнопкой."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Проверяем, нажата ли левая кнопка мыши и находится ли курсор внутри виджета
            if event.button == 1 and self.rect.collidepoint(mouse_x, mouse_y):
                self.is_dragging = True
                self.offset_x = mouse_x - self.x
                self.offset_y = mouse_y - self.y

            # Игнорируем правый клик мыши
            elif event.button == 3 and self.rect.collidepoint(mouse_x, mouse_y):
                pass
    
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_x, mouse_y = event.pos
                self.x = mouse_x - self.offset_x
                self.y = mouse_y - self.offset_y
                self.rect.topleft = (self.x, self.y)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_x, mouse_y = event.pos
            if event.button == 1 and self.rect.collidepoint(mouse_x, mouse_y):
                mouse_x, mouse_y = event.pos
                self.snap_to_cell(mouse_x, mouse_y)
                self.is_dragging = False
                


        