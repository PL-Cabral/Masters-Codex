import firebase_admin

from firebase_admin import credentials
from firebase_admin import db

# Caminho da chave privada do Firebase
FIREBASE_KEY_PATH = "secrets/firebase_key.json"

# Copie essa URL direto do seu Realtime Database no Firebase Console
DATABASE_URL = "https://masters-codex-default-rtdb.firebaseio.com/"

# Inicializa o Firebase apenas uma vez
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)

    firebase_admin.initialize_app(cred, {
        "databaseURL": DATABASE_URL
    })

def save_entity(table_id, entity):
    entity.table_id = table_id

    data = entity.to_dict()

    ref = db.reference(f"tables/{table_id}/entities/{entity.id}")
    ref.set(data)

    return entity.id