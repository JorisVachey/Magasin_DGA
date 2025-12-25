import sqlite3


def ajouter_user(pseudo, role, nom_departement)->bool:
    connexion = None
    try:
        connexion = sqlite3.connect('DGA_ERP.db')
        curseur = connexion.cursor()
        curseur.execute("PRAGMA foreign_keys = ON;")
        
        query = """
            INSERT INTO Utilisateurs (pseudo, role, departement_id)
            VALUES (?, ?, (SELECT id FROM Departements WHERE nom = ?))
        """
        
        curseur.execute(query, (pseudo, role, nom_departement))
        
        connexion.commit()
        print(f"Succès : Utilisateur '{pseudo}' ajouté.")
        return True

    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout de l'utilisateur '{pseudo}' : {e}")
        return False

    finally:
        if connexion:
            connexion.close()
        


def ajouter_produit(nom, description, prix, stock, nom_departement) -> bool:
    connexion = None
    try:
        connexion = sqlite3.connect('DGA_ERP.db')
        curseur = connexion.cursor()
        curseur.execute("PRAGMA foreign_keys = ON;")

        query = """
            INSERT INTO Produits (nom, description, prix, quantite_stock, departement_id)
            VALUES (?, ?, ?, ?, (SELECT id FROM Departements WHERE nom = ?))
        """
        
        curseur.execute(query, (nom, description, prix, stock, nom_departement))
        
        connexion.commit()
        print(f"Succès : Produit '{nom}' ajouté au stock.")
        return True

    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout du produit '{nom}' : {e}")
        return False
    
    finally:
        if connexion:
            connexion.close()
            
            
