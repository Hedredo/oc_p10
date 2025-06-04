# [OC] Plan d'action pour le projet de recommandation d'articles

- [ ] Définir la structure du projet (dossiers frontend et backend)
- [ ] Préparer la base de données d'articles et les interactions utilisateurs (mock ou réelle)
- [ ] Développer le backend :
    - [ ] Créer une Azure Function en Python
    - [ ] Implémenter le modèle de filtrage collaboratif (CF Based)
    - [ ] Créer une API qui prend un identifiant utilisateur et retourne 5 articles recommandés
    - [ ] Tester l'API localement
    - [ ] Déployer l'API sur Azure Functions
- [ ] Développer le frontend :
    - [ ] Choisir un framework (Gradio, Flask ou Streamlit)
    - [ ] Créer une interface web avec un champ pour l'identifiant utilisateur
    - [ ] Appeler l'API backend et afficher les 5 recommandations
    - [ ] Tester l'interface localement
    - [ ] Déployer le frontend comme application web
- [ ] Intégration :
    - [ ] Vérifier la communication entre le frontend et le backend
    - [ ] Valider l'affichage correct des recommandations
- [ ] Préparer la documentation et les instructions de déploiement

# [MENTOR] Synthèse du cahier des charges et étapes projet

Ce projet est orienté vers la recommandation de contenu, qui est un problème important dans l'industrie (amazon, netflix, cdiscount, spotify, twitter, facebook, instagram, tiktok, partout). Cela consiste à recommander du contenu qui intéresse l'utilisateur, pour cela on peut se baser sur toutes les expériences passées (cookies, interaction avec la plateforme, achat, clic, etc).

Dans le cadre de ce projet, on veut recommander des articles de presse à des utilisateurs de la plateforme. Le dataset est d'ailleurs constitué d'une façon peu habituelle pour le domaine, on va retrouver la liste des articles consultés par chacun des utilisateurs à travers le temps. À vous de préparer le dataset pour avoir d'un côté l'historique des utilisateurs et de l'autre les futurs articles qui seront lus (un genre de train / test en fait).

Les particularités : connecter l'application mobile avec l'API qui sera implémentée avec Azure Functions.

- [Vidéo de présentation](#)
- [Introduction à la recommandation](#)
- [Tuto Implicit](#)
- [Tuto Implicit #2](#)

## 1. Nettoyage des données
- [ ] a. Fusionner les fichiers de clicks dans un seul dataframe
- [ ] b. Fusionner les dataframes clicks et metadata
- [ ] c. Supprimer les utilisateurs ayant lu moins de N articles
- [ ] d. Supprimer les articles ayant été lus moins de N fois

## 2. Préparation des données
- [ ] a. Diviser la base de données en deux en fixant un point temporel qui séparera d'un côté le train (l'historique des articles consulté) et le test (les articles que l'on devrait recommander si la méthode était parfaite)
- [ ] b. Supprimer les utilisateurs si aucune lecture dans la base de train (sans historique, pas de recommandation)
- [ ] c. Étudier la durée entre deux lectures : est-ce utile de recommander un article publié il y a un an, par rapport à un autre publié la semaine dernière ?

## 3. Approche Item based (similarité)
- [ ] a. On recommande un article en utilisant comme point de référence un des articles lus précédemment. ([similarité cosinus](#) des plongements pour calculer la ressemblance). Pour un identifiant utilisateur donné : proposer 5 articles à lire.
- [ ] b. **Concevoir une façon d'évaluer les performances** : à vous de définir une métrique d'évaluation pour mesurer la performance du système (par exemple : les 5 articles recommandés sont-ils finalement lus par l'utilisateur ? tous ?)

## 4. Approche CF (collaborative filtering) based
- [ ] a. On utilise l'historique des utilisateurs pour apprendre un modèle de recommandation. Utilisation de la librairie Implicit pour implémenter une approche comme SVD.

## 5. Implémentation de l’API
- [ ] a. Implémentation de la fonction de prédiction
- [ ] b. Intégration avec Azure Functions
    - https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python#publish-the-project-to-azure
    - https://github.com/Azure-Samples/fastapi-on-azure-functions/tree/main
    - https://learn.microsoft.com/en-us/samples/azure-samples/fastapi-on-azure-functions/fastapi-on-azure-functions/
    - https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python
- [ ] c. Si nécessaire, stockage du modèle sur le azure blob storage

## 6. Implémentation d’une interface gradio
- [ ] 

# Notes pour le projet de recommandation d'articles
## Instructions séparées pour le Frontend et le Backend

### Frontend

- **Objectif :** Construire une interface web simple pour la recommandation d'articles.
- **Framework :** Gradio, Flask ou Streamlit.
- **Fonctionnalités :**
  - Champ de saisie pour l'identifiant utilisateur.
  - Affichage d'une liste de 5 articles recommandés pour cet utilisateur.
- **Déploiement :** Déployer le frontend en tant qu'application web (Gradio, Flask ou Streamlit).

### Backend

- **Objectif :** Servir des recommandations personnalisées d'articles basées sur les interactions utilisateur.
- **Framework :** Azure Functions (Python).
- **Fonctionnalités :**
  - Implémenter un modèle de filtrage collaboratif (CF Based).
  - Exposer une API qui prend un identifiant utilisateur et retourne 5 articles recommandés depuis la base d'articles.
- **Déploiement :** Déployer le backend en tant qu'Azure Function.

**Intégration :**
Le frontend doit appeler l'API du backend (Azure Function) avec l'identifiant utilisateur et afficher les recommandations retournées.
