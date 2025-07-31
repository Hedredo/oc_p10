from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import pickle

# Connexion au blob storage
blob_service_client = BlobServiceClient.from_connection_string("<ta_chaine_de_connexion>")
container_client = blob_service_client.get_container_client("<nom_du_conteneur>")

# Lire un fichier Parquet
blob_client = container_client.get_blob_client("ton_fichier.parquet")
parquet_bytes = blob_client.download_blob().readall()
df = pd.read_parquet(io.BytesIO(parquet_bytes))

# Lire un fichier Pickle
blob_client = container_client.get_blob_client("articles_embeddings_compressed.pickle")
pickle_bytes = blob_client.download_blob().readall()
embeddings = pickle.loads(pickle_bytes)