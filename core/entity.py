# ABC e abstractmethod permitem criar uma classe abstrata
from abc import ABC, abstractmethod

# dataclass cria automaticamente o método __init__
# Ex: class exemple():
#       def __init__(self):
#           pass
from dataclasses import dataclass, field

# uuid4 gera um ID único para cada entidade
from uuid import uuid4

# Criação de erros personalizados
class AttributeValidationError(Exception):
    pass


class EntityCannotActError(Exception):
    pass


class DuplicateSkillError(Exception):
    pass

# Criação da classe abstrata Entidade e seus parâmetros
@dataclass
class Entity(ABC):
    # Atributos obrigatórios da entidade
    name: str
    max_hp: int
    level: int = 1

    id: str = field(default_factory=lambda: str(uuid4()))
    table_id: str = None
    current_hp: int = None

    attributes: dict = field(default_factory=dict)
    skills: list = field(default_factory=list)
    conditions: list = field(default_factory=list)

    # Campo para anotações
    notes: str = ""

    # Validar os dados iniciais da entidade
    def __post_init__(self):
        self.name = self.name.strip()

        if self.name == "":
            raise AttributeValidationError("A entidade precisa ter um nome.")

        if self.max_hp <= 0:
            raise AttributeValidationError(
                "O HP máximo precisa ser maior que zero.")

        if self.level <= 0:
            raise AttributeValidationError(
                "O nível precisa ser maior que zero.")

        if self.current_hp is None:
            self.current_hp = self.max_hp

        if self.current_hp < 0:
            raise AttributeValidationError(
                "O HP atual não pode ser menor que zero.")

        if self.current_hp > self.max_hp:
            raise AttributeValidationError(
                "O HP atual não pode ser maior que o HP máximo.")

    # Métodos abstrados
    @property
    @abstractmethod
    def entity_type(self):
        pass

    @abstractmethod
    def perform_action(self):
        pass

    @abstractmethod
    def show_details(self):
        pass

    # Ações padrões da classe e validações de ações
    def is_alive(self):
        return self.current_hp > 0

    def validate_can_act(self):
        if not self.is_alive():
            raise EntityCannotActError(
                f"{self.name} está com 0 de HP e não pode agir.")

    def take_damage(self, damage):
        if damage < 0:
            raise AttributeValidationError("O dano não pode ser negativo.")

        self.current_hp -= damage

        if self.current_hp < 0:
            self.current_hp = 0

    def heal(self, amount):
        if amount < 0:
            raise AttributeValidationError("A cura não pode ser negativa.")

        self.current_hp += amount

        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp

    def add_condition(self, condition):
        condition = condition.strip().lower()

        if condition == "":
            raise AttributeValidationError("A condição não pode ser vazia.")

        if condition not in self.conditions:
            self.conditions.append(condition)

    def remove_condition(self, condition):
        condition = condition.strip().lower()

        if condition in self.conditions:
            self.conditions.remove(condition)

    def add_skill(self, skill):
        if not isinstance(skill, dict):
            raise AttributeValidationError(
                "A habilidade precisa ser um dicionário.")

        skill_name = skill.get("name")

        if not skill_name:
            raise AttributeValidationError("A habilidade precisa ter um nome.")

        skill_name = skill_name.strip().lower()

        for existing_skill in self.skills:
            existing_name = existing_skill.get("name", "").strip().lower()

            if existing_name == skill_name:
                raise DuplicateSkillError(
                    f"{self.name} já possui a habilidade '{skill_name}'.")

        self.skills.append(skill)

    def remove_skill(self, skill_name):
        skill_name = skill_name.strip().lower()

        self.skills = [
            skill
            for skill in self.skills
            if skill.get("name", "").strip().lower() != skill_name
        ]

    def list_skills(self):
        return self.skills.copy()

    def to_dict(self):
        return {
            "id": self.id,
            "table_id": self.table_id,
            "entity_type": self.entity_type,
            "name": self.name,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "level": self.level,
            "attributes": self.attributes,
            "skills": self.skills,
            "conditions": self.conditions,
            "notes": self.notes,
        }

    # Métodos da classe abstrata
    @classmethod
    def get_base_fields(cls, data):
        return {
            "id": data.get("id", str(uuid4())),
            "table_id": data.get("table_id"),
            "name": data.get("name", ""),
            "max_hp": data.get("max_hp", 1),
            "current_hp": data.get("current_hp", data.get("max_hp", 1)),
            "level": data.get("level", 1),
            "attributes": data.get("attributes", {}),
            "skills": data.get("skills", []),
            "conditions": data.get("conditions", []),
            "notes": data.get("notes", ""),
        }

    # Definir como a entidade vai aparecer quando usarmos print(entity)
    def __str__(self):
        return f"{self.name} ({self.entity_type}) - HP {self.current_hp}/{self.max_hp}"

    # Apoio para debug e testes
    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"hp={self.current_hp}/{self.max_hp}, "
            f"level={self.level}"
            f")"
        )