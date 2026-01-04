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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/main")
def main():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    # Récupération des paramètres de recherche et de tri
    query = request.args.get('q', '')
    tri = request.args.get('sort', 'nom')
    
    produits = commandes.rechercher_et_trier_produits(session["departement_id"], query, tri)
    return render_template("main.html", user=session, produits=produits, search_query=query, current_sort=tri)
@app.route("/produit/modifier/<int:id>", methods=["GET", "POST"])
def modifier_produit(id):
    if not session.get("user_id"): return redirect(url_for("login"))
    produit = commandes.get_produit_by_id(id)
    
    if request.method == "POST":
        commandes.modifier_produit(
            id, request.form['nom'], request.form['fabricant'],
            produit['reference'], request.form['prix'], 
            request.form['stock'], session['departement_id']
        )
        flash("Produit mis à jour !", "success")
        return redirect(url_for("main"))
    return render_template("produit_form.html", action="Modifier", produit=produit)

@app.route("/produit/supprimer/<int:id>")
def supprimer_produit(id):
    if not session.get("user_id"): return redirect(url_for("login"))
    if commandes.supprimer_produit(id):
        flash("Produit supprimé.", "success")
    return redirect(url_for("main"))

@app.route("/ajouter_panier/<int:id>")
def ajouter_panier(id):
    if not session.get("user_id"): return redirect(url_for("login"))
    
    produit = commandes.get_produit_by_id(id)
    if not produit:
        flash("Produit introuvable.", "error")
        return redirect(url_for("main"))
        
    panier = session.get("panier", {})

    pid_str = str(id)
    current_qty = panier.get(pid_str, 0)
    
    if current_qty + 1 > produit['quantite_stock']:
        flash("Stock insuffisant pour ajouter ce produit.", "error")
    else:
        panier[pid_str] = current_qty + 1
        session["panier"] = panier
        flash("Produit ajouté au panier.", "success")
        
    return redirect(url_for("main"))

@app.route("/panier")
def voir_panier():
    if not session.get("user_id"): return redirect(url_for("login"))
    
    panier = session.get("panier", {})
    produits_panier = []
    total = 0
    
    for pid, qty in panier.items():
        p = commandes.get_produit_by_id(int(pid))
        if p:
            subtotal = p['prix'] * qty
            total += subtotal
            produits_panier.append({
                'id': p['id'],
                'nom': p['nom'],
                'prix': p['prix'],
                'quantite': qty,
                'subtotal': subtotal
            })
            
    return render_template("panier.html", produits=produits_panier, total=total)

@app.route("/panier/valider")
def valider_panier():
    if not session.get("user_id"): return redirect(url_for("login"))
    
    panier = session.get("panier", {})
    if not panier:
        flash("Votre panier est vide.", "error")
        return redirect(url_for("main"))
        
    success, message = commandes.valider_panier(session["user_id"], panier)
    
    if success:
        session["panier"] = {}
        flash(message, "success")
    else:
        flash(message, "error")
        
    return redirect(url_for("main"))

@app.route("/panier/supprimer/<int:id>")
def supprimer_du_panier(id):
    if not session.get("user_id"): return redirect(url_for("login"))
    
    panier = session.get("panier", {})
    if str(id) in panier:
        del panier[str(id)]
        session["panier"] = panier
        flash("Produit retiré du panier.", "success")
        
    return redirect(url_for("voir_panier"))

@app.route("/produit/ajouter", methods=["GET", "POST"])
def ajouter_produit():
    if not session.get("user_id"): return redirect(url_for("login"))
    
    if session.get("role") not in ["Admin", "Manager"]:
        flash("Accès refusé : vous n'avez pas les droits pour ajouter des produits.", "error")
        return redirect(url_for("main"))
    
    if request.method == "POST":
        commandes.ajouter_produit(
            request.form['nom'], request.form['fabricant'], 
            "REF-" + request.form['nom'][:3].upper(), 
            request.form['prix'], request.form['stock'], 
            session['dept_nom']
        )
        flash("Produit ajouté avec succès !", "success")
        return redirect(url_for("main"))
    return render_template("produit_form.html", action="Ajouter")


if __name__ == "__main__":
    app.run(debug=True)