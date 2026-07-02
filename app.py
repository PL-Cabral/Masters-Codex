import os
from flask import Flask, render_template, request, jsonify

# A CORREÇÃO PRINCIPAL ESTÁ AQUI: "Dices" com D maiúsculo!
from engine.Dices import execute_roll_command

# Importações originais do seu projeto
from core.table import Table
from core.monster import Monster
from core.npc import NPC
from core.player import Player
from core.users.master_user import MasterUser
from core.users.player_user import PlayerUser

# Força a Vercel a encontrar a pasta templates corretamente
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-rpg")

# Inicialização do Firebase adaptada
firebase_enabled = False
try:
    from services.firebase_service import save_table, get_table, save_entity, save_user, get_entity, get_user_by_username
    from firebase_admin import db
    firebase_enabled = True
except Exception as error:
    print(f"Modo Local ativado. Firebase falhou: {error}")

# Dicionários de fallback local
local_tables = {}
local_entities = {}
local_users = {}
local_passwords = {}

# --- FUNÇÕES DE PERSISTÊNCIA REAPROVEITADAS E EXPANDIDAS ---
def save_table_password(table_id, username, password):
    if firebase_enabled:
        try:
            ref = db.reference(f"passwords/{table_id}/{username}")
            ref.set(password)
            return
        except: pass
    local_passwords[f"{table_id}_{username}"] = password

def check_table_password(table_id, username, password):
    if firebase_enabled:
        try:
            ref = db.reference(f"passwords/{table_id}/{username}")
            saved = ref.get()
            if saved: return saved == password
        except: pass
    return local_passwords.get(f"{table_id}_{username}") == password

def has_table_password(table_id, username):
    if firebase_enabled:
        try:
            ref = db.reference(f"passwords/{table_id}/{username}")
            return ref.get() is not None
        except: pass
    return f"{table_id}_{username}" in local_passwords

def persist_user(user):
    if firebase_enabled:
        try: save_user(user); return
        except Exception: pass
    local_users[user.username] = user

def load_user(username):
    if firebase_enabled:
        try: return get_user_by_username(username)
        except Exception: pass
    return local_users.get(username)

def persist_table(table):
    if firebase_enabled:
        try: save_table(table); return
        except Exception: pass
    local_tables[table.id] = table

def load_table(table_id):
    if firebase_enabled:
        try: return get_table(table_id)
        except Exception: pass
    return local_tables.get(table_id)

def persist_entity(entity):
    if firebase_enabled:
        try: save_entity(entity); return
        except Exception: pass
    local_entities[entity.id] = entity

def load_entity(entity_id):
    if firebase_enabled:
        try: return get_entity(entity_id)
        except Exception: pass
    return local_entities.get(entity_id)


# --- ROTAS DA APLICAÇÃO ---

@app.route('/')
def index():
    return render_template('index.html', firebase=firebase_enabled)

@app.route('/api/login/master', methods=['POST'])
def master_login():
    data = request.json
    username = data.get('username')
    if not username: return jsonify({"status": "error", "message": "Nome obrigatório."}), 400
        
    user = load_user(username)
    if user is None:
        user = MasterUser(username=username)
        persist_user(user)
    return jsonify({"status": "success", "role": "master", "user_id": user.id, "username": user.username})

@app.route('/api/login/player', methods=['POST'])
def player_login():
    data = request.json
    username = data.get('username')
    table_id = data.get('table_id')
    password = data.get('password')

    table = load_table(table_id)
    if not table: return jsonify({"status": "error", "message": "Mesa não encontrada."}), 404

    # Verifica senha ou se precisa criar char
    if has_table_password(table_id, username):
        if not check_table_password(table_id, username, password):
            return jsonify({"status": "error", "message": "Senha incorreta!"}), 401
        
        # Encontra o ID da entidade (personagem) que tem o nome do jogador
        char_id = None
        for ent_id in table.entity_ids:
            ent = load_entity(ent_id)
            if ent and getattr(ent, 'entity_type', '') == 'player' and ent.name == username:
                char_id = ent.id
                break
                
        return jsonify({"status": "success", "role": "player", "username": username, "char_id": char_id, "table_id": table_id})
    else:
        # Primeiro acesso à mesa
        return jsonify({"status": "needs_creation", "username": username, "table_id": table_id})

@app.route('/api/player/create_character', methods=['POST'])
def create_character():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    table_id = data.get('table_id')
    char_class = data.get('char_class')
    hp = int(data.get('hp', 20))
    attributes = data.get('attributes')

    table = load_table(table_id)
    if not table: return jsonify({"status": "error"}), 404

    # Salva senha e cria jogador
    save_table_password(table_id, username, password)
    
    player_ent = Player(name=username, max_hp=hp, level=1, character_class=char_class, race="Humano", attributes=attributes)
    persist_entity(player_ent)
    
    table.add_entity(player_ent)
    persist_table(table)

    return jsonify({"status": "success", "role": "player", "username": username, "char_id": player_ent.id, "table_id": table_id})

@app.route('/api/table/create', methods=['POST'])
def create_table():
    data = request.json
    table_name = data.get('table_name')
    master_id = data.get('master_id')
    
    new_table = Table(name=table_name, master_user_id=master_id)
    persist_table(new_table)
    return jsonify({"status": "success", "table_id": new_table.id, "table_name": new_table.name})

@app.route('/api/table/<table_id>', methods=['GET'])
def get_table_info(table_id):
    table = load_table(table_id)
    if not table: return jsonify({"status": "error", "message": "Mesa não encontrada."}), 404
        
    players_list = []
    monsters_list = []
    
    for ent_id in table.entity_ids:
        ent = load_entity(ent_id)
        if ent:
            ent_data = {
                "id": ent.id, "name": ent.name, "hp": ent.current_hp, "max_hp": ent.max_hp,
                "type": getattr(ent, 'entity_type', 'npc'), "class": getattr(ent, 'character_class', getattr(ent, 'monster_type', ''))
            }
            if ent_data["type"] == "player":
                players_list.append(ent_data)
            else:
                monsters_list.append(ent_data)
            
    return jsonify({
        "status": "success",
        "id": table.id,
        "name": table.name,
        "state": table.session.state,
        "players": players_list,
        "monsters": monsters_list,
        "logs": getattr(table, 'logs', [])[-10:] # Manda apenas os ultimos 10 logs
    })

@app.route('/api/table/add_entity', methods=['POST'])
def add_entity():
    data = request.json
    table_id = data.get('table_id')
    ent_type = data.get('type') # monster / npc
    monster_type = data.get('monster_type', 'npc')
    name = data.get('name')
    hp = int(data.get('hp', 10))
    level = int(data.get('level', 1))
    attributes = data.get('attributes')
    threat = int(data.get('threat', 1))
    
    table = load_table(table_id)
    if not table: return jsonify({"status": "error"}), 404
        
    if ent_type == 'monster':
        # Valores de Armor Class e Damage Type padrão adicionados para não quebrar a regra da classe
        entity = Monster(name=name, max_hp=hp, level=level, threat_level=threat, natural_damage_type="bludgeoning", armor_class=10, monster_type=monster_type, attributes=attributes)
    else:
        entity = NPC(name=name, max_hp=hp, level=level, attributes=attributes)
        
    persist_entity(entity)
    table.add_entity(entity)
    persist_table(table)
    
    return jsonify({"status": "success", "message": f"Mob {name} adicionado!"})

@app.route('/api/combat/action', methods=['POST'])
def perform_combat_action():
    data = request.json
    table_id = data.get('table_id')
    attacker_id = data.get('attacker_id')
    target_id = data.get('target_id')
    action_name = data.get('action_name')
    dice_type = int(data.get('dice_type', 20))

    attacker = load_entity(attacker_id)
    target = load_entity(target_id) if target_id else None

    if not attacker: return jsonify({"status": "error", "message": "Atacante não encontrado."}), 404

    dice_response = execute_roll_command({dice_type: 1})
    dice_result = dice_response.get("total_score", 1)

    log_message = f"[{attacker.name}] rolou D{dice_type} para {action_name}: Tirou {dice_result}."

    # Lógica simplificada de combate/cura
    if target:
        if action_name == 'Cura':
            target.heal(dice_result)
            log_message += f" e curou [{target.name}] em {dice_result} HP!"
        elif action_name in ['Ataque Físico', 'Ataque Mágico']:
            target.take_damage(dice_result)
            log_message += f" e causou {dice_result} de dano em [{target.name}]!"
            if target.current_hp <= 0:
                log_message += f" [{target.name}] FOI DERROTADO!"
        
        persist_entity(target)

    # Salva no log da mesa
    table = load_table(table_id)
    if table:
        table.add_log(log_message)
        persist_table(table)
            
    return jsonify({"status": "success", "log": log_message})

if __name__ == '__main__':
    app.run(debug=True)