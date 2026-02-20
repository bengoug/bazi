import os
import sys
import re
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# MAPPINGS
# ============================================================
TRONC_INFO = {
    '甲': {'pinyin':'Jiǎ','element':'Bois','pol':'+'},
    '乙': {'pinyin':'Yǐ','element':'Bois','pol':'-'},
    '丙': {'pinyin':'Bǐng','element':'Feu','pol':'+'},
    '丁': {'pinyin':'Dīng','element':'Feu','pol':'-'},
    '戊': {'pinyin':'Wù','element':'Terre','pol':'+'},
    '己': {'pinyin':'Jǐ','element':'Terre','pol':'-'},
    '庚': {'pinyin':'Gēng','element':'Métal','pol':'+'},
    '辛': {'pinyin':'Xīn','element':'Métal','pol':'-'},
    '壬': {'pinyin':'Rén','element':'Eau','pol':'+'},
    '癸': {'pinyin':'Guǐ','element':'Eau','pol':'-'},
}

BRANCHE_INFO = {
    '子': {'pinyin':'Zǐ','element':'Eau','animal':'Rat 🐀'},
    '丑': {'pinyin':'Chǒu','element':'Terre','animal':'Buffle 🐂'},
    '寅': {'pinyin':'Yín','element':'Bois','animal':'Tigre 🐅'},
    '卯': {'pinyin':'Mǎo','element':'Bois','animal':'Lapin 🐇'},
    '辰': {'pinyin':'Chén','element':'Terre','animal':'Dragon 🐉'},
    '巳': {'pinyin':'Sì','element':'Feu','animal':'Serpent 🐍'},
    '午': {'pinyin':'Wǔ','element':'Feu','animal':'Cheval 🐴'},
    '未': {'pinyin':'Wèi','element':'Terre','animal':'Chèvre 🐐'},
    '申': {'pinyin':'Shēn','element':'Métal','animal':'Singe 🐒'},
    '酉': {'pinyin':'Yǒu','element':'Métal','animal':'Coq 🐓'},
    '戌': {'pinyin':'Xū','element':'Terre','animal':'Chien 🐕'},
    '亥': {'pinyin':'Hài','element':'Eau','animal':'Cochon 🐖'},
}

SHISHEN_FR = {
    '比':'Parallèle','劫':'Rob. Richesse','食':'Dieu Gourmand',
    '伤':'Off. Blessant','才':'Ric. Partielle','财':'Ric. Directe',
    '杀':'7e Tueur','官':'Off. Direct','枭':'Sceau Partiel','印':'Sceau Direct',
    '--':'Maître du Jour'
}

# 12 phases (长生…)
PHASE_FR = {
    '长生': 'Longévité (naissance)', '沐浴': 'Bain (purification)', '冠带': 'Couronne (mise en forme)',
    '临官': 'Prise de fonction', '帝旺': 'Apogée', '衰': 'Déclin', '病': 'Maladie',
    '死': 'Fin / Mort', '墓': 'Tombe / Stockage', '绝': 'Extinction', '胎': 'Fœtus', '养': 'Gestation'
}

# 30 NaYin (纳音) uniques
NAYIN_FR = {
    '海中金': "Métal dans la mer",
    '炉中火': "Feu du four",
    '大林木': "Bois de grande forêt",
    '路旁土': "Terre en bord de route",
    '剑锋金': "Métal – lame d'épée",
    '山头火': "Feu du sommet",
    '涧下水': "Eau du ravin",
    '城头土': "Terre des remparts",
    '白蜡金': "Métal de cire blanche",
    '杨柳木': "Bois de saule",
    '泉中水': "Eau de la source",
    '屋上土': "Terre sur le toit",
    '霹雳火': "Feu du tonnerre",
    '松柏木': "Bois de pin/cyprès",
    '长流水': "Eau de long cours",
    '沙中金': "Métal dans le sable",
    '山下火': "Feu au pied de la montagne",
    '平地木': "Bois de plaine",
    '壁上土': "Terre sur le mur",
    '金箔金': "Métal – feuille d'or",
    '佛灯火': "Feu de la lampe du Bouddha",
    '天河水': "Eau de la Voie lactée",
    '大驿土': "Terre de la grande poste",
    '钗钏金': "Métal des bijoux",
    '桑柘木': "Bois de mûrier",
    '大溪水': "Eau du grand ruisseau",
    '沙中土': "Terre dans le sable",
    '天上火': "Feu céleste",
    '石榴木': "Bois de grenadier",
    '大海水': "Eau de l'océan",
}

def _strip_ansi(s: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*m', '', s)

def _ganzhi_details(gz: str):
    """Return structured info for a ganzhi string like '甲子'."""
    if not gz or len(gz) < 2:
        return None
    t, b = gz[0], gz[1]
    ti = TRONC_INFO.get(t, {})
    bi = BRANCHE_INFO.get(b, {})
    return {
        'ganzhi': gz,
        'tronc': t,
        'branche': b,
        'tronc_pinyin': ti.get('pinyin', ''),
        'branche_pinyin': bi.get('pinyin', ''),
        'tronc_element': ti.get('element', ''),
        'branche_element': bi.get('element', ''),
        'animal': bi.get('animal', ''),
    }

def _safe_int(val, default, min_v=None, max_v=None):
    try:
        x = int(str(val).strip())
        if min_v is not None and x < min_v:
            return default
        if max_v is not None and x > max_v:
            return default
        return x
    except Exception:
        return default

# ============================================================
# PARSING
# ============================================================
def parse_bazi_output(raw, include_texts=False):
    c = _strip_ansi(raw)
    result = {}

    # --- QUATRE PILIERS ---
    m = re.search(r'四柱：(\S{2})\s+(\S{2})\s+(\S{2})\s+(\S{2})', c)
    if m:
        pillars = [m.group(1), m.group(2), m.group(3), m.group(4)]
        result['quatre_piliers'] = ' '.join(pillars)
        names = ['annee','mois','jour','heure']
        result['piliers'] = {}
        for i, name in enumerate(names):
            gz = pillars[i]
            det = _ganzhi_details(gz) or {'ganzhi': gz}
            result['piliers'][name] = {
                'tronc': det.get('tronc',''),
                'branche': det.get('branche',''),
                'binome': det.get('ganzhi', gz),
                'tronc_pinyin': det.get('tronc_pinyin',''),
                'branche_pinyin': det.get('branche_pinyin',''),
                'tronc_element': det.get('tronc_element',''),
                'branche_element': det.get('branche_element',''),
                'animal': det.get('animal',''),
            }

    # --- DIX DIEUX (SHISHEN) ---
    m = re.search(
        r'([甲乙丙丁戊己庚辛壬癸])\s+([甲乙丙丁戊己庚辛壬癸])\s+([甲乙丙丁戊己庚辛壬癸])\s+([甲乙丙丁戊己庚辛壬癸])\s+'
        r'(比|劫|食|伤|才|财|杀|官|枭|印|--)\s+(比|劫|食|伤|才|财|杀|官|枭|印|--)\s+(比|劫|食|伤|才|财|杀|官|枭|印|--)\s+(比|劫|食|伤|才|财|杀|官|枭|印|--)',
        c)
    if m and 'piliers' in result:
        gods = [m.group(5), m.group(6), m.group(7), m.group(8)]
        for i, name in enumerate(['annee','mois','jour','heure']):
            result['piliers'][name]['shishen'] = gods[i]
            result['piliers'][name]['shishen_fr'] = SHISHEN_FR.get(gods[i], gods[i])

    # --- CINQ ELEMENTS ---
    m = re.search(r'金(\d+)\s+木(\d+)\s+水(\d+)\s+火(\d+)\s+土(\d+)', c)
    if m:
        result['wuxing'] = {
            'metal': int(m.group(1)), 'bois': int(m.group(2)),
            'eau': int(m.group(3)), 'feu': int(m.group(4)),
            'terre': int(m.group(5))
        }

    # --- FORCE ---
    m = re.search(r'强弱:(\d+)\s+中值(\d+)', c)
    if m:
        result['force'] = int(m.group(1))
        result['moyenne'] = int(m.group(2))

    # --- ORGANES ---
    organes = {}
    for cn, fr in {'胆':'vesicule','肝':'foie','小肠':'intestin_grele',
                   '心':'coeur','胃':'estomac','脾':'rate',
                   '大肠':'gros_intestin','肺':'poumon',
                   '膀胱':'vessie','肾':'rein'}.items():
        m2 = re.search(cn + r':\s*(\d+)', c)
        if m2:
            organes[fr] = int(m2.group(1))
    if organes:
        result['organes'] = organes

    # --- DA YUN (grandes fortunes) ---
    dayun = []
    for m2 in re.finditer(
        r'^(\d+)\s{2,}([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+(\S+)\s+(\S+)',
        c, re.MULTILINE):
        gz = m2.group(2)
        det = _ganzhi_details(gz) or {}
        phase = m2.group(3)
        nayin = m2.group(4)
        dayun.append({
            'age': int(m2.group(1)),
            'ganzhi': gz,
            'tronc': det.get('tronc',''),
            'branche': det.get('branche',''),
            'tronc_element': det.get('tronc_element',''),
            'branche_element': det.get('branche_element',''),
            'animal': det.get('animal',''),
            'phase': phase,
            'phase_fr': PHASE_FR.get(phase, phase),
            'nayin': nayin,
            'nayin_fr': NAYIN_FR.get(nayin, nayin),
        })
    if dayun:
        result['dayun'] = dayun

    # --- DATES ---
    m = re.search(r'公历:\s*(\d+)年(\d+)月(\d+)日', c)
    if m:
        result['date_solaire'] = f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
    m = re.search(r'农历:\s*(\d+)年(\d+)月(\d+)日', c)
    if m:
        result['date_lunaire'] = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # --- PALAIS SPECIAUX ---
    for pat, key in [('命宫:(\S+)','ming_gong'),
                     ('胎元:(\S+)','tai_yuan'),
                     ('身宫:(\S+)','shen_gong')]:
        m = re.search(pat, c)
        if m:
            gz = m.group(1)
            result[key] = gz                       # compat (string)
            result[key + '_details'] = _ganzhi_details(gz)  # version détaillée

    # --- TEXTES CLASSIQUES (optionnel) ---
    if include_texts:
        for title, key in [('穷通宝鉴','qiong_tong'),
                           ('三命通会','san_ming'),
                           ('六十日用法口诀','liu_shi_ri')]:
            idx = c.find(f'《{title}')
            if idx >= 0:
                start = c.find('\n', c.find('=', idx))
                if start >= 0:
                    ends = []
                    for marker in ['\n\n\n《', '\n\n\n大运', '\n\n大运', '\n星宿']:
                        pos = c.find(marker, start + 1)
                        if pos > 0:
                            ends.append(pos)
                    end = min(ends) if ends else len(c)
                    text = c[start:end].strip()
                    text = re.sub(r'=+', '', text).strip()
                    if text:
                        result[key] = text

    return result

# ============================================================
# ROUTES
# ============================================================
@app.route('/')
def index():
    return jsonify({
        'message': '🏮 API BaZi active',
        'usage': 'POST /bazi avec {year, month, day, hour, gender} (option: ?debug=1&include_texts=1)'
    })

@app.route('/bazi', methods=['GET','POST'])
def calculate_bazi():
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args

        # sécurise/normalise un minimum
        year = _safe_int(data.get('year', 1990), 1990, 1800, 2200)
        month = _safe_int(data.get('month', 5), 5, 1, 12)
        day = _safe_int(data.get('day', 15), 15, 1, 31)
        hour = _safe_int(data.get('hour', 8), 8, 0, 23)
        gender = str(data.get('gender', 'M')).upper().strip()

        debug = str(data.get('debug', '0')).strip() == '1'
        include_texts = str(data.get('include_texts', '0')).strip() == '1'

        cmd = [sys.executable, os.path.join(BASE_DIR, 'bazi.py'),
               str(year), str(month), str(day), str(hour), '-g']
        if gender == 'F':
            cmd.append('-n')

        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=30, cwd=BASE_DIR)

        if proc.returncode != 0:
            return jsonify({
                'success': False,
                'error': 'Erreur d’exécution bazi.py',
                'stderr': proc.stderr
            }), 500

        output = proc.stdout or ""
        if not output.strip():
            return jsonify({
                'success': False,
                'error': 'Pas de sortie du calcul',
                'stderr': proc.stderr
            }), 500

        parsed = parse_bazi_output(output, include_texts=include_texts)
        parsed['success'] = True

        # IMPORTANT: évite d’envoyer du chinois brut au front, sauf debug
        if debug:
            parsed['sortie_brute'] = output

        return jsonify(parsed)

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
