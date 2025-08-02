import pandas as pd
from glob import glob
import requests
import zipfile
import os
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import shutil
import tempfile
import logging
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from azure.storage.blob import BlobServiceClient
import azure.functions as func


# Customizable parameters
ZIP_URL = os.environ["ZIP_URL"]  # URL of the ZIP file to download
BLOB_CONNECTION_STRING = os.environ["AzureWebJobsStorage"]  # Connection string
CONTAINER_NAME = os.environ["CONTAINER_NAME"]
PCA_N_COMPONENTS = float(os.environ["PCA_N_COMPONENTS"])  # Variance percentage to keep for PCA
THRESHOLD_DT = int(os.environ["THRESHOLD_DT"])  # Minimum clicks per day to keep the date
EMBEDDINGS_BLOB_NAME = os.environ["EMBEDDINGS_BLOB_NAME"]  # Name
PICKLE_BLOB_NAME = os.environ["PICKLE_BLOB_NAME"]         # Name of the CSV to extract from the ZIP

def ensure_container_exists(blob_service_client: BlobServiceClient, container_name: str) -> None:
    """Ensure the Azure Blob Storage container exists."""
    try:
        container_client = blob_service_client.get_container_client(container_name)
        container_client.get_container_properties()
        logging.info(f"Container '{container_name}' already exists.")
    except Exception:
        logging.info(f"🔹 Container '{container_name}' does not exist, creating...")
        blob_service_client.create_container(container_name)
        logging.info(f"✅ Container '{container_name}' created successfully.")

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True,
)
def download_and_extract_zip(url: str, extract_to: str) -> None:
    """Download a zip file from a URL and extract it to a specified directory, with retry."""
    try:
        logging.info(f"Downloading ZIP from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        logging.info("ZIP downloaded successfully.")
        zip_path = os.path.join(extract_to, "data.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        os.remove(zip_path)
        if os.path.exists(os.path.join(extract_to, "clicks_sample.csv")):
            os.remove(os.path.join(extract_to, "clicks_sample.csv"))
        logging.info("ZIP extracted with success.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Download error: {e}, retrying...")
        raise
    except zipfile.BadZipFile as e:
        logging.error(f"Decompression error: {e}, aborting operation.")
        raise

def compress_embeddings(extract_to: str, n_components: float|int, 
                        embeddings_filename: str) -> None:
    """Compress embeddings using PCA."""
    # Ensure the directory exists
    os.makedirs(extract_to, exist_ok=True)
    # Load the embeddings
    embeddings = pd.read_pickle(os.path.join(extract_to, "articles_embeddings.pickle"))
    if getattr(embeddings, "size", 0) == 0:
        logging.error("No embeddings found to compress.")
        return
    # Standardize the embeddings
    scaler = StandardScaler()
    pca = PCA(n_components=n_components)
    embeddings_scaled = scaler.fit_transform(embeddings)
    embeddings_pca = pca.fit_transform(embeddings_scaled)
    logging.info(f"Reduced embeddings to {embeddings_pca.shape[1]} dimensions.")
    # export as pickle
    with open(os.path.join(extract_to, embeddings_filename), "wb") as f:
        pd.to_pickle(embeddings_pca, f)
    logging.info(f"Embeddings compressed and saved as {embeddings_filename}.")
    os.remove(os.path.join(extract_to, "articles_embeddings.pickle"))
    logging.info("Original embeddings file removed.")

def _unzip_clicks_data(extract_to: str) -> None:
    """Unzip clicks data from the specified directory."""
    zip_path = os.path.join(extract_to, "clicks.zip")
    if not os.path.exists(zip_path):
        logging.error(f"ZIP file not found: {zip_path}")
        return
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    logging.info("Clicks data unzipped successfully.")
    os.remove(zip_path)
    logging.info("Original ZIP file removed.")

def _clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the DataFrame by removing rows with NaN values and duplicates."""
    initial_shape = df.shape
    df = df.dropna()
    df = df.drop_duplicates()
    final_shape = df.shape
    logging.info(f"Data cleaned: {initial_shape[0] - final_shape[0]} rows removed.")
    return df

def _optimize_data_types(df: pd.DataFrame, timestamp_cols: list[str] = None) -> pd.DataFrame:
    """Optimize data types of a DataFrame."""
    if timestamp_cols is not None:
        # Convert timestamp columns to datetime and numeric types to best integer type to save memory
        df = df.assign(
            **{
                col: lambda df, col=col: pd.to_datetime(df[col], unit="ms")
                for col in timestamp_cols
            }
        )
    else:
        timestamp_cols = []
    df = df.assign(
        **{
            col: lambda df, col=col: pd.to_numeric(df[col], downcast="integer")
            for col in df.columns
            if col not in timestamp_cols
        }
    )
    logging.info("Data types optimized.")
    return df

def _filter_dates(clicks_df: pd.DataFrame, threshold: int) -> pd.DataFrame:
    daily_clicks = (
        clicks_df.set_index("click_timestamp")
        .resample("D")
        .size()
        .reset_index(name="nb_clicks")
    )
    shape = daily_clicks.shape
    filtered = daily_clicks.loc[
        daily_clicks["nb_clicks"] >= threshold, "click_timestamp"
    ].dt.date
    logging.info(
        f"Filtered {shape[0] - filtered.shape[0]} dates with less than {threshold} clicks."
    )
    clicks_df_filtered = clicks_df[clicks_df["click_timestamp"].dt.date.isin(filtered)]
    return clicks_df_filtered

def _create_features(clicks_df: pd.DataFrame) -> pd.DataFrame:
    """Create features as article popularity and click_ranking from clicks data."""
    # Compute article popularity
    clicks_df = clicks_df.merge(
        clicks_df["click_article_id"]
        .value_counts(normalize=True)
        .rename("article_popularity")
        .reset_index(),
        on="click_article_id",
        how="left",
    )
    # Create click_ranking
    clicks_df = clicks_df.sort_values(
        ["session_start", "click_timestamp"], ascending=True
    ).assign(
        **{
            "click_ranking": lambda df: df.groupby("session_id")["click_timestamp"]
            .rank(method="first")
            .astype(int),
        }
    )
    logging.info("Features created: article_popularity and click_ranking.")
    return clicks_df

def load_clicks_data(extract_to: str, threshold: int) -> pd.DataFrame:
    """Load clicks data from the extracted directory."""
    clicks_dir = os.path.join(extract_to, "clicks")
    # Unzip clicks data if not already done
    if not os.path.exists(clicks_dir):
        _unzip_clicks_data(extract_to)
    clicks_files = glob(os.path.join(clicks_dir, "*.csv"))
    if not clicks_files:
        logging.error("No clicks data files found.")
        return pd.DataFrame()
    clicks_df = pd.concat((pd.read_csv(f) for f in clicks_files), ignore_index=True)
    logging.info(f"Loaded {len(clicks_df)} rows of clicks data.")
    # remove the clicks directory and its files
    if os.path.exists(clicks_dir):
        shutil.rmtree(clicks_dir)
        logging.info(f"Removed clicks directory: {clicks_dir}")
    # Clean the data
    clicks_df = _clean_data(clicks_df)
    # Optimize data types
    timestamp_cols = ["session_start", "click_timestamp"]
    clicks_df = _optimize_data_types(clicks_df, timestamp_cols)
    # Filter dates with less than 1000 clicks
    clicks_df = _filter_dates(clicks_df, threshold=threshold)
    # Create features
    clicks_df = _create_features(clicks_df.iloc[:, :6])  # Keep only the first 6 columns
    return clicks_df

def load_articles_data(extract_to: str) -> pd.DataFrame:
    """Load articles data from the extracted directory."""
    # Check if articles directory exists
    articles_path = os.path.join(extract_to, "articles_metadata.csv")
    if not os.path.exists(articles_path):
        logging.error(f"Articles data file not found: {articles_path}")
        return pd.DataFrame()
    articles_df = pd.read_csv(articles_path).sort_values("article_id", ascending=True)
    logging.info(f"Loaded {len(articles_df)} rows of articles data.")
    # Clean the data
    articles_df = _clean_data(articles_df)
    # Optimize data types
    timestamp_cols = ["created_at_ts"]
    articles_df = _optimize_data_types(articles_df, timestamp_cols)
    os.remove(articles_path)  # Remove the original articles file
    logging.info(f"Removed original articles file: {articles_path}")
    return articles_df

def etl_pipeline_clicks_articles(extract_to: str, threshold: int, merged_file: str) -> pd.DataFrame:
    """Load merged clicks and articles data."""
    clicks_df = load_clicks_data(extract_to, threshold=threshold)
    if clicks_df.empty:
        logging.error("Clicks data is empty, cannot merge.")
        return pd.DataFrame()
    articles_df = load_articles_data(extract_to)
    if articles_df.empty:
        logging.error("Articles data is empty, cannot merge.")
        return pd.DataFrame()
    # Merge clicks and articles data
    merged_df = clicks_df.merge(
        articles_df, left_on="click_article_id", right_on="article_id", how="left"
    )
    logging.info(f"Merged data contains {len(merged_df)} rows.")
    # Save the merged data as a pickle file
    merged_df.to_pickle(os.path.join(extract_to, merged_file))
    logging.info(
        f"Saved merged data to: {os.path.join(extract_to, merged_file)}"
    )

def upload_to_blob(blob_service_client, container_name, file_path, blob_name):
    try:
        logging.info(f"🔹 Upload de {file_path} vers Azure Blob Storage ({container_name}/{blob_name}) ...")
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        logging.info("Upload ended with success.")
    except Exception as e:
        logging.error(f"Error uploading to Azure Blob Storage: {e}")
        raise

def main(mytimer: func.TimerRequest) -> None:
    """Main function to run the ETL pipeline and upload data to Azure Blob Storage."""
    logging.basicConfig(level=logging.INFO)
    logging.info("=== Starting planified task UploadDataTimer ===")
    try:
        # Récupérer la chaîne de connexion depuis les variables d'environnement Azure
        BLOB_CONNECTION_STRING = os.environ["AzureWebJobsStorage"]
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

        # Vérifier/créer le conteneur
        ensure_container_exists(blob_service_client, CONTAINER_NAME)

        with tempfile.TemporaryDirectory() as tmpdir:
            download_and_extract_zip(ZIP_URL, tmpdir)
            compress_embeddings(tmpdir, n_components=PCA_N_COMPONENTS, embeddings_filename=EMBEDDINGS_BLOB_NAME)
            upload_to_blob(blob_service_client, CONTAINER_NAME, os.path.join(tmpdir, EMBEDDINGS_BLOB_NAME), EMBEDDINGS_BLOB_NAME)
            etl_pipeline_clicks_articles(tmpdir, threshold=THRESHOLD_DT, merged_file=PICKLE_BLOB_NAME)
            upload_to_blob(blob_service_client, CONTAINER_NAME, os.path.join(tmpdir, PICKLE_BLOB_NAME), PICKLE_BLOB_NAME)

        logging.info("=== Task UploadDataTimer ended with success ===")
    except Exception as e:
        logging.error(f"Error in UploadDataTimer function: {e}")