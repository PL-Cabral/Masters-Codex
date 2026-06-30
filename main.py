from core.table import Table
from core.monster import Monster
from core.npc import NPC

from core.users.master_user import MasterUser
from core.users.player_user import PlayerUser

# Firebase opcional
firebase_enabled = False
firebase_error = None

try:
    from services.firebase_service import save_table
    from services.firebase_service import get_table
    from services.firebase_service import save_entity
    from services.firebase_service import save_user
    firebase_enabled = True
except Exception as error:
    firebase_error = error

local_tables = {}

def print_header():
    print("\n" + "-" * 65)
    print("MASTER'S CODEX")
    print("D&D SESSION MANAGEMENT SYSTEM")
    print("-" * 65)

    if firebase_enabled:
        print("Modo atual: FIREBASE CLOUD")
    else:
        print("Modo atual: LOCAL BACKUP")

def separator():
    print("-" * 65)

def persist_table(table):
    # Tenta salvar no Firebase. Se falhar, salva localmente.
    global firebase_enabled

    if firebase_enabled:
        try:
            save_table(table)
            print("Mesa sincronizada com Firebase.")
            return
        except Exception as error:
            print("\nFirebase indisponível.")
            print(error)
            firebase_enabled = False

    local_tables[table.id] = table
    print("Mesa salva localmente.")

def load_table(table_id):
    if firebase_enabled:
        try:
            return get_table(table_id)
        except Exception as error:
            print("Erro ao carregar do Firebase:")
            print(error)

    return local_tables.get(table_id)

def login_menu():
    print("\nLOGIN")
    print("1 - Mestre")
    print("2 - Jogador")
    print("0 - Sair")

    return input("Escolha: ")

def master_start_menu():
    print("\nMESTRE")
    print("1 - Criar mesa")
    print("2 - Entrar em mesa existente")
    print("0 - Logout")

    return input("Escolha: ")

def master_menu():
    print("\nPAINEL DO MESTRE")
    print("1 - Ver mesa")
    print("2 - Adicionar entidade")
    print("3 - Alterar estado da sessão")
    print("4 - Adicionar log")
    print("0 - Logout")

    return input("Escolha: ")

def player_menu():
    print("\nPAINEL DO JOGADOR")
    print("1 - Ver mesa")
    print("0 - Logout")

    return input("Escolha: ")

def show_table(table):
    separator()

    print("Mesa:", table.name)
    print("Table ID:", table.id)
    print("Master ID:", table.master_user_id)
    print("Estado:", table.session.state)
    print("Players:", len(table.players))
    print("Entities:", len(table.entities))

    if table.players:
        print("\nJogadores:")
        for player in table.players:
            print("-", player["username"])

    if table.entities:
        print("\nEntidades:")
        for entity in table.entities:
            print("-", entity["name"], f"({entity['type']})")

    separator()

def create_entity():
    print("\nCRIAR ENTIDADE")
    print("1 - Monster")
    print("2 - NPC")
    print("0 - Cancelar")

    choice = input("Escolha: ")

    if choice == "0":
        return None

    name = input("Nome: ")
    hp = int(input("HP máximo: "))
    level = int(input("Nível: "))

    if choice == "1":
        entity = Monster(
            name=name,
            max_hp=hp,
            level=level
        )

        return entity

    elif choice == "2":
        entity = NPC(
            name=name,
            max_hp=hp,
            level=level
        )

        return entity

    print("Opção inválida.")
    return None

def main():
    print_header()

    while True:
        choice = login_menu()

        if choice == "0":
            print("\nEncerrando sistema...")
            break

        elif choice == "1":
            username = input("Nome do mestre: ")

            master = MasterUser(
                username=username
            )

            if firebase_enabled:
                save_user(master)

            current_table = None

            choice = master_start_menu()

            if choice == "0":
                continue

            elif choice == "1":
                table_name = input("Nome da mesa: ")

                current_table = Table(
                    name=table_name,
                    master_user_id=master.id
                )

                persist_table(current_table)

                print("\nMesa criada com sucesso.")
                print("Código da mesa:", current_table.id)

            elif choice == "2":
                table_id = input("Código da mesa: ")

                current_table = load_table(table_id)

                if current_table is None:
                    print("Mesa não encontrada.")
                    continue

            else:
                print("Opção inválida.")
                continue

            while True:
                choice = master_menu()

                if choice == "0":
                    break

                elif choice == "1":
                    show_table(current_table)

                elif choice == "2":
                    entity = create_entity()

                    if entity is not None:
                        if firebase_enabled:
                            save_entity(entity)

                        current_table.add_entity(entity)
                        persist_table(current_table)

                        print("Entidade adicionada.")

                elif choice == "3":
                    print("\nEstados:")
                    print("lobby")
                    print("exploration")
                    print("combat")
                    print("paused")
                    print("ended")

                    state = input("Novo estado: ")

                    try:
                        current_table.session.change_state(state)
                        persist_table(current_table)
                    except Exception as error:
                        print(error)

                elif choice == "4":
                    log = input("Novo log: ")
                    current_table.add_log(log)
                    persist_table(current_table)

                else:
                    print("Opção inválida.")

        elif choice == "2":
            username = input("Nome do jogador: ")

            player = PlayerUser(
                username=username
            )

            if firebase_enabled:
                save_user(player)

            table_id = input("Código da mesa: ")

            current_table = load_table(table_id)

            if current_table is None:
                print("Mesa não encontrada.")
                continue

            current_table.add_player(player)
            persist_table(current_table)

            print("\nVocê entrou na mesa com sucesso.")
            print("Seu Player ID:", player.id)

            while True:
                choice = player_menu()

                if choice == "0":
                    break

                elif choice == "1":
                    show_table(current_table)

                else:
                    print("Opção inválida.")

        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()