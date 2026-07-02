from dataclasses import dataclass
from core.users.user import User
from utility.exceptions import UserValidationError

@dataclass
class PlayerUser(User):
    # ID da entidade/ficha controlada pelo jogador
    linked_entity_id: str = None

    def __post_init__(self):
        # Executa validações da classe User primeiro
        super().__post_init__()

        if self.linked_entity_id is not None:
            self.linked_entity_id = self.linked_entity_id.strip()

            if self.linked_entity_id == "":
                raise UserValidationError(
                    "O ID da entidade não pode ser vazio."
                )

    @property
    def user_type(self):
        return "player"

    def access_panel(self):
        return {
            "user_id": self.id,
            "username": self.username,
            "panel": "player_panel",
            "permissions": [
                "view_character",
                "roll_dice",
                "edit_own_notes"
            ]
        }

    # Vincular uma ficha ao jogador
    def link_entity(self, entity_id):
        entity_id = entity_id.strip()

        if entity_id == "":
            raise UserValidationError(
                "O ID da entidade não pode ser vazio."
            )

        self.linked_entity_id = entity_id

    # Desvincular ficha
    def unlink_entity(self):
        self.linked_entity_id = None

    def to_dict(self):
        data = super().to_dict()

        data["linked_entity_id"] = self.linked_entity_id

        return data

    @classmethod
    def from_dict(cls, data):
        fields = cls.get_base_fields(data)
        fields["linked_entity_id"] = data.get("linked_entity_id")

        return cls(**fields)

    def __str__(self):
        return (
            f"{self.username} "
            f"(player) - "
            f"Entity: {self.linked_entity_id}"
        )