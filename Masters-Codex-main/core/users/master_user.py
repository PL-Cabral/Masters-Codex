from dataclasses import dataclass
from core.users.user import User
from utility.exceptions import TableValidationError

@dataclass
class MasterUser(User):

    @property
    def user_type(self):
        return "master"

    def access_panel(self):
        return {
            "user_id": self.id,
            "username": self.username,
            "panel": "master_panel",
            "permissions": [
                "create_table",
                "delete_table",
                "add_entity",
                "remove_entity",
                "manage_players",
            ]
        }

    def create_table(self, table_name):
        table_name = table_name.strip()

        if table_name == "":
            raise TableValidationError("O nome da mesa não pode ser vazio.")

        return {
            "action": "create_table",
            "table_name": table_name,
            "master_id": self.id,
            "message": (
                f"Mesa '{table_name}' criada por {self.username}."
            )
        }

    def delete_table(self, table_id):
        table_id = table_id.strip()

        if table_id == "":
            raise TableValidationError("O ID da mesa não pode ser vazio.")

        return {
            "action": "delete_table",
            "table_id": table_id,
            "master_id": self.id,
            "message": (
                f"Mesa {table_id} removida por {self.username}."
            )
        }

    def add_entity_to_table(self, entity):
        return {
            "action": "add_entity",
            "master_id": self.id,
            "entity_id": entity.id,
            "entity_name": entity.name,
            "message": (
                f"{entity.name} foi adicionado à mesa."
            )
        }

    def remove_entity_from_table(self, entity):
        return {
            "action": "remove_entity",
            "master_id": self.id,
            "entity_id": entity.id,
            "entity_name": entity.name,
            "message": (
                f"{entity.name} foi removido da mesa."
            )
        }

    def to_dict(self):
        data = super().to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        fields = cls.get_base_fields(data)
        return cls(**fields)