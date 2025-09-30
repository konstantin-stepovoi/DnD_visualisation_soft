import pygame
from Gameclass import Game, load_game_assets
import Gameclass
import maptools
from EntityWidgets import EntityWidget
import EntityWidgets
from SpellWidgets import BowSpell, LinearSpell, CircularSpell, TriangleSpell

class Button:
    def __init__(self, x, y, width, height, text, font, color, text_color, action=None, hotkey=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color
        self.action = action
        self.hotkey = hotkey  # Горячая клавиша (по умолчанию None)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        # Клик мышью
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

        # Нажатие горячей клавиши (только для этой кнопки)
        if event.type == pygame.KEYDOWN and event.key == self.hotkey:
            if self.action:
                self.action()

pygame.init()
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("RaDnDom fight visualiser")

game = Game()
map_image, players, monsters, num_tiles, map_type = load_game_assets(game)
print(map_type)
print(Gameclass.CURRENT_COLOR_PRESET)
Gameclass.set_color_preset(map_type)  # Устанавливаем нужный пресет
print(Gameclass.CURRENT_COLOR_PRESET)

screen_width, screen_height = screen.get_size()
left_top, right_bottom, scaled_width, scaled_height = maptools.get_scaled_image_properties(
    map_image, screen_width, screen_height
)
rows, cols = num_tiles, num_tiles
tile_width = scaled_width // cols
tile_height = scaled_height // rows
corrected_width = tile_width * cols
corrected_height = tile_height * rows
map_image_surface = pygame.image.fromstring(map_image.tobytes(), map_image.size, map_image.mode)
scaled_image_surface = pygame.transform.scale(map_image_surface, (corrected_width, corrected_height))

grid = maptools.create_grid(
    rows, cols,
    cell_width=scaled_width // cols,
    cell_height=scaled_height // rows,
    start_x=left_top[0],
    start_y=left_top[1],
    total_width=corrected_width,
    total_height=corrected_height
)

map_manager = maptools.MapManager(grid)

hero_widgets = []
monster_widgets = []
widget_diameter = grid[0][0].rect.width 
hero_start_x = left_top[0] + corrected_width + 40
hero_start_y = left_top[1] + 100
monster_start_x = left_top[0] - widget_diameter - 40
monster_start_y = left_top[1] + 100
widget_spacing = widget_diameter + 20
x, y, cell_size = 0, 0, scaled_width // cols
spell_widgets = [BowSpell(screen, x, y, cell_size, map_manager), LinearSpell(screen, x, y, cell_size, map_manager), 
                 CircularSpell(screen, x, y, cell_size, map_manager), TriangleSpell(screen, x, y, cell_size, map_manager)]

for i, hero in enumerate(players):
    widget_x = hero_start_x
    widget_y = hero_start_y + i * widget_spacing
    hero_widgets.append(EntityWidget(hero, widget_diameter, widget_x, widget_y, widget_diameter, map_manager, screen, spell_widgets))

for i, monster in enumerate(monsters):
    widget_x = monster_start_x
    widget_y = monster_start_y + i * widget_spacing
    monster_widgets.append(EntityWidget(monster, widget_diameter, widget_x, widget_y, widget_diameter, map_manager, screen, spell_widgets))
all_fighters = players + monsters

initiative_manager = maptools.InitiativeManager(map_manager, all_fighters)

all_widgets = hero_widgets + monster_widgets + spell_widgets
entity_widgets = all_widgets
print(monster_widgets)

hotkeys = list("qwertyuiopasdfghjklzxcvbnm")

for widget, key in zip(monster_widgets, hotkeys):
    widget.entity.hotkey = key
print([widget.entity.hotkey for widget in monster_widgets])


def recalculate_damage():
    for widget in entity_widgets:
        if isinstance(widget, EntityWidget):
            widget.get_damage()
    pygame.display.flip()
    map_manager.reset_damage()

font = pygame.font.Font(None, 36)
button_width, button_height = 200, 50
button_x = screen_width - button_width - 20
button_y = screen_height - button_height - 20

recalculate_button = Button(
    x=button_x, 
    y=button_y, 
    width=button_width, 
    height=button_height, 
    text="Recalc Damage", 
    font=font, 
    color=Gameclass.CURRENT_COLOR_PRESET.button_fill, 
    text_color=Gameclass.CURRENT_COLOR_PRESET.button_font, 
    action=recalculate_damage, 
    hotkey=pygame.K_TAB  # Только эта кнопка будет реагировать на TAB
)

small_button_width = (button_width - 20) // 3
small_button_x = button_x
small_button_y = button_y - button_height - 10

prev_button = Button(small_button_x, small_button_y, small_button_width, button_height, 
                     "<=", font, Gameclass.CURRENT_COLOR_PRESET.button_fill, Gameclass.CURRENT_COLOR_PRESET.button_font, lambda: initiative_manager.update_current_index())
roll_button = Button(small_button_x + small_button_width + 10, small_button_y, small_button_width, button_height, 
                     "Roll I", font, Gameclass.CURRENT_COLOR_PRESET.button_fill, Gameclass.CURRENT_COLOR_PRESET.button_font, initiative_manager.set_initiatives)
next_button = Button(small_button_x + 2 * (small_button_width + 10), small_button_y, small_button_width, button_height, 
                     "=>", font, Gameclass.CURRENT_COLOR_PRESET.button_fill, Gameclass.CURRENT_COLOR_PRESET.button_font, lambda: initiative_manager.gowngrade_current_index())

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            for widget in monster_widgets:
                #print(event.unicode)
                if event.unicode == widget.entity.hotkey:
                    widget.is_active = not widget.is_active
                    pygame.display.flip()

        recalculate_button.handle_event(event)
        prev_button.handle_event(event)
        roll_button.handle_event(event)
        next_button.handle_event(event)

        for widget in entity_widgets:
            widget.handle_event(event)

    screen.fill((100, 100, 100))
    screen.blit(scaled_image_surface, left_top)

    for row in grid:
        for cell in row:
            if cell.is_hovered(mouse_pos):
                cell.draw(screen, border_color=(255, 255, 255), fill_color=(255, 255, 255, 80))
            else:
                cell.draw(screen, border_color=(255, 255, 255), fill_color=(0, 0, 0, 50))

        # Отрисовка виджетов
    for widget in all_widgets:
        if isinstance(widget, BowSpell) and widget.visible:  
            mx, my = pygame.mouse.get_pos()
            widget.draw(mx, my)
        elif isinstance(widget, LinearSpell) and widget.visible:  
            mx, my = pygame.mouse.get_pos()
            widget.draw(mx, my)
        elif isinstance(widget, TriangleSpell) and widget.visible:  
            mx, my = pygame.mouse.get_pos()
            widget.draw(mx, my)
        elif isinstance(widget, CircularSpell) and widget.visible:  
            mx, my = pygame.mouse.get_pos()
            widget.draw(mx, my)
        else:
            try:
                widget.draw(screen)
            except TypeError:
                ...

    if initiative_manager.initiatives_set:
        initiative_manager.draw_current_entity_rect(screen)
    
    prev_button.draw(screen)
    roll_button.draw(screen)
    next_button.draw(screen)
    recalculate_button.draw(screen)
    pygame.display.flip()

pygame.quit()
