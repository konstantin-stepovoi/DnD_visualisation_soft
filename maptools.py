import pygame
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring

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
        col = int((x - self.start_x) // self.cell_width)
        row = int((y - self.start_y) // self.cell_height)

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

    def get_damage(self, x, y):
        indices = self._get_cell_indices(x, y)
        if indices:
            row, col = indices
            damage = self.damage_table[row][col]
            return damage

    def report_entities(self):
        print(f'E status check started')
        for row in range(self.rows):
            for col in range(self.cols):
                if self.table[row][col] is not None:
                    entity = self.table[row][col]
                    print(f'found En at {row}, {col}, {entity}')
        print(f'E status check ended')

    def get_entity_coordinates_by_name(self, entity_name):
        """
        Ищет сущность по имени и возвращает координаты центра соответствующей клетки.

        :param entity_name: Имя сущности, которую нужно найти
        :return: Кортеж (x, y) — координаты центра клетки или None, если сущность не найдена
        """
        for row in range(self.rows):
            for col in range(self.cols):
                entity = self.table[row][col]
                if entity and getattr(entity, 'name', '') == entity_name:  # Проверяем имя сущности
                    # Рассчитываем координаты центра клетки
                    center_x = self.start_x + col * self.cell_width + self.cell_width / 2
                    center_y = self.start_y + row * self.cell_height + self.cell_height / 2
                    return center_x, center_y
        return None


class InitiativeManager:
    
    def __init__(self, map, ents):
        self.map_manager = map
        self.entities = ents
        self.current_index = 0
        self.roundtrip = len(ents) - 1
        self.initiatives_set = False
        self.names = [entity.name for entity in self.entities]

    def update_current_index(self):
        # Переход к следующему индексу, игнорируя сущности, которых нет на поле
        next_index = self.current_index + 1 if self.current_index + 1 <= self.roundtrip else 0
        current_entity = self.entities[next_index]

        # Проверяем, находится ли сущность на поле
        while self.map_manager.get_entity_coordinates_by_name(current_entity.name) is None:
            next_index = next_index + 1 if next_index + 1 <= self.roundtrip else 0
            current_entity = self.entities[next_index]

        self.current_index = next_index  # Обновляем индекс

    def gowngrade_current_index(self):
        # Переход к предыдущему индексу, игнорируя сущности, которых нет на поле
        prev_index = self.current_index - 1 if self.current_index - 1 >= 0 else self.roundtrip
        current_entity = self.entities[prev_index]

        # Проверяем, находится ли сущность на поле
        while self.map_manager.get_entity_coordinates_by_name(current_entity.name) is None:
            prev_index = prev_index - 1 if prev_index - 1 >= 0 else self.roundtrip
            current_entity = self.entities[prev_index]

        self.current_index = prev_index  # Обновляем индекс
    
    @staticmethod
    def input_boxes_tk(names):
        """
        Создает окно с полями ввода для каждого имени из списка.
        Возвращает список введенных значений (None, если ввод пустой).
        """
        root = tk.Tk()
        root.title("Input Names")
        root.geometry("300x" + str(50 * len(names)))
        root.attributes("-topmost", True)
    
        entries = {}
    
        for i, name in enumerate(names):
            label = tk.Label(root, text=name)
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(root)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="e")
            entries[name] = entry
    
        def submit():
            root.result = [entry.get() if entry.get() else None for entry in entries.values()]
            root.destroy()
    
        submit_button = tk.Button(root, text="OK", command=submit)
        submit_button.grid(row=len(names), column=0, columnspan=2, pady=10)
    
        root.result = None
        root.mainloop()
        return root.result
    
    def set_initiatives(self):
        namelist = [entity.name for entity in self.entities]
        numbers = []
        for number in self.input_boxes_tk(namelist):
            try:
                numbers.append(int(number))
            except (ValueError, TypeError):
                numbers.append(0)

        for entity, number in zip(self.entities, numbers):
            entity.initiative = number
    
        # Сортируем entities по инициативе
        self.entities.sort(key=lambda entity: entity.initiative, reverse=True)
        self.initiatives_set = True

    def draw_current_entity_rect(self, screen):
        if not self.initiatives_set:
            return  # Если инициатива не установлена, ничего не рисуем

        current_entity = self.entities[self.current_index]

        # Получаем координаты центра клетки для текущей сущности
        try:
            center_x, center_y = self.map_manager.get_entity_coordinates_by_name(current_entity.name)
        except TypeError:
            self.update_current_index()
            return
        if center_x is None or center_y is None:
            return  # Если не найдено, ничего не рисуем

        # Создаем pygame.Rect с заданными параметрами
        rect = pygame.Rect(center_x - self.map_manager.cell_width / 2, 
                           center_y - self.map_manager.cell_height / 2, 
                           self.map_manager.cell_width, 
                           self.map_manager.cell_height)
        
        # Рисуем прямоугольник с прозрачным зеленым фоном
        pygame.draw.rect(screen, (0, 255, 0), rect, 2)  # Обводка прямоугольника (зеленая)

        
        

        
        
