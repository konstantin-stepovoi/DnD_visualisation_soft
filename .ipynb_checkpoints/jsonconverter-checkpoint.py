import json

def convert_txt_to_json(txt_file_path, json_file_path):
    # Чтение данных из текстового файла
    with open(txt_file_path, 'r') as txt_file:
        lines = txt_file.readlines()

    # Преобразование строк в формат JSON
    entities = []
    current_entity = {}
    for line in lines:
        line = line.strip()
        
        # Пропускаем пустые строки или строки, которые не содержат ":"
        if not line or ':' not in line:
            continue
        
        if line.startswith('{'):
            current_entity = {}
        elif line.startswith('}'):
            # Завершение текущего объекта
            entities.append(current_entity)
        else:
            # Разделение строки на ключ и значение
            key, value = line.split(':', 1)
            key = key.strip().strip('"').strip()
            value = value.strip().strip('"').strip()
            current_entity[key] = value

    # Сохранение данных в JSON файл
    with open(json_file_path, 'w') as json_file:
        json.dump(entities, json_file, indent=4)
# Пример использования:
# Замените 'players.txt' на путь к вашему текстовому файлу
txt_file_path =  input('txt name: ')
json_file_path = input('json name: ')

convert_txt_to_json(txt_file_path, json_file_path)
