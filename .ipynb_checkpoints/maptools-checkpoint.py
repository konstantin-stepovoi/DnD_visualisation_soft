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
