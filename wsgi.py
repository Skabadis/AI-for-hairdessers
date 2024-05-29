import sys
import os
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Ajouter le chemin src au sys.path pour pouvoir importer main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
