import os
from flask import Flask, render_template, request, jsonify
from engine.Dices import execute_roll_command
from core.table import Table
from core.monster import Monster
from core.npc import NPC
from core.player import Player
from core.users.master_user import MasterUser
from core.users.player_user import PlayerUser

# Configuração Base
app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key")

# Firebase setup
firebase_enabled = False
try:
    from services.firebase_service import save_table, get_table, save_entity, save_user, get_entity
    from firebase_admin import db
    firebase_enabled = True
except: pass

local_tables, local_entities, local_passwords = {}, {}, {}

def persist_table(t):
    if firebase_enabled: save_table(t)
    local_tables[t.id] = t

def load_table(tid):
    if firebase_enabled: return get_table(tid)
    return local_tables.get(tid)

def persist_entity(e):
    if firebase_enabled: save_entity(e)
    local_entities[e.id] = e

def load_entity(eid):
    if firebase_enabled: return get_entity(eid)
    return local_entities.get(eid)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/login/master', methods=['POST'])
def master_login():
    data = request.json
    tid = data.get('table_id')
    pwd = data.get('password')
    
    # Se forneceu ID, tenta validar senha
    if tid:
        table = load_table(tid)
        if not table: return jsonify({"status": "error", "message": "Mesa não encontrada"}), 404
        if local_passwords.get(f"{tid}_MASTER") != pwd:
            return jsonify({"status": "error", "message": "Senha incorreta"}), 401
    
    return jsonify({"status": "success", "role": "master", "table_id": tid})

@app.route('/api/login/player', methods=['POST'])
def player_login():
    data = request.json
    table = load_table(data.get('table_id'))
    if not table: return jsonify({"status": "error", "message": "Mesa inválida"}), 404
    
    # Procura jogador pelo nome
    for eid in table.entity_ids:
        ent = load_entity(eid)
        if ent and hasattr(ent, 'character_class') and ent.name == data.get('username'):
            return jsonify({"status": "success", "char_id": ent.id, "table_id": table.id})
    return jsonify({"status": "needs_creation", "table_id": table.id})

@app.route('/api/table/create', methods=['POST'])
def create_table():
    data = request.json
    t = Table(name=data.get('table_name'), master_user_id="MASTER")
    persist_table(t)
    if data.get('password'): local_passwords[f"{t.id}_MASTER"] = data.get('password')
    return jsonify({"status": "success", "table_id": t.id})

@app.route('/api/player/create_character', methods=['POST'])
def create():
    data = request.json
    p = Player(name=data.get('username'), max_hp=20, level=1, character_class=data.get('char_class'))
    persist_entity(p)
    table = load_table(data.get('table_id'))
    table.add_entity(p)
    persist_table(table)
    return jsonify({"status": "success", "char_id": p.id, "table_id": table.id})

@app.route('/api/table/<tid>', methods=['GET'])
def get_info(tid):
    t = load_table(tid)
    if not t: return jsonify({"status": "error"}), 404
    p_list, m_list = [], []
    for eid in t.entity_ids:
        ent = load_entity(eid)
        if ent:
            is_p = hasattr(ent, 'character_class')
            d = {"id": ent.id, "name": ent.name, "hp": ent.current_hp, "class": getattr(ent, 'character_class', 'NPC')}
            if is_p: p_list.append(d)
            else: m_list.append(d)
    return jsonify({"name": t.name, "players": p_list, "monsters": m_list})

if __name__ == '__main__': app.run(debug=True)