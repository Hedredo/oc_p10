Voici une synthèse en Markdown sur la méthodologie des deux notebooks, couvrant les différentes approches, la préparation des données, les modèles utilisés, les métriques d’évaluation, la baseline et les résultats.

---

# Synthèse méthodologique des notebooks RecSys

## 1. Préparation et exploration des données

- **Sources de données :**
  - Métadonnées des articles (`articles_metadata.csv` ou `shared_articles.csv`)
  - Logs d’interactions utilisateurs-articles (`clicks_hour_000.csv` ou `users_interactions.csv`)
  - Embeddings d’articles (`articles_embeddings.pickle`)

- **Étapes de préparation :**
  - Nettoyage et filtrage des articles (ex : ne garder que les articles partagés, supprimer les valeurs aberrantes sur le nombre de mots).
  - Agrégation des interactions par utilisateur et article.
  - Pondération des interactions selon leur type (vue, like, commentaire…).
  - Filtrage des utilisateurs avec peu d’interactions (souvent <5) pour éviter le cold-start.
  - Séparation des jeux de données en train/test (holdout, typiquement 20-25% pour le test).

---

## 2. Approches de recommandation testées
### a. **Baseline / Popularity Model**
- Recommande les articles les plus populaires à tous les utilisateurs.
- Sert de référence minimale pour évaluer les autres modèles.

### b. **Content-Based Filtering**
- **Par catégorie** : Recommande les articles des catégories préférées de l’utilisateur, selon ses clics passés.
- **Par embeddings** : Utilise les embeddings d’articles pour calculer la similarité (cosinus) entre articles lus et articles à recommander.
- **TF-IDF** : Construction de profils utilisateurs et articles à partir du texte, puis recommandation par similarité.

### c. **Collaborative Filtering**
- **Matrix Factorization (SVD)** : Factorisation de la matrice utilisateur-article pour prédire les préférences.
- **Librairie Surprise** : Utilisation de SVD sur une matrice utilisateur/catégorie, évaluation par RMSE et top-N.

### d. **Hybrid Model**
- Combine les scores des modèles content-based et collaborative filtering (pondération ajustable).
- Vise à tirer parti des forces de chaque approche.

---

## 3. Métriques d’évaluation

### 3.1. **GPT recommendation metrics**
- **Recall@N** : Taux de présence des articles réellement consultés dans le top-N des recommandations (N=5, 10).
- **RMSE** : Pour la prédiction de notes (utilisé avec Surprise).
- **Comparaison des modèles** : Les performances sont comparées à la baseline (popularity) et entre elles via des graphiques.

### 3.2. **Introduction des métriques**

Recommandations & rankings systems ont un objectif en commun : retourner une liste d'articles triés par pertinence pour un utilisateur donné.



---

## 4. Résultats principaux

- **Baseline (Popularité)** : Recall@5 ≈ 24%, Recall@10 ≈ 37%
- **Content-Based Filtering** :
  - Par catégorie : résultats proches de la baseline.
  - Par TF-IDF : Recall@5 ≈ 16%, Recall@10 ≈ 26%
  - Par embeddings : permet une personnalisation plus fine, mais coûteux en ressources.
- **Collaborative Filtering (SVD)** : Recall@5 ≈ 33%, Recall@10 ≈ 46%
- **Hybrid Model** : Recall@5 ≈ 34%, Recall@10 ≈ 48% (meilleure performance globale)

---

## 5. Limites et pistes d’amélioration

- **Cold-start** : Difficulté à recommander pour les nouveaux utilisateurs ou articles.
- **Ressources** : Les méthodes par embeddings peuvent être limitées par la RAM/CPU.
- **Contextualisation** : Prendre en compte le temps, le device, la localisation, etc.
- **Modèles avancés** : Deep learning, factorisation avancée, frameworks spécialisés (Surprise, Spark ALS…).

---

## 6. Conclusion

- Les modèles hybrides surpassent les approches individuelles.
- La méthodologie proposée permet de comparer objectivement différentes stratégies de recommandation sur des données réelles.
- Les notebooks constituent une base solide pour explorer, tester et améliorer des systèmes de recommandation.

---