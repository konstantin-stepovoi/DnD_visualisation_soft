import json

class Entity:
    def __init__(self, name, hp, armor_class, step_size, entity_type, avatar, death_avatar):
        self.name = name
        self.hp = hp
        self.armor_class = armor_class
        self.step_size = step_size
        self.entity_type = entity_type
        self.avatar = avatar
        self.pos = (0, 0)
        self.initiative = 0
        self.death_avatar = death_avatar
        self.hotkey = None

def load_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    entities = []
    for entity_data in data:
        name = entity_data['name']
        hp = entity_data['hp']
        armor_class = entity_data['armor_class']
        step_size = entity_data.get('step_size', 1)  
        entity_type = entity_data['entity_type']
        avatar = entity_data['avatar_path']
        death_avatar = entity_data['death_avatar']
        entity = Entity(name, hp, armor_class, step_size, entity_type, avatar, death_avatar)
        entities.append(entity)
    return entities
