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

def ajouter_produit(nom, fabricant, reference, prix, stock, nom_departement) -> bool:
    connexion = None
    try:
        connexion = get_db_connection()
        curseur = connexion.cursor()
        curseur.execute("PRAGMA foreign_keys = ON;")

        query = """
            INSERT INTO Produits (nom, fabricant, reference, prix, quantite_stock, departement_id)
            VALUES (?, ?, ?, ?, ?, (SELECT id FROM Departements WHERE nom = ?))
        """
        
        curseur.execute(query, (nom, fabricant, reference, prix, stock, nom_departement))
        
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
        SELECT P.nom, P.fabricant, P.reference, P.prix, P.quantite_stock, D.nom as dept_nom
        FROM Produits P
        JOIN Departements D ON P.departement_id = D.id
    """).fetchall()
    connexion.close()
    return products

def get_produits_id_dpt(id):
    connexion = get_db_connection()
    produits = connexion.execute("""select P.nom, P.fabricant, P.reference, P.prix, P.quantite_stock FROM Produits as P JOIN Departements D ON D.id = P.departement_id WHERE D.id = ?""" , (id,)).fetchall()
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

def get_produit_by_id(produit_id):
    connexion = get_db_connection()
    produit = connexion.execute("SELECT * FROM Produits WHERE id = ?", (produit_id,)).fetchone()
    connexion.close()
    return produit

def modifier_produit(id, nom, fabricant, reference, prix, stock, departement_id) -> bool:
    connexion = None
    try:
        connexion = get_db_connection()
        curseur = connexion.cursor()
        query = """
            UPDATE Produits 
            SET nom = ?, fabricant = ?, reference = ?, prix = ?, quantite_stock = ?, departement_id = ?
            WHERE id = ?
        """
        curseur.execute(query, (nom, fabricant, reference, prix, stock, departement_id, id))
        connexion.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur modif produit : {e}")
        return False
    finally:
        if connexion: connexion.close()

def supprimer_produit(produit_id) -> bool:
    connexion = None
    try:
        connexion = get_db_connection()
        connexion.execute("DELETE FROM Produits WHERE id = ?", (produit_id,))
        connexion.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        if connexion: connexion.close()

def rechercher_et_trier_produits(dept_id, recherche="", tri="nom"):
    connexion = get_db_connection()
    query = """
        SELECT * FROM Produits 
        WHERE departement_id = ? 
        AND (lower(nom) LIKE ? OR lower(reference) LIKE lower(?))
    """
    tris_autorises = {"nom": "nom", "prix": "prix", "quantite": "quantite_stock"}
    ordre = tris_autorises.get(tri, "nom")
    
    query += f" ORDER BY {ordre} ASC"
    
    resultats = connexion.execute(query, (dept_id, f"%{recherche}%", f"%{recherche}%")).fetchall()
    connexion.close()
    return resultats

def valider_panier(user_id, panier):
    connexion = get_db_connection()
    try:
        connexion.execute("BEGIN TRANSACTION")
        
        for produit_id, quantite in panier.items():
            produit_id = int(produit_id)
            quantite = int(quantite)
            
            produit = connexion.execute("SELECT quantite_stock FROM Produits WHERE id = ?", (produit_id,)).fetchone()
            if not produit or produit['quantite_stock'] < quantite:
                connexion.rollback()
                return False, f"Stock insuffisant pour le produit ID {produit_id}"
            
            connexion.execute("INSERT INTO Commandes (utilisateur_id, produit_id, quantite) VALUES (?, ?, ?)", 
                             (user_id, produit_id, quantite))
            
            connexion.execute("UPDATE Produits SET quantite_stock = quantite_stock - ? WHERE id = ?", 
                             (quantite, produit_id))
            
        connexion.commit()
        return True, "Commande validée avec succès"
        
    except sqlite3.Error as e:
        connexion.rollback()
        print(f"Erreur validation panier : {e}")
        return False, "Erreur technique lors de la validation"
    finally:
        connexion.close()

def passer_commande(utilisateur_id, produit_id, quantite=1):
    connexion = get_db_connection()
    try:

        produit = connexion.execute("SELECT quantite_stock FROM Produits WHERE id = ?", (produit_id,)).fetchone()
        if produit and produit['quantite_stock'] >= quantite:
            connexion.execute("INSERT INTO Commandes (utilisateur_id, produit_id, quantite) VALUES (?, ?, ?)", 
                             (utilisateur_id, produit_id, quantite))
            connexion.execute("UPDATE Produits SET quantite_stock = quantite_stock - ? WHERE id = ?", 
                             (quantite, produit_id))
            connexion.commit()
            return True
        return False
    except sqlite3.Error as e:
        print(f"Erreur lors de la commande : {e}")
        return False
    finally:
        connexion.close()