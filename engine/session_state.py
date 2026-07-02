from dataclasses import dataclass, field
from utility.exceptions import TableValidationError

@dataclass
class SessionState:
    # Estado atual da sessão
    state: str = "lobby"

    # Ordem de combate
    initiative_order: list = field(default_factory=list)

    # Índice do turno atual
    current_turn_index: int = 0

    def __post_init__(self):
        valid_states = [
            "lobby",
            "exploration",
            "combat",
            "paused",
            "ended"
        ]

        if self.state not in valid_states:
            raise TableValidationError(
                "Estado de sessão inválido."
            )

    # Alterar estado da sessão
    def change_state(self, new_state):
        valid_states = [
            "lobby",
            "exploration",
            "combat",
            "paused",
            "ended"
        ]

        if new_state not in valid_states:
            raise TableValidationError(
                "Estado de sessão inválido."
            )

        self.state = new_state

    # Iniciar combate
    def start_combat(self, initiative_order):
        if not initiative_order:
            raise TableValidationError(
                "Combate precisa de ordem de iniciativa."
            )

        self.initiative_order = initiative_order
        self.current_turn_index = 0
        self.state = "combat"

    # Retorna quem está no turno atual
    def get_current_turn_entity(self):
        if not self.initiative_order:
            return None

        return self.initiative_order[
            self.current_turn_index
        ]

    # Avançar turno
    def next_turn(self):
        if not self.initiative_order:
            return None

        self.current_turn_index += 1

        if self.current_turn_index >= len(self.initiative_order):
            self.current_turn_index = 0

        return self.get_current_turn_entity()

    def to_dict(self):
        return {
            "state": self.state,
            "initiative_order": self.initiative_order,
            "current_turn_index": self.current_turn_index
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            state=data.get("state", "lobby"),
            initiative_order=data.get(
                "initiative_order", []
            ),
            current_turn_index=data.get(
                "current_turn_index", 0
            )
        )

    def __str__(self):
        return (
            f"SessionState("
            f"state='{self.state}'"
            f")"
        )