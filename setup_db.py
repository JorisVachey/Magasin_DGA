import sqlite3

def creer_tables() -> bool:
    try:
        
        # --- CONNEXION ---
        
        connexion = sqlite3.connect('DGA_ERP.db')
        curseur = connexion.cursor()
        
        # --- DELETION DE LA BASE ---
        
        curseur.execute("PRAGMA foreign_keys = ON;")
        curseur.execute("DROP TABLE IF EXISTS Commandes;")
        curseur.execute("DROP TABLE IF EXISTS Produits;")
        curseur.execute("DROP TABLE IF EXISTS Utilisateurs;")
        curseur.execute("DROP TABLE IF EXISTS Departements;")

        # --- CRÉATION DE LA BASE---

        curseur.execute("""
            CREATE TABLE Departements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE CHECK(nom IN ("Haute-Technologie", "Logistique", "Cyber"))
            );
        """)

        curseur.execute("""
            CREATE TABLE Utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pseudo TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL CHECK(role IN ("Admin", "Employe", "Manager")),
                departement_id INTEGER,
                FOREIGN KEY (departement_id) REFERENCES Departements(id)
            );
        """)

        curseur.execute("""
            CREATE TABLE Produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                description TEXT,
                prix FLOAT NOT NULL CHECK(prix >= 0),
                quantite_stock INTEGER NOT NULL CHECK(quantite_stock >= 0),
                departement_id INTEGER,
                FOREIGN KEY (departement_id) REFERENCES Departements(id)
            );
        """)

        curseur.execute("""
            CREATE TABLE Commandes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilisateur_id INTEGER,
                produit_id INTEGER,
                quantite INTEGER NOT NULL CHECK(quantite > 0),
                date_commande TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id),
                FOREIGN KEY (produit_id) REFERENCES Produits(id)
            );
        """)

        connexion.commit()
        print("Base de données et tables créées avec succès.")
        return True

    except sqlite3.Error as e:
        print(f"Erreur lors de la création de la base de données : {e}")
        return False
        
    finally:
        if connexion:
            connexion.close()

# Pour tester :
if __name__ == "__main__":
    creer_tables()