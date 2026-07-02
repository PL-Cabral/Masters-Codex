from dataclasses import dataclass
import random
import json

# STEP 1: Core Dice Structure **PASSO 1: Estrutura Principal dos Dados
@dataclass
class Die:
    sides: int
    current_roll: int = None

    def roll(self):
        """Simulates rolling the die."""
        self.current_roll = random.randint(1, self.sides)
        return self.current_roll

# STEP 2: The Roll Command Function **PASSO 2: Comando Para Funcao de Rolagem de Dados 

def execute_roll_command(dice_selection):
    """Executes a dice roll command based on user selection.
    Outputs results grouped by die type, ordered from smallest die to largest.
    
    :param dice_selection: Dict specifying the number of each die type.
    e.g., {6: 3, 20: 1} means 3d6 and 1d20."""
    
    # Define the strict "dice order" (smallest to largest) **Define a Ordem dos Dados  
    ordered_dice_types = [4, 6, 10, 20, 100]
    
    payload_rolls = {}
    total_sum = 0
    
    # Iterate through our strict dice order **Interacao Para Seguir a Ordem dos Dados 
    for sides in ordered_dice_types:
        # Check if the user actually requested this die type **Checa se o usuario solicitou o dado
        if sides in dice_selection and dice_selection[sides] > 0:
            quantity = dice_selection[sides]
            roll_results = []
            
            # Roll the requested quantity for this specific die type **Rola a Quantidade Especifica do Tipo Escolhido de Dado
            for _ in range(quantity):
                die = Die(sides=sides)
                result = die.roll()
                roll_results.append(result)
                total_sum += result
            
            # Save just the results under the die's name (e.g., "d6") **Salva o Resultado Junto do Dado Que Obteu este Resultado (ex: d6 - 7)
            # The order inside this list is just the chronological order they were rolled **A Ordem da lista e a Ordem em que os Dados Foram Rolados
            payload_rolls[f"d{sides}"] = roll_results

    if not payload_rolls:
        return {"status": "error", "message": "No valid dice selected to roll."}

    # Package the final Master's Codex payload **Pacote "payload" do Master's Codex
    return {
        "status": "success",
        "total_score": total_sum,
        "rolls": payload_rolls
    }



# TEST EXAMPLE
if __name__ == "__main__":
    print("--- Master's Codex: Dice-Ordered Command ---")
    
    # Let's roll a chaotic mix of dice out of order:
    my_chosen_dice = {
        100: 2,  # two d100
        6: 3,    # three d6
        4: 1,    # one d4
        20: 1    # one d20
    }
    
    # Run the command
    api_response = execute_roll_command(my_chosen_dice)
    
    # Print the clean JSON output
    print(json.dumps(api_response, indent=2))