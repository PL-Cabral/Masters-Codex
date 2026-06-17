from player import Player

player = Player(
    name="Arthas",
    max_hp=20,
    level=1,
    character_class="fighter",
    race="human",
    attributes={
        "strength": 15,
        "dexterity": 12,
        "constitution": 14,
        "intelligence": 10,
        "wisdom": 8,
        "charisma": 11,
    }
)

print(player.show_details())

action = player.perform_action(
    action_name="Ataque com espada",
    ability_name="strength",
    dice_result=15
)

print(action["message"])