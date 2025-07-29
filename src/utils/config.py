import os
from pathlib import Path

# Configuration des chemins
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Chemins des fichiers de données
EMBEDDINGS_PATH = DATA_DIR / "workbase" / "articles_embeddings.pickle"
TRAIN_DATA_PATH = DATA_DIR / "workbase" / "train_filtered_10.pickle"

# Configuration du modèle
DEFAULT_K = 5
DEFAULT_W_RECENCY = 0.25
DEFAULT_W_POSITION = 0.5
DEFAULT_W_CATEGORY = True
DEFAULT_SPLIT_DATE = "2017-10-10"

# Configuration Azure Functions
FUNCTIONS_WORKER_RUNTIME = "python"
FUNCTIONS_EXTENSION_VERSION = "~4"