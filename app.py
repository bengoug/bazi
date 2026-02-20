<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏮 Calculateur BAZI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1a0a0a 0%, #2d1f1f 50%, #1a0a0a 100%);
            color: #f0e6d3;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 20px;
        }

        .container {
            background: rgba(45, 20, 20, 0.9);
            border: 2px solid #c4a44a;
            border-radius: 15px;
            padding: 40px;
            max-width: 750px;
            width: 100%;
            box-shadow: 0 0 30px rgba(196, 164, 74, 0.3);
        }

        h1 { text-align: center; color: #c4a44a; font-size: 2em; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #a89070; margin-bottom: 30px; font-style: italic; }
        .form-group { margin-bottom: 20px; }

        label { display: block; color: #c4a44a; margin-bottom: 5px; font-weight: bold; }

        input, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #c4a44a;
            border-radius: 8px;
            background: rgba(26, 10, 10, 0.8);
            color: #f0e6d3;
            font-size: 16px;
        }

        input:focus, select:focus {
            outline: none;
            border-color: #ffd700;
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        }

        .row { display: flex; gap: 15px; }
        .row .form-group { flex: 1; }

        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #c4a44a, #8b6914);
            color: #1a0a0a;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
            transition: all 0.3s;
        }

        button:hover { background: linear-gradient(135deg, #ffd700, #c4a44a); transform: translateY(-2px); }
        button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

        .loading { text-align: center; color: #c4a44a; font-size: 1.2em; margin-top: 20px; display: none; }

        .error {
            background: rgba(180, 0, 0, 0.3);
            border: 1px solid #ff4444;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            color: #ff9999;
            display: none;
        }

        .resultat { margin-top: 30px; display: none; }

        .section-title {
            color: #c4a44a;
            font-size: 1.1em;
            margin: 20px 0 10px 0;
            border-bottom: 1px solid #c4a44a44;
            padding-bottom: 5px;
        }

        /* PILIERS */
        .piliers-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }

        .pilier-item {
            background: rgba(196, 164, 74, 0.1);
            border: 1px solid #c4a44a;
            border-radius: 10px;
            padding: 15px 10px;
            text-align: center;
        }

        .pilier-item.jour-pilier {
            border-color: #ffd700;
            background: rgba(255, 215, 0, 0.15);
        }

        .pilier-titre { font-size: 0.75em; color: #a89070; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
        .pilier-tronc { font-size: 2.2em; color: #ffd700; margin-bottom: 2px; }
        .pilier-branche { font-size: 2.2em; color: #c4a44a; margin-bottom: 8px; }
        .pilier-element-tronc { font-size: 0.75em; color: #a89070; margin-bottom: 2px; }
        .pilier-element-branche { font-size: 0.75em; color: #a89070; margin-bottom: 2px; }
        .pilier-animal { font-size: 0.8em; color: #c4a44a; margin-bottom: 4px; }
        .pilier-shishen {
            font-size: 0.7em;
            background: rgba(196, 164, 74, 0.2);
            border-radius: 4px;
            padding: 2px 6px;
            color: #ffd700;
            margin-top: 4px;
            display: inline-block;
        }

        /* WUXING */
        .wuxing-grid {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }

        .wuxing-item {
            flex: 1;
            min-width: 80px;
            background: rgba(196, 164, 74, 0.1);
            border: 1px solid #c4a44a55;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
        }

        .wuxing-nom { font-size: 0.8em; color: #c4a44a; margin-bottom: 4px; }
        .wuxing-val { font-size: 1.4em; color: #ffd700; font-weight: bold; }

        .wuxing-barre-fond {
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            height: 6px;
            margin-top: 6px;
            overflow: hidden;
        }

        .wuxing-barre {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s;
        }

        /* DAYUN */
        .dayun-list {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 10px;
        }

        .dayun-item {
            background: rgba(196, 164, 74, 0.1);
            border: 1px solid #c4a44a55;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            min-width: 75px;
            flex-shrink: 0;
            cursor: default;
            transition: all 0.2s;
        }

        .dayun-item:hover {
            background: rgba(196, 164, 74, 0.25);
            border-color: #c4a44a;
        }

        .dayun-age { font-size: 0.7em; color: #a89070; margin-bottom: 4px; }
        .dayun-gz { font-size: 1.3em; color: #ffd700; margin-bottom: 4px; }
        .dayun-el { font-size: 0.65em; color: #a89070; line-height: 1.4; }

        /* TEXTES */
        .texte-classique {
            background: rgba(0,0,0,0.3);
            border-left: 3px solid #c4a44a;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            font-size: 0.85em;
            color: #d4c4a4;
            line-height: 1.7;
            white-space: pre-wrap;
            margin-bottom: 10px;
        }

        /* INFO BOXES */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }

        .info-box {
            background: rgba(196, 164, 74, 0.1);
            border: 1px solid #c4a44a55;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
        }

        .info-box-titre { font-size: 0.7em; color: #a89070; margin-bottom: 4px; }
        .info-box-val { font-size: 1em; color: #ffd700; }

        pre {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            font-size: 0.75em;
            overflow-x: auto;
            white-space: pre-wrap;
            color: #a89070;
        }

        details summary {
            cursor: pointer;
            color: #c4a44a;
            padding: 8px 0;
            user-select: none;
        }

        details summary:hover { color: #ffd700; }
    </style>
</head>
<body>
<div class="container">
    <h1>🏮 Calculateur BaZi</h1>
    <p class="subtitle">八字命理 · Analyse des Huit Caractères</p>

    <form id="baziForm">
        <div class="row">
            <div class="form-group">
                <label>📅 Année</label>
                <input type="number" id="annee" value="1990" min="1900" max="2100">
            </div>
            <div class="form-group">
                <label>📅 Mois</label>
                <input type="number" id="mois" value="5" min="1" max="12">
            </div>
        </div>

        <div class="row">
            <div class="form-group">
                <label>📅 Jour</label>
                <input type="number" id="jour" value="15" min="1" max="31">
            </div>
            <div class="form-group">
                <label>⏰ Heure</label>
                <input type="number" id="heure" value="8" min="0" max="23">
            </div>
        </div>

        <div class="form-group">
            <label>⚧ Genre</label>
            <select id="genre">
                <option value="M">👨 Masculin</option>
                <option value="F">👩 Féminin</option>
            </select>
        </div>

        <button type="submit" id="btn">🔮 Calculer mon BaZi</button>
    </form>

    <div class="loading" id="loading">⏳ Calcul en cours...</div>
    <div class="error" id="erreur"></div>
    <div class="resultat" id="resultat"></div>
</div>

<script>
    const API_URL = "https://bazi-production-99fb.up.railway.app/bazi";

    const COULEURS_ELEMENT = {
        'Métal': '#c0c0c0',
        'Bois':  '#4caf50',
        'Eau':   '#2196f3',
        'Feu':   '#f44336',
        'Terre': '#ff9800'
    };

    document.getElementById('baziForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const btn     = document.getElementById('btn');
        const loading = document.getElementById('loading');
        const erreur  = document.getElementById('erreur');
        const resultat = document.getElementById('resultat');

        btn.disabled = true;
        loading.style.display = 'block';
        erreur.style.display  = 'none';
        resultat.style.display = 'none';

        const data = {
            year:   parseInt(document.getElementById('annee').value),
            month:  parseInt(document.getElementById('mois').value),
            day:    parseInt(document.getElementById('jour').value),
            hour:   parseInt(document.getElementById('heure').value),
            gender: document.getElementById('genre').value
        };

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                afficherResultat(result);
            } else {
                erreur.textContent = "❌ Erreur : " + (result.error || "Calcul impossible");
                erreur.style.display = 'block';
            }

        } catch (err) {
            erreur.textContent = "❌ Impossible de contacter l'API : " + err.message;
            erreur.style.display = 'block';
        }

        loading.style.display = 'none';
        btn.disabled = false;
    });

    function afficherResultat(data) {
        let html = '';

        // ========== QUATRE PILIERS ==========
        html += `<div class="section-title">🏮 Les Quatre Piliers</div>`;
        html += `<div class="piliers-grid">`;

        const noms = ['Année', 'Mois', 'Jour', 'Heure'];
        const cles = ['annee', 'mois', 'jour', 'heure'];

        if (data.piliers) {
            cles.forEach((cle, i) => {
                const p = data.piliers[cle];
                if (!p) return;

                const couleurTronc = COULEURS_ELEMENT[p.tronc_element] || '#c4a44a';
                const couleurBranche = COULEURS_ELEMENT[p.branche_element] || '#c4a44a';
                const estJour = cle === 'jour';

                html += `
                <div class="pilier-item ${estJour ? 'jour-pilier' : ''}">
                    <div class="pilier-titre">${noms[i]}${estJour ? ' ★' : ''}</div>
                    <div class="pilier-tronc" style="color:${couleurTronc}">${p.tronc || '?'}</div>
                    <div class="pilier-branche" style="color:${couleurBranche}">${p.branche || '?'}</div>
                    <div class="pilier-element-tronc" style="color:${couleurTronc}">⬡ ${p.tronc_element || ''}</div>
                    <div class="pilier-element-branche" style="color:${couleurBranche}">⬡ ${p.branche_element || ''}</div>
                    <div class="pilier-animal">${p.animal || ''}</div>
                    ${p.shishen_fr ? `<span class="pilier-shishen">${p.shishen_fr}</span>` : ''}
                </div>`;
            });
        }
        html += `</div>`;

        // ========== INFOS GENERALES ==========
        if (data.date_solaire || data.ming_gong || data.force !== undefined) {
            html += `<div class="info-grid">`;
            if (data.date_solaire) html += `<div class="info-box"><div class="info-box-titre">📅 Date solaire</div><div class="info-box-val">${data.date_solaire}</div></div>`;
            if (data.ming_gong)    html += `<div class="info-box"><div class="info-box-titre">🏠 Palais du Destin</div><div class="info-box-val">${data.ming_gong}</div></div>`;
            if (data.force !== undefined) html += `<div class="info-box"><div class="info-box-titre">💪 Force du Jour</div><div class="info-box-val">${data.force} / ${data.moyenne} moy.</div></div>`;
            if (data.tai_yuan)     html += `<div class="info-box"><div class="info-box-titre">🌱 Taiyuan</div><div class="info-box-val">${data.tai_yuan}</div></div>`;
            if (data.shen_gong)    html += `<div class="info-box"><div class="info-box-titre">🎯 Palais du Corps</div><div class="info-box-val">${data.shen_gong}</div></div>`;
            if (data.date_lunaire) html += `<div class="info-box"><div class="info-box-titre">🌙 Date lunaire</div><div class="info-box-val">${data.date_lunaire}</div></div>`;
            html += `</div>`;
        }

        // ========== CINQ ELEMENTS ==========
        if (data.wuxing) {
            const wx = data.wuxing;
            const total = wx.metal + wx.bois + wx.eau + wx.feu + wx.terre || 1;
            const elements = [
                { nom: '⚙️ Métal', val: wx.metal, el: 'Métal' },
                { nom: '🌿 Bois',  val: wx.bois,  el: 'Bois'  },
                { nom: '💧 Eau',   val: wx.eau,   el: 'Eau'   },
                { nom: '🔥 Feu',   val: wx.feu,   el: 'Feu'   },
                { nom: '🪨 Terre', val: wx.terre, el: 'Terre' }
            ];

            html += `<div class="section-title">🔯 Cinq Éléments (Wu Xing)</div>`;
            html += `<div class="wuxing-grid">`;
            elements.forEach(e => {
                const pct = Math.round((e.val / total) * 100);
                const couleur = COULEURS_ELEMENT[e.el] || '#c4a44a';
                html += `
                <div class="wuxing-item">
                    <div class="wuxing-nom">${e.nom}</div>
                    <div class="wuxing-val" style="color:${couleur}">${e.val}</div>
                    <div class="wuxing-barre-fond">
                        <div class="wuxing-barre" style="width:${pct}%; background:${couleur}"></div>
                    </div>
                </div>`;
            });
            html += `</div>`;
        }

        // ========== GRANDES FORTUNES ==========
        if (data.dayun && data.dayun.length > 0) {
            // Dédoublonner par age+ganzhi
            const unique = [];
            const vus = new Set();
            data.dayun.forEach(d => {
                const cle = `${d.age}-${d.ganzhi}`;
                if (!vus.has(cle)) { vus.add(cle); unique.push(d); }
            });

            html += `<div class="section-title">🌊 Grandes Fortunes (Da Yun)</div>`;
            html += `<div class="dayun-list">`;
            unique.slice(0, 9).forEach(d => {
                const couleur = COULEURS_ELEMENT[d.tronc_element] || '#ffd700';
                html += `
                <div class="dayun-item">
                    <div class="dayun-age">${d.age} ans</div>
                    <div class="dayun-gz" style="color:${couleur}">${d.ganzhi}</div>
                    <div class="dayun-el">${d.tronc_element || ''}</div>
                    <div class="dayun-el">${d.animal || ''}</div>
                </div>`;
            });
            html += `</div>`;
        }

        // ========== TEXTES CLASSIQUES ==========
        const textes = [
            { cle: 'liu_shi_ri', titre: '📜 Six Dix Jours (口诀)' },
            { cle: 'qiong_tong', titre: '📖 Qiong Tong Bao Jian (穷通宝鉴)' },
            { cle: 'san_ming',   titre: '📚 San Ming Tong Hui (三命通会)' }
        ];

        textes.forEach(t => {
            if (data[t.cle]) {
                html += `
                <details style="margin-top:15px;">
                    <summary class="section-title" style="list-style:none; cursor:pointer;">
                        ${t.titre} ▼
                    </summary>
                    <div class="texte-classique">${data[t.cle]}</div>
                </details>`;
            }
        });

        // ========== DONNEES BRUTES ==========
        html += `
        <details style="margin-top:15px;">
            <summary style="cursor:pointer; color:#c4a44a; padding:8px 0;">
                📋 Voir toutes les données JSON ▼
            </summary>
            <pre>${JSON.stringify(data, null, 2)}</pre>
        </details>`;

        const resultat = document.getElementById('resultat');
        resultat.innerHTML = html;
        resultat.style.display = 'block';
    }
</script>
</body>
</html>
