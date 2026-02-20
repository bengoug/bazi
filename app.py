# app.py
# API Flask pour le calculateur BAZI
# Wrapper autour du code existant de china-testing/bazi

import os
import sys
import io
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def run_bazi(annee, mois, jour, heure, genre="homme", calendrier="gregorien"):
    """
    Exécute bazi.py en sous-processus et capture la sortie texte.
    C'est la méthode la plus sûre car le code original
    est conçu pour le terminal.
    """
    try:
        # Construire la commande
        cmd = [sys.executable, "bazi.py", 
               str(annee), str(mois), str(jour), str(heure)]
        
        # Ajouter -g pour calendrier grégorien (公历)
        if calendrier == "gregorien":
            cmd.append("-g")
        
        # Ajouter -n pour femme (女)
        if genre == "femme":
            cmd.append("-n")
        
        # Exécuter le script et capturer la sortie
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        
        sortie = result.stdout
        erreur = result.stderr
        
        if result.returncode != 0:
            return {
                "success": False,
                "erreur": f"Erreur du calcul BAZI: {erreur}",
                "code_retour": result.returncode
            }
        
        # Parser la sortie pour extraire les infos clés
        resultat = parser_sortie_bazi(sortie)
        resultat["success"] = True
        resultat["sortie_brute"] = sortie
        
        return resultat
        
    except subprocess.TimeoutExpired:
        return {"success": False, "erreur": "Timeout - calcul trop long"}
    except Exception as e:
        return {"success": False, "erreur": str(e)}


def parser_sortie_bazi(texte):
    """
    Parse la sortie texte de bazi.py pour extraire
    les informations structurées.
    """
    resultat = {
        "date_solaire": "",
        "date_lunaire": "",
        "quatre_piliers": "",
        "details_complet": "",
        "piliers": {
            "annee": {"tronc": "", "branche": ""},
            "mois":  {"tronc": "", "branche": ""},
            "jour":  {"tronc": "", "branche": ""},
            "heure": {"tronc": "", "branche": ""}
        }
    }
    
    lignes = texte.strip().split("\n")
    
    for ligne in lignes:
        ligne_clean = ligne.strip()
        
        # Chercher la date grégorienne (公历)
        if "公历" in ligne_clean:
            resultat["date_solaire"] = ligne_clean
        
        # Chercher la date lunaire (农历)
        if "农历" in ligne_clean:
            resultat["date_lunaire"] = ligne_clean
        
        # Chercher lunar_python qui contient les 4 piliers
        if "lunar_python" in ligne_clean:
            # Format: "lunar_python: 丁巳 己酉 癸未 壬戌"
            parties = ligne_clean.split(":")
            if len(parties) > 1:
                piliers_str = parties[1].strip()
                resultat["quatre_piliers"] = piliers_str
                
                # Séparer les 4 piliers
                piliers = piliers_str.split()
                if len(piliers) >= 4:
                    # Chaque pilier = 2 caractères : Tronc + Branche
                    noms = ["annee", "mois", "jour", "heure"]
                    for i, nom in enumerate(noms):
                        if i < len(piliers) and len(piliers[i]) >= 2:
                            resultat["piliers"][nom]["tronc"] = piliers[i][0]
                            resultat["piliers"][nom]["branche"] = piliers[i][1]
    
    # Garder le texte complet nettoyé
    resultat["details_complet"] = texte.strip()
    
    return resultat


# ===========================
# ROUTES API
# ===========================

@app.route('/api/bazi', methods=['POST'])
def bazi_endpoint():
    """
    Endpoint principal appelé par WordPress.
    
    JSON attendu:
    {
        "annee": 1990,
        "mois": 5,
        "jour": 15,
        "heure": 8,
        "genre": "homme",          (optionnel, défaut: homme)
        "calendrier": "gregorien"  (optionnel, défaut: gregorien)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False, 
                "erreur": "Aucune donnée reçue"
            }), 400
        
        # Paramètres obligatoires
        annee = int(data.get('annee', 0))
        mois  = int(data.get('mois', 0))
        jour  = int(data.get('jour', 0))
        heure = int(data.get('heure', 0))
        
        # Paramètres optionnels
        genre      = data.get('genre', 'homme')       # homme ou femme
        calendrier = data.get('calendrier', 'gregorien')  # gregorien ou lunaire
        
        # Validation
        if not (1900 <= annee <= 2100):
            return jsonify({
                "success": False, 
                "erreur": "Année doit être entre 1900 et 2100"
            }), 400
        if not (1 <= mois <= 12):
            return jsonify({
                "success": False, 
                "erreur": "Mois doit être entre 1 et 12"
            }), 400
        if not (1 <= jour <= 31):
            return jsonify({
                "success": False, 
                "erreur": "Jour doit être entre 1 et 31"
            }), 400
        if not (0 <= heure <= 23):
            return jsonify({
                "success": False, 
                "erreur": "Heure doit être entre 0 et 23"
            }), 400
        
        # Appeler le calcul BAZI
        resultat = run_bazi(annee, mois, jour, heure, genre, calendrier)
        
        return jsonify(resultat)
        
    except ValueError as e:
        return jsonify({
            "success": False, 
            "erreur": f"Valeur invalide: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False, 
            "erreur": f"Erreur serveur: {str(e)}"
        }), 500


@app.route('/api/test', methods=['GET'])
def test():
    """Route de test pour vérifier que l'API fonctionne."""
    return jsonify({
        "status": "✅ API BAZI opérationnelle",
        "source": "github.com/bengoug/bazi",
        "endpoints": {
            "POST /api/bazi": "Calculer un thème BAZI",
            "GET /api/test": "Tester l'API"
        },
        "exemple_requete": {
            "annee": 1990,
            "mois": 5,
            "jour": 15,
            "heure": 8,
            "genre": "homme",
            "calendrier": "gregorien"
        }
    })


@app.route('/', methods=['GET'])
def accueil():
    """Page d'accueil."""
    return jsonify({
        "message": "🏮 Calculateur BAZI - API",
        "documentation": "Envoyez un POST à /api/bazi",
        "test": "Visitez /api/test"
    })


# ===========================
# DÉMARRAGE
# ===========================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
