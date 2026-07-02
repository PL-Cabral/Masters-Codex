from dataclasses import dataclass, field

from core.entity import Entity, AttributeValidationError

@dataclass
class NPC(Entity):
    # Atributos próprios do NPC
    story_role: str = "commoner"
    friendly: bool = True

    # Falas públicas que podem aparecer para os jogadores
    dialogue_lines: list = field(default_factory=list)

    # Informação reservada para o mestre
    master_notes: str = ""

    @property
    def entity_type(self):
        return "npc"

    # Valida os dados do NPC depois de validar os dados da Entity
    def __post_init__(self):
        super().__post_init__()

        self.story_role = self.story_role.strip().lower()

        if self.story_role == "":
            raise AttributeValidationError(
                "A função narrativa do NPC não pode ser vazia.")

        if not isinstance(self.friendly, bool):
            raise AttributeValidationError(
                "O campo friendly precisa ser verdadeiro ou falso.")

    # Ação narrativa simples do NPC
    def perform_action(self, action_name="Interação", dice_result=0):
        self.validate_can_act()

        if self.friendly:
            behavior = "amigável"
            message = f"{self.name} realizou {action_name} de forma amigável."
        else:
            behavior = "hostil"
            message = f"{self.name} realizou {action_name} de forma hostil ou desconfiada."

        return {
            "entity_id": self.id,
            "entity_name": self.name,
            "entity_type": self.entity_type,
            "action_name": action_name,
            "behavior": behavior,
            "dice_result": dice_result,
            "message": message,
        }

    # Mostra apenas informações narrativas do NPC
    def show_details(self):
        text = f"Nome: {self.name}\n"
        text += "Tipo: NPC\n"
        text += f"Função na história: {self.story_role}\n"
        text += f"Amigável: {'Sim' if self.friendly else 'Não'}\n"

        text += "\nFalas conhecidas:\n"

        if len(self.dialogue_lines) == 0:
            text += "- Nenhuma fala cadastrada.\n"
        else:
            for line in self.dialogue_lines:
                text += f"- {line}\n"

        return text

    def add_dialogue_line(self, line):
        line = line.strip()

        if line == "":
            raise AttributeValidationError("A fala do NPC não pode ser vazia.")

        self.dialogue_lines.append(line)

    def remove_dialogue_line(self, line):
        line = line.strip().lower()

        self.dialogue_lines = [
            dialogue
            for dialogue in self.dialogue_lines
            if dialogue.strip().lower() != line
        ]

    def set_friendly(self, value):
        if not isinstance(value, bool):
            raise AttributeValidationError(
                "O valor de friendly precisa ser verdadeiro ou falso.")

        self.friendly = value

    # Mostra informações completas para o mestre
    def show_master_details(self):
        text = self.show_details()

        text += "\nInformações do mestre:\n"
        text += f"HP: {self.current_hp}/{self.max_hp}\n"
        text += f"Nível: {self.level}\n"

        if self.master_notes != "":
            text += f"Notas secretas: {self.master_notes}\n"
        else:
            text += "Notas secretas: Nenhuma.\n"

        return text

    # Transforma o NPC em dicionário para salvar em JSON/Firebase
    def to_dict(self):
        data = super().to_dict()

        data.update({
            "story_role": self.story_role,
            "friendly": self.friendly,
            "dialogue_lines": self.dialogue_lines,
            "master_notes": self.master_notes,
        })

        return data

    # Cria um NPC a partir de um dicionário salvo
    @classmethod
    def from_dict(cls, data):
        base_fields = Entity.get_base_fields(data)

        return cls(
            **base_fields,
            story_role=data.get("story_role", "commoner"),
            friendly=data.get("friendly", True),
            dialogue_lines=data.get("dialogue_lines", []),
            master_notes=data.get("master_notes", ""),
        )