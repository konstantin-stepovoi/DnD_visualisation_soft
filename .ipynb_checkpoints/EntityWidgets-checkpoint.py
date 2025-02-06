import pygame
from PIL import Image, ImageDraw
import math
import maptools
import tkinter as tk
from tkinter.simpledialog import askstring
from fight_tools import Button, Toolbar
import Gameclass


class EntityWidget:
    def __init__(self, entity, diameter, initial_x, initial_y, cell_size, map_manager, screen, spell_widgets):
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
        self.map_manager = map_manager
        avatar_image = Image.open(self.entity.avatar).resize((diameter, diameter))
        self.avatar_surface = self._create_circular_avatar(avatar_image)
        # Теперь займёмся генерацией тулбара
        self.toolbar = None
        self.screen = screen
        self.spell_widgets = spell_widgets
        
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
        """Рисует виджет и тулбар (если он есть) на заданной поверхности."""
        avatar_path = self.entity.avatar if self.entity.hp > 0 else self.entity.death_avatar
        avatar_image = Image.open(avatar_path).resize((self.diameter, self.diameter))
        self.avatar_surface = self._create_circular_avatar(avatar_image)

        surface.blit(self.avatar_surface, (self.x, self.y))
        center_x, center_y = self.x + self.diameter / 2, self.y + self.diameter / 2

        if self.entity.entity_type is not None:
            self._draw_hp_and_armor(surface, center_x, center_y)

        if self.toolbar:
            self.toolbar.draw_yourself(surface)
            if self.toolbar.sub_toolbar.isdrawn:
                self.toolbar.sub_toolbar.draw_yourself(surface)



    def _draw_hp_and_armor(self, surface, center_x, center_y):
        """Отдельный метод для отрисовки HP и Armor."""
        square_side = (math.sqrt(3) / 4) * self.diameter
        hp_x = center_x + self.diameter / 4
        hp_y = center_y - square_side
        hp_rect = pygame.Rect(hp_x, hp_y, square_side, square_side)
        
        if self.entity.entity_type == 'Player':
            square_color = Gameclass.CURRENT_COLOR_PRESET.hp_fill
            border_color = Gameclass.CURRENT_COLOR_PRESET.hp_border
        else:
            square_color = Gameclass.CURRENT_COLOR_PRESET.hp_fill
            border_color = Gameclass.CURRENT_COLOR_PRESET.hp_border
        
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
        penta_color = Gameclass.CURRENT_COLOR_PRESET.armor_border
        penta_border_color = Gameclass.CURRENT_COLOR_PRESET.armor_border
        
        pygame.draw.polygon(surface, penta_color, pentagon_points)
        pygame.draw.polygon(surface, penta_border_color, pentagon_points, width=2)

        # Рисуем текст armor_class
        font = pygame.font.Font(None, int(0.5 * self.diameter))  # Меньший шрифт
        ac_text = font.render(str(self.entity.armor_class), True, (0, 0, 0))
        ac_rect = ac_text.get_rect(center=(pentagon_x0, pentagon_y0 + pentagon_height / 2))
        surface.blit(ac_text, ac_rect)


    def snap_to_cell(self, mouse_x, mouse_y):
        """
        Автоцентровка виджета по клетке.
        """
        # Проверяем, что координаты внутри границ карты
        if not (self.map_manager.start_x <= mouse_x <= self.map_manager.start_x + self.map_manager.cols * self.map_manager.cell_width and
                self.map_manager.start_y <= mouse_y <= self.map_manager.start_y + self.map_manager.rows * self.map_manager.cell_height):
            return  # Если координаты вне поля, ничего не делаем

        # Получаем индексы клетки
        cell_indices = self.map_manager._get_cell_indices(mouse_x, mouse_y)
        row, col = cell_indices

        # Проверяем, занята ли клетка
        if self.map_manager.get_entity(mouse_x, mouse_y) is not None:
            # Если клетка занята, пробуем соседнюю
            self.snap_to_cell(mouse_x + self.diameter, mouse_y)
            return

        # Если клетка свободна, перемещаем виджет
        self.map_manager.remove_entity_by_value(self.entity)
        cell_corner_x = self.map_manager.start_x + (col * self.map_manager.cell_width)
        cell_corner_y = self.map_manager.start_y + (row * self.map_manager.cell_height)
        self.x = cell_corner_x
        self.y = cell_corner_y
        self.rect.topleft = (self.x, self.y)
        self.map_manager.set_entity(mouse_x, mouse_y, self.entity)
        #self.map_manager.report_entities()



                    
    def update_toolbar_position(self):
        """Обновляет положение тулбара в зависимости от текущей позиции виджета."""
        if self.toolbar:
            toolbar_x = self.x + self.diameter + 10  # Смещение справа от виджета
            toolbar_y = self.y
            self.toolbar.x = toolbar_x
            self.toolbar.y = toolbar_y
            self.toolbar.sub_toolbar.x = toolbar_x
            self.toolbar.sub_toolbar.y = toolbar_y

            # Обновляем позиции кнопок в тулбаре
            for i, button in enumerate(self.toolbar.buttons):
                button.x = toolbar_x + i * (self.cell_size + 10)
                button.y = toolbar_y
                button.rect.topleft = (button.x, button.y)
            for i, button in enumerate(self.toolbar.sub_toolbar.buttons):
                button.x = toolbar_x + i * (self.cell_size + 10)
                button.y = toolbar_y + self.cell_size
                button.rect.topleft = (button.x, button.y)

    def update_position(self):
        if self.map_manager.get_entity(self.x, self.y) is None:
            self.map_manager.set_entity(self.x, self.y, self.entity)

    def get_damage(self):
        damage = self.map_manager.get_damage(self.x, self.y)
        if isinstance(damage, int):
            self.entity.hp = self.entity.hp - damage

    def open_stat_adjustment_window(self):
        """Открывает окно Tkinter для ввода значений HP и Armor."""
        root = tk.Tk()
        root.withdraw()  # Скрыть основное окно
        root.attributes("-topmost", True)  # Поверх всех окон

        input_window = tk.Toplevel(root)
        input_window.title("Adjust Stats")
        input_window.geometry("200x150")
        input_window.resizable(False, False)
    
        tk.Label(input_window, text="HP:").pack()
        hp_entry = tk.Entry(input_window)
        hp_entry.pack()
    
        tk.Label(input_window, text="Armor:").pack()
        armor_entry = tk.Entry(input_window)
        armor_entry.pack()
    
        def apply_changes():
            hp_change = hp_entry.get().strip()
            armor_change = armor_entry.get().strip()
        
            try:
                hp_value = int(hp_change) if hp_change else 0
            except ValueError:
                hp_value = 0
        
            try:
                armor_value = int(armor_change) if armor_change else 0
            except ValueError:
                armor_value = 0
        
            self.entity.hp += hp_value
            self.entity.armor_class += armor_value
        
            input_window.destroy()
            root.destroy()
            pygame.display.flip()
    
        apply_button = tk.Button(input_window, text="OK", command=apply_changes)
        apply_button.pack()
        input_window.mainloop()



#######################################################################################

    
    def handle_event(self, event):
        self.update_position()
        """Обрабатывает события мыши для перетаскивания или клика правой кнопкой."""
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Проверяем, нажата ли левая кнопка мыши и находится ли курсор внутри виджета
            if event.button == 1 and self.rect.collidepoint(mouse_x, mouse_y):
                self.is_dragging = True
                self.offset_x = mouse_x - self.x
                self.offset_y = mouse_y - self.y
                
            elif self.toolbar and event.button == 1 and any(button.rect.collidepoint(event.pos) for button in self.toolbar.buttons):
                for button in self.toolbar.buttons:
                    if button.rect.collidepoint(event.pos):
                        button.on_click()
                        self.update_position()
                        return
            elif self.toolbar and self.toolbar.sub_toolbar.isdrawn and event.button == 1 and any(button.rect.collidepoint(event.pos) for button in self.toolbar.sub_toolbar.buttons):
                for button in self.toolbar.sub_toolbar.buttons:
                    if button.rect.collidepoint(event.pos):
                        button.on_click()
                        self.update_position()
                        return
            
            elif event.button == 3 and self.rect.collidepoint(mouse_x, mouse_y):
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.open_stat_adjustment_window()
                else:
                    if self.toolbar:
                        self.toolbar = None
                        self.update_position()
                    else:
                        # Создаём тулбар на текущей позиции виджета
                        toolbar_x = self.x + self.diameter + 10  # Смещение справа от виджета
                        toolbar_y = self.y
                        self.toolbar = Toolbar(self, self.entity, toolbar_x, toolbar_y, self.diameter, self.spell_widgets)
                        self.update_position()
                return
    
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_x, mouse_y = event.pos
                self.x = mouse_x - self.offset_x
                self.y = mouse_y - self.offset_y
                self.rect.topleft = (self.x, self.y)
                self.update_toolbar_position()

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_dragging:
                mouse_x, mouse_y = event.pos
                self.map_manager.remove_entity_by_value(self.entity)
                if event.button == 1 and self.rect.collidepoint(mouse_x, mouse_y):
                    self.snap_to_cell(mouse_x, mouse_y)
                    self.update_position()
                    self.update_toolbar_position()
                self.is_dragging = False


                


        