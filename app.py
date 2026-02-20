import os
import sys
import re
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

# ============================================================
# PARSING
# ============================================================
def parse_bazi_output(raw):
    c = re.sub(r'\x1b\[[0-9;]*m', '', raw)
    result = {}

    # --- QUATRE PILIERS ---
    m = re.search(r'四柱：(\S{2})\s+(\S{2})\s+(\S{2})\s+(\S{2})', c)
    if m:
        pillars = [m.group(1), m.group(2), m.group(3), m.group(4)]
        result['quatre_piliers'] = ' '.join(pillars)
        names = ['annee','mois','jour','heure']
        result['piliers'] = {}
        for i, name in enumerate(names):
            t, b = pillars[i][0], pillars[i][1]
            ti = TRONC_INFO.get(t, {})
            bi = BRANCHE_INFO.get(b, {})
            result['piliers'][name] = {
                'tronc': t, 'branche': b,
                'binome': pillars[i],
                'tronc_pinyin': ti.get('pinyin',''),
                'branche_pinyin': bi.get('pinyin',''),
                'tronc_element': ti.get('element',''),
                'branche_element': bi.get('element',''),
                'animal': bi.get('animal',''),
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
        ti = TRONC_INFO.get(gz[0], {})
        bi = BRANCHE_INFO.get(gz[1], {})
        dayun.append({
            'age': int(m2.group(1)), 'ganzhi': gz,
            'tronc': gz[0], 'branche': gz[1],
            'tronc_element': ti.get('element',''),
            'branche_element': bi.get('element',''),
            'animal': bi.get('animal',''),
            'phase': m2.group(3), 'nayin': m2.group(4)
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
            result[key] = m.group(1)

    # --- TEXTES CLASSIQUES ---
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
        'usage': 'POST /bazi avec {year, month, day, hour, gender}'
    })

@app.route('/bazi', methods=['GET','POST'])
def calculate_bazi():
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args

        year = str(data.get('year', '1990'))
        month = str(data.get('month', '5'))
        day = str(data.get('day', '15'))
        hour = str(data.get('hour', '8'))
        gender = str(data.get('gender', 'M'))

        cmd = [sys.executable, os.path.join(BASE_DIR, 'bazi.py'),
               year, month, day, hour, '-g']
        if gender == 'F':
            cmd.append('-n')

        proc = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=30, cwd=BASE_DIR)
        output = proc.stdout

        if not output.strip():
            return jsonify({
                'success': False,
                'error': 'Pas de sortie du calcul',
                'stderr': proc.stderr
            }), 500

        parsed = parse_bazi_output(output)
        parsed['success'] = True
        parsed['sortie_brute'] = output

        return jsonify(parsed)

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500

# ============================================================
# START
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
