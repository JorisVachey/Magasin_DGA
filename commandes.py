import sqlite3
import hashlib

def get_db_connection():
    conn = sqlite3.connect('DGA_ERP.db')
    conn.row_factory = sqlite3.Row
    return conn

def ajouter_user(pseudo, mdp, role, nom_departement) -> bool:
    connexion = None
    try:
        connexion = get_db_connection()
        curseur = connexion.cursor()
        curseur.execute("PRAGMA foreign_keys = ON;")
        
        mdp_hash = hashlib.sha256(mdp.encode('utf-8')).hexdigest()
        
        query = """
            INSERT INTO Utilisateurs (pseudo, mdp, role, departement_id)
            VALUES (?, ?, ?, (SELECT id FROM Departements WHERE nom = ?))
        """
        
        curseur.execute(query, (pseudo, mdp_hash, role, nom_departement))
        
        connexion.commit()
        return True

    except sqlite3.Error as e:
        print(f"Erreur ajout user : {e}")
        return False

    finally:
        if connexion:
            connexion.close()

def ajouter_produit(nom, description, prix, stock, nom_departement) -> bool:
    connexion = None
    try:
        connexion = get_db_connection()
        curseur = connexion.cursor()
        curseur.execute("PRAGMA foreign_keys = ON;")

        query = """
            INSERT INTO Produits (nom, description, prix, quantite_stock, departement_id)
            VALUES (?, ?, ?, ?, (SELECT id FROM Departements WHERE nom = ?))
        """
        
        curseur.execute(query, (nom, description, prix, stock, nom_departement))
        
        connexion.commit()
        return True

    except sqlite3.Error as e:
        print(f"Erreur ajout produit : {e}")
        return False
    
    finally:
        if connexion:
            connexion.close()

def verifier_login(pseudo, mot_de_passe_clair):
    connexion = get_db_connection()
    user = connexion.execute('SELECT U.*, D.nom as dept_nom FROM Utilisateurs as U JOIN Departements as D ON U.departement_id = D.id WHERE pseudo = ?', (pseudo,)).fetchone()
    connexion.close()
    
    if user is None:
        return None 
    
    mdp_input_hash = hashlib.sha256(mot_de_passe_clair.encode('utf-8')).hexdigest()
    
    if mdp_input_hash == user['mdp']:
        return user
    else:
        return None

def get_users():
    connexion = get_db_connection()
    users = connexion.execute("""
        SELECT U.id, U.pseudo, U.role, D.nom as dept_nom 
        FROM Utilisateurs U
        JOIN Departements D ON U.departement_id = D.id
    """).fetchall()
    connexion.close()
    return users

def get_produits():
    connexion = get_db_connection()
    products = connexion.execute("""
        SELECT P.nom, P.description, P.prix, P.quantite_stock, D.nom as dept_nom
        FROM Produits P
        JOIN Departements D ON P.departement_id = D.id
    """).fetchall()
    connexion.close()
    return products

def get_produits_id_dpt(id):
    connexion = get_db_connection()
    produits = connexion.execute("""select P.nom, P.prix, P.quantite_stock FROM Produits as P JOIN Departements D ON D.id = P.departement_id WHERE D.id = ?""" , (id,)).fetchall()
    connexion.close()
    return produits

def get_employes_by_dept(dept_id):
    connexion = get_db_connection()
    employes = connexion.execute("""
        SELECT U.id, U.pseudo, U.role 
        FROM Utilisateurs U
        WHERE U.departement_id = ?
    """, (dept_id,)).fetchall()
    connexion.close()
    return employes