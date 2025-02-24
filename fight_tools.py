import pygame
from PIL import Image, ImageDraw
import math
import maptools
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring
from SpellWidgets import BowSpell, LinearSpell, CircularSpell, TriangleSpell


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
    
class Button:
    def __init__(self, button_name, entity, callback, x, y, size, icon_path):
        self.button_name = button_name
        self.entity = entity
        self.callback = callback
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)  # Прямоугольник кнопки
        padding = 10
        self.icon = pygame.transform.smoothscale(pygame.image.load(icon_path), (size - padding, size - padding))
        self.is_pressed = False

    def draw_button(self, surface):
        """Рисует кнопку на переданном surface."""
        # Скругленный прямоугольник
        color = (200, 200, 200) if not self.is_pressed else (150, 150, 150)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)  # Скругленные края

        # Отрисовка иконки
        icon_rect = self.icon.get_rect(center=self.rect.center)  # Центрирование иконки
        surface.blit(self.icon, icon_rect.topleft)  # Рисуем иконку

    def on_click(self):
        self.is_pressed = True
        if self.callback:
            self.callback(self.entity)  # Выполняем привязанную функцию

class SubToolbar:
    def __init__(self, parent_toolbar, entity, x, y, cell_size, spell_icons, callbacks):
        self.parent_toolbar = parent_toolbar
        self.entity = entity
        self.isdrawn = False
        self.x = x
        self.y = y + cell_size
        self.cell_size = cell_size

        # Создаем кнопки для подменю
        self.buttons = [
            Button(f"spell_{i}", entity, callback, self.x + i * (cell_size + 10), self.y, cell_size, icon)
            for i, (icon, callback) in enumerate(zip(spell_icons, callbacks))
        ]

    def draw_yourself(self, surface):
        """Рисует тулбар на переданном surface."""
        if self.isdrawn == False:
            return
        for button in self.buttons:
            button.draw_button(surface)
        self.isdrawn = True


    def handle_event(self, event):
        """Обрабатывает события для подменю."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.rect.collidepoint(click_pos):
                    button.on_click()


class Toolbar:
    def __init__(self, widget, entity, x, y, cell_size, spell_widgets):
        self.entity = entity
        self.isdrawn = None
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.widget = widget
        self.spell_widgets = spell_widgets
        spell_icons = ['Line_icon.png', 'Con_icon.png', 'Rad_icon.png']
        callbacks = [self.cast_line, self.cast_cone, self.cast_radius]
        self.sub_toolbar = SubToolbar(self, self.entity, self.x, self.y, self.cell_size, spell_icons, callbacks)
        self.subtoolbar_active = False  # Флаг активности сабтулбара

        # Иконки и функции для кнопок
        button_icons = ["steps.png", "sword.png", "bow.png", "magic.png"]
        button_names = ["steps", "sword", "bow", "magic"]
        button_callbacks = [self.move_steps, self.attack_sword, self.attack_bow, self.cast_magic]

        # Создаем кнопки
        self.buttons = [
            Button(button_name, entity, callback, x + i * (cell_size + 10), y, cell_size, icon_path)
            for i, (button_name, callback, icon_path) in enumerate(zip(button_names, button_callbacks, button_icons))
        ]

    def draw_yourself(self, surface):
        """Рисует панель и кнопки на переданном surface."""
        for button in self.buttons:
            button.draw_button(surface)

    
    '''методы, привязанные к кнопкам'''

    
    def move_steps(self, entity):
        cell_size = self.cell_size
        num_steps = int(self.entity.step_size)
        rect_len = (2 * num_steps + 1) * cell_size

    # Центровка квадрата
        widget_center_x = self.widget.x + cell_size // 2
        widget_center_y = self.widget.y + cell_size // 2
        top_left_x = widget_center_x - rect_len // 2
        top_left_y = widget_center_y - rect_len // 2
        step_surface = pygame.Surface((rect_len, rect_len), pygame.SRCALPHA)
        step_surface.fill((152, 251, 152, 20))  # Цвет с альфа-каналом
        # Рисуем поверхность на экране
        cur_rect = self.widget.screen.blit(step_surface, (top_left_x, top_left_y))
        pygame.display.flip()
        # Ожидание клика
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_pos = pygame.mouse.get_pos()
                    mx, my = click_pos
                    if not cur_rect.collidepoint(mx, my):
                        return
                    enemy = self.widget.map_manager.get_entity(mx, my)
                    row, col = self.widget.map_manager._get_cell_indices(mx, my)
                    print(f'Step detected enemy at {row}, {col}: {enemy}')
                    if enemy is not None:
                        return
                    self.widget.map_manager.remove_entity(mx, my)
                    self.widget.map_manager.remove_entity_by_value(self.entity)
                    self.widget.snap_to_cell(mx, my)
                    self.widget.update_toolbar_position()
                    waiting = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()


    def attack_sword(self, entity):
        # Отрисовываем предел досягаемости рукопашной атаки
        cell_size = self.cell_size
        num_steps = 1
        rect_len = (2 * num_steps + 1) * cell_size
        widget_center_x = self.widget.x + cell_size // 2
        widget_center_y = self.widget.y + cell_size // 2
        top_left_x = widget_center_x - rect_len // 2
        top_left_y = widget_center_y - rect_len // 2
        # Создаем полупрозрачную поверхность
        step_surface = pygame.Surface((rect_len, rect_len), pygame.SRCALPHA)
        # Рисуем только границу
        border_color = (130, 0, 0, 255)  # Цвет границы (RGBA)
        border_width = 2  # Толщина границы
        cur_rect = pygame.draw.rect(step_surface, border_color, (0, 0, rect_len, rect_len), border_width)
        hitbox_rect = pygame.Rect(top_left_x, top_left_y, rect_len, rect_len)
        # Рисуем поверхность на экране
        self.widget.screen.blit(step_surface, (top_left_x, top_left_y))
        pygame.display.flip()
        #Ожидание клика
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_pos = pygame.mouse.get_pos()
                    mx, my = click_pos
                    if not hitbox_rect.collidepoint(mx, my):
                        return
                    entity = self.widget.map_manager.get_entity(mx, my)
                    enemy = self.widget.map_manager.get_entity(mx, my)
                    row, col = self.widget.map_manager._get_cell_indices(mx, my)
                    print(f'Sword detected enemy at {row}, {col}: {enemy}')
                    if entity:
                        armor_class = entity.armor_class
                        roll_input = input_box_tk("Enter roll")
                        if roll_input and roll_input.isdigit():
                            roll = int(roll_input)
                            if roll >= armor_class:
                                message_box('Попадание!')
                                # Ввод урона
                                damage_input = input_box_tk("Enter damage")
                                if damage_input and damage_input.isdigit():
                                    damage = int(damage_input)
                                    self.widget.map_manager.set_damage(mx, my, damage)
                                else:
                                    print("Invalid damage input.")
                            else:
                                message_box('Промах')
                        else:
                            print("Invalid roll input.")
                    waiting = False
                    
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    

    def attack_bow(self, entity):
        attack_widget = self.spell_widgets[0]
        attack_widget.visible = True
        mx, my = pygame.mouse.get_pos()
        attack_widget.draw(mx, my)


    def cast_magic(self, entity):
        spell_icons = ['Line_icon.png', 'Con_icon.png', 'Rad_icon.png']
        callbacks = [self.cast_line, self.cast_cone, self.cast_radius]
        if self.sub_toolbar.isdrawn:
            self.sub_toolbar.isdrawn = False
        else:
            self.sub_toolbar.isdrawn = True
            self.sub_toolbar.draw_yourself(self.widget.screen)
        pygame.display.flip()


    def cast_line(self, entity):
        center_x, center_y = self.widget.x + self.widget.diameter / 2, self.widget.y + self.widget.diameter / 2
        attack_widget = self.spell_widgets[1]
        attack_widget.visible = True
        attack_widget.x = center_x
        attack_widget.y = center_y
        attack_widget.draw(center_x, center_y)

    def cast_cone(self, entity):
        center_x, center_y = self.widget.x + self.widget.diameter / 2, self.widget.y + self.widget.diameter / 2
        attack_widget = self.spell_widgets[3]
        attack_widget.x = center_x
        attack_widget.y = center_y
        attack_widget.visible = True
        attack_widget.draw(center_x, center_y)

    def cast_radius(self, entity):
        attack_widget = self.spell_widgets[2]
        attack_widget.visible = True
        mx, my = pygame.mouse.get_pos()
        attack_widget.draw(mx, my)
