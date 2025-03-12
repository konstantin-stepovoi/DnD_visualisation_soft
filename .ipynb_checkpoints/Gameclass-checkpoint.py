import tkinter as tk
from tkinter import filedialog, messagebox
import json
from PIL import Image
import EntityManager

class Game:
    def __init__(self):
        """Инициализация атрибутов игры."""
        self.title = ""
        self.map_path = ""
        self.players_path = ""
        self.monsters_path = ""
        self.map_type = ""
        self.num_tiles = 0

        # Вызов окна для выбора JSON-файла битвы
        self.load_game_from_json()

    def load_game_from_json(self):
        """Открыть окно для выбора JSON-файла битвы и загрузить данные."""
        root = tk.Tk()
        root.withdraw()  # Скрываем основное окно Tkinter

        # Открываем диалог для выбора JSON-файла
        file_path = filedialog.askopenfilename(
            title="Выберите JSON-файл битвы",
            filetypes=[("JSON Files", "*.json")]
        )

        if not file_path:
            messagebox.showerror("Ошибка", "Файл не выбран. Игра не создана.")
            return

        try:
            # Загружаем данные из выбранного JSON-файла
            with open(file_path, 'r') as file:
                data = json.load(file)

            # Заполняем атрибуты экземпляра игры
            self.title = data.get("title", "Без названия")
            self.map_path = data.get("map_path", "")
            self.players_path = data.get("players_path", "")
            self.monsters_path = data.get("monsters_path", "")
            self.num_tiles = data.get("num_tiles", 2)
            self.map_type = data.get("map_type", "")

            # Выводим подтверждение
            messagebox.showinfo("Успех", f"Игра '{self.title}' успешно загружена!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить игру: {e}")

        finally:
            root.destroy()

    def __repr__(self):
        """Отображение информации об игре."""
        return (f"Game(title={self.title}, "
                f"map_path={self.map_path}, "
                f"players_path={self.players_path}, "
                f"monsters_path={self.monsters_path})")


def load_game_assets(game):
    try:
        map_image = Image.open(game.map_path)
    except Exception as e:
        raise FileNotFoundError(f"Не удалось загрузить карту по пути {game.map_path}: {e}")

    num_tiles = game.num_tiles
    map_type = game.map_type
    # Загружаем игроков и монстров
    players_entities = EntityManager.load_from_json(game.players_path)
    monsters_entities = EntityManager.load_from_json(game.monsters_path)
    
    return map_image, players_entities, monsters_entities, num_tiles, map_type


class ColorPreset:
    def __init__(self, ava_border, hp_fill, hp_border, armor_border, initiative, widget_font):
        self.ava_border = ava_border
        self.hp_fill = hp_fill
        self.hp_border = hp_border
        self.armor_border = armor_border
        self.initiative = initiative
        self.widget_font = widget_font
        self.button_fill = (50, 50, 50, 255)
        self.button_border = (200, 200, 200, 255)
        self.button_font = (255, 255, 255, 255)
        self.monster_spells_fill = (255, 165, 0, 100)
        self.monster_spells_border = (255, 69, 0, 255)
        self.player_spells_border = (0, 255, 255, 150)
        self.player_spells_fill = (0, 255, 255, 10)

# --- Словарь пресетов ---
COLOR_PRESETS = {
    "forest": ColorPreset(
        ava_border=(34, 139, 34, 255),  # Тёмно-зелёный
        hp_fill=(0, 128, 0, 200),       # Зелёный
        hp_border=(0, 255, 0, 255),     # Ярко-зелёный
        armor_border=(139, 69, 19, 255),  # Коричневый
        initiative=(255, 215, 0, 255),  # Золотой
        widget_font=(255, 255, 255, 255)  # Белый
    ),
    "duna": ColorPreset(
        ava_border=(210, 180, 140, 255),  # Тан
        hp_fill=(255, 215, 0, 200),  # Золотой
        hp_border=(218, 165, 32, 255),  # Золотистый
        armor_border=(139, 69, 19, 255),  # Коричневый
        initiative=(205, 133, 63, 255),  # Персиковый
        widget_font=(0, 0, 0, 255)  # Чёрный
    ),
    "snowy": ColorPreset(
        ava_border=(176, 224, 230, 255),  # Голубой ледяной
        hp_fill=(135, 206, 250, 200),  # Светло-голубой
        hp_border=(70, 130, 180, 255),  # Стальной синий
        armor_border=(100, 100, 100, 255),  # Серый
        initiative=(255, 255, 255, 255),  # Белый
        widget_font=(0, 0, 0, 255)  # Чёрный
    ),
    "cave": ColorPreset(
        ava_border=(105, 105, 105, 255),  # Тёмно-серый
        hp_fill=(169, 169, 169, 200),  # Серый
        hp_border=(211, 211, 211, 255),  # Светло-серый
        armor_border=(47, 79, 79, 255),  # Тёмно-бирюзовый
        initiative=(255, 69, 0, 255),  # Красный
        widget_font=(255, 255, 255, 255)  # Белый
    ),
    "dunge": ColorPreset(
        ava_border=(128, 0, 0, 255),  # Тёмно-красный
        hp_fill=(139, 0, 0, 200),  # Тёмно-бордовый
        hp_border=(255, 0, 0, 255),  # Красный
        armor_border=(105, 105, 105, 255),  # Тёмно-серый
        initiative=(255, 140, 0, 255),  # Оранжевый
        widget_font=(255, 255, 255, 255)  # Белый
    ),
    "indoor": ColorPreset(
        ava_border=(169, 169, 169, 255),  # Светло-серый
        hp_fill=(192, 192, 192, 200),  # Серебристый
        hp_border=(220, 220, 220, 255),  # Белёсый
        armor_border=(128, 128, 128, 255),  # Серый
        initiative=(0, 0, 255, 255),  # Синий
        widget_font=(0, 0, 0, 255)  # Чёрный
    )
}

# --- Глобальная переменная для хранения текущего пресета ---
CURRENT_COLOR_PRESET = None

def set_color_preset(preset_name):
    """Устанавливает текущий цветовой пресет"""
    global CURRENT_COLOR_PRESET
    if preset_name in COLOR_PRESETS:
        CURRENT_COLOR_PRESET = COLOR_PRESETS[preset_name]
    else:
        raise ValueError(f"Пресет '{preset_name}' не найден!")



