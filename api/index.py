import os
import sys

# Garante que a Vercel consiga enxergar as pastas 'core', 'services' e o 'app.py' na raiz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa a aplicação Flask do seu arquivo app.py
from app import app