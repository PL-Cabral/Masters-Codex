from dataclasses import dataclass

from core.entity import Entity, AttributeValidationError


# Atributos usados também pelos monstros
ABILITY_NAMES = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]

# Valores padrão caso o monstro seja criado sem atributos
DEFAULT_ATTRIBUTES = {
    "strength": 10,
    "dexterity": 10,
    "constitution": 10,
    "intelligence": 10,
    "wisdom": 10,
    "charisma": 10,
}

# Tipos de dano
DAMAGE_TYPES = [
    "slashing",
    "piercing",
    "bludgeoning",
    "fire",
    "cold",
    "poison",
    "necrotic",
    "radiant",
]


@dataclass
class Monster(Entity):
    # Atributos próprios do monstro
    threat_level: int = 1
    natural_damage_type: str = "slashing"
    armor_class: int = 10
    monster_type: str = "beast"

    @property
    def entity_type(self):
        return "monster"

    # Valida os dados do Monster depois de validar os dados da Entity
    def __post_init__(self):
        super().__post_init__()

        self.natural_damage_type = self.natural_damage_type.strip().lower()
        self.monster_type = self.monster_type.strip().lower()

        if self.threat_level < 1 or self.threat_level > 5:
            raise AttributeValidationError(
                "O nível de ameaça do monstro precisa estar entre 1 e 5."
            )

        if self.natural_damage_type not in DAMAGE_TYPES:
            raise AttributeValidationError("Tipo de dano inválido.")

        if self.armor_class <= 0:
            raise AttributeValidationError(
                "A classe de armadura precisa ser maior que zero."
            )

        if self.monster_type == "":
            raise AttributeValidationError(
                "O tipo do monstro não pode ser vazio.")

        self.prepare_attributes()

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

    # Calcula o modificador de atributo no estilo D&D
    # Exemplo: atributo 10 = 0, atributo 14 = +2, atributo 8 = -1
    def get_ability_modifier(self, ability_name):
        ability_name = ability_name.strip().lower()

        if ability_name not in ABILITY_NAMES:
            raise AttributeValidationError(
                f"Atributo inválido: {ability_name}")

        score = self.attributes[ability_name]

        return (score - 10) // 2

    # Bônus baseado no nível de ameaça do monstro
    def get_attack_bonus(self):
        return self.threat_level + 1

    # Ação ataque: dado + bônus de ameaça
    def perform_action(self, action_name="Ataque natural", dice_result=0):
        self.validate_can_act()

        attack_bonus = self.get_attack_bonus()
        total = dice_result + attack_bonus

        return {
            "entity_id": self.id,
            "entity_name": self.name,
            "entity_type": self.entity_type,
            "action_name": action_name,
            "dice_result": dice_result,
            "attack_bonus": attack_bonus,
            "total": total,
            "damage_type": self.natural_damage_type,
            "message": f"{self.name} realizou {action_name} e obteve total {total}.",
        }

    # Mostra os detalhes principais do monstro
    def show_details(self):
        text = f"Nome: {self.name}\n"
        text += "Tipo: Monstro\n"
        text += f"Categoria: {self.monster_type}\n"
        text += f"Nível: {self.level}\n"
        text += f"Nível de ameaça: {self.threat_level}\n"
        text += f"HP: {self.current_hp}/{self.max_hp}\n"
        text += f"CA: {self.armor_class}\n"
        text += f"Tipo de dano natural: {self.natural_damage_type}\n"
        text += f"Bônus de ataque: +{self.get_attack_bonus()}\n"

        text += "\nAtributos:\n"

        for ability_name in ABILITY_NAMES:
            score = self.attributes[ability_name]
            modifier = self.get_ability_modifier(ability_name)

            if modifier >= 0:
                modifier_text = f"+{modifier}"
            else:
                modifier_text = str(modifier)

            text += f"- {ability_name}: {score} ({modifier_text})\n"

        text += "\nCondições:\n"

        if len(self.conditions) == 0:
            text += "- Nenhuma condição ativa.\n"
        else:
            for condition in self.conditions:
                text += f"- {condition}\n"

        if self.notes != "":
            text += f"\nNotas:\n{self.notes}\n"

        return text

    # Transforma o Monster em dicionário para salvar em JSON/Firebase
    def to_dict(self):
        data = super().to_dict()

        data.update({
            "threat_level": self.threat_level,
            "natural_damage_type": self.natural_damage_type,
            "armor_class": self.armor_class,
            "monster_type": self.monster_type,
        })

        return data

    # Cria um Monster a partir de um dicionário salvo
    @classmethod
    def from_dict(cls, data):
        base_fields = Entity.get_base_fields(data)

        return cls(
            **base_fields,
            threat_level=data.get("threat_level", 1),
            natural_damage_type=data.get("natural_damage_type", "slashing"),
            armor_class=data.get("armor_class", 10),
            monster_type=data.get("monster_type", "beast"),
        )