import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import setup_db
import commandes

app = Flask(__name__)
app.secret_key = "-l.~m1Yc&2wmIT9S&aRs[eH8Xip-G$M%"  # Clé secrète pour les sessions

# --- AUTOMATISATION DE L"INIT DE LA BDD ---
def verifier_bdd_au_demarrage():
    nom_bdd = "DGA_ERP.db"
    if not os.path.exists(nom_bdd):
        print(f"Le fichier {nom_bdd} est manquant.")
        print("Lancement automatique du script d'installation...")
        setup_db.initialisation_complete()
    else:
        print(f"La base de données {nom_bdd} est déjà présente.")

verifier_bdd_au_demarrage()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pseudo_form = request.form["pseudo"]
        mdp_form = request.form["password"]

        user = commandes.verifier_login(pseudo_form, mdp_form)      
        if user:
            session["user_id"] = user["id"]
            session["pseudo"] = user["pseudo"]
            session["role"] = user["role"]
            session["departement_id"] = user["departement_id"]
            session["is_admin"] = False
            session["dept_nom"] = user["dept_nom"]
            session["panier"] = {}
            if session["role"] == "Admin":
                session["is_admin"] = True
            return redirect(url_for("main"))
        else:
            flash("Identifiant ou mot de passe incorrect.", "error")
            
    return render_template("connexion.html")


@app.route("/main")
def main():
    if not session.get("user_id"):
        flash("Veuillez vous connecter pour accéder au tableau de bord.")
        return redirect(url_for("login"))
    
    return render_template("main.html", user=session, produits=commandes.get_produits_id_dpt(session["departement_id"]))
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)