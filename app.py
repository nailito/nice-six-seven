import streamlit as st
from supabase import create_client
from datetime import datetime, date
import time

# ─────────────────────────────────────────────
# CONFIG — à remplir avec tes clés Supabase
# ─────────────────────────────────────────────
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# ─────────────────────────────────────────────
# CSS CUSTOM
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Header hero */
.hero {
    background: linear-gradient(160deg, #0c4a6e 0%, #075985 60%, #0ea5e9 100%);
    border-radius: 18px;
    padding: 28px 28px 36px;
    color: white;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -16px; left: -10%; right: -10%;
    height: 36px;
    background: #f0f7ff;
    border-radius: 50%;
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
.hero-sub {
    font-size: 14px;
    opacity: 0.8;
    margin: 0;
}

/* Stats bar */
.stats-row {
    display: flex;
    gap: 12px;
    margin-top: 18px;
    flex-wrap: wrap;
}
.stat-chip {
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(8px);
    border-radius: 10px;
    padding: 8px 16px;
    min-width: 80px;
}
.stat-val {
    font-family: 'DM Mono', monospace;
    font-size: 24px;
    font-weight: 700;
    line-height: 1;
}
.stat-label {
    font-size: 11px;
    opacity: 0.75;
    margin-top: 2px;
}

/* Compte à rebours */
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
.countdown-name {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 700;
}
.countdown-detail {
    font-size: 12px;
    opacity: 0.8;
    margin-top: 2px;
}
.countdown-time {
    font-family: 'DM Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    text-align: right;
    line-height: 1;
}
.countdown-sublabel {
    font-size: 10px;
    opacity: 0.65;
    text-align: right;
    margin-top: 3px;
}

/* Carte membre */
.membre-card {
    background: white;
    border-radius: 14px;
    padding: 14px 18px 14px 22px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.04);
    border-left: 4px solid #e2e8f0;
    position: relative;
}
.membre-card.arrive   { border-left-color: #10b981; }
.membre-card.en_route { border-left-color: #f59e0b; }
.membre-card.pas_parti { border-left-color: #94a3b8; }

.membre-top {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
.membre-nom {
    font-family: 'Playfair Display', serif;
    font-size: 17px;
    font-weight: 700;
    color: #0f172a;
}
.badge {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    letter-spacing: 0.03em;
}
.badge-arrive   { background: #ecfdf5; color: #10b981; }
.badge-en_route { background: #fffbeb; color: #f59e0b; }
.badge-pas_parti { background: #f1f5f9; color: #94a3b8; }

.membre-trajet {
    font-size: 13px;
    color: #64748b;
    margin-top: 3px;
}
.membre-horaires {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: #94a3b8;
    margin-top: 2px;
}

/* Formulaire */
.form-box {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 0 0 2px #f97316, 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 24px;
}
.form-title {
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 16px;
}

/* Vide */
.empty-state {
    text-align: center;
    padding: 48px 24px;
    background: white;
    border-radius: 16px;
    color: #94a3b8;
}
.empty-icon { font-size: 40px; margin-bottom: 12px; }
.empty-title {
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    color: #475569;
    margin-bottom: 6px;
}

/* Override Streamlit */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: #f0f7ff;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
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

def compute_statut(membre: dict) -> str:
    if membre["statut"] == "arrive":
        return "arrive"
    now = datetime.now()
    try:
        date_arr = datetime.strptime(membre["date_arrivee"], "%Y-%m-%d").date() if membre.get("date_arrivee") else now.date()
        h_dep = datetime.strptime(membre["heure_depart"], "%H:%M").time()
        h_arr = datetime.strptime(membre["heure_arrivee"], "%H:%M").time()
        dt_dep = datetime.combine(date_arr, h_dep)
        dt_arr = datetime.combine(date_arr, h_arr)
    except Exception:
        return membre["statut"]
    if now < dt_dep:
        return "pas_parti"
    if dt_dep <= now < dt_arr:
        return "en_route"
    return "arrive"

STATUT_CONFIG = {
    "pas_parti": {"label": "Pas encore parti",  "icon": "🏠", "badge": "badge-pas_parti", "card": "pas_parti"},
    "en_route":  {"label": "En route",           "icon": "🚄", "badge": "badge-en_route",  "card": "en_route"},
    "arrive":    {"label": "Arrivé·e !",          "icon": "🎉", "badge": "badge-arrive",    "card": "arrive"},
}

def format_countdown(membre: dict) -> str:
    try:
        date_arr = datetime.strptime(membre["date_arrivee"], "%Y-%m-%d").date() if membre.get("date_arrivee") else date.today()
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


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "my_id" not in st.session_state:
    st.session_state.my_id = None
if "show_form" not in st.session_state:
    st.session_state.show_form = False
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()


# ─────────────────────────────────────────────
# DONNÉES
# ─────────────────────────────────────────────
membres = get_membres()
nb_total   = len(membres)
nb_arrives = sum(1 for m in membres if compute_statut(m) == "arrive")
nb_route   = sum(1 for m in membres if compute_statut(m) == "en_route")
nb_attente = nb_total - nb_arrives - nb_route

en_route_sorted = sorted(
    [m for m in membres if compute_statut(m) == "en_route"],
    key=lambda m: m["heure_arrivee"]
)
prochain = en_route_sorted[0] if en_route_sorted else None


# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
stats_html = ""
if nb_total > 0:
    stats_html = f"""
    <div class="stats-row">
        <div class="stat-chip">
            <div class="stat-val" style="color:#10b981">{nb_arrives}</div>
            <div class="stat-label">arrivé·e·s</div>
        </div>
        <div class="stat-chip">
            <div class="stat-val" style="color:#f59e0b">{nb_route}</div>
            <div class="stat-label">en route</div>
        </div>
        <div class="stat-chip">
            <div class="stat-val" style="color:#94a3b8">{nb_attente}</div>
            <div class="stat-label">pas encore partis</div>
        </div>
    </div>
    """

st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">Vacances d'été 2025</div>
    <h1 class="hero-title">On arrive à Nice ☀️</h1>
    <p class="hero-sub">Suis les arrivées de toute la bande en temps réel</p>
    {stats_html}
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FORMULAIRE
# ─────────────────────────────────────────────
if not st.session_state.my_id:
    if not st.session_state.show_form:
        if st.button("＋ Ajouter mon trajet", use_container_width=True, type="primary"):
            st.session_state.show_form = True
            st.rerun()
    else:
        st.markdown('<div class="form-box"><div class="form-title">Mon trajet vers Nice</div></div>', unsafe_allow_html=True)

        with st.container():
            prenom = st.text_input("Prénom *", placeholder="ex. Sophie")
            ville  = st.text_input("Ville de départ *", placeholder="ex. Paris Gare de Lyon")
            d_arr  = st.date_input("Date d'arrivée à Nice *", value=None, min_value=date.today())
            col1, col2 = st.columns(2)
            with col1:
                h_dep = st.time_input("Heure de départ *", value=None)
            with col2:
                h_arr = st.time_input("Heure d'arrivée à Nice *", value=None)
            train = st.text_input("Numéro de train (optionnel)", placeholder="ex. TGV 6173")

            col_save, col_cancel = st.columns([2, 1])
            with col_save:
                if st.button("Enregistrer mon trajet", use_container_width=True, type="primary"):
                    if not prenom or not ville or not d_arr or not h_dep or not h_arr:
                        st.error("Remplis tous les champs obligatoires.")
                    else:
                        data = {
                            "prenom": prenom.strip(),
                            "ville_depart": ville.strip(),
                            "date_arrivee": d_arr.strftime("%Y-%m-%d"),
                            "heure_depart": h_dep.strftime("%H:%M"),
                            "heure_arrivee": h_arr.strftime("%H:%M"),
                            "numero_train": train.strip() or None,
                            "statut": "pas_parti",
                        }
                        result = add_membre(data)
                        if result:
                            st.session_state.my_id = result["id"]
                            st.session_state.show_form = False
                            st.success(f"Trajet de {prenom} enregistré !")
                            st.rerun()
                        else:
                            st.error("Erreur lors de l'enregistrement. Vérifie les clés Supabase.")
            with col_cancel:
                if st.button("Annuler", use_container_width=True):
                    st.session_state.show_form = False
                    st.rerun()


# ─────────────────────────────────────────────
# COMPTE À REBOURS
# ─────────────────────────────────────────────
if prochain:
    countdown = format_countdown(prochain)
    date_str = datetime.strptime(prochain["date_arrivee"], "%Y-%m-%d").strftime("%-d %b") if prochain.get("date_arrivee") else ""
    st.markdown(f"""
    <div class="countdown-box">
        <div class="countdown-left">
            <div class="eyebrow">Prochaine arrivée</div>
            <div class="countdown-name">{prochain['prenom']}</div>
            <div class="countdown-detail">{prochain['ville_depart']} → Nice · {date_str} {prochain['heure_arrivee']}</div>
        </div>
        <div>
            <div class="countdown-time">{countdown}</div>
            <div class="countdown-sublabel">avant l'arrivée</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LISTE DES MEMBRES
# ─────────────────────────────────────────────
if not membres:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🚉</div>
        <div class="empty-title">Personne n'a encore ajouté son trajet</div>
        <div>Sois le premier à indiquer ton heure d'arrivée.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for m in membres:
        statut = compute_statut(m)
        cfg = STATUT_CONFIG[statut]
        train_str = f" · {m['numero_train']}" if m.get("numero_train") else ""
        date_str = datetime.strptime(m["date_arrivee"], "%Y-%m-%d").strftime("%-d %b") if m.get("date_arrivee") else ""

        st.markdown(f"""
        <div class="membre-card {cfg['card']}">
            <div class="membre-top">
                <span style="font-size:20px">{cfg['icon']}</span>
                <span class="membre-nom">{m['prenom']}</span>
                <span class="badge {cfg['badge']}">{cfg['label']}</span>
            </div>
            <div class="membre-trajet">{m['ville_depart']} → Nice</div>
            <div class="membre-horaires">🚆 {date_str} · {m['heure_depart']} → {m['heure_arrivee']}{train_str}</div>
        </div>
        """, unsafe_allow_html=True)

        # Boutons d'action si c'est mon trajet
        if m["id"] == st.session_state.my_id:
            col_arr, col_del, _ = st.columns([1.5, 1, 2])
            with col_arr:
                if statut != "arrive":
                    if st.button("🎉 Je suis arrivé·e !", key=f"arr_{m['id']}", use_container_width=True):
                        update_statut(m["id"], "arrive")
                        st.rerun()
            with col_del:
                if st.button("Supprimer", key=f"del_{m['id']}", use_container_width=True):
                    delete_membre(m["id"])
                    st.session_state.my_id = None
                    st.rerun()


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