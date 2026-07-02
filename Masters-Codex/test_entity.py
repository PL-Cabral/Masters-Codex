from core.player import Player
from core.monster import Monster
from engine.Dices import execute_roll_command

print("=== TESTE DO PLAYER ===")
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

print("\n=== FICHA INICIAL ===")
print(player.show_details())

print("\n=== TESTE DE HABILIDADE CUSTOMIZADA ===")
player.add_custom_skill(
    "Rajada Arcana",
    "Dispara energia mágica contra um alvo."
)

print(player.show_details())

print("\n=== TESTE DE ROLAGEM COM D20 ===")
dice_response = execute_roll_command({20: 1})

if dice_response["status"] == "success":
    dice_result = dice_response["total_score"]

    action = player.perform_action(
        action_name="Teste de Inteligência",
        ability_name="intelligence",
        dice_result=dice_result
    )

    print(f"Resultado do dado: {dice_result}")
    print(f"Modificador: {action['modifier']}")
    print(f"Total: {action['total']}")
    print(action["message"])
else:
    print(dice_response["message"])

print("\n=== TESTE DE DANO ===")
player.take_damage(5)
print(f"HP depois do dano: {player.current_hp}/{player.max_hp}")

print("\n=== TESTE DE CURA ===")
player.heal(3)
print(f"HP depois da cura: {player.current_hp}/{player.max_hp}")

print("\n=== TESTE DE INVENTÁRIO ===")
player.add_item("Spellbook")
player.add_item("Dagger")

print(player.show_details())

print("\n=== TESTE DE CONVERSÃO PARA DICIONÁRIO ===")
player_data = player.to_dict()

print(player_data)

print("=== TESTE DO MONSTER ===")

monster = Monster(
    name="Goblin",
    max_hp=12,
    level=1,
    threat_level=1,
    natural_damage_type="piercing",
    armor_class=15,
    monster_type="humanoid",
    attributes={
        "strength": 8,
        "dexterity": 14,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 8,
        "charisma": 8,
    }
)

print("\n=== FICHA INICIAL ===")
print(monster.show_details())


print("\n=== TESTE DE ROLAGEM COM D20 ===")

dice_response = execute_roll_command({20: 1})

if dice_response["status"] == "success":
    dice_result = dice_response["total_score"]

    action = monster.perform_action(
        action_name="Ataque com adaga",
        dice_result=dice_result
    )

    print(f"Resultado do dado: {dice_result}")
    print(f"Bônus de ataque: {action['attack_bonus']}")
    print(f"Total: {action['total']}")
    print(f"Tipo de dano: {action['damage_type']}")
    print(action["message"])
else:
    print(dice_response["message"])


print("\n=== TESTE DE DANO ===")

monster.take_damage(5)

print(f"HP depois do dano: {monster.current_hp}/{monster.max_hp}")


print("\n=== TESTE DE CURA ===")

monster.heal(3)

print(f"HP depois da cura: {monster.current_hp}/{monster.max_hp}")


print("\n=== TESTE DE CONDIÇÃO ===")

monster.add_condition("poisoned")

print(monster.show_details())


print("\n=== TESTE DE REMOVER CONDIÇÃO ===")

monster.remove_condition("poisoned")

print(monster.show_details())


print("\n=== TESTE DE CONVERSÃO PARA DICIONÁRIO ===")

monster_data = monster.to_dict()

print(monster_data)