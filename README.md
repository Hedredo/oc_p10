# Projet : Système de recommandation d'articles avec Azure Functions

## Description
Ce projet met en place une architecture serverless basée sur Azure Functions pour réaliser un système de recommandation d'articles. Les données sont stockées sur Azure Blob Storage et le pipeline de traitement est automatisé.

Deux Azure Functions principales sont utilisées :
- **UploadDataTimer** : Fonction planifiée (Timer Trigger) qui télécharge, traite et met à jour les données (embeddings, clics, articles) sur Azure Blob Storage à intervalle régulier.
- **HttpRecommender** : Fonction HTTP Trigger qui expose une API permettant d'obtenir des recommandations d'articles pour un utilisateur donné.

## Fonctionnement général
1. **UploadDataTimer**
   - Télécharge un ZIP de données depuis une URL.
   - Décompresse, nettoie et fusionne les données utilisateurs/articles.
   - Applique une réduction de dimension (PCA) sur les embeddings.
   - Upload les fichiers traités sur Azure Blob Storage.
   - Permet de prendre en compte automatiquement les nouveaux utilisateurs et articles à chaque exécution.

2. **HttpRecommender**
   - Récupère les fichiers de données et d'embeddings depuis Azure Blob Storage.
   - Expose une API HTTP pour obtenir des recommandations personnalisées.
   - Si l'utilisateur n'existe pas, propose les articles les plus populaires (cold start).
   - Sinon, utilise un algorithme de recommandation basé sur le contenu et les préférences utilisateur.

## Déploiement et configuration
- Toutes les variables sensibles (chaîne de connexion, noms de blobs, etc.) sont à renseigner dans `local.settings.json` (local) ou dans la configuration Azure (prod).
- Le déploiement peut être automatisé via GitHub Actions.

## Exemple de requête à l'API de recommandation

### En local
```bash
curl "http://localhost:7071/api/HttpRecommender?user_id=123"
```

### En production (exemple)
```bash
curl "https://<votre-app-name>.azurewebsites.net/api/HttpRecommender?user_id=123"
```

- **Paramètres** :
  - `user_id` : identifiant de l'utilisateur pour lequel on souhaite obtenir des recommandations
  - `k` (optionnel) : nombre de recommandations à retourner (par défaut 5)

### Réponse attendue
```json
{
  "user_id": 123,
  "recommendations": [101, 202, 303, 404, 505],
  "method": "weighted_content_based"
}
```

## Organisation du code
- `UploadDataTimer/` : fonction timer pour l'ETL et l'upload des données
- `HttpRecommender/` : fonction HTTP pour l'API de recommandation
- `requirements.txt` : dépendances Python
- `local.settings.json` : variables d'environnement pour le local

## Licence
Ce projet est fourni à titre pédagogique.