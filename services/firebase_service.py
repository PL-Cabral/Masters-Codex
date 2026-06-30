from firebase_admin import credentials
from firebase_admin import db
import firebase_admin

from core.table import Table
from core.entity import Entity
from core.users.user import User

FIREBASE_CREDENTIALS_PATH = "secrets/firebase_key.json"

DATABASE_URL = ("https://masters-codex-default-rtdb.firebaseio.com/")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)

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

    return data

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

    return data

def delete_entity(entity_id):
    ref = db.reference(
        f"entities/{entity_id}"
    )

    ref.delete()

def ping_database():
    ref = db.reference("/")

    return ref.get()