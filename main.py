import json
from player import Player, ABILITY_NAMES
from entity import AttributeValidationError
from dice import Die, execute_roll_command  # Importando o sistema de dados que criamos

# Banco de dados temporário em memória para guardar os personagens criados
players_database = {}

def create_new_character():
    """Menu para criação de um novo personagem passo a passo."""
    print("\n=== CRIAR NOVO PERSONAGEM ===")
    name = input("Nome do personagem: ").strip()
    if not name:
        print("Erro: O nome não pode ser vazio.")
        return None

    try:
        max_hp = int(input("HP Máximo (ex: 20): "))
        
        print("\nClasses disponíveis: fighter, wizard, cleric, rogue, barbarian")
        character_class = input("Escolha a classe: ").strip().lower()
        
        print("\nRaças disponíveis: human, elf, dwarf")
        race = input("Escolha a raça: ").strip().lower()
        
        print("\n--- Definição de Atributos (Valores base entre 1 e 30) ---")
        attributes = {}
        for ability in ABILITY_NAMES:
            val = int(input(f"Valor base para {ability.capitalize()} (padrão 10): ") or 10)
            attributes[ability] = val

        # Instancia o novo jogador utilizando a classe existente
        new_player = Player(
            name=name,
            max_hp=max_hp,
            character_class=character_class,
            race=race,
            attributes=attributes
        )
        
        players_database[new_player.name.lower()] = new_player
        print(f"\n[Sucesso] {new_player.name} foi criado e salvo com sucesso!")
        return new_player

    except ValueError:
        print("Erro: Entrada inválida. Certifique-se de digitar números onde necessário.")
        return None
    except AttributeValidationError as e:
        print(f"Erro de validação do sistema: {e}")
        return None

def select_character():
    """Menu para selecionar um personagem existente."""
    if not players_database:
        print("\nNenhum personagem cadastrado ainda. Crie um novo!")
        return None
    
    print("\n=== SELECIONAR PERSONAGEM ===")
    for idx, name in enumerate(players_database.keys(), 1):
        print(f"{idx}. {players_database[name].name}")
    
    choice = input("Digite o nome do personagem que vai jogar: ").strip().lower()
    if choice in players_database:
        return players_database[choice]
    else:
        print("Personagem não encontrado.")
        return None

def handle_roll_dice(current_player):
    """Executa a rolagem escolhendo o tipo de teste e os dados utilizados."""
    print("\n=== TESTE DE ATRIBUTO / ROLAGEM ===")
    print("Escolha o atributo para o teste:")
    for idx, ability in enumerate(ABILITY_NAMES, 1):
        print(f"{idx}. {ability.capitalize()}")
    
    try:
        attr_choice = int(input("Escolha o número do atributo: ")) - 1
        if attr_choice < 0 or attr_choice >= len(ABILITY_NAMES):
            print("Opção inválida.")
            return
        
        selected_ability = ABILITY_NAMES[attr_choice]
        
        print("\nQuais dados você deseja rolar para esse teste?")
        print("Formatos aceitos (d4, d6, d10, d20, d100)")
        
        # Monta a seleção de dados interativamente
        dice_selection = {}
        for sides in [4, 6, 10, 20, 100]:
            qty = int(input(f"Quantos d{sides} quer rolar? (0 para nenhum): ") or 0)
            if qty > 0:
                dice_selection[sides] = qty
                
        if not dice_selection:
            print("Nenhum dado selecionado. Teste cancelado.")
            return

        # 1. Executa a nossa função de rolagem original ordenada por tipo de dado
        roll_payload = execute_roll_command(dice_selection)
        
        if roll_payload.get("status") == "error":
            print(f"Erro na rolagem: {roll_payload.get('message')}")
            return
            
        # 2. Resgata o total bruto dos dados rolados
        dice_total = roll_payload["total_score"]
        
        # 3. Executa a ação da sua classe Player para computar o modificador de atributo
        action_result = current_player.perform_action(
            action_name=f"Teste de {selected_ability.capitalize()}",
            ability_name=selected_ability,
            dice_result=dice_total
        )
        
        # 4. Apresenta o retorno final estruturado para a API / Codex do Mestre
        print("\n" + "="*40)
        print("  RESULTADO ENVIADO AO MASTER'S CODEX")
        print("="*40)
        
        # Customizando o print final para mostrar exatamente o que foi pedido
        api_output = {
            "status": "success",
            "player": current_player.name,
            "teste": f"Modificador de {selected_ability.capitalize()}: {action_result['modifier']}",
            "dados_rolados": roll_payload["rolls"],
            "total_dados": dice_total,
            "total_com_atributos": action_result["total"]
        }
        
        print(json.dumps(api_output, indent=2, ensure_ascii=False))
        print("="*40)
        
    except ValueError:
        print("Por favor, insira valores numéricos válidos.")

def main_game_loop():
    """Gerencia os menus principal e secundário do sistema."""
    current_player = None
    
    # Adicionando um personagem de exemplo para facilitar os testes iniciais
    example = Player(name="Arthas", max_hp=20, character_class="fighter", race="human")
    players_database["arthas"] = example

    while True:
        # MENU INICIAL: Se não houver jogador selecionado
        if current_player is None:
            print("\n=================================")
            print("    MASTER'S CODEX - INITIAL     ")
            print("=================================")
            print("1. Escolher Personagem Existente")
            print("2. Criar Novo Personagem (Ficha)")
            print("3. Sair do Sistema")
            print("=================================")
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                current_player = select_character()
            elif opcao == "2":
                current_player = create_new_character()
            elif opcao == "3":
                print("Encerrando Master's Codex. Até a próxima aventura!")
                break
            else:
                print("Opção inválida.")
        
        # MENU SECUNDÁRIO: Se um jogador já estiver ativo na sessão
        else:
            print(f"\n=================================")
            print(f" JOGADOR ATIVO: {current_player.name.upper()} (Nível {current_player.level})")
            print("=================================")
            print("1. Rolar Dados 'Fazer Teste' ")
            print("2. Adicionar XP ")
            print("3. Usar Item (Ainda não implementado)")
            print("4. Trocar de Personagem")
            print("5. Mostrar Detalhes da Ficha")
            print("6. Sair do Sistema")
            print("=================================")
            
            opcao = input("O que deseja fazer? ").strip()
            
            if opcao == "1":
                handle_roll_dice(current_player)
            elif opcao == "2":
                try:
                    xp_amount = int(input("Quantidade de XP a adicionar: "))
                    current_player.gain_xp(xp_amount)
                    print(f"[XP] {xp_amount} de XP adicionados! Total atual: {current_player.xp}")
                except ValueError:
                    print("Por favor, insira um número inteiro.")
                except AttributeValidationError as e:
                    print(e)
            elif opcao == "3":
                print("\n[Inventário] O sistema de inventário será integrado aqui no futuro.")
            elif opcao == "4":
                current_player = None  # Reseta o jogador ativo para voltar ao menu inicial
                print("\nTrocando de personagem...")
            elif opcao == "5":
                print("\n" + current_player.show_details())
            elif opcao == "6":
                print("Encerrando Master's Codex. Até a próxima aventura!")
                break
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    main_game_loop()