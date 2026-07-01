from dataclasses import dataclass, field
from uuid import uuid4
from engine.session_state import SessionState
from utility.exceptions import TableValidationError

@dataclass
class Table:
    name: str
    master_user_id: str

    id: str = field(default_factory=lambda: str(uuid4()))

    players: list = field(default_factory=list)
    entity_ids: list = field(default_factory=list)

    logs: list = field(default_factory=list)

    session: SessionState = field(
        default_factory=SessionState
    )

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TableValidationError(
                "Nome da mesa inválido."
            )

        self.name = self.name.strip()

        if self.name == "":
            raise TableValidationError(
                "A mesa precisa ter um nome."
            )

        if not isinstance(self.master_user_id, str):
            raise TableValidationError(
                "ID de mestre inválido."
            )

        if self.master_user_id.strip() == "":
            raise TableValidationError(
                "A mesa precisa de um mestre."
            )

    def add_player(self, player):
        for existing_player in self.players:
            if existing_player["id"] == player.id:
                return

        self.players.append({
            "id": player.id,
            "username": player.username
        })

    def remove_player(self, player_id):
        self.players = [
            player
            for player in self.players
            if player["id"] != player_id
        ]

    def add_entity(self, entity):
        if entity.id not in self.entity_ids:
            self.entity_ids.append(entity.id)

    def remove_entity(self, entity_id):
        self.entity_ids = [
            existing_entity_id
            for existing_entity_id in self.entity_ids
            if existing_entity_id != entity_id
        ]

    def add_log(self, message):
        if not isinstance(message, str):
            return

        message = message.strip()

        if message:
            self.logs.append(message)

    def clear_logs(self):
        self.logs.clear()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "master_user_id": self.master_user_id,
            "players": self.players,
            "entity_ids": self.entity_ids,
            "logs": self.logs,
            "session": self.session.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        try:
            table = cls(
                id=data["id"],
                name=data["name"],
                master_user_id=data["master_user_id"]
            )
        except KeyError as error:
            raise TableValidationError(
                f"Campo ausente na mesa: {error}"
            )

        table.players = data.get(
            "players",
            []
        )

        table.entity_ids = data.get(
            "entity_ids",
            []
        )

        table.logs = data.get(
            "logs",
            []
        )

        session_data = data.get(
            "session"
        )

        if session_data:
            table.session = SessionState.from_dict(
                session_data
            )

        return table

    def __str__(self):
        return (
            f"Mesa '{self.name}' | "
            f"Players: {len(self.players)} | "
            f"Entities: {len(self.entity_ids)}"
        )

    def __repr__(self):
        return (
            f"Table("
            f"name='{self.name}', "
            f"players={len(self.players)}, "
            f"entities={len(self.entity_ids)}"
            f")"
        )