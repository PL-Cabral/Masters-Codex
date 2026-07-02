from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import uuid4
from engine.Dices import execute_roll_command
from utility.exceptions import UserValidationError

@dataclass
class User(ABC):
    # Dados básicos do usuário
    username: str

    id: str = None
    firebase_uid: str = None

    # usado apenas para cache local da mesa conectada
    connected_table_id: str = None

    # Validação inicial
    def __post_init__(self):
        self.username = self.username.strip()

        if self.username == "":
            raise UserValidationError("O usuário precisa ter um nome.")

        if self.firebase_uid is not None:
            self.firebase_uid = self.firebase_uid.strip()

            if self.firebase_uid == "":
                raise UserValidationError("O firebase_uid não pode ser vazio.")

        if self.connected_table_id is not None:
            self.connected_table_id = self.connected_table_id.strip()

            if self.connected_table_id == "":
                raise UserValidationError("O ID da mesa não pode ser vazio.")

        if self.id is None:
            self.id = str(uuid4())

    # Cada tipo de usuário terá um painel diferente
    @property
    @abstractmethod
    def user_type(self):
        pass

    @abstractmethod
    def access_panel(self):
        pass

    def roll_dice(self, dice_selection):
        result = execute_roll_command(dice_selection)

        if result["status"] == "error":
            return result

        return {
            "user_id": self.id,
            "username": self.username,
            "roll_result": result
        }

    # Preparar para salvar em JSON/Firebase
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "firebase_uid": self.firebase_uid,
            "connected_table_id": self.connected_table_id,
            "user_type": self.user_type,
        }

    # Base para subclasses
    @classmethod
    def get_base_fields(cls, data):
        return {
            "id": data.get("id"),
            "username": data.get("username", ""),
            "firebase_uid": data.get("firebase_uid"),
            "connected_table_id": data.get("connected_table_id"),
        }

    def __str__(self):
        return (
            f"{self.username} "
            f"({self.user_type})"
        )
    
    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"username='{self.username}', "
            f"user_type='{self.user_type}'"
            f")"
        )