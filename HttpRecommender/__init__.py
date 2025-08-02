import os
import json
import pickle
from pandas import to_datetime

from azure.storage.blob import BlobServiceClient
import azure.functions as func

from .recommender import PopularityRecommender, WeightedContentBasedRecommender

# Connect to blob storage
blob_service_client = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])
container_client = blob_service_client.get_container_client(os.environ["CONTAINER_NAME"])

# Load Pickle data and Embeddings from the blob
blob_client = container_client.get_blob_client(os.environ["PICKLE_BLOB_NAME"])
pickle_bytes = blob_client.download_blob().readall()
clicks_df = pickle.loads(pickle_bytes)

blob_client = container_client.get_blob_client(os.environ["EMBEDDINGS_BLOB_NAME"])
pickle_bytes = blob_client.download_blob().readall()
embeddings = pickle.loads(pickle_bytes)

# Load max date to use as split date for recency weighting
SPLIT_DATE = clicks_df["click_timestamp"].max()
SPLIT_DATE = to_datetime(clicks_df["click_timestamp"].max()).to_pydatetime()

# Main Azure HTTP Trigger function
def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.params.get('user_id')
        if not user_id:
            try:
                req_body = req.get_json()
            except ValueError:
                req_body = None
            if req_body:
                user_id = req_body.get('user_id')
        if not user_id:
            return func.HttpResponse(
                json.dumps({"error": "user_id parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )
        user_id = int(user_id)
        k = int(req.params.get('k', 5))

        # Cold start: if unknown user_id, use PopularityRecommender
        if user_id not in clicks_df['user_id'].values:
            recommender = PopularityRecommender(k=k, train_data=clicks_df)
            recommender.fit_transform(clicks_df)  # We can use the same df for fit here
            recommendations = recommender.recommend(user_id)
            method = "popularity"
        else:
            recommender = WeightedContentBasedRecommender(
                k=k,
                train_data=clicks_df,
                split_date=SPLIT_DATE,
                embeddings=embeddings,
                w_recency=0.35,
                w_position=0.75,
                w_category=True
            )
            recommender.fit_transform(clicks_df)
            recommendations = recommender.recommend(user_id)
            method = "weighted_content_based"

        return func.HttpResponse(
            json.dumps({
                "user_id": user_id,
                "recommendations": recommendations,
                "method": method
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )