import pygame
from PIL import Image


def get_scaled_image_properties(map_image, screen_width, screen_height):
    """
    Масштабирует изображение и рассчитывает его положение в окне.

    :param map_image: Изображение карты (объект PIL.Image)
    :param screen_width: Ширина окна
    :param screen_height: Высота окна
    :return: (left_top, right_bottom, scaled_width, scaled_height)
        - left_top: Координаты левого верхнего угла (x, y)
        - right_bottom: Координаты правого нижнего угла (x, y)
        - scaled_width: Ширина масштабированного изображения
        - scaled_height: Высота масштабированного изображения
    """
    # Размеры оригинального изображения
    map_width, map_height = map_image.size

    # Соотношение сторон изображения и окна
    image_aspect = map_width / map_height
    screen_aspect = screen_width / screen_height

    # Определяем размеры масштабированного изображения
    if image_aspect > screen_aspect:
        # Ограничение по ширине
        scaled_width = screen_width
        scaled_height = int(screen_width / image_aspect)
    else:
        # Ограничение по высоте
        scaled_height = screen_height
        scaled_width = int(screen_height * image_aspect)

    # Координаты центра изображения
    left_top_x = (screen_width - scaled_width) // 2
    left_top_y = (screen_height - scaled_height) // 2
    left_top = (left_top_x, left_top_y)

    right_bottom_x = left_top_x + scaled_width
    right_bottom_y = left_top_y + scaled_height
    right_bottom = (right_bottom_x, right_bottom_y)

    return left_top, right_bottom, scaled_width, scaled_height




class GridCell:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, border_color=(255, 255, 255), border_width=1, fill_color=None):
        # Отрисовка заливки с прозрачностью
        if fill_color:
            fill_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            fill_surface.fill(fill_color)
            surface.blit(fill_surface, (self.rect.x, self.rect.y))
        
        # Отрисовка границ
        pygame.draw.rect(surface, border_color, self.rect, border_width)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


def create_grid(rows, cols, cell_width, cell_height, start_x=0, start_y=0, total_width=None, total_height=None):
    grid = []
    for row in range(rows):
        grid_row = []
        for col in range(cols):
            # Рассчитываем ширину и высоту клетки с учетом остатка
            current_cell_width = cell_width + (1 if col < (total_width % cols) else 0) if total_width else cell_width
            current_cell_height = cell_height + (1 if row < (total_height % rows) else 0) if total_height else cell_height
            
            cell_x = start_x + col * cell_width + min(col, total_width % cols) if total_width else start_x + col * cell_width
            cell_y = start_y + row * cell_height + min(row, total_height % rows) if total_height else start_y + row * cell_height
            
            grid_row.append(GridCell(cell_x, cell_y, current_cell_width, current_cell_height))
        grid.append(grid_row)
    return grid



class MapManager:
    def __init__(self, grid):
        """
        Инициализация менеджера карты.

        :param grid: Сетка (двумерный список объектов GridCell)
        """
        # Создаем таблицу для объектов
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.table = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        # Создаем таблицу для урона
        self.damage_table = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # Сохраняем границы ячеек для перевода координат
        self.cell_width = grid[0][0].rect.width if self.rows > 0 and self.cols > 0 else 0
        self.cell_height = grid[0][0].rect.height if self.rows > 0 and self.cols > 0 else 0
        self.start_x = grid[0][0].rect.x if self.rows > 0 and self.cols > 0 else 0
        self.start_y = grid[0][0].rect.y if self.rows > 0 and self.cols > 0 else 0

    def _get_cell_indices(self, x, y):
        """
        Преобразует абсолютные координаты в индексы ячейки.

        :param x: Абсолютная координата X
        :param y: Абсолютная координата Y
        :return: Кортеж (row, col) или None, если координаты вне сетки
        """
        col = (x - self.start_x) // self.cell_width
        row = (y - self.start_y) // self.cell_height

        if 0 <= col < self.cols and 0 <= row < self.rows:
            return row, col
        return None

    def is_empty(self, x, y):
        """
        Проверяет, пустая ли ячейка по заданным координатам.

        :param x: Абсолютная координата X
        :param y: Абсолютная координата Y
        :return: True, если ячейка пуста, иначе False
        """
        indices = self._get_cell_indices(x, y)
        if indices:
            row, col = indices
            return self.table[row][col] is None
        return False

    def set_entity(self, x, y, entity):
        """
        Устанавливает объект в ячейку по заданным координатам.

        :param x: Абсолютная координата X
        :param y: Абсолютная координата Y
        :param entity: Объект, который нужно установить
        :return: True, если операция успешна, иначе False
        """
        indices = self._get_cell_indices(x, y)
        if indices:
            row, col = indices
            for r in range(len(self.table)):
                for c in range(len(self.table[r])):
                    if self.table[r][c] == entity and (r != row or c != col):
                        self.table[r][c] = None  # Очистка клетки
            self.table[row][col] = entity
            return True
        return False

    def remove_entity(self, x, y):
        """
        Убирает объект из ячейки по заданным координатам.

        :param x: Абсолютная координата X
        :param y: Абсолютная координата Y
        :return: True, если операция успешна, иначе False
        """
        indices = self._get_cell_indices(x, y)
        if indices:
            row, col = indices
            self.table[row][col] = None
            return True
        return False

    def get_entity(self, x, y):
        """
        Возвращает объект из ячейки по заданным координатам.

        :param x: Абсолютная координата X
        :param y: Абсолютная координата Y
        :return: Объект в ячейке или None
        """
        indices = self._get_cell_indices(x, y)
        if indices:
            row, col = indices
            return self.table[row][col]
        return None

    def remove_entity_by_value(self, entity):
        """
        Удаляет все вхождения заданного объекта из таблицы.

        :param entity: Объект, который нужно удалить
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.table[row][col] == entity:
                    self.table[row][col] = None

    def set_damage(self, x, y, damage):
        """
        Устанавливает значение урона в таблицу damage_table по заданным координатам.

        :param x: Абсолютная координата X
        :param y: Абсолютная координата Y
        :param damage: Значение урона (int)
        :return: True, если операция успешна, иначе False
        """
        indices = self._get_cell_indices(x, y)
        if indices:
            row, col = indices
            self.damage_table[row][col] = damage
            return True
        return False

    def reset_damage(self):
        """
        Обнуляет всю таблицу damage_table.
        """
        for row in range(self.rows):
            for col in range(self.cols):
                self.damage_table[row][col] = 0

        


