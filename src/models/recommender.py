import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import logging

class WeightedContentBasedRecommender:
    """
    Système de recommandation basé sur le contenu avec pondérations.
    Version optimisée pour la production.
    """
    
    def __init__(self, 
                 embeddings_path: str,
                 train_data_path: str,
                 split_date: str = "2017-10-10",
                 w_recency: float = 0.25,
                 w_position: float = 0.5,
                 w_category: bool = True):
        """
        Initialize the recommender with optimized parameters.
        """
        self.split_date = pd.to_datetime(split_date)
        self.w_recency = w_recency
        self.w_position = w_position
        self.w_category = w_category
        
        # Chargement des données
        self._load_data(embeddings_path, train_data_path)
        logging.info("WeightedContentBasedRecommender initialized successfully")
    
    def _load_data(self, embeddings_path: str, train_data_path: str):
        """Charge et prépare les données."""
        try:
            # Charger les embeddings
            embeddings_array = pd.read_pickle(embeddings_path)
            self.embeddings = pd.DataFrame(embeddings_array)
            self.embeddings.index.name = "click_article_id"
            
            # Charger les données d'entraînement
            self.train_data = pd.read_pickle(train_data_path)
            
            # Filtrer les embeddings
            valid_articles = set(self.train_data["click_article_id"].unique())
            self.embeddings = self.embeddings.loc[
                self.embeddings.index.intersection(valid_articles), :
            ]
            
            # Précalculer les métriques de popularité
            self.article_popularity = (
                self.train_data["click_article_id"]
                .value_counts(normalize=True)
                .to_dict()
            )
            
            logging.info(f"Loaded {len(self.embeddings)} article embeddings")
            logging.info(f"Loaded {len(self.train_data)} training interactions")
            
        except Exception as e:
            logging.error(f"Error loading data: {str(e)}")
            raise
    
    def _recency_weight(self, date_str):
        """Calcule le poids de récence."""
        delta = (self.split_date - date_str).days
        return np.exp(-self.w_recency * delta)
    
    def _ranking_weight(self, position):
        """Calcule le poids de position de clic."""
        return np.exp(-self.w_position * (position - 1))
    
    def build_user_profile(self, user_id: int) -> pd.Series:
        """Construit un profil utilisateur pondéré."""
        user_df = self.train_data.loc[
            self.train_data["user_id"] == user_id,
            ["click_article_id", "click_timestamp", "click_ranking", "category_id"],
        ]
        
        if user_df.empty:
            return pd.Series(0, index=self.embeddings.columns)
        
        weighted_embeddings = []
        w_user_category = user_df["category_id"].value_counts(normalize=True).to_dict()
        
        for row in user_df.itertuples():
            article_id = row.click_article_id
            if article_id not in self.embeddings.index:
                continue
                
            embedding = self.embeddings.loc[article_id]
            
            # Calculer les poids
            recency_weight = self._recency_weight(row.click_timestamp)
            ranking_weight = self._ranking_weight(row.click_ranking)
            category_weight = w_user_category.get(
                row.category_id, 1.0 / len(w_user_category)
            )
            
            # Combiner les poids
            if self.w_category:
                weight = recency_weight * ranking_weight * category_weight
            else:
                weight = recency_weight * ranking_weight
            
            weighted_embeddings.append(embedding * weight)
        
        if weighted_embeddings:
            return sum(weighted_embeddings) / len(weighted_embeddings)
        else:
            return pd.Series(0, index=self.embeddings.columns)
    
    def recommend(self, user_id: int, k: int = 5) -> dict:
        """Recommande k articles pour un utilisateur."""
        try:
            # Vérifier si l'utilisateur existe
            if user_id not in self.train_data["user_id"].values:
                # Retourner les articles les plus populaires
                popular_articles = list(
                    pd.Series(self.article_popularity)
                    .sort_values(ascending=False)
                    .head(k)
                    .index
                )
                return {
                    "user_id": user_id,
                    "recommendations": popular_articles,
                    "method": "popularity_fallback",
                    "count": len(popular_articles)
                }
            
            # Articles déjà lus
            read_articles = set(
                self.train_data.loc[
                    self.train_data["user_id"] == user_id, "click_article_id"
                ].unique()
            )
            
            # Articles non lus
            articles_not_read = self.embeddings[
                ~self.embeddings.index.isin(read_articles)
            ]
            
            if articles_not_read.empty:
                return {
                    "user_id": user_id,
                    "recommendations": [],
                    "method": "no_new_articles",
                    "count": 0
                }
            
            # Construire le profil utilisateur
            user_profile = self.build_user_profile(user_id)
            
            # Calculer les similarités
            similarities = cosine_similarity(
                articles_not_read.values,
                user_profile.values.reshape(1, -1)
            ).flatten()
            
            # Créer un DataFrame avec les scores
            scores_df = pd.DataFrame({
                "article_id": articles_not_read.index,
                "similarity": similarities
            }).sort_values("similarity", ascending=False)
            
            recommendations = scores_df["article_id"].head(k).tolist()
            
            return {
                "user_id": user_id,
                "recommendations": recommendations,
                "method": "weighted_content_based",
                "count": len(recommendations)
            }
            
        except Exception as e:
            logging.error(f"Error generating recommendations for user {user_id}: {str(e)}")
            return {
                "user_id": user_id,
                "recommendations": [],
                "method": "error",
                "error": str(e),
                "count": 0
            }