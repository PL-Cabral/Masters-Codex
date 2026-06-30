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
    entities: list = field(default_factory=list)

    logs: list = field(default_factory=list)

    session: SessionState = field(
        default_factory=SessionState
    )

    def __post_init__(self):
        self.name = self.name.strip()

        if self.name == "":
            raise TableValidationError(
                "A mesa precisa ter um nome."
            )

        if not self.master_user_id:
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
        for existing_entity in self.entities:
            if existing_entity["id"] == entity.id:
                return

        self.entities.append({
            "id": entity.id,
            "name": entity.name,
            "type": entity.entity_type
        })

    def remove_entity(self, entity_id):
        self.entities = [
            entity
            for entity in self.entities
            if entity["id"] != entity_id
        ]

    def add_log(self, message):
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
            "entities": self.entities,
            "logs": self.logs,
            "session": self.session.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        table = cls(
            id=data["id"],
            name=data["name"],
            master_user_id=data["master_user_id"]
        )

        table.players = data.get(
            "players",
            []
        )

        table.entities = data.get(
            "entities",
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
            f"Entities: {len(self.entities)}"
        )

    def __repr__(self):
        return (
            f"Table("
            f"name='{self.name}', "
            f"players={len(self.players)}, "
            f"entities={len(self.entities)}"
            f")"
        )