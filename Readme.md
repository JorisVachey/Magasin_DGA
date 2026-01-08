# DGA ERP - Système de Gestion de Magasin

Ce projet est une application web de gestion d'inventaire et de commandes interne (magasin).
Ce projet a été rélisé en vu de l'entretien du 16/01/2026

## Instructions pour lancer le projet

1.  **Prérequis** : Comme le projet est en flask, il faut s'assurer d'avoir python d'installé
2.  **Installation des dépendances** :
    Installez Flask via votre terminal :
    pip install requirements.txt
3.  **Lancement de l'application** :
    Exécutez le fichier principal `app.py` :
    python app.py
4.  **Accès** : Ouvrez votre navigateur et rendez-vous à l'adresse `http://127.0.0.1:5000`.
5.  **Initialisation automatique** : Au premier lancement, l'application détecte l'absence de la base de données `DGA_ERP.db` et lance automatiquement le script d'installation `setup_db.py` pour créer les tables et insérer les données de test.

**Comptes de test (mots de passe configurés dans `setup_db.py`) :**
* **Admin** : `Benjamin Granet` (MDP : `1234`)
* **Employé** : `Paul Boissonade` (MDP : `JeSuisPaul`)
* **Manager** : `Alice Dupont` (MDP : `MDPAlice`)

##  Choix techniques

* **Framework Backend** : **Flask** a été choisi car il est le framework utilisé en cours.
* **Base de données** : **SQLite** est utilisé car demandé.
* **Sécurité des mots de passe** : Utilisation de l'algorithme **SHA-256** pour hacher les mots de passe avant le stockage en base de données.
* **Interface** : Utilisation de CSS pur pour un design sobre et de JavaScript pour une fonctionnalité de recherche dynamique.

## ⚠️ Limites connues

* **Gestion des sessions** : Les sessions sont stockées côté client via des cookies signés.
* **Filtrage par département** : Les utilisateurs ne peuvent voir que les produits liés à leur département, ce qui limite la visibilité globale de l'inventaire.
* **Recherche** : La fonction de recherche actuelle soumet le formulaire à chaque saisie, provoquant un rechargement de la page.
* **Persistance du Panier** : Le panier est stocké en session côté client ; il est donc perdu si l'utilisateur change de navigateur ou si la session expire avant la validation.

* **Sécurité des clés** : La clé secrète de l'application (secret_key) est écrite en dur dans le code, ce qui est une pratique à éviter en environnement de production.

* **Serveur de développement** : L'application utilise actuellement le serveur de développement intégré de Flask, qui n'est pas adapté pour une mise en production réelle.

##  Améliorations possibles

* **Section "Général"** : Implémenter un département commun dont les produits seraient visibles et commandables par tous les employés, quel que soit leur département d'origine.

* **Historique des commandes** : Ajouter une vue permettant aux utilisateurs de consulter leurs anciennes commandes et aux Managers de suivre les sorties de stock.

* **Alertes de stock critique** : Mettre en place un indicateur visuel (ex: ligne en rouge) dans le tableau si la quantite_stock tombe en dessous d'un certain seuil.

* **Tableau de bord Admin** : Créer une interface permettant à l'administrateur de créer, modifier ou supprimer des utilisateurs directement depuis l'application (actuellement géré via setup_db.py).

* **Export de données** : Ajouter une fonctionnalité d'exportation de l'inventaire au format CSV ou PDF pour les rapports d'audit.