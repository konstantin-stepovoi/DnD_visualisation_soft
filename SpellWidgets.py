import pygame
import pygame.gfxdraw
import sys
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring
from math import floor, sqrt, atan2, cos, sin, radians, degrees
import math
import Gameclass

def input_box_tk(prompt):
    root = tk.Tk()
    root.geometry("0x0")  # Делаем окно невидимым
    root.overrideredirect(1)  # Убираем заголовок окна
    """
    Окно ввода с использованием tkinter.
    Возвращает введенное значение.
    """
    root.withdraw()  
    root.attributes("-topmost", True)
    result = askstring("Input", prompt)
    root.attributes("-topmost", False)  # Снять приоритет
    root.deiconify()  # Вернуть окно tkinter
    root.destroy()
    return result

def message_box(message):
    root = tk.Tk()
    root.withdraw()
    def close_window(event=None):
        custom_window.destroy()
    title = ''
    custom_window = tk.Toplevel()
    custom_window.title(title)
    custom_window.geometry("100x70")
    custom_window.resizable(False, False)

    # Центрируем окно на экране
    custom_window.update_idletasks()
    width = custom_window.winfo_width()
    height = custom_window.winfo_height()
    x = (custom_window.winfo_screenwidth() // 2) - (width // 2)
    y = (custom_window.winfo_screenheight() // 2) - (height // 2)
    custom_window.geometry(f"{width}x{height}+{x}+{y}")

    # Сообщение
    label = tk.Label(custom_window, text=message, padx=10, pady=10)
    label.pack()
    button = tk.Button(custom_window, text="OK", command=close_window)
    button.pack()
    custom_window.bind("<Return>", close_window)
    custom_window.focus_force()
    custom_window.transient()  # Устанавливаем как модальное окно
    custom_window.grab_set()  # Захватываем фокус
    # Ожидание действия пользователя
    custom_window.transient()  # Устанавливаем как модальное окно
    custom_window.grab_set()  # Захватываем фокус
    custom_window.wait_window(custom_window)
    root.destroy()



class SpellWidget:
    def __init__(self, screen, x, y, cell_size, map_manager):
        self.screen = screen
        self.cell_size = int(cell_size * 1)  # Уменьшаем размер на 10%
        self.x = x
        self.y = y
        self.visible = False  # Для отслеживания видимости
        self.rect = pygame.Rect(self.x, self.y, self.cell_size, self.cell_size)
        self.dragging = False  # Флаг для отслеживания перетаскивания
        self.offset_x = 0  # Смещение по x для таскания из центра
        self.offset_y = 0  # Смещение по y для таскания из центра
        self.dropped_position = (self.x, self.y)  # Координаты последнего дропа
        self.map_manager = map_manager
        self.fillingcol = Gameclass.CURRENT_COLOR_PRESET.player_spells_fill
        self.bordercol = Gameclass.CURRENT_COLOR_PRESET.player_spells_border
        self.iconic_path = ['arrow.png', 'flow.png', 'spray.png', 'explosion.png']

    def draw(self, x, y):
        if self.visible:  # Отрисовываем только если видим
            center_x = x
            center_y = y
            radius = self.cell_size // 2
            center = self.rect.center
            pygame.gfxdraw.filled_circle(self.screen, center[0], center[1], radius, self.fillingcol)
            pygame.gfxdraw.aacircle(self.screen, center[0], center[1], radius, self.bordercol)
            
    def snap_to_cell(self, mouse_x, mouse_y):
        # Проверяем, что координаты внутри границ карты
        if not (self.map_manager.start_x <= mouse_x <= self.map_manager.start_x + self.map_manager.cols * self.map_manager.cell_width and
                self.map_manager.start_y <= mouse_y <= self.map_manager.start_y + self.map_manager.rows * self.map_manager.cell_height):
            return  # Если координаты вне поля, ничего не делаем

        # Получаем индексы клетки
        cell_indices = self.map_manager._get_cell_indices(mouse_x, mouse_y)
        row, col = cell_indices
        cell_corner_x = self.map_manager.start_x + (col * self.map_manager.cell_width)
        cell_corner_y = self.map_manager.start_y + (row * self.map_manager.cell_height)
        self.x = cell_corner_x
        self.y = cell_corner_y
        self.rect.topleft = (self.x, self.y)

    def delete(self):
        self.visible = False
        self.rect.topleft = (0, 0)
        self.dragging = False
        # Сбрасываем флаг инициализации
    
        # Обнуляем специфические параметры для каждого заклинания
        if isinstance(self, LinearSpell):
            self.length = 0
            self.initialized = False
        elif isinstance(self, TriangleSpell):
            self.initialized = False
            self.height = 0
            self.base = 0
        elif isinstance(self, CircularSpell):
            self.initialized = False
            self.radius = 0


    def attack(self, x, y):
        print(x, y)

    def handle_event(self, event):
        if not self.visible:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.offset_x = self.rect.centerx - event.pos[0]
                self.offset_y = self.rect.centery - event.pos[1]

        elif event.type == pygame.MOUSEBUTTONUP:
            # Когда отпустили кнопку мыши — останавливаем перетаскивание
            mx, my = event.pos
            if self.dragging:
                self.dragging = False
                self.snap_to_cell(self.rect.x, self.rect.y)
                self.attack(mx, my)
                self.delete()
                

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # Перемещаем виджет, учитывая смещение для центрирования
                self.rect.x = event.pos[0] + self.offset_x - self.rect.width // 2
                self.rect.y = event.pos[1] + self.offset_y - self.rect.height // 2


class BowSpell(SpellWidget):
    def __init__(self, screen, x, y, cell_size, map_manager):
        super().__init__(screen, x, y, cell_size, map_manager)
        self.dragging = False  # НЕ в режиме перетаскивания при создании

    def draw(self, x, y):
        """Рисует стрелу вокруг курсора, если она активна."""
        if self.visible:
            self.rect.center = (x, y)
            arrow_image = pygame.image.load(self.iconic_path[0]).convert()
            arrow_image.set_colorkey((255, 255, 255))
            arrow_image = arrow_image.convert_alpha()
            scaled_size = (self.cell_size, self.cell_size)
            arrow_image = pygame.transform.smoothscale(arrow_image, scaled_size)
            for i in range(scaled_size[0]):
                for j in range(scaled_size[1]):
                    r, g, b, a = arrow_image.get_at((i, j))
                    arrow_image.set_at((i, j), (r, g, b, min(a, 120)))  # Ограничиваем прозрачность
            image_rect = arrow_image.get_rect(center=self.rect.center)
            self.screen.blit(arrow_image, image_rect.topleft)


    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.center = event.pos  # Двигаем за мышью

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.dragging:  
                # Первый клик (начало прицеливания)
                self.dragging = True
            else:
                # Второй клик (атака)
                self.dragging = False
                mx, my = event.pos
                self.snap_to_cell(mx, my)
                pygame.display.flip()
                self.attack(mx, my)
                self.delete()

    def attack(self, x, y):
        """Проверка на попадание и нанесение урона."""
        mx, my = x, y
        enemy = self.map_manager.get_entity(mx, my)
        try:
            row, col = self.map_manager._get_cell_indices(mx, my)
        except TypeError:
            return
        
        print(f'Bow detected enemy at {row}, {col}: {enemy}, visibility: {self.visible}')
        if enemy is None:
            return
        
        roll_input = input_box_tk("Enter roll")
        armor_class = enemy.armor_class
        if roll_input and roll_input.isdigit():
            roll = int(roll_input)
            if roll >= armor_class:
                message_box('Попадание!')
                damage_input = input_box_tk("Enter damage")
                if damage_input and damage_input.isdigit():
                    damage = int(damage_input)
                    self.map_manager.set_damage(mx, my, damage)
            else:
                message_box('Промах!')




class LinearSpell(SpellWidget):
    def __init__(self, screen, x, y, cell_size, map_manager):
        super().__init__(screen, x, y, cell_size, map_manager)
        self.length = 0
        self.initialized = False
        self.angle = 0  # Угол поворота
        self.dragging = False  
        
    def draw(self, x, y):
        if self.visible:
            if not self.initialized:
                try:
                    self.length = int(input_box_tk("Enter length"))
                    self.initialized = True
                except (TypeError, ValueError):
                    self.initialized, self.visible = False, False
                    return
            dx = x - self.x
            dy = y - self.y
            self.angle = atan2(dy, dx)  # Сохраняем угол для атаки
            abs_length = (self.length + 0.5) * self.cell_size
            width = self.cell_size * 0.5
            center_x = self.x + cos(self.angle) * abs_length / 2
            center_y = self.y + sin(self.angle) * abs_length / 2
            flow_image = pygame.image.load(self.iconic_path[1]).convert()
            flow_image.set_colorkey((255, 255, 255))
            flow_image = flow_image.convert_alpha()
            scaled_size = (abs_length, width)  # Масштабируем по длине и ширине
            flow_image = pygame.transform.smoothscale(flow_image, scaled_size)
            rotated_flow_image = pygame.transform.rotate(flow_image, -degrees(self.angle))
            flow_rect = rotated_flow_image.get_rect(center=(center_x, center_y))
            self.screen.blit(rotated_flow_image, flow_rect.topleft)



    def attack(self):
        """Проводит атаку по всем врагам в линии (кроме клетки с магом)"""
        enemies_hit = []
    
        # Получаем клеточные координаты мага
        start_x = round(self.x / self.cell_size)
        start_y = round(self.y / self.cell_size)
    
        # Вычисляем шаги вдоль линии в координатах сетки, начиная со следующей клетки
        for i in range(1, self.length + 1):
            check_x = self.x + cos(self.angle) * i * self.cell_size
            check_y = self.y + sin(self.angle) * i * self.cell_size

            enemy = self.map_manager.get_entity(check_x, check_y)
            if enemy:
                enemies_hit.append((enemy, check_x, check_y))
        
        if not enemies_hit:
            return  
    
        roll_input = input_box_tk("Enter roll")
        if not roll_input or not roll_input.isdigit():
            return  
        roll = int(roll_input)
    
        # Фильтруем, кого можно атаковать
        successful_hits = [(enemy, x, y) for enemy, x, y in enemies_hit if roll >= enemy.armor_class]
    
        if not successful_hits:
            message_box("Промах!")
            return
    
        damage_input = input_box_tk("Enter damage")
        if not damage_input or not damage_input.isdigit():
            return
        damage = int(damage_input)
    
        for _, x, y in successful_hits:
            self.map_manager.set_damage(x, y, damage)



    def handle_event(self, event):
        """Обрабатывает ввод игрока"""
        if not self.visible:
            return

        if event.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = event.pos
            self.draw(mx, my)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.dragging:
                self.dragging = True
            else:
                self.dragging = False
                self.attack()
                self.delete()



class TriangleSpell(SpellWidget):
    def __init__(self, screen, x, y, cell_size, map_manager):
        super().__init__(screen, x, y, cell_size, map_manager)
        self.height = 0
        self.base = 0
        self.initialized = False  
        self.angle = 0  # Угол поворота
        self.dragging = False
        self.image = pygame.image.load('spray.png').convert_alpha()

    def draw(self, x, y):
        if self.visible:
            if not self.initialized:
                try:
                    self.height = int(input_box_tk("Enter height"))
                    self.base = int(input_box_tk("Enter base"))
                    self.initialized = True
                except (TypeError, ValueError):
                    self.initialized, self.visible = False, False
                    return

            dx = x - self.x
            dy = y - self.y
            self.angle = atan2(dy, dx)  # Угол в радианах

            # Координаты вершины треугольника (закреплены на маге)
            top_x, top_y = self.x, self.y
            
            # Вычисляем координаты основания
            base_half = (self.base * self.cell_size) / 2
            base_center_x = self.x + cos(self.angle) * self.height * self.cell_size
            base_center_y = self.y + sin(self.angle) * self.height * self.cell_size
            
            left_x = base_center_x + sin(self.angle) * base_half
            left_y = base_center_y - cos(self.angle) * base_half
            right_x = base_center_x - sin(self.angle) * base_half
            right_y = base_center_y + cos(self.angle) * base_half

            self.triangle_points = [(top_x, top_y), (left_x, left_y), (right_x, right_y)]

            triangle_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

            # Рисуем обводку
            pygame.draw.polygon(triangle_surface, self.bordercol, self.triangle_points, width=3)

            # Рисуем заливку
            pygame.draw.polygon(triangle_surface, self.fillingcol, self.triangle_points)

            # Накладываем на экран
            self.screen.blit(triangle_surface, (0, 0))

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = event.pos
            self.draw(mx, my)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.dragging:
                self.dragging = True
            else:
                self.dragging = False
                self.attack()
                self.delete()

    def attack(self):
        enemies_hit = []
        
        min_x = int(min(p[0] for p in self.triangle_points))
        max_x = int(max(p[0] for p in self.triangle_points))
        min_y = int(min(p[1] for p in self.triangle_points))
        max_y = int(max(p[1] for p in self.triangle_points))
        
        for check_x in np.arange(min_x, max_x, self.cell_size):
            for check_y in np.arange(min_y, max_y, self.cell_size):
                if self.is_inside_triangle((check_x, check_y)) and (check_x, check_y) != (self.x, self.y):
                    enemy = self.map_manager.get_entity(check_x, check_y)
                    if enemy:
                        enemies_hit.append((enemy, check_x, check_y))

        if not enemies_hit:
            return  
            
        print(enemies_hit)
        enemies_hit = enemies_hit[:-1]
        roll_input = input_box_tk("Enter roll")
        if not roll_input or not roll_input.isdigit():
            return  
        roll = int(roll_input)

        successful_hits = [(enemy, x, y) for enemy, x, y in enemies_hit if roll >= enemy.armor_class]
        
        if not successful_hits:
            message_box("Промах!")
            return

        damage_input = input_box_tk("Enter damage")
        if not damage_input or not damage_input.isdigit():
            return
        damage = int(damage_input)

        for _, x, y in successful_hits:
            self.map_manager.set_damage(x, y, damage)

    def is_inside_triangle(self, point):
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        
        def check_point(p):
            px, py = p
            v1, v2, v3 = self.triangle_points
            d1 = sign((px, py), v1, v2)
            d2 = sign((px, py), v2, v3)
            d3 = sign((px, py), v3, v1)
            
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            
            return not (has_neg and has_pos)
        
        px, py = point
        r = self.cell_size / 2
        
        # Генерируем точки по окружности + саму точку
        check_points = [(px, py)]  # Исходная точка
        for angle in range(0, 360, 45):  # Берем 8 точек по кругу
            rad = math.radians(angle)
            x_offset = r * math.cos(rad)
            y_offset = r * math.sin(rad)
            check_points.append((px + x_offset, py + y_offset))
        
        # Если хотя бы одна из точек попадает в треугольник, возвращаем True
        return any(check_point(p) for p in check_points)



class CircularSpell(SpellWidget):
    def __init__(self, screen, x, y, cell_size, map_manager):
        super().__init__(screen, x, y, cell_size, map_manager)
        self.radius = 0
        self.initialized = False  
        self.dragging = False  

    def draw(self, x, y):
        if self.visible:
            if not self.initialized:
                try:
                    self.radius = int(input_box_tk("Enter radius"))
                    self.initialized = True
                except (TypeError, ValueError):
                    self.initialized, self.visible = False, False
                    return
    
            self.rect.center = (x, y)
    
            # Загружаем картинку
            explosion_image = pygame.image.load(self.iconic_path[3]).convert_alpha()
    
            # Масштабируем под нужный размер круга
            scaled_size = (self.radius * self.cell_size * 2, self.radius * self.cell_size * 2)
            explosion_image = pygame.transform.smoothscale(explosion_image, scaled_size)
    
            # Делаем белый цвет прозрачным
            explosion_image = explosion_image.copy()
            explosion_image.set_colorkey((255, 255, 255))  # Убираем белый
    
            # Устанавливаем прозрачность (альфа-канал = 120)
            explosion_image.set_alpha(120)
    
            # Получаем координаты, чтобы центрировать картинку
            draw_x = x - self.radius * self.cell_size
            draw_y = y - self.radius * self.cell_size
    
            # Рисуем изображение
            self.screen.blit(explosion_image, (draw_x, draw_y))

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.center = event.pos  

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.dragging:  
                self.dragging = True  
            else:
                self.dragging = False  
                mx, my = event.pos
                self.snap_to_cell(mx, my)
                pygame.display.flip()
                self.attack(mx, my)
                self.delete()

    def attack(self, x, y):
        """Атака по всем врагам в круге."""
        cx, cy = x, y  
        radius_px = self.radius * self.cell_size  

        enemies_hit = []
        
        # Проходим по квадрату (2R + 1) x (2R + 1) вокруг центра
        for row in range(-self.radius, self.radius + 1):
            for col in range(-self.radius, self.radius + 1):
                # Преобразуем смещение в координаты клеток
                check_x = cx + col * self.cell_size
                check_y = cy + row * self.cell_size
                
                # Проверяем, находится ли клетка внутри круга
                if (check_x - cx) ** 2 + (check_y - cy) ** 2 <= radius_px ** 2:
                    enemy = self.map_manager.get_entity(check_x, check_y)
                    if enemy:
                        enemies_hit.append((enemy, check_x, check_y))

        if not enemies_hit:
            return  

        roll_input = input_box_tk("Enter roll")
        if not roll_input or not roll_input.isdigit():
            return  
        roll = int(roll_input)

        # Фильтруем, кого можно атаковать
        successful_hits = [(enemy, x, y) for enemy, x, y in enemies_hit if roll >= enemy.armor_class]

        if not successful_hits:
            message_box("Промах!")
            return

        damage_input = input_box_tk("Enter damage")
        if not damage_input or not damage_input.isdigit():
            return
        damage = int(damage_input)

        for _, x, y in successful_hits:
            self.map_manager.set_damage(x, y, damage)


