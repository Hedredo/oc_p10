# Standard library imports
from datetime import datetime
from abc import ABC, abstractmethod

# Third-party imports
import pandas as pd
import numpy as np


class Recommender(ABC):
    """
    Abstract base class for recommender systems that provides a common interface.
    Choose a value for k to define the number of recommendations to return and to evaluate, as metric@k.
    """

    def __init__(self, k: int, train_data: pd.DataFrame):
        self.k = k
        self.train_data = train_data

    @abstractmethod
    def fit_transform(self, test_data: pd.DataFrame) -> None:
        """
        Fit the recommender model to the training data.

        Args:
            data (pd.DataFrame): The training data.
        """
        pass

    @abstractmethod
    def recommend(self, user_id: int) -> list[int]:
        """
        Recommend items for a given user.

        Args:
            user_id (int): The ID of the user to recommend items for.
        Returns:
            list[int]: A list of recommended item IDs.
        """
        pass

    def evaluate(self, test_data: pd.DataFrame) -> dict:
        """
        Evaluate the recommender model on the test data.

        Args:
            test_data (pd.DataFrame): The test data containing user-item interactions.
        Returns:
            float: The evaluation metric score (e.g., precision, recall, etc.).
        """
        # Fit the model and transform the test data
        self.fit_transform(test_data)

        # Instantiate lists to store evaluation metrics
        hits, precisions, recalls, f1s = [], [], [], []

        # Iterate over each user in the test data
        for user_id in test_data["user_id"].unique():
            true_items = set(
                test_data.loc[
                    test_data["user_id"] == user_id, "click_article_id"
                ].unique()
            )
            # If a user has no true items, skip evaluation for this user
            if not true_items:
                continue

            recommended_items = self.recommend(user_id)
            top_k = set(recommended_items[: self.k])
            n_hit = len(true_items & top_k)

            hit = 1.0 if n_hit > 0 else 0.0
            precision = n_hit / len(top_k)
            recall = n_hit / len(true_items)
            f1 = (
                2 * precision * recall / (precision + recall)
                if precision + recall > 0
                else 0.0
            )

            hits.append(hit)
            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)

        return {
            f"Hit@{self.k}": np.mean(hits).round(4),
            f"Precision@{self.k}": np.mean(precisions).round(4),
            f"Recall@{self.k}": np.mean(recalls).round(4),
            f"F1@{self.k}": np.mean(f1s).round(4),
        }
    
class PopularityRecommender(Recommender):
    """
    Recommender system that recommends items based on their popularity.
    """

    def __init__(self, k: int, train_data: pd.DataFrame):
        super().__init__(k, train_data)
        self.train_article_popularity = None
        self.train_category_popularity = None
        self.article_popularity = None

    def fit_transform(self, test_data: pd.DataFrame) -> None:
        """
        Fit the recommender model to the training data by calculating item popularity.
        """
        self.train_article_popularity = (
            self.train_data["click_article_id"].value_counts(normalize=True).to_dict()
        )
        self.train_category_popularity = (
            self.train_data["category_id"].value_counts(normalize=True).to_dict()
        )

        # Create a Series with article popularity for test articles
        test_article_popularity = (
            test_data["click_article_id"]
            .drop_duplicates()
            .map(lambda x: self.train_article_popularity.get(x, np.nan))
        )

        # Fill NaN values with category popularity (using the article's category)
        article_to_category = test_data.drop_duplicates("click_article_id").set_index(
            "click_article_id"
        )["category_id"]
        test_article_popularity = test_article_popularity.fillna(
            article_to_category.map(self.train_category_popularity)
        ).to_dict()
        # Create a Series with article popularity from both train and test data
        self.article_popularity = pd.Series(
            {**self.train_article_popularity, **test_article_popularity}
        ).sort_values(ascending=False)

    def recommend(self, user_id: int) -> list[int]:
        """
        Recommend items for a given user based on item popularity.
        """
        if self.article_popularity is None:
            raise ValueError("Model has not been fitted yet.")

        try:
            read_articles = set(
                self.train_data.loc[
                    self.train_data["user_id"] == user_id, "click_article_id"
                ].unique()
            )
        except KeyError:
            print(f"User ID {user_id} not found in the training data.")

        # Get the article popularity
        articles_not_read = self.article_popularity[
            ~self.article_popularity.index.isin(read_articles)
        ]
        # Filter out the articles already read by the user
        recommendations = articles_not_read.head(self.k)
        # Return the top N recommendations
        return recommendations.index.tolist()

class ContentBasedRecommender(Recommender):
    """
    Recommender system that recommends items based on content similarity.
    """

    def __init__(
        self,
        k: int,
        train_data: pd.DataFrame,
        embeddings: np.ndarray,
    ):
        super().__init__(k, train_data)
        self.embeddings = embeddings
        self.valid_articles_ids = None

    def get_valid_articles_ids(self, test_data: pd.DataFrame) -> set[int] :
        """
        Get the set of valid article IDs that can be recommended.
        Returns:
            set[int]: A set of valid article IDs.
        """
        return set(self.train_data["click_article_id"].unique()) | set(
            test_data["click_article_id"].unique()
        )

    def fit_transform(self, test_data: pd.DataFrame) -> None:
        """
        Fit the recommender model to the training data by loading embeddings.
        """
        self.embeddings = pd.DataFrame(self.embeddings)
        self.embeddings.index.name = "click_article_id"
        # Filter the embeddings to only include articles present in the train and test data
        self.valid_articles_ids = self.get_valid_articles_ids(test_data)
        self.embeddings = self.embeddings.loc[
            self.embeddings.index.intersection(self.valid_articles_ids), :
        ]

    def build_user_profile(self, user_id: int, read_articles: set[int]) -> pd.Series:
        """
        Build a user profile based on the embeddings of articles read by the user.
        """
        if self.embeddings is None:
            raise ValueError("Model has not been fitted yet.")

        # Get the embeddings of articles read by the user
        read_embeddings = self.embeddings.loc[list(read_articles)]

        # Calculate the mean embedding for the user's read articles
        user_profile = read_embeddings.mean(axis=0)

        return user_profile

    def recommend(self, user_id: int) -> list[int]:
        """
        Recommend items for a given user based on content similarity.
        """
        if self.valid_articles_ids is None:
            raise ValueError("Model has not been fitted yet.")

        read_articles = set(
            self.train_data.loc[
                self.train_data["user_id"] == user_id, "click_article_id"
            ].unique()
        )

        # Get the embeddings of articles not read by the user
        articles_not_read = self.embeddings[~self.embeddings.index.isin(read_articles)]

        # Calculate similarity scores with the mean embedding of read articles
        scores = articles_not_read.dot(self.build_user_profile(user_id, read_articles))

        # Get the top N recommendations based on scores
        recommendations = scores.nlargest(self.k)

        return recommendations.index.tolist()

class WeightedContentBasedRecommender(ContentBasedRecommender):
    """
    Recommender system that recommends items based on content similarity with user preferences weighted according to article categories, recency and click position.
    """

    def __init__(
        self,
        k: int,
        train_data: pd.DataFrame,
        split_date: datetime,
        embeddings: np.ndarray,
        w_recency: float = .35,
        w_position: float = .75,
        w_category: bool = True,
    ):
        super().__init__(k, train_data, embeddings)
        self.w_recency = w_recency
        self.w_position = w_position
        self.split_date = split_date
        self.w_category = w_category
        self.w_user_category = None

    def recency_weight(self, date_str: datetime) -> float:
        delta = (self.split_date - date_str).days
        return np.exp(-self.w_recency * delta)

    def ranking_weight(self, position: int) -> float:
        return np.exp(-self.w_position * (position - 1))

    def build_user_profile(self, user_id: int, read_articles: set[int]) -> pd.Series:
        """
        Build a user profile based on the embeddings of articles read by the user.
        """
        if self.embeddings is None:
            raise ValueError("Model has not been fitted yet.")

        # Build the weighted user profile
        weighted_embeddings = []
        # Get the DataFrame of articles read by the user
        user_df = self.train_data.loc[
            self.train_data["user_id"] == user_id,
            ["click_article_id", "click_timestamp", "click_ranking", "category_id"],
        ]
        self.w_user_category = (
            user_df["category_id"].value_counts(normalize=True).to_dict()
        )

        # Iterate through each read article to calculate the weighted embedding
        for row in user_df.itertuples():
            article_id = row.click_article_id
            # Get the embedding for the article
            embedding = self.embeddings.loc[article_id]

            # Calculate weights
            recency_weight = self.recency_weight(row.click_timestamp)
            ranking_weight = self.ranking_weight(row.click_ranking)
            category_weight = self.w_user_category.get(
                row.category_id, 1.0 / sum(self.w_user_category.values())
            )

            # Combine weights
            weight = (
                recency_weight * ranking_weight * category_weight
                if self.w_category
                else recency_weight * ranking_weight
            )

            # Append weighted embedding
            weighted_embeddings.append(embedding * weight)

        user_profile = (
            sum(weighted_embeddings) / len(weighted_embeddings)
            if weighted_embeddings
            else pd.Series(dtype=float)
        )

        return user_profile