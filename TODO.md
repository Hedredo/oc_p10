# TODO & Ressources Structurées

## 1. Nettoyage et préparation des données
- [X] Introduction reco kaggle : [Tutoriel d’introduction aux systèmes de recommandation sur Kaggle](https://www.kaggle.com/code/devmaxime/intro-to-recommendation-systems)
- [X] Data kaggle : [Jeu de données d’interactions utilisateurs sur un portail d’actualités](https://www.kaggle.com/datasets/gspmoreira/news-portal-user-interactions-by-globocom#clicks_sample.csv)
- [ ] [Recommenders Team GitHub : Exemples et notebooks](https://github.com/recommenders-team/recommenders)
- [X] [Kaggle : Recommender systems in Python 101](https://www.kaggle.com/code/gspmoreira/recommender-systems-in-python-101)
- [X] Fusionner les fichiers de clicks dans un seul dataframe
- [X] Fusionner les dataframes clicks et metadata
- [X] EDA metadata
- [ ] Supprimer les utilisateurs ayant lu moins de N articles
- [ ] Supprimer les articles ayant été lus moins de N fois
- [ ] Diviser la base de données en train/test selon un point temporel
- [ ] Supprimer les utilisateurs sans historique dans le train
- [ ] Étudier la durée entre deux lectures (fraîcheur des articles) + autres EDA
- [ ] Cleanup EDA

## 2. Approches de recommandation
### 2.1 Item-based (similarité)
- [ ] lire le notebook pour l'idée de base line , metriques ,e tc...
- [ ] Implémenter la recommandation item-based (cosinus, embeddings)
- [ ] [Tuto CF Based RealPython : Créer un moteur de recommandation collaboratif](https://realpython.com/build-recommendation-engine-collaborative-filtering/)
- [X] https://medium.com/cometheartbeat/recommender-systems-with-python-part-i-content-based-filtering-5df4940bd831831
- [ ] Concevoir une métrique d’évaluation des performances

### 2.2 Collaborative Filtering (CF)
- [ ] Implémenter le modèle CF (ALS, SVD, etc.)
- [ ] [Tuto Implicit (librairie)](https://github.com/benfred/implicit)
- [ ] [Tuto CF ALS & Implicit Medium](https://medium.com/radon-dev/als-implicit-collaborative-filtering-5ed653ba39fe)
- [ ] [Tuto LightFM (hybride)](https://towardsdatascience.com/building-a-recommender-system-with-lightfm-using-python-2f0c8b1d3e4a)
- [ ] [Tuto Surprise (librairie)](https://surprise.readthedocs.io/en/stable/getting_started.html)
- [ ] [Tuto CF Scikit-learn](https://scikit-learn.org/stable/modules/collaborative_filtering.html)
- [X] [Medium : Recommender system with scikit-surprise](https://medium.com/hacktive-devs/recommender-system-made-easy-with-scikit-surprise-569cbb689824)

## 3. Implémentation de l’API Backend
- [ ] Créer une Azure Function en Python
- [ ] Implémenter la fonction de prédiction
- [ ] Créer une API qui prend un identifiant utilisateur et retourne 5 articles recommandés
- [ ] Tester l’API localement
- [ ] Déployer l’API sur Azure Functions
- [ ] Si nécessaire, stockage du modèle sur Azure Blob Storage
- [ ] [Doc Azure Functions (scalabilité)](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [ ] [Azure Functions Python dev guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference?tabs=blob&pivots=programming-language-python)
- [ ] [Créer une Azure Function avec VS Code (fr)](https://learn.microsoft.com/fr-fr/azure/azure-functions/create-first-function-vs-code-python)
- [ ] [Module de formation serverless Azure](https://learn.microsoft.com/fr-fr/training/modules/create-serverless-logic-with-azure-functions/)
- [ ] [Bindings Azure Blob Storage](https://learn.microsoft.com/fr-fr/azure/azure-functions/functions-bindings-storage-blob-input?tabs=python-v2%2Cisolated-process%2Cnodejs-v4&pivots=programming-language-csharp)
- [ ] [Bindings Azure CosmosDB](https://learn.microsoft.com/fr-fr/azure/azure-functions/functions-bindings-cosmosdb-v2-input?tabs=python-v2%2Cisolated-process%2Cnodejs-v4%2Cextensionv4&pivots=programming-language-csharp)
- [ ] [Tuto vidéo Azure Functions 1](https://www.youtube.com/watch?v=2b1a8d9c3f4)
- [ ] [Tuto vidéo Azure Functions 2](https://www.youtube.com/watch?v=6g0j7k5sX6E)
- [ ] [FastAPI on Azure Functions (exemple)](https://github.com/Azure-Samples/fastapi-on-azure-functions/tree/main)
- [ ] [Sample FastAPI on Azure Functions](https://learn.microsoft.com/en-us/samples/azure-samples/fastapi-on-azure-functions/fastapi-on-azure-functions/)
- [ ] [Seuils gratuité Azure (PDF)](https://s3.eu-west-1.amazonaws.com/course.oc-static.com/projects/Ing%C3%A9nieur_IA_P7/Seuils_gratuite%CC%81_Azure.pdf)

## 4. Implémentation du Frontend
- [ ] Choisir un framework (Gradio, Flask ou Streamlit)
- [ ] Créer une interface web avec un champ pour l’identifiant utilisateur
- [ ] Appeler l’API backend et afficher les 5 recommandations
- [ ] Tester l’interface localement
- [ ] Déployer le frontend comme application web
- [ ] [Implémentation d’une interface Gradio](https://www.gradio.app/)
- [ ] [Implémentation d’une interface Streamlit](https://streamlit.io/)

## 5. Intégration & Documentation
- [ ] Vérifier la communication entre le frontend et le backend
- [ ] Valider l’affichage correct des recommandations
- [ ] Préparer la documentation et les instructions de déploiement

## 6. Vidéos avancées et concepts recommandation
- [X] [Introduction aux systèmes de recommandation (YouTube)](https://www.youtube.com/watch?v=YMZmLx-AUvY)
- [ ] [Triggers et bindings dans Azure Functions (YouTube)](https://www.youtube.com/watch?v=9RLbuEnW-6g&list=PLbl2SbVIi-Wo2W81Jyqlv5B375W_EcUsj&index=13)
- [ ] [Playlist complète Azure Function avec VS Code](https://www.youtube.com/watch?v=coT4IlGQLCw&list=PLbl2SbVIi-Wo2W81Jyqlv5B375W_EcUsj)
- [ ] [GNN Short Course Chapter 5 - Recommendation Systems](https://www.youtube.com/watch?v=yHg5ZplW62c)
- [ ] [GReS: Workshop on Graph Neural Networks for Recommendation](https://www.youtube.com/watch?v=VYDMwuImCOE)
- [ ] [Tutorial 3A: Hands-on Explainable Recommender Systems with Knowledge Graphs](https://www.youtube.com/watch?v=qPiIvcCOyBg)
- [ ] [When Graph Neural Networks Meet the Neighborhood](https://www.youtube.com/watch?v=hwNEKB0ie5Q)
- [ ] [Session 2: Effective and Efficient Training for Sequential Recommendation](https://www.youtube.com/watch?v=qeyfR1bj5D0)
- [ ] [Building an AI-Powered Video Recommender](https://www.youtube.com/watch?v=v2ru1mF58I8)
- [ ] [Macro Graph Neural Networks for Online Billion-Scale Recommender Systems](https://www.youtube.com/watch?v=8_htR_v_p2k)
- [ ] [Graph Pretraining and Prompt Learning for Recommendation](https://www.youtube.com/watch?v=eLUoW8LvBic)
- [ ] [KDD 2023 - Criteria Preference-Aware Light Graph Convolution Network](https://www.youtube.com/watch?v=ccCJKixRr7Q)
- [ ] [Introduction to Deep Learning for Recommendation Systems](https://www.youtube.com/watch?v=m-wkCYe1cD4)
- [ ] https://arxiv.org/abs/1808.00076