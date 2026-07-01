from flask import Flask, render_template, request, jsonify, session
import os

# Importações originais do seu projeto
from core.table import Table
from core.monster import Monster
from core.npc import NPC
from core.player import Player
from core.users.master_user import MasterUser
from core.users.player_user import PlayerUser

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-rpg")

# Inicialização do Firebase adaptada do seu main.py
firebase_enabled = False
try:
    from services.firebase_service import save_table, get_table, save_entity, save_user, get_entity, get_user_by_username
    firebase_enabled = True
except Exception as error:
    print(f"Modo Local ativado. Firebase falhou: {error}")

# Dicionários de fallback local caso o Firebase falhe na Vercel
local_tables = {}
local_entities = {}
local_users = {}

# --- FUNÇÕES DE PERSISTÊNCIA REAPROVEITADAS ---
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

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    role = data.get('role') # 'master' ou 'player'
    
    if not username:
        return jsonify({"status": "error", "message": "Nome de usuário obrigatório."}), 400
        
    if role == 'master':
        user = load_user(username)
        if user is None:
            user = MasterUser(username=username)
            persist_user(user)
        return jsonify({"status": "success", "role": "master", "user_id": user.id, "username": user.username})
    else:
        user = load_user(username)
        if user is None:
            user = PlayerUser(username=username)
            persist_user(user)
        return jsonify({"status": "success", "role": "player", "user_id": user.id, "username": user.username})

@app.route('/api/table/create', methods=['POST'])
def create_table():
    data = request.json
    table_name = data.get('table_name')
    master_id = data.get('master_id')
    
    if not table_name or not master_id:
        return jsonify({"status": "error", "message": "Dados incompletos."}), 400
        
    new_table = Table(name=table_name, master_user_id=master_id)
    persist_table(new_table)
    
    return jsonify({"status": "success", "table_id": new_table.id, "table_name": new_table.name})

@app.route('/api/table/<table_id>', methods=['GET'])
def get_table_info(table_id):
    table = load_table(table_id)
    if not table:
        return jsonify({"status": "error", "message": "Mesa não encontrada."}), 404
        
    # Carrega os dados das entidades anexadas à mesa
    entities_details = []
    for ent_id in table.entity_ids:
        ent = load_entity(ent_id)
        if ent:
            entities_details.append({"name": ent.name, "type": getattr(ent, 'entity_type', 'Desconhecido'), "hp": ent.current_hp})
            
    return jsonify({
        "status": "success",
        "id": table.id,
        "name": table.name,
        "state": table.session.state,
        "players": table.players,
        "entities": entities_details,
        "logs": getattr(table, 'logs', [])
    })

@app.route('/api/table/add_entity', methods=['POST'])
def add_entity():
    data = request.json
    table_id = data.get('table_id')
    ent_type = data.get('type') # 'monster' ou 'npc'
    name = data.get('name')
    hp = int(data.get('hp', 10))
    level = int(data.get('level', 1))
    
    table = load_table(table_id)
    if not table:
        return jsonify({"status": "error", "message": "Mesa não encontrada."}), 404
        
    if ent_type == 'monster':
        entity = Monster(name=name, max_hp=hp, level=level)
    else:
        entity = NPC(name=name, max_hp=hp, level=level)
        
    persist_entity(entity)
    table.add_entity(entity)
    persist_table(table)
    
    return jsonify({"status": "success", "message": f"Entidade {name} adicionada com sucesso!"})

if __name__ == '__main__':
    app.run(debug=True)