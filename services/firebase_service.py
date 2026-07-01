from pathlib import Path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from core.table import Table
from core.player import Player
from core.monster import Monster
from core.npc import NPC

from core.users.master_user import MasterUser
from core.users.player_user import PlayerUser

BASE_DIR = Path(__file__).resolve().parent.parent

FIREBASE_CREDENTIALS_PATH = (
    BASE_DIR / "secrets" / "firebase_key.json"
)

DATABASE_URL = ("https://masters-codex-default-rtdb.firebaseio.com/")

if not firebase_admin._apps:
    cred = credentials.Certificate(
        FIREBASE_CREDENTIALS_PATH
    )

    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": DATABASE_URL
        }
    )

def save_user(user):
    ref = db.reference(
        f"users/{user.id}"
    )

    ref.set(
        user.to_dict()
    )

    return user.id

def get_user(user_id):
    ref = db.reference(
        f"users/{user_id}"
    )

    data = ref.get()

    if data is None:
        return None

    user_type = data.get("user_type")

    if user_type == "master":
        return MasterUser.from_dict(data)

    if user_type == "player":
        return PlayerUser.from_dict(data)

    raise ValueError(
        f"Tipo de usuário inválido: {user_type}"
    )

def get_user_by_username(username):
    username = username.strip()

    if username == "":
        return None

    ref = db.reference("users")
    users = ref.get()

    if users is None:
        return None

    for _, user_data in users.items():
        if user_data.get("username") == username:
            user_type = user_data.get("user_type")

            if user_type == "master":
                return MasterUser.from_dict(user_data)

            if user_type == "player":
                return PlayerUser.from_dict(user_data)

            raise ValueError(
                f"Tipo de usuário inválido: {user_type}"
            )

    return None

def delete_user(user_id):
    ref = db.reference(
        f"users/{user_id}"
    )

    ref.delete()

def save_table(table):
    ref = db.reference(
        f"tables/{table.id}"
    )

    ref.set(
        table.to_dict()
    )

    return table.id

def get_table(table_id):
    ref = db.reference(
        f"tables/{table_id}"
    )

    data = ref.get()

    if data is None:
        return None

    return Table.from_dict(data)

def delete_table(table_id):
    ref = db.reference(
        f"tables/{table_id}"
    )

    ref.delete()

def save_entity(entity):
    ref = db.reference(
        f"entities/{entity.id}"
    )

    ref.set(
        entity.to_dict()
    )

    return entity.id

def get_entity(entity_id):
    ref = db.reference(
        f"entities/{entity_id}"
    )

    data = ref.get()

    if data is None:
        return None

    entity_type = data.get("entity_type")

    if entity_type == "player":
        return Player.from_dict(data)

    if entity_type == "monster":
        return Monster.from_dict(data)

    if entity_type == "npc":
        return NPC.from_dict(data)

    raise ValueError(
        f"Tipo de entidade inválido: {entity_type}"
    )

def delete_entity(entity_id):
    ref = db.reference(
        f"entities/{entity_id}"
    )

    ref.delete()

def entity_exists(entity_id):
    ref = db.reference(
        f"entities/{entity_id}"
    )

    return ref.get() is not None

def table_exists(table_id):
    ref = db.reference(
        f"tables/{table_id}"
    )

    return ref.get() is not None

def user_exists(user_id):
    ref = db.reference(
        f"users/{user_id}"
    )

    return ref.get() is not None

def ping_database():
    ref = db.reference("/")

    return ref.get()