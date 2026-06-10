import streamlit as st
from supabase import create_client
from datetime import datetime, date, time as dtime, timedelta
import time
import calendar
import requests
from functools import lru_cache
from streamlit_searchbox import st_searchbox
from functools import lru_cache

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
SUPABASE_URL  = st.secrets["SUPABASE_URL"]
SUPABASE_KEY  = st.secrets["SUPABASE_KEY"]
SNCF_API_KEY  = st.secrets["SNCF_API_KEY"]

SNCF_BASE = "https://api.sncf.com/v1/coverage/sncf"


with st.sidebar:
    st.markdown("### 🔧 Debug API")
    test_query = st.text_input("Gare à tester", value="Paris", key="debug_q")
    if st.button("Test direct API SNCF", key="debug_btn"):
        try:
            r = requests.get(
                f"{SNCF_BASE}/places",
                params={"q": test_query, "type[]": "stop_area", "count": 3},
                auth=(SNCF_API_KEY, ""),
                timeout=8,
            )
            st.write(f"**Status:** `{r.status_code}`")
            st.write(f"**URL:** `{r.url}`")
            if r.status_code == 200:
                st.json(r.json())
            else:
                st.code(r.text[:800])
        except Exception as e:
            st.error(f"Exception : {e}")
    
    if st.button("Vider cache", key="clear_cache_sidebar"):
        st.cache_data.clear()
        st.success("Cache vidé")

    st.markdown("---")
    st.markdown("### 🔧 Debug Journeys")
    if st.button("Test Journeys Paris→Nice", key="debug_journeys"):
        try:
            r = requests.get(
                f"{SNCF_BASE}/journeys",
                params={
                    "from": "stop_area:SNCF:87686006",
                    "to":   "stop_area:SNCF:87756056",
                    "datetime": "20260725T060000",
                    "datetime_represents": "departure",
                    "count": 3,
                    "data_freshness": "base_schedule",
                },
                auth=(SNCF_API_KEY, ""),
                timeout=10,
            )
            st.write(f"**Status:** `{r.status_code}`")
            st.write(f"**URL:** `{r.url}`")
            if r.status_code == 200:
                data = r.json()
                journeys = data.get("journeys", [])
                st.write(f"**Journeys:** {len(journeys)}")
                if journeys:
                    for s in journeys[0].get("sections", []):
                        st.write(f"- type=`{s.get('type')}` | mode=`{s.get('display_informations', {}).get('commercial_mode', '')}`")
                else:
                    st.json(data.get("error", data))
            else:
                st.code(r.text[:1000])
        except Exception as e:
            st.error(f"Exception : {e}")

NICE_STOP_ID  = "stop_area:SNCF:87756056"   # Nice-Ville

WEEKEND_START = date(2026, 7, 24)
WEEKEND_END   = date(2026, 7, 27)
DATE_DEFAULT  = date(2026, 7, 25)

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

label, .stRadio label, .stTextInput label,
.stTimeInput label, .stDateInput label,
p, div, span, [data-testid="stWidgetLabel"] {
    color: #1e293b !important;
}
.stRadio > div > label > div > p {
    color: #1e293b !important;
    font-weight: 500 !important;
}
.stRadio [data-baseweb="radio"] [data-checked="true"] ~ div,
.stRadio [aria-checked="true"] ~ div span {
    color: #0284c7 !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #475569 !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    color: #0284c7 !important;
}
[data-testid="stMetricLabel"] { color: #475569 !important; font-weight: 600 !important; }
[data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 700 !important; }

.hero {
    background: linear-gradient(160deg, #0c4a6e 0%, #075985 60%, #0ea5e9 100%);
    border-radius: 18px;
    padding: 28px 28px 32px;
    color: white;
    margin-bottom: 16px;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.7;
    margin-bottom: 6px;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    font-weight: 700;
    margin: 0 0 6px 0;
    line-height: 1.1;
}
.hero-sub { font-size: 14px; opacity: 0.8; margin: 0; }

.countdown-box {
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
    border-radius: 14px;
    padding: 16px 20px;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 18px rgba(14,165,233,0.3);
}
.countdown-left .eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    opacity: 0.8;
    margin-bottom: 4px;
}
.countdown-name { font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 700; }
.countdown-detail { font-size: 12px; opacity: 0.8; margin-top: 2px; }
.countdown-time {
    font-family: 'DM Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    text-align: right;
    line-height: 1;
}
.countdown-sublabel { font-size: 10px; opacity: 0.65; text-align: right; margin-top: 3px; }

.membre-card {
    background: white;
    border-radius: 14px;
    padding: 14px 18px 14px 22px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.04);
    border-left: 4px solid #e2e8f0;
}
.membre-card.arrive    { border-left-color: #10b981; }
.membre-card.en_route  { border-left-color: #f59e0b; }
.membre-card.pas_parti { border-left-color: #94a3b8; }
.membre-card.retour    { border-left-color: #8b5cf6; }

.membre-top { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.membre-nom { font-family: 'Playfair Display', serif; font-size: 17px; font-weight: 700; color: #0f172a; }

.badge {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.03em;
}
.badge-arrive    { background: #d1fae5; color: #065f46; }
.badge-en_route  { background: #fef3c7; color: #92400e; }
.badge-pas_parti { background: #e2e8f0; color: #334155; }
.badge-retour    { background: #ede9fe; color: #4c1d95; }

.direction-tag {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 20px;
    letter-spacing: 0.05em;
    background: #e2e8f0;
    color: #334155;
}

.membre-trajet  { font-size: 13px; color: #475569; margin-top: 3px; font-weight: 500; }
.membre-horaires { font-family: 'DM Mono', monospace; font-size: 12px; color: #64748b; margin-top: 2px; }

.section-title {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #64748b;
    margin: 20px 0 10px 2px;
}

/* ── Résultats de recherche trains ── */
.train-result {
    background: white;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    transition: border-color 0.15s;
    cursor: pointer;
}
.train-result:hover { border-color: #0ea5e9; }
.train-result.selected {
    border-color: #0284c7;
    background: #f0f9ff;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.15);
}
.train-result-top {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 4px;
}
.train-num {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #0284c7;
    background: #e0f2fe;
    padding: 2px 10px;
    border-radius: 20px;
}
.train-type {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    color: #64748b;
    background: #f1f5f9;
    padding: 2px 8px;
    border-radius: 20px;
    text-transform: uppercase;
}
.train-direct {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    color: #065f46;
    background: #d1fae5;
    padding: 2px 8px;
    border-radius: 20px;
}
.train-correspondance {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    color: #92400e;
    background: #fef3c7;
    padding: 2px 8px;
    border-radius: 20px;
}
.train-nuit {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    color: #3730a3;
    background: #e0e7ff;
    padding: 2px 8px;
    border-radius: 20px;
}
.train-horaires {
    font-family: 'DM Mono', monospace;
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
}
.train-duree {
    font-size: 12px;
    color: #64748b;
    font-weight: 500;
}
.search-info {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: #0369a1;
    margin-bottom: 12px;
    font-weight: 500;
}
.search-error {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: #c2410c;
    margin-bottom: 12px;
    font-weight: 500;
}
.prefill-banner {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: #166534;
    margin-bottom: 12px;
    font-weight: 500;
}

/* Calendrier custom */
.cal-wrap {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.04);
    margin-bottom: 8px;
}
.empty-state {
    text-align: center;
    padding: 48px 24px;
    background: white;
    border-radius: 16px;
    color: #94a3b8;
}
.empty-icon { font-size: 40px; margin-bottom: 12px; }
.empty-title { font-family: 'Playfair Display', serif; font-size: 18px; color: #475569; margin-bottom: 6px; }

.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] { background: #f0f7ff; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS SUPABASE
# ─────────────────────────────────────────────
def get_membres():
    res = supabase.table("membres").select("*").order("date_arrivee").order("heure_arrivee").execute()
    return res.data or []

def add_membre(data: dict):
    res = supabase.table("membres").insert(data).execute()
    return res.data[0] if res.data else None

def update_statut(membre_id: str, statut: str):
    supabase.table("membres").update({"statut": statut}).eq("id", membre_id).execute()

def delete_membre(membre_id: str):
    supabase.table("membres").delete().eq("id", membre_id).execute()


# ─────────────────────────────────────────────
# API SNCF (Navitia)
# ─────────────────────────────────────────────
def sncf_get(endpoint: str, params: dict = None) -> dict | None:
    try:
        r = requests.get(
            f"{SNCF_BASE}/{endpoint}",
            params=params or {},
            auth=(SNCF_API_KEY, ""),
            timeout=8,
        )
        if r.status_code == 200:
            return r.json()
        print(f"[SNCF] {r.status_code} — {r.url} — {r.text[:200]}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[SNCF] Exception : {e}")
        return None

# Module-level dict : label affiché → stop_id
_gare_id_map: dict[str, str] = {}

@lru_cache(maxsize=256)
def autocomplete_gare(query: str) -> list[str]:
    if not query or len(query.strip()) < 2:
        return []
    
    cache_key = f"_gare_cache_{query.strip().lower()}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    data = sncf_get("places", {
        "q": query.strip(),
        "type[]": "stop_area",
        "count": 8,
        "disable_geojson": "true",
    })
    if not data or not data.get("places"):
        return []

    if "_gare_id_map" not in st.session_state:
        st.session_state["_gare_id_map"] = {}

    labels = []
    for place in data["places"]:
        name    = place.get("name", "")
        stop_id = place.get("id", "")
        admin   = place.get("administrative_regions") or []
        context = admin[0].get("name", "") if admin else ""
        label   = f"{name} — {context}" if context and context.lower() not in name.lower() else name
        if stop_id:
            st.session_state["_gare_id_map"][label] = stop_id
            labels.append(label)

    st.session_state[cache_key] = labels
    return labels

@st.cache_data(ttl=300, show_spinner=False)
def search_trains(from_id: str, to_id: str, dt_str: str) -> list[dict]:
    data = sncf_get("journeys", {
        "from": from_id,
        "to": to_id,
        "datetime": dt_str,
        "datetime_represents": "departure",
        "count": 8,
        "min_nb_journeys": 3,
        "data_freshness": "base_schedule",
    })
    if not data or not data.get("journeys"):
        return []

    results = []
    for j in data["journeys"]:
        sections = j.get("sections", [])

        pt_sections = [s for s in sections if s.get("type") == "public_transport"]
        if not pt_sections:
            continue

        first_pt = pt_sections[0]
        disp = first_pt.get("display_informations", {})
        train_number = disp.get("headsign", "") or disp.get("label", "")
        train_name   = disp.get("commercial_mode", "") or disp.get("physical_mode", "")

        dep_raw = j.get("departure_date_time", "")
        arr_raw = j.get("arrival_date_time", "")

        def parse_dt(s):
            try:
                return datetime.strptime(s, "%Y%m%dT%H%M%S")
            except Exception:
                return None

        dep_dt = parse_dt(dep_raw)
        arr_dt = parse_dt(arr_raw)
        if not dep_dt or not arr_dt:
            continue

        duration_min = int(j.get("duration", 0)) // 60
        nb_transfers = int(j.get("nb_transfers", 0))

        # ── Détection train de nuit : arrivée le lendemain du départ ──
        is_night_train = arr_dt.date() > dep_dt.date()

        results.append({
            "dep": dep_dt.strftime("%H:%M"),
            "arr": arr_dt.strftime("%H:%M"),
            "dep_date": dep_dt.strftime("%-d %b"),   # ex. "24 juil" affiché si train de nuit
            "arr_date": arr_dt.strftime("%-d %b"),
            "duration_min": duration_min,
            "nb_transfers": nb_transfers,
            "train_number": train_number,
            "train_name": train_name,
            "dep_dt": dep_dt,
            "arr_dt": arr_dt,
            "is_night_train": is_night_train,
        })

    results.sort(key=lambda x: (x["nb_transfers"], x["dep_dt"]))
    return results


# ─────────────────────────────────────────────
# LOGIQUE STATUT
# ─────────────────────────────────────────────
def compute_statut(membre: dict) -> str:
    if membre["statut"] == "arrive":
        return "arrive"
    now = datetime.now()
    try:
        date_arr = datetime.strptime(membre["date_arrivee"], "%Y-%m-%d").date() \
                   if membre.get("date_arrivee") else now.date()
        h_dep = datetime.strptime(membre["heure_depart"], "%H:%M").time()
        h_arr = datetime.strptime(membre["heure_arrivee"], "%H:%M").time()

        dt_arr = datetime.combine(date_arr, h_arr)

        # ── FIX train de nuit : si h_dep > h_arr, le départ était la veille ──
        date_dep = date_arr - timedelta(days=1) if h_dep > h_arr else date_arr
        dt_dep   = datetime.combine(date_dep, h_dep)

    except Exception:
        return membre["statut"]

    if now < dt_dep:
        return "pas_parti"
    if dt_dep <= now < dt_arr:
        return "en_route"
    return "arrive"

def get_badge_class(statut: str, direction: str) -> str:
    if direction == "retour":
        return "badge-retour"
    return f"badge-{statut}"

def get_badge_label(statut: str, direction: str) -> str:
    if direction == "retour" and statut == "pas_parti":
        return "Pas encore reparti"
    labels = {"pas_parti": "Pas encore parti", "en_route": "En route", "arrive": "Arrivé·e !"}
    return labels.get(statut, statut)

def get_card_class(statut: str, direction: str) -> str:
    if direction == "retour" and statut in ("pas_parti", "en_route"):
        return "retour"
    return statut

def format_countdown(membre: dict) -> str:
    try:
        date_arr = datetime.strptime(membre["date_arrivee"], "%Y-%m-%d").date() \
                   if membre.get("date_arrivee") else date.today()
        target = datetime.combine(date_arr, datetime.strptime(membre["heure_arrivee"], "%H:%M").time())
        delta = target - datetime.now()
        if delta.total_seconds() <= 0:
            return "maintenant"
        total_s = int(delta.total_seconds())
        h, rem = divmod(total_s, 3600)
        m, s = divmod(rem, 60)
        if h >= 24:
            jours = h // 24
            return f"{jours}j {h % 24}h"
        if h > 0:
            return f"{h}h {m:02d}m"
        if m > 0:
            return f"{m}m {s:02d}s"
        return f"{s}s"
    except Exception:
        return "—"

def fmt_date(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%-d %b")
    except Exception:
        return ""


# ─────────────────────────────────────────────
# CALENDRIER
# ─────────────────────────────────────────────
def render_calendrier(membres: list):
    import streamlit.components.v1 as components

    by_date: dict = {}
    for m in membres:
        d = m.get("date_arrivee")
        if d:
            by_date.setdefault(d, []).append(m)

    year, month = 2026, 7
    today = date.today()
    cal = calendar.monthcalendar(year, month)
    jours_fr = ["Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"]
    weekend_days = {24, 25, 26, 27}

    grid_html = ""
    for dow in jours_fr:
        grid_html += f'<div class="cal-dow">{dow}</div>'

    for week in cal:
        for day_num in week:
            if day_num == 0:
                grid_html += '<div class="cal-day empty"></div>'
                continue

            d_obj = date(year, month, day_num)
            d_str = d_obj.strftime("%Y-%m-%d")
            trajets = by_date.get(d_str, [])

            classes = "cal-day"
            if day_num in weekend_days:
                classes += " weekend-bg"
            if d_obj == today:
                classes += " today"

            dots_html = ""
            if trajets:
                dots_html = '<div class="cal-dots">'
                for t in trajets:
                    dot_cls = "dot-retour" if t.get("direction") == "retour" else "dot-aller"
                    prenom_safe = t["prenom"].replace('"', '')
                    dots_html += f'<span class="dot {dot_cls}" title="{prenom_safe}"></span>'
                dots_html += "</div>"

            grid_html += f'<div class="{classes}"><div class="cal-day-num">{day_num}</div>{dots_html}</div>'

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=DM+Mono:wght@500&family=Playfair+Display:wght@700&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'DM Sans', sans-serif; background: white; padding: 20px; border-radius: 16px; }}
  h2 {{ font-family: 'Playfair Display', serif; font-size: 20px; color: #0f172a; margin-bottom: 16px; }}
  .cal-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; text-align: center; }}
  .cal-dow {{ font-family: 'DM Mono', monospace; font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; padding: 4px 0; letter-spacing: 0.05em; }}
  .cal-day {{ font-size: 12px; padding: 5px 2px; border-radius: 8px; min-height: 52px; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding-top: 5px; background: #f8fafc; }}
  .cal-day.empty {{ background: transparent; }}
  .cal-day.weekend-bg {{ background: #eff6ff; }}
  .cal-day.today {{ outline: 2px solid #0ea5e9; }}
  .cal-day-num {{ font-weight: 700; color: #0f172a; font-size: 13px; }}
  .cal-day.weekend-bg .cal-day-num {{ color: #0284c7; }}
  .cal-dots {{ display: flex; gap: 2px; flex-wrap: wrap; justify-content: center; margin-top: 3px; }}
  .dot {{ width: 7px; height: 7px; border-radius: 50%; display: inline-block; }}
  .dot-aller  {{ background: #0ea5e9; }}
  .dot-retour {{ background: #8b5cf6; }}
  .legend {{ display: flex; gap: 16px; margin-top: 14px; font-size: 12px; color: #475569; align-items: center; flex-wrap: wrap; }}
  .legend span {{ display: flex; align-items: center; gap: 5px; }}
  .ldot {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex-shrink: 0; }}
  .weekend-badge {{ background: #eff6ff; padding: 2px 10px; border-radius: 20px; font-size: 11px; color: #0284c7; font-weight: 700; }}
</style>
</head>
<body>
  <h2>📅 Juillet 2026</h2>
  <div class="cal-grid">{grid_html}</div>
  <div class="legend">
    <span><span class="ldot" style="background:#0ea5e9"></span> Aller vers Nice</span>
    <span><span class="ldot" style="background:#8b5cf6"></span> Retour</span>
    <span class="weekend-badge">Weekend 24–27 juillet</span>
  </div>
</body>
</html>"""

    components.html(full_html, height=360, scrolling=False)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "my_ids":            [],
    "show_form":         False,
    "form_prenom":       "",
    "form_ville":        "",
    "form_date":         DATE_DEFAULT,
    "form_h_dep":        None,
    "form_h_arr":        None,
    "form_train":        "",
    "form_direction":    "Aller — vers Nice",
    "search_done":       False,
    "search_results":    [],
    "search_query_ville": "",
    "search_query_date": DATE_DEFAULT,
    "selected_train_idx": None,
    "form_gare_stop_id": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# DONNÉES
# ─────────────────────────────────────────────
membres = get_membres()

allers  = [m for m in membres if m.get("direction", "aller") == "aller"]
retours = [m for m in membres if m.get("direction") == "retour"]

nb_arrives = sum(1 for m in allers if compute_statut(m) == "arrive")
nb_route   = sum(1 for m in allers if compute_statut(m) == "en_route")
nb_attente = len(allers) - nb_arrives - nb_route

en_route_sorted = sorted(
    [m for m in allers if compute_statut(m) == "en_route"],
    key=lambda m: (m.get("date_arrivee", ""), m["heure_arrivee"])
)
prochain = en_route_sorted[0] if en_route_sorted else None


# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Weekend du 25 juillet 2026</div>
    <h1 class="hero-title">Nous à Nice ☀️</h1>
    <p class="hero-sub">Mettez vos trains les zamis</p>
</div>
""", unsafe_allow_html=True)

if allers:
    col1, col2, col3 = st.columns(3)
    col1.metric("Arrivé·e·s", nb_arrives)
    col2.metric("En route", nb_route)
    col3.metric("Pas encore partis", nb_attente)


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_dashboard, tab_calendrier = st.tabs(["🚄 Trajets", "📅 Calendrier"])


# ══════════════════════════════════════════════
# TAB DASHBOARD
# ══════════════════════════════════════════════
with tab_dashboard:

    def prefill_from_train(idx: int):
        results = st.session_state.search_results
        if idx < 0 or idx >= len(results):
            return
        t = results[idx]
        st.session_state.form_h_dep   = t["dep_dt"].time()
        st.session_state.form_h_arr   = t["arr_dt"].time()
        st.session_state.form_train   = t["train_number"]
        st.session_state.selected_train_idx = idx

    def reset_search():
        st.session_state.search_done        = False
        st.session_state.search_results     = []
        st.session_state.selected_train_idx = None
        st.session_state.form_h_dep         = None
        st.session_state.form_h_arr         = None
        st.session_state.form_train         = ""

    def render_formulaire():
        direction_idx = 0 if st.session_state.form_direction == "Aller — vers Nice" else 1
        direction = st.radio(
            "Type de trajet",
            ["Aller — vers Nice", "Retour — depuis Nice"],
            index=direction_idx,
            horizontal=True,
            key="radio_direction",
        )
        st.session_state.form_direction = direction
        is_retour = direction.startswith("Retour")

        prenom = st.text_input("Prénom *", value=st.session_state.form_prenom,
                               placeholder="ex. Sophie", key="input_prenom")
        st.session_state.form_prenom = prenom

        ville_label = "Destination *"             if is_retour else "Gare de départ *"
        date_label  = "Date d'arrivée à destination *"
        dep_label   = "Heure de départ de Nice *" if is_retour else "Heure de départ *"
        arr_label   = "Heure d'arrivée *"

        st.markdown(f'''<label style="font-size:14px;font-weight:600;color:#1e293b">{ville_label}</label>''',
                    unsafe_allow_html=True)
        selected_gare = st_searchbox(
            autocomplete_gare,
            key="searchbox_gare",
            placeholder="ex. Paris Gare de Lyon...",
            label=None,
            default=st.session_state.get("form_gare_tuple"),
            default_use_searchterm=True,
            edit_after_submit="option",
        )

        if isinstance(selected_gare, str) and selected_gare.strip():
            gare_label   = selected_gare
            gare_stop_id = st.session_state.get("_gare_id_map", {}).get(selected_gare)
        else:
            gare_label, gare_stop_id = "", None

        if gare_label != st.session_state.form_ville:
            reset_search()
        st.session_state.form_ville = gare_label
        st.session_state.form_gare_stop_id = gare_stop_id

        d_sel = st.date_input(
            date_label,
            value=st.session_state.form_date,
            min_value=date(2026, 7, 1),
            max_value=date(2026, 8, 31),
            key="input_date",
        )
        if d_sel != st.session_state.form_date:
            reset_search()
        st.session_state.form_date = d_sel

        # ── Info contextuelle train de nuit ──
        st.markdown("""
        <div style="font-size:12px; color:#64748b; margin: 2px 0 8px 0; font-style:italic;">
            🌙 Train de nuit ? Indique la date d'<strong>arrivée</strong> — les horaires de départ la veille seront gérés automatiquement.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        col_search, col_reset = st.columns([3, 1])
        with col_search:
            do_search = st.button(
                "🔍 Rechercher les trains SNCF",
                use_container_width=True,
                disabled=not gare_label.strip(),
                key="btn_search",
            )
        with col_reset:
            if st.session_state.search_done:
                if st.button("✕ Effacer", use_container_width=True, key="btn_clear_search"):
                    reset_search()
                    st.rerun()

            if st.button("Vider le cache API"):
                autocomplete_gare.clear()
                search_trains.clear()
                st.success("Cache vidé")

        if do_search and gare_label.strip():
            with st.spinner("Recherche des trains…"):
                stop_id = gare_stop_id
                if not stop_id:
                    autocomplete_gare(gare_label.strip())
                    stop_id = st.session_state.get("_gare_id_map", {}).get(gare_label.strip())

                if not stop_id:
                    st.session_state.search_done = True
                    st.session_state.search_results = []
                    st.session_state.search_query_ville = gare_label.strip()
                    st.session_state.search_query_date = d_sel
                else:
                    from_id = stop_id      if not is_retour else NICE_STOP_ID
                    to_id   = NICE_STOP_ID if not is_retour else stop_id

                    # ── FIX train de nuit : on démarre la recherche la veille à 18h00
                    #    pour capturer les trains de nuit qui partent le soir précédent.
                    search_date = d_sel - timedelta(days=1)
                    dt_str = search_date.strftime("%Y%m%dT180000")

                    trains  = search_trains(from_id, to_id, dt_str)
                    st.session_state.search_done = True
                    st.session_state.search_results = trains
                    st.session_state.search_query_ville = gare_label.strip()
                    st.session_state.search_query_date = d_sel
            st.rerun()

        if st.session_state.search_done:
            results = st.session_state.search_results
            if not results:
                stop_used = st.session_state.get("form_gare_stop_id", "inconnu")
                st.markdown(f"""
                <div class="search-error">
                    😕 Aucun train trouvé pour <strong>{st.session_state.search_query_ville}</strong>
                    le {st.session_state.search_query_date.strftime("%-d %B %Y")}.<br>
                    <span style="font-size:11px;opacity:0.7">stop_id utilisé : {stop_used}</span><br>
                    Vérifie le nom de la gare ou remplis les horaires manuellement ci-dessous.
                </div>
                """, unsafe_allow_html=True)
            else:
                n = len(results)
                date_fmt = st.session_state.search_query_date.strftime("%-d %B")
                nb_nuit = sum(1 for t in results if t.get("is_night_train"))
                nuit_info = f" dont {nb_nuit} train{'s' if nb_nuit > 1 else ''} de nuit 🌙" if nb_nuit else ""
                st.markdown(f"""
                <div class="search-info">
                    🚄 {n} train{"s" if n > 1 else ""} trouvé{"s" if n > 1 else ""}
                    depuis <strong>{st.session_state.search_query_ville}</strong>
                    le {date_fmt}{nuit_info} — clique pour pré-remplir
                </div>
                """, unsafe_allow_html=True)

                for i, t in enumerate(results):
                    is_selected = st.session_state.selected_train_idx == i
                    card_cls = "train-result selected" if is_selected else "train-result"
                    tag_direct = (
                        '<span class="train-direct">Direct</span>'
                        if t["nb_transfers"] == 0
                        else f'<span class="train-correspondance">{t["nb_transfers"]} correspondance{"s" if t["nb_transfers"] > 1 else ""}</span>'
                    )
                    # Badge train de nuit
                    tag_nuit = '<span class="train-nuit">🌙 Nuit</span>' if t.get("is_night_train") else ""

                    h = t["duration_min"] // 60
                    mn = t["duration_min"] % 60
                    duree_str = f"{h}h{mn:02d}" if h else f"{mn}min"
                    num_str = f'<span class="train-num">{t["train_number"]}</span>' if t["train_number"] else ""
                    type_str = f'<span class="train-type">{t["train_name"]}</span>' if t["train_name"] else ""

                    # Affiche les dates si train de nuit (départ ≠ arrivée)
                    if t.get("is_night_train"):
                        horaires_str = f'{t["dep_date"]} {t["dep"]} → {t["arr_date"]} {t["arr"]}'
                    else:
                        horaires_str = f'{t["dep"]} → {t["arr"]}'

                    st.markdown(f"""
                    <div class="{card_cls}">
                        <div class="train-result-top">
                            {num_str}{type_str}{tag_direct}{tag_nuit}
                        </div>
                        <div style="display:flex; align-items:baseline; gap:10px; margin-top:4px;">
                            <span class="train-horaires">{horaires_str}</span>
                            <span class="train-duree">({duree_str})</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_label = "✓ Sélectionné" if is_selected else "Choisir ce train"
                    if st.button(btn_label, key=f"pick_{i}", use_container_width=True,
                                 type="primary" if not is_selected else "secondary"):
                        prefill_from_train(i)
                        st.rerun()

        if st.session_state.selected_train_idx is not None:
            t = st.session_state.search_results[st.session_state.selected_train_idx]
            nuit_mention = " · 🌙 Train de nuit" if t.get("is_night_train") else ""
            st.markdown(f"""
            <div class="prefill-banner">
                ✅ Train <strong>{t['train_number']}</strong> sélectionné —
                {t['dep']} → {t['arr']} · horaires pré-remplis ci-dessous{nuit_mention}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="color:#94a3b8; font-size:12px; margin: 8px 0 4px 0; font-family: 'DM Mono', monospace; text-transform:uppercase; letter-spacing:0.08em;">
                ou remplis manuellement
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            h_dep_val = st.session_state.form_h_dep
            h_dep = st.time_input(dep_label, value=h_dep_val, key="input_h_dep")
            st.session_state.form_h_dep = h_dep
        with col2:
            h_arr_val = st.session_state.form_h_arr
            h_arr = st.time_input(arr_label, value=h_arr_val, key="input_h_arr")
            st.session_state.form_h_arr = h_arr

        # ── Avertissement visuel si saisie manuelle détecte un train de nuit ──
        if h_dep and h_arr and h_dep > h_arr:
            st.markdown("""
            <div style="background:#eef2ff; border:1px solid #c7d2fe; border-radius:8px;
                        padding:8px 12px; font-size:12px; color:#3730a3; margin-top:4px;">
                🌙 <strong>Train de nuit détecté</strong> — le départ sera considéré la veille de la date d'arrivée saisie.
            </div>
            """, unsafe_allow_html=True)

        train = st.text_input(
            "n°voiture et n°place (optionnel)",
            value=st.session_state.form_train,
            placeholder="ex. Voiture 3 Place 306",
            key="input_train",
        )
        st.session_state.form_train = train

        st.markdown("")
        col_save, col_cancel = st.columns([2, 1])
        with col_save:
            if st.button("Enregistrer", use_container_width=True, type="primary", key="btn_save"):
                if not prenom or not gare_label.strip() or not d_sel or not h_dep or not h_arr:
                    st.error("Remplis tous les champs obligatoires.")
                else:
                    data = {
                        "prenom":        prenom.strip(),
                        "ville_depart":  gare_label.strip(),
                        "date_arrivee":  d_sel.strftime("%Y-%m-%d"),
                        "heure_depart":  h_dep.strftime("%H:%M"),
                        "heure_arrivee": h_arr.strftime("%H:%M"),
                        "numero_train":  train.strip() or None,
                        "statut":        "pas_parti",
                        "direction":     "retour" if is_retour else "aller",
                    }
                    result = add_membre(data)
                    if result:
                        st.session_state.my_ids.append(result["id"])
                        st.session_state.show_form  = False
                        st.session_state.form_prenom = ""
                        st.session_state.form_ville  = ""
                        st.session_state.form_date   = DATE_DEFAULT
                        reset_search()
                        st.success(f"Trajet de {prenom} enregistré !")
                        st.rerun()
                    else:
                        st.error("Erreur lors de l'enregistrement. Vérifie les clés Supabase.")
        with col_cancel:
            if st.button("Annuler", use_container_width=True, key="btn_cancel"):
                st.session_state.show_form = False
                reset_search()
                st.rerun()

    if not st.session_state.show_form:
        st.button("＋ Ajouter un trajet", use_container_width=True, type="primary",
                  on_click=lambda: st.session_state.update(show_form=True))
    else:
        with st.container(border=True):
            st.markdown("**Mon trajet**")
            render_formulaire()

    if prochain:
        countdown = format_countdown(prochain)
        date_str  = fmt_date(prochain.get("date_arrivee", ""))
        st.markdown(f"""
        <div class="countdown-box">
            <div class="countdown-left">
                <div class="eyebrow">Prochaine arrivée à Nice</div>
                <div class="countdown-name">{prochain['prenom']}</div>
                <div class="countdown-detail">{prochain['ville_depart']} → Nice · {date_str} à {prochain['heure_arrivee']}</div>
            </div>
            <div>
                <div class="countdown-time">{countdown}</div>
                <div class="countdown-sublabel">avant l'arrivée</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def render_trajet(m: dict):
        statut    = compute_statut(m)
        direction = m.get("direction", "aller")
        card_cls  = get_card_class(statut, direction)
        badge_cls = get_badge_class(statut, direction)
        badge_lbl = get_badge_label(statut, direction)
        train_str = f" · {m['numero_train']}" if m.get("numero_train") else ""
        date_str  = fmt_date(m.get("date_arrivee", ""))
        dir_tag   = "RETOUR" if direction == "retour" else "ALLER"
        icon      = "🎉" if statut == "arrive" else ("🚄" if statut == "en_route" else ("🏠" if direction == "aller" else "🧳"))
        trajet_str = f"Nice → {m['ville_depart']}" if direction == "retour" else f"{m['ville_depart']} → Nice"

        # ── Indicateur train de nuit en saisie manuelle ──
        try:
            h_dep_t = datetime.strptime(m["heure_depart"], "%H:%M").time()
            h_arr_t = datetime.strptime(m["heure_arrivee"], "%H:%M").time()
            nuit_icon = " 🌙" if h_dep_t > h_arr_t else ""
        except Exception:
            nuit_icon = ""

        st.markdown(f"""
        <div class="membre-card {card_cls}">
            <div class="membre-top">
                <span style="font-size:20px">{icon}</span>
                <span class="membre-nom">{m['prenom']}</span>
                <span class="badge {badge_cls}">{badge_lbl}</span>
                <span class="direction-tag">{dir_tag}</span>
            </div>
            <div class="membre-trajet">{trajet_str}</div>
            <div class="membre-horaires">🚆 {date_str} · {m['heure_depart']} → {m['heure_arrivee']}{train_str}{nuit_icon}</div>
        </div>
        """, unsafe_allow_html=True)

        if m["id"] in st.session_state.my_ids:
            c1, c2, _ = st.columns([1.5, 1, 2])
            with c1:
                if statut != "arrive":
                    label = "🎉 Je suis arrivé·e !" if direction == "aller" else "🎉 Je suis rentré·e !"
                    if st.button(label, key=f"arr_{m['id']}", use_container_width=True):
                        update_statut(m["id"], "arrive")
                        st.rerun()
            with c2:
                if st.button("Supprimer", key=f"del_{m['id']}", use_container_width=True):
                    delete_membre(m["id"])
                    st.session_state.my_ids.remove(m["id"])
                    st.rerun()

    if not membres:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🚉</div>
            <div class="empty-title">Personne n'a encore ajouté son trajet</div>
            <div>Sois le premier à indiquer ton heure d'arrivée.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if allers:
            st.markdown('<div class="section-title">Arrivées à Nice</div>', unsafe_allow_html=True)
            for m in allers:
                render_trajet(m)
        if retours:
            st.markdown('<div class="section-title">Retours</div>', unsafe_allow_html=True)
            for m in retours:
                render_trajet(m)


# ══════════════════════════════════════════════
# TAB CALENDRIER
# ══════════════════════════════════════════════
with tab_calendrier:
    render_calendrier(membres)

    if membres:
        by_date_sorted = {}
        for m in membres:
            d = m.get("date_arrivee", "")
            by_date_sorted.setdefault(d, []).append(m)

        for d_str in sorted(by_date_sorted.keys()):
            try:
                d_obj = datetime.strptime(d_str, "%Y-%m-%d")
                label = d_obj.strftime("%A %-d %B %Y").capitalize()
            except Exception:
                label = d_str
            st.markdown(f'<div class="section-title">{label}</div>', unsafe_allow_html=True)
            for m in by_date_sorted[d_str]:
                direction  = m.get("direction", "aller")
                trajet_str = f"Nice → {m['ville_depart']}" if direction == "retour" else f"{m['ville_depart']} → Nice"
                dir_tag    = "RETOUR" if direction == "retour" else "ALLER"
                statut     = compute_statut(m)
                icon       = "🎉" if statut == "arrive" else ("🚄" if statut == "en_route" else ("🏠" if direction == "aller" else "🧳"))
                try:
                    h_dep_t = datetime.strptime(m["heure_depart"], "%H:%M").time()
                    h_arr_t = datetime.strptime(m["heure_arrivee"], "%H:%M").time()
                    nuit_icon = " 🌙" if h_dep_t > h_arr_t else ""
                except Exception:
                    nuit_icon = ""
                st.markdown(f"""
                <div class="membre-card {get_card_class(statut, direction)}">
                    <div class="membre-top">
                        <span style="font-size:18px">{icon}</span>
                        <span class="membre-nom">{m['prenom']}</span>
                        <span class="badge {get_badge_class(statut, direction)}">{get_badge_label(statut, direction)}</span>
                        <span class="direction-tag">{dir_tag}</span>
                    </div>
                    <div class="membre-trajet">{trajet_str}</div>
                    <div class="membre-horaires">🚆 {m['heure_depart']} → {m['heure_arrivee']}{' · ' + m['numero_train'] if m.get('numero_train') else ''}{nuit_icon}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📅</div>
            <div class="empty-title">Aucun trajet planifié</div>
            <div>Ajoute ton trajet dans l'onglet Trajets.</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# REFRESH AUTO
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:32px; font-size:11px;
color:#cbd5e1; font-family:'DM Mono', monospace;">
    Mise à jour automatique toutes les 15 secondes
</div>
""", unsafe_allow_html=True)

time.sleep(15)
st.rerun()