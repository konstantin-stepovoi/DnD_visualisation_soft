import pygame
import pygame.gfxdraw
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring

def input_box_tk(prompt):
    root = tk.Tk()
    root.geometry("0x0")  # Делаем окно невидимым
    root.overrideredirect(1)  # Убираем заголовок окна
    """
    Окно ввода с использованием tkinter.
    Возвращает введенное значение.
    """
    root.withdraw()  # Скрыть основное окно tkinter
    root.attributes("-topmost", True)  # Поверх всех окон
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
        self.rect = pygame.Rect(self.x, self.y, self.cell_size, self.cell_size)  # Площадь, занимаемая виджетом
        self.dragging = False  # Флаг для отслеживания перетаскивания
        self.offset_x = 0  # Смещение по x для таскания из центра
        self.offset_y = 0  # Смещение по y для таскания из центра
        self.dropped_position = (self.x, self.y)  # Координаты последнего дропа
        self.map_manager = map_manager

    def draw(self):
        if self.visible:  # Отрисовываем только если видим
            radius = self.cell_size // 2
            center = self.rect.center
            pygame.gfxdraw.filled_circle(self.screen, center[0], center[1], radius, (100, 0, 0, 100))
            pygame.gfxdraw.aacircle(self.screen, center[0], center[1], radius, (100, 0, 0, 100))
            
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

    def attack(self, x, y):
        print(x, y)

    def handle_event(self, event):
        if not self.visible:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                # Вычисляем смещение от центра виджета
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


# Подклассы для разных типов заклинаний
class BowSpell(SpellWidget):
    def __init__(self, screen, x, y, cell_size, map_manager):
        super().__init__(screen, x, y, cell_size, map_manager)
        
    def attack(self, x, y):
        mx, my = x, y
        enemy = self.map_manager.get_entity(mx, my)
        row, col = self.map_manager._get_cell_indices(mx, my)
        print(f'Bow detected enemy at {row}, {col}: {enemy}')
        #print(f'bow attack to {mx, my}')
        #print(self.map_manager.table)
        entity = self.map_manager.get_entity(mx, my)
        print(entity)
        if entity is None:
            return
        roll_input = input_box_tk("Enter roll")
        armor_class = entity.armor_class
        if roll_input and roll_input.isdigit():
            roll = int(roll_input)
            if roll >= armor_class:
                message_box('Попадание!')
                damage_input = input_box_tk("Enter damage")
                if damage_input and damage_input.isdigit():
                    damage = int(damage_input)
                    self.map_manager.set_damage(mx, my, damage)
            else: message_box('Промах!')
        return

class LinearSpell(SpellWidget):
    def __init__(self, screen, x, y, cell_size, map_manager):
        super().__init__(screen, x, y, cell_size, map_manager)
        # Логика для LinearSpell

class TriangleSpell(SpellWidget):
    def __init__(self, screen, x, y, cell_size, map_manager):
        super().__init__(screen, x, y, cell_size, map_manager)
        # Логика для TriangleSpell

class CircularSpell(SpellWidget):
    def __init__(self, screen, x, y, cell_size, map_manager):
        super().__init__(screen, x, y, cell_size, map_manager)
        # Логика для CircularSpell