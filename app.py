import os
from flask import Flask, render_template, request, jsonify

# Tratamento de erro de Maiúsculas/Minúsculas no Linux (Vercel) vs Windows
try:
    from engine.dices import execute_roll_command
except ImportError:
    from engine.Dices import execute_roll_command

# Importações originais do seu projeto
from core.table import Table
from core.monster import Monster
from core.npc import NPC
from core.player import Player
from core.users.master_user import MasterUser
from core.users.player_user import PlayerUser

# Força a Vercel a encontrar a pasta templates
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-rpg")

# Inicialização do Firebase
firebase_enabled = False
try:
    from services.firebase_service import save_table, get_table, save_entity, save_user, get_entity, get_user_by_username
    from firebase_admin import db
    firebase_enabled = True
except Exception as error:
    print(f"Aviso: Firebase falhou, operando em modo local. Erro: {error}")

local_tables, local_entities, local_users, local_passwords = {}, {}, {}, {}

# --- FUNÇÕES DE PERSISTÊNCIA ---
def save_table_password(tid, pwd):
    if firebase_enabled:
        try: db.reference(f"passwords/{tid}_MASTER").set(pwd); return
        except: pass
    local_passwords[f"{tid}_MASTER"] = pwd

def check_table_password(tid, pwd):
    if firebase_enabled:
        try: return db.reference(f"passwords/{tid}_MASTER").get() == pwd
        except: pass
    return local_passwords.get(f"{tid}_MASTER") == pwd

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

def persist_table(t):
    if firebase_enabled:
        try: save_table(t); return
        except: pass
    local_tables[t.id] = t

def load_table(tid):
    if firebase_enabled:
        try: return get_table(tid)
        except: pass
    return local_tables.get(tid)

def persist_entity(e):
    if firebase_enabled:
        try: save_entity(e); return
        except: pass
    local_entities[e.id] = e

def load_entity(eid):
    if firebase_enabled:
        try: return get_entity(eid)
        except: pass
    return local_entities.get(eid)

# --- ROTAS DA APLICAÇÃO ---
@app.route('/')
def index():
    return render_template('index.html', firebase=firebase_enabled)

@app.route('/api/login/master', methods=['POST'])
def master_login():
    data = request.json
    tid = data.get('table_id')
    pwd = data.get('password')
    username = data.get('username')

    if not username: return jsonify({"status": "error", "message": "Nome obrigatório."}), 400

    # Carregar Mesa Existente (GM)
    if tid:
        table = load_table(tid)
        if not table: return jsonify({"status": "error", "message": "Mesa não encontrada."}), 404
        if not check_table_password(tid, pwd):
            return jsonify({"status": "error", "message": "Senha do Mestre incorreta!"}), 401
        
        user = load_user(username) or MasterUser(username=username)
        persist_user(user)
        return jsonify({"status": "success", "role": "master", "username": user.username, "table_id": tid})
    
    # Prepara para Criar Nova Mesa (GM)
    user = load_user(username) or MasterUser(username=username)
    persist_user(user)
    return jsonify({"status": "success", "role": "master", "username": user.username})

@app.route('/api/login/player', methods=['POST'])
def player_login():
    data = request.json
    username = data.get('username')
    tid = data.get('table_id')

    if not username or not tid: return jsonify({"status": "error", "message": "Nome e ID da Mesa são obrigatórios."}), 400

    table = load_table(tid)
    if not table: return jsonify({"status": "error", "message": "Mesa inválida ou não encontrada."}), 404
    
    # Verifica se o jogador já existe na mesa (Não usa senha)
    char_id = None
    for eid in table.entity_ids:
        ent = load_entity(eid)
        if ent and hasattr(ent, 'character_class') and ent.name == username:
            char_id = ent.id
            break
            
    if char_id:
        return jsonify({"status": "success", "role": "player", "username": username, "char_id": char_id, "table_id": tid})
    
    # Jogador não existe, precisa criar personagem
    return jsonify({"status": "needs_creation", "username": username, "table_id": tid})

@app.route('/api/table/create', methods=['POST'])
def create_table():
    data = request.json
    t_name = data.get('table_name')
    pwd = data.get('password')
    
    if not t_name or not pwd: return jsonify({"status": "error", "message": "Nome e Senha são obrigatórios."}), 400

    t = Table(name=t_name, master_user_id="MASTER")
    persist_table(t)
    save_table_password(t.id, pwd)
    
    return jsonify({"status": "success", "table_id": t.id})

@app.route('/api/player/create_character', methods=['POST'])
def create_character():
    data = request.json
    username = data.get('username')
    tid = data.get('table_id')
    char_class = data.get('char_class')
    
    p = Player(name=username, max_hp=20, level=1, character_class=char_class)
    persist_entity(p)
    
    table = load_table(tid)
    if not table: return jsonify({"status": "error", "message": "Mesa perdida"}), 404
    
    table.add_entity(p)
    table.add_log(f"⚔️ O jogador(a) [{username}] ingressou como {char_class}!")
    persist_table(table)
    
    return jsonify({"status": "success", "char_id": p.id, "table_id": tid})

@app.route('/api/table/<tid>', methods=['GET'])
def get_info(tid):
    t = load_table(tid)
    if not t: return jsonify({"status": "error"}), 404
    
    p_list, m_list = [], []
    for eid in t.entity_ids:
        ent = load_entity(eid)
        if ent:
            is_p = hasattr(ent, 'character_class')
            ent_data = {
                "id": ent.id, 
                "name": ent.name, 
                "hp": ent.current_hp, 
                "max_hp": ent.max_hp, 
                "class": getattr(ent, 'character_class', getattr(ent, 'monster_type', 'NPC'))
            }
            if is_p: p_list.append(ent_data)
            else: m_list.append(ent_data)
            
    return jsonify({
        "status": "success",
        "name": t.name, 
        "id": t.id, 
        "players": p_list, 
        "monsters": m_list, 
        "logs": getattr(t, 'logs', [])[-15:]
    })

@app.route('/api/table/add_entity', methods=['POST'])
def add_entity():
    data = request.json
    table = load_table(data.get('table_id'))
    if not table: return jsonify({"status": "error"}), 404
    
    ent = Monster(
        name=data.get('name'), 
        max_hp=int(data.get('hp', 10)), 
        level=1, 
        monster_type="Monstro", 
        natural_damage_type="bludgeoning", 
        armor_class=10
    )
    persist_entity(ent)
    table.add_entity(ent)
    table.add_log(f"🔮 O Mestre invocou: {ent.name} (HP: {ent.max_hp})!")
    persist_table(table)
    return jsonify({"status": "success"})

@app.route('/api/combat/action', methods=['POST'])
def combat():
    data = request.json
    att = load_entity(data.get('attacker_id'))
    tar = load_entity(data.get('target_id')) if data.get('target_id') else None
    
    if not att: return jsonify({"status": "error", "message": "Atacante não encontrado"}), 404

    roll = execute_roll_command({int(data.get('dice_type', 20)): 1}).get("total_score", 1)
    action_name = data.get('action_name', 'Ação')
    
    msg = f"🎲 [{att.name}] usou {action_name} e rolou {roll}."
    
    if tar:
        if action_name == 'Cura': 
            tar.heal(roll)
            msg += f" Curou [{tar.name}] em {roll} HP! 💚"
        else: 
            tar.take_damage(roll)
            msg += f" Causou {roll} de dano em [{tar.name}]! 💥"
            if tar.current_hp <= 0:
                msg += f" [{tar.name}] foi derrotado!"
        persist_entity(tar)
        
    t = load_table(data.get('table_id'))
    t.add_log(msg)
    persist_table(t)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)