import azure.functions as func
import json
import logging
import os
from pathlib import Path

# Import local modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.recommender import WeightedContentBasedRecommender
from utils.config import (
    EMBEDDINGS_PATH, 
    TRAIN_DATA_PATH, 
    DEFAULT_K,
    DEFAULT_W_RECENCY,
    DEFAULT_W_POSITION,
    DEFAULT_W_CATEGORY,
    DEFAULT_SPLIT_DATE
)

# Instance globale du recommandeur (chargé une seule fois)
recommender = None

def init_recommender():
    """Initialise le recommandeur au premier appel."""
    global recommender
    if recommender is None:
        try:
            recommender = WeightedContentBasedRecommender(
                embeddings_path=str(EMBEDDINGS_PATH),
                train_data_path=str(TRAIN_DATA_PATH),
                split_date=DEFAULT_SPLIT_DATE,
                w_recency=DEFAULT_W_RECENCY,
                w_position=DEFAULT_W_POSITION,
                w_category=DEFAULT_W_CATEGORY
            )
            logging.info("Recommender initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize recommender: {str(e)}")
            raise

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Fonction principale de l'API de recommandation."""
    logging.info('Recommendation API request received')
    
    try:
        # Initialiser le recommandeur
        init_recommender()
        
        # Extraire les paramètres
        user_id = req.params.get('user_id')
        k = req.params.get('k', DEFAULT_K)
        
        # Vérifier si les paramètres sont dans le body JSON
        if not user_id:
            try:
                req_body = req.get_json()
                if req_body:
                    user_id = req_body.get('user_id')
                    k = req_body.get('k', DEFAULT_K)
            except ValueError:
                pass
        
        # Validation des paramètres
        if not user_id:
            return func.HttpResponse(
                json.dumps({
                    "error": "user_id parameter is required",
                    "usage": "GET /api/recommend?user_id=123&k=5 or POST with JSON body"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        try:
            user_id = int(user_id)
            k = int(k)
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "user_id and k must be integers"}),
                status_code=400,
                mimetype="application/json"
            )
        
        if k <= 0 or k > 50:
            return func.HttpResponse(
                json.dumps({"error": "k must be between 1 and 50"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Générer les recommandations
        result = recommender.recommend(user_id, k)
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in recommendation API: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )