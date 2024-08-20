# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Détermine le répertoire de base du projet
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')  # Chemin relatif basé sur le répertoire de base
