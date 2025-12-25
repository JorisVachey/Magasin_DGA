import sqlite3
from hashlib import sha256
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
                mdp TEXT,
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
            
def initialiser_bd():
    try:
        connexion = sqlite3.connect('DGA_ERP.db')
        curseur = connexion.cursor()
        curseur.execute("PRAGMA foreign_keys = ON;")

        # --- Départements ---
        
        departements = [("Haute-Technologie",), ("Logistique",), ("Cyber",)]
        curseur.executemany("INSERT OR IGNORE INTO Departements (nom) VALUES (?);", departements)

        # --- Utilisateurs ---

        utilisateurs = [
            ("Benjamin Granet", "Admin",sha256("1234".encode()).hexdigest(), "Haute-Technologie"),
            ("Paul Boissonade", "Employe",sha256("JeSuisPaul".encode()).hexdigest(), "Logistique"),
            ("Alice Dupont", "Manager",sha256("MDPAlice".encode()).hexdigest(), "Cyber"), 
            ("Joris Vachey", "Employe",sha256("Siroj1234".encode()).hexdigest(), "Haute-Technologie")
        ]
        
        curseur.executemany("""
            INSERT OR IGNORE INTO Utilisateurs (pseudo, role, mdp, departement_id)
            VALUES (?, ?,?, (SELECT id FROM Departements WHERE nom = ?));
        """, utilisateurs)

        # --- Produits ---
        
        produits = [
            ("Supercalculateur Quantum", "Ordinateur quantique", 1500000.0, 2, "Haute-Technologie"),
            ("Drone de surveillance", "Autonomie 48h", 2500.0, 50, "Cyber"),
            ("Camion Blindé", "Transport sécurisé", 85000.0, 5, "Logistique"),
            ("Pare-feu IA", "Protection avancée", 500.0, 100, "Cyber")
        ]

        curseur.executemany("""
            INSERT INTO Produits (nom, description, prix, quantite_stock, departement_id)
            VALUES (?, ?, ?, ?, (SELECT id FROM Departements WHERE nom = ?))
        """, produits)

        connexion.commit()
        print("Données de test initialisées.")

    except sqlite3.Error as e:
        print(f"Erreur d'initialisation : {e}")
    finally:
        if connexion:
            connexion.close()

def initialisation_complete() -> bool:
    if creer_tables():
        initialiser_bd()
        return True
    else:
        creer_tables()
        initialiser_bd()
        return True

if __name__ == "__main__":
    initialisation_complete()