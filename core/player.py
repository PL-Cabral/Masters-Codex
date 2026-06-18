from dataclasses import dataclass, field

from entity import Entity, AttributeValidationError


# Lista dos 6 atributos básicos de D&D
ABILITY_NAMES = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]

# Valores padrão caso o jogador seja criado sem atributos
DEFAULT_ATTRIBUTES = {
    "strength": 10,
    "dexterity": 10,
    "constitution": 10,
    "intelligence": 10,
    "wisdom": 10,
    "charisma": 10,
}

# Raças disponíveis na versão simples do sistema
# Cada raça concede alguns bônus nos atributos
RACE_BONUSES = {
    "human": {
        "strength": 1,
        "dexterity": 1,
        "constitution": 1,
        "intelligence": 1,
        "wisdom": 1,
        "charisma": 1,
    },
    "elf": {
        "dexterity": 2,
        "intelligence": 1,
    },
    "dwarf": {
        "constitution": 2,
        "strength": 1,
    },
}

# Classes disponíveis
ALLOWED_CLASSES = [
    "fighter",
    "wizard",
    "cleric",
    "rogue",
    "barbarian",
]

@dataclass
class Player(Entity):
    # Atributos próprios do jogador
    character_class: str = "fighter"
    race: str = "human"
    xp: int = 0

    inventory: list = field(default_factory=list)

    @property
    def entity_type(self):
        return "player"

    # Valida os dados do Player depois de validar os dados da Entity
    def __post_init__(self):
        super().__post_init__()

        self.character_class = self.character_class.strip().lower()
        self.race = self.race.strip().lower()

        if self.character_class not in ALLOWED_CLASSES:
            raise AttributeValidationError("Classe inválida.")

        if self.race not in RACE_BONUSES:
            raise AttributeValidationError("Raça inválida.")

        if self.xp < 0:
            raise AttributeValidationError("O XP não pode ser negativo.")

        self.prepare_attributes()

        # Se o jogador ainda não tiver habilidades,
        # recebe automaticamente as habilidades da classe escolhida.
        if len(self.skills) == 0:
            self.add_class_skills()

    # Garante que todos os atributos básicos existem e são válidos
    def prepare_attributes(self):
        for ability_name, default_value in DEFAULT_ATTRIBUTES.items():
            if ability_name not in self.attributes:
                self.attributes[ability_name] = default_value

        for ability_name, value in self.attributes.items():
            if ability_name not in ABILITY_NAMES:
                raise AttributeValidationError(
                    f"Atributo inválido: {ability_name}")

            if not isinstance(value, int):
                raise AttributeValidationError(
                    f"O atributo {ability_name} precisa ser um número inteiro."
                )

            if value < 1 or value > 30:
                raise AttributeValidationError(
                    f"O atributo {ability_name} precisa estar entre 1 e 30."
                )

        self.apply_race_bonus()

    # Aplica os bônus da raça nos atributos do personagem
    def apply_race_bonus(self):
        race_bonus = RACE_BONUSES[self.race]

        for ability_name, bonus in race_bonus.items():
            self.attributes[ability_name] += bonus

            if self.attributes[ability_name] > 30:
                self.attributes[ability_name] = 30

    # Adiciona as 5 habilidades da classe escolhida
    def add_custom_skill(self, skill_name, description=""):
        skill_name = skill_name.strip()
        description = description.strip()

        if skill_name == "":
            raise AttributeValidationError("A habilidade precisa ter um nome.")

        skill = {
            "name": skill_name,
            "description": description,
        }

        self.add_skill(skill)

    # Calcula o modificador de atributo no estilo D&D
    # Ex: atributo 10 = 0, atributo 14 = +2, atributo 8 = -1
    def get_ability_modifier(self, ability_name):
        ability_name = ability_name.strip().lower()

        if ability_name not in ABILITY_NAMES:
            raise AttributeValidationError(
                f"Atributo inválido: {ability_name}")

        score = self.attributes[ability_name]

        return (score - 10) // 2

    # Ação baseada em uma rolagem de dado + modificador de atributo
    def perform_action(self, action_name="Ação", ability_name="strength", dice_result=0):
        self.validate_can_act()

        ability_name = ability_name.strip().lower()

        if ability_name not in ABILITY_NAMES:
            raise AttributeValidationError(
                f"Atributo inválido: {ability_name}")

        modifier = self.get_ability_modifier(ability_name)
        total = dice_result + modifier

        return {
            "entity_id": self.id,
            "entity_name": self.name,
            "entity_type": self.entity_type,
            "action_name": action_name,
            "ability_name": ability_name,
            "dice_result": dice_result,
            "modifier": modifier,
            "total": total,
            "message": f"{self.name} realizou {action_name} usando {ability_name} e obteve total {total}.",
        }

    # Mostra os detalhes principais da ficha do jogador
    def show_details(self):
        text = f"Nome: {self.name}\n"
        text += "Tipo: Jogador\n"
        text += f"Classe: {self.character_class}\n"
        text += f"Raça: {self.race}\n"
        text += f"Nível: {self.level}\n"
        text += f"XP: {self.xp}\n"
        text += f"HP: {self.current_hp}/{self.max_hp}\n"

        text += "\nAtributos:\n"

        for ability_name in ABILITY_NAMES:
            score = self.attributes[ability_name]
            modifier = self.get_ability_modifier(ability_name)

            if modifier >= 0:
                modifier_text = f"+{modifier}"
            else:
                modifier_text = str(modifier)

            text += f"- {ability_name}: {score} ({modifier_text})\n"

        text += "\nHabilidades de classe:\n"

        if len(self.skills) == 0:
            text += "- Nenhuma habilidade cadastrada.\n"
        else:
            for skill in self.skills:
                text += f"- {skill.get('name')}\n"

        text += "\nInventário:\n"

        if len(self.inventory) == 0:
            text += "- Inventário vazio.\n"
        else:
            for item in self.inventory:
                text += f"- {item}\n"

        if self.notes != "":
            text += f"\nNotas:\n{self.notes}\n"

        return text

    def add_item(self, item):
        item = item.strip()

        if item == "":
            raise AttributeValidationError("O item não pode ter nome vazio.")

        self.inventory.append(item)

    def remove_item(self, item_name):
        item_name = item_name.strip().lower()

        self.inventory = [
            item
            for item in self.inventory
            if item.strip().lower() != item_name
        ]

    def gain_xp(self, amount):
        if amount < 0:
            raise AttributeValidationError(
                "A quantidade de XP ganho não pode ser negativa.")

        self.xp += amount

    # Transforma o Player em dicionário para salvar em JSON/Firebase
    def to_dict(self):
        data = super().to_dict()

        data.update({
            "character_class": self.character_class,
            "race": self.race,
            "xp": self.xp,
            "inventory": self.inventory,
        })

        return data

    # Cria um Player a partir de um dicionário salvo
    @classmethod
    def from_dict(cls, data):
        base_fields = Entity.get_base_fields(data)

        return cls(
            **base_fields,
            character_class=data.get("character_class", "fighter"),
            race=data.get("race", "human"),
            xp=data.get("xp", 0),
            inventory=data.get("inventory", []),
        )