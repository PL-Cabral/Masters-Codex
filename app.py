import os
from flask import Flask, render_template, request, jsonify

# Importação do Motor de Dados
from engine.Dices import execute_roll_command

# Importações originais
from core.table import Table
from core.monster import Monster
from core.npc import NPC
from core.player import Player
from core.users.master_user import MasterUser
from core.users.player_user import PlayerUser

# Configuração base
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-rpg")

# Inicialização Firebase
firebase_enabled = False
try:
    from services.firebase_service import save_table, get_table, save_entity, save_user, get_entity, get_user_by_username
    from firebase_admin import db
    firebase_enabled = True
except Exception as error:
    print(f"Modo Local ativado. Firebase falhou: {error}")

local_tables = {}
local_entities = {}
local_users = {}
local_passwords = {}

# --- FUNÇÕES DE PERSISTÊNCIA ---
def save_table_password(table_id, username, password):
    if firebase_enabled:
        try: db.reference(f"passwords/{table_id}/{username}").set(password)
        except: pass
    local_passwords[f"{table_id}_{username}"] = password

def check_table_password(table_id, username, password):
    if firebase_enabled:
        try: return db.reference(f"passwords/{table_id}/{username}").get() == password
        except: pass
    return local_passwords.get(f"{table_id}_{username}") == password

def persist_user(user):
    if firebase_enabled:
        try: save_user(user); return
        except: pass
    local_users[user.username] = user

def load_user(username):
    if firebase_enabled:
        try: return get_user_by_username(username)
        except: pass
    return local_users.get(username)

def persist_table(table):
    if firebase_enabled:
        try: save_table(table); return
        except: pass
    local_tables[table.id] = table

def load_table(table_id):
    if firebase_enabled:
        try: return get_table(table_id)
        except: pass
    return local_tables.get(table_id)

def persist_entity(entity):
    if firebase_enabled:
        try: save_entity(entity); return
        except: pass
    local_entities[entity.id] = entity

def load_entity(entity_id):
    if firebase_enabled:
        try: return get_entity(entity_id)
        except: pass
    return local_entities.get(entity_id)


# --- ROTAS ---
@app.route('/')
def index():
    return render_template('index.html', firebase=firebase_enabled)

@app.route('/api/login/master', methods=['POST'])
def master_login():
    data = request.json
    username = data.get('username')
    table_id = data.get('table_id')
    password = data.get('password')
    user = load_user(username) or MasterUser(username=username)
    persist_user(user)
    
    if table_id:
        if not check_table_password(table_id, 'MASTER_PWD', password):
            return jsonify({"status": "error", "message": "Senha do Mestre incorreta!"}), 401
        return jsonify({"status": "success", "role": "master", "user_id": user.id, "username": user.username, "table_id": table_id})
    return jsonify({"status": "success", "role": "master", "user_id": user.id, "username": user.username})

@app.route('/api/login/player', methods=['POST'])
def player_login():
    data = request.json
    username = data.get('username')
    table_id = data.get('table_id')
    table = load_table(table_id)
    if not table: return jsonify({"status": "error", "message": "Mesa não encontrada."}), 404
    
    char_id = None
    for ent_id in table.entity_ids:
        ent = load_entity(ent_id)
        if ent and hasattr(ent, 'character_class') and ent.name == username:
            char_id = ent.id
            break
            
    if char_id:
        return jsonify({"status": "success", "role": "player", "username": username, "char_id": char_id, "table_id": table_id})
    return jsonify({"status": "needs_creation", "username": username, "table_id": table_id})

@app.route('/api/player/create_character', methods=['POST'])
def create_character():
    data = request.json
    username = data.get('username')
    table_id = data.get('table_id')
    char_class = data.get('char_class')
    attr = data.get('attributes')
    
    # CÁLCULO HP: Base 20 + Bônus de Constituição (Atributo CON / 2)
    hp = 20 + int(int(attr.get('con', 10)) / 2)
    
    player_ent = Player(name=username, max_hp=hp, level=1, character_class=char_class, race="Humano", attributes=attr)
    persist_entity(player_ent)
    
    table = load_table(table_id)
    table.add_entity(player_ent)
    table.add_log(f"⚔️ {username} ({char_class}) entrou na mesa!")
    persist_table(table)

    return jsonify({"status": "success", "char_id": player_ent.id})

@app.route('/api/table/create', methods=['POST'])
def create_table():
    data = request.json
    new_table = Table(name=data.get('table_name'), master_user_id=data.get('master_id'))
    persist_table(new_table)
    if data.get('password'): save_table_password(new_table.id, 'MASTER_PWD', data.get('password'))
    return jsonify({"status": "success", "table_id": new_table.id})

@app.route('/api/table/<table_id>', methods=['GET'])
def get_table_info(table_id):
    table = load_table(table_id)
    if not table: return jsonify({"status": "error"}), 404
    
    p_list, m_list = [], []
    for ent_id in table.entity_ids:
        ent = load_entity(ent_id)
        if ent:
            is_player = hasattr(ent, 'character_class')
            ent_data = {"id": ent.id, "name": ent.name, "hp": ent.current_hp, "max_hp": ent.max_hp, "class": getattr(ent, 'character_class', getattr(ent, 'monster_type', 'NPC'))}
            if is_player: p_list.append(ent_data)
            else: m_list.append(ent_data)
            
    return jsonify({"status": "success", "name": table.name, "players": p_list, "monsters": m_list, "logs": getattr(table, 'logs', [])[-15:]})

@app.route('/api/table/add_entity', methods=['POST'])
def add_entity():
    data = request.json
    table = load_table(data.get('table_id'))
    ent = Monster(name=data.get('name'), max_hp=int(data.get('hp')), level=int(data.get('level')), monster_type=data.get('monster_type'), attributes=data.get('attributes'))
    persist_entity(ent)
    table.add_entity(ent)
    persist_table(table)
    return jsonify({"status": "success"})

@app.route('/api/combat/action', methods=['POST'])
def perform_combat_action():
    data = request.json
    attacker = load_entity(data.get('attacker_id'))
    target = load_entity(data.get('target_id')) if data.get('target_id') else None
    
    roll = execute_roll_command({int(data.get('dice_type')): 1})["total_score"]
    msg = f"🎲 [{attacker.name}] rolou {data.get('action_name')}: {roll}."
    
    if target:
        if data.get('action_name') == 'Cura': target.heal(roll)
        else: target.take_damage(roll)
        persist_entity(target)
        msg += f" (Efeito: {roll})"
        
    table = load_table(data.get('table_id'))
    table.add_log(msg)
    persist_table(table)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)