import os
from flask import Flask, render_template, request, jsonify
from engine.Dices import execute_roll_command
from core.table import Table
from core.monster import Monster
from core.npc import NPC
from core.player import Player
from core.users.master_user import MasterUser
from core.users.player_user import PlayerUser

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-rpg")

firebase_enabled = False
try:
    from services.firebase_service import save_table, get_table, save_entity, save_user, get_entity
    from firebase_admin import db
    firebase_enabled = True
except: pass

local_tables, local_entities, local_passwords = {}, {}, {}

def persist_table(t):
    if firebase_enabled: 
        save_table(t) # Firebase save já é interno
    local_tables[t.id] = t

def load_table(tid):
    if firebase_enabled:
        t = get_table(tid)
        return t
    return local_tables.get(tid)

def persist_entity(e):
    if firebase_enabled: save_entity(e)
    local_entities[e.id] = e

def load_entity(eid):
    if firebase_enabled: return get_entity(eid)
    return local_entities.get(eid)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/login/player', methods=['POST'])
def player_login():
    data = request.json
    table = load_table(data.get('table_id'))
    if not table: return jsonify({"status": "error", "message": "Mesa inválida"}), 404
    
    char_id = None
    for eid in table.entity_ids:
        ent = load_entity(eid)
        if ent and hasattr(ent, 'character_class') and ent.name == data.get('username'):
            char_id = ent.id
            break
    if char_id: return jsonify({"status": "success", "char_id": char_id, "table_id": table.id})
    return jsonify({"status": "needs_creation", "table_id": table.id})

@app.route('/api/player/create_character', methods=['POST'])
def create():
    data = request.json
    attr = data.get('attributes', {})
    hp = 20 + int(int(attr.get('con', 10)) / 2)
    p = Player(name=data.get('username'), max_hp=hp, level=1, character_class=data.get('char_class'), attributes=attr)
    persist_entity(p)
    table = load_table(data.get('table_id'))
    table.add_entity(p)
    table.add_log(f"⚔️ {p.name} entrou na mesa!")
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
            p_list.append({"id": ent.id, "name": ent.name, "hp": ent.current_hp, "max": ent.max_hp, "class": getattr(ent, 'character_class', 'Player')}) if is_p else m_list.append({"id": ent.id, "name": ent.name, "hp": ent.current_hp, "max": ent.max_hp, "class": getattr(ent, 'monster_type', 'NPC')})
    return jsonify({"name": t.name, "id": t.id, "players": p_list, "monsters": m_list, "logs": getattr(t, 'logs', [])[-15:]})

@app.route('/api/combat/action', methods=['POST'])
def combat():
    data = request.json
    att = load_entity(data.get('attacker_id'))
    tar = load_entity(data.get('target_id')) if data.get('target_id') else None
    roll = execute_roll_command({int(data.get('dice_type')): 1})["total_score"]
    msg = f"🎲 {att.name} ({data.get('action_name')}) -> {roll}"
    if tar:
        if data.get('action_name') == 'Cura': tar.heal(roll)
        else: tar.take_damage(roll)
        persist_entity(tar)
    t = load_table(data.get('table_id'))
    t.add_log(msg)
    persist_table(t)
    return jsonify({"status": "success"})

if __name__ == '__main__': app.run(debug=True)