# Guide d'exécution du projet

## 1. Prérequis
- Exécutez `prerequis.ipynb` pour installer toutes les bibliothèques nécessaires.
- Le fichier `utils.py` contient des fonctions utilitaires utilisées dans le projet.

## 2. Préparation des données
Exécutez `factors_transformation.py` pour :
- Importer et nettoyer les données
- Effectuer les jointures nécessaires
- Créer un dataframe global avec tous les indicateurs

## 3. Analyse des dimensions
Utilisez `reduc_dim_facteurs.py` pour :
- Observer les corrélations dans le dataframe
- Effectuer des analyses en composantes principales (ACP)
- Appliquer des algorithmes de clustering aux niveaux communal et cantonal

## 4. Création de groupes
Le fichier `groupes_creation.py` détaille :
- La méthode de groupement d'indicateurs
- La pondération des variables
- L'ACP et le clustering aux niveaux communal et cantonal

## 5. Visualisations
Dans le dossier `visualisation/` :
- `clustering_com.py` et `clustering_can.py` : Affichage des clusters communaux et cantonaux (tous facteurs sans haute corrélation)
- `grp_clustering_com.py` et `grp_clustering_can.py` : Affichage des clusters (groupements de variables pondérées)
- `all_factors.py` : Visualisation de tous les facteurs
- `grp_factors.py` : Visualisation des groupes de facteurs

## 6. Analyse  complémentaire
Le notebook `analyse_avec_visuels.ipynb` contient :
- Calculs de l'indice de Moran
- Analyses de régression
- Visualisations associées

Les bases de données ne sont pas fournis dans ce répertoire, et de même pour les cartes et résultats car trop lourds pour GIT HUB.
