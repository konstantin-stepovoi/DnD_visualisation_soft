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
    # Загружаем игроков и монстров
    players_entities = EntityManager.load_from_json(game.players_path)
    monsters_entities = EntityManager.load_from_json(game.monsters_path)
    
    return map_image, players_entities, monsters_entities, num_tiles

