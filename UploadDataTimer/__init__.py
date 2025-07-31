import logging
import os
import tempfile
import requests
import zipfile
import pandas as pd
from azure.storage.blob import BlobServiceClient
import azure.functions as func

# Pour la compression PCA
from sklearn.decomposition import PCA
import pickle

# Paramètres à personnaliser
ZIP_URL = "https://ton-url-source/ton-fichier.zip"
CONTAINER_NAME = "nom-du-conteneur"
CSV_FILENAME = "ton_fichier.csv"         # Nom du CSV à extraire du ZIP
PARQUET_FILENAME = "ton_fichier.parquet" # Nom du fichier Parquet à uploader
EMBEDDINGS_FILENAME = "articles_embeddings.pickle"  # Nom du pickle à uploader
EMBEDDINGS_BLOB_NAME = "articles_embeddings_compressed.pickle"  # Nom sur le blob
N_COMPONENTS_PCA = 100  # À ajuster selon ton besoin

def ensure_container_exists(blob_service_client, container_name):
    try:
        container_client = blob_service_client.get_container_client(container_name)
        container_client.get_container_properties()
        logging.info(f"✅ Le conteneur '{container_name}' existe déjà.")
    except Exception:
        logging.info(f"🔹 Le conteneur '{container_name}' n'existe pas, création en cours...")
        blob_service_client.create_container(container_name)
        logging.info(f"✅ Conteneur '{container_name}' créé avec succès.")

def download_zip(url, dest_path):
    try:
        logging.info(f"🔹 Téléchargement de {url} ...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info("✅ Téléchargement terminé !")
    except Exception as e:
        logging.error(f"❌ Erreur lors du téléchargement : {e}")
        raise

def extract_zip(zip_path, extract_to):
    try:
        logging.info(f"🔹 Extraction de {zip_path} ...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        logging.info("✅ Extraction terminée !")
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'extraction : {e}")
        raise

def convert_csv_to_parquet(csv_path, parquet_path):
    try:
        logging.info(f"🔹 Conversion {csv_path} → {parquet_path} ...")
        df = pd.read_csv(csv_path)
        df.to_parquet(parquet_path)
        logging.info("✅ Conversion terminée !")
    except Exception as e:
        logging.error(f"❌ Erreur lors de la conversion CSV → Parquet : {e}")
        raise

def compress_embeddings_with_pca(pickle_path, compressed_pickle_path, n_components=100):
    try:
        logging.info(f"🔹 Compression PCA de {pickle_path} ...")
        with open(pickle_path, "rb") as f:
            embeddings = pickle.load(f)
        # Si embeddings est un DataFrame ou ndarray
        pca = PCA(n_components=n_components)
        embeddings_reduced = pca.fit_transform(embeddings)
        with open(compressed_pickle_path, "wb") as f:
            pickle.dump(embeddings_reduced, f)
        logging.info(f"✅ Compression PCA terminée ({n_components} composantes).")
    except Exception as e:
        logging.error(f"❌ Erreur lors de la compression PCA : {e}")
        raise

def upload_to_blob(blob_service_client, container_name, file_path, blob_name):
    try:
        logging.info(f"🔹 Upload de {file_path} vers Azure Blob Storage ({container_name}/{blob_name}) ...")
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        logging.info("✅ Upload terminé !")
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'upload sur Azure Blob Storage : {e}")
        raise

def main(mytimer: func.TimerRequest) -> None:
    logging.info("=== Début de la tâche planifiée UploadDataTimer ===")
    try:
        # Récupérer la chaîne de connexion depuis les variables d'environnement Azure
        BLOB_CONNECTION_STRING = os.environ["AzureWebJobsStorage"]
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

        # Vérifier/créer le conteneur
        ensure_container_exists(blob_service_client, CONTAINER_NAME)

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "data.zip")
            download_zip(ZIP_URL, zip_path)
            extract_zip(zip_path, tmpdir)

            # CSV → Parquet
            csv_path = os.path.join(tmpdir, CSV_FILENAME)
            parquet_path = os.path.join(tmpdir, PARQUET_FILENAME)
            if not os.path.exists(csv_path):
                logging.error(f"❌ Fichier CSV {CSV_FILENAME} introuvable après extraction.")
            else:
                convert_csv_to_parquet(csv_path, parquet_path)
                upload_to_blob(blob_service_client, CONTAINER_NAME, parquet_path, PARQUET_FILENAME)

            # Embeddings pickle → PCA compressé → upload
            embeddings_path = os.path.join(tmpdir, EMBEDDINGS_FILENAME)
            compressed_embeddings_path = os.path.join(tmpdir, EMBEDDINGS_BLOB_NAME)
            if not os.path.exists(embeddings_path):
                logging.error(f"❌ Fichier embeddings {EMBEDDINGS_FILENAME} introuvable après extraction.")
            else:
                compress_embeddings_with_pca(embeddings_path, compressed_embeddings_path, N_COMPONENTS_PCA)
                upload_to_blob(blob_service_client, CONTAINER_NAME, compressed_embeddings_path, EMBEDDINGS_BLOB_NAME)

        logging.info("=== Tâche UploadDataTimer terminée avec succès ===")
    except Exception as e:
        logging.error(f"❌ Erreur dans la fonction UploadDataTimer : {e}")