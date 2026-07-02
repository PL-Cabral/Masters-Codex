from core.player import Player
from services.firebase_service import save_entity

print("Criando personagem...")

player = Player(
    name="Aelar",
    max_hp=18,
    level=1,
    character_class="wizard",
    race="elf",
    attributes={
        "strength": 8,
        "dexterity": 14,
        "constitution": 12,
        "intelligence": 16,
        "wisdom": 13,
        "charisma": 10,
    }
)

player.add_custom_skill(
    "Rajada Arcana",
    "Dispara energia mágica contra um alvo."
)

print("Enviando para o Firebase...")

entity_id = save_entity("mesa_teste", player)

print("Personagem salvo no Firebase!")
print(f"ID do personagem: {entity_id}")