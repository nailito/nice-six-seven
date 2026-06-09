# Dashboard Vacances Nice 🌊

## Structure du projet

```
nice-dashboard/
├── app.py
├── requirements.txt
└── .streamlit/
    └── secrets.toml
```

---

## Étape 1 — Supabase (base de données)

1. Crée un compte gratuit sur https://supabase.com
2. Crée un nouveau projet (région : eu-west — Frankfurt, plus proche)
3. Va dans **SQL Editor** et exécute ce SQL :

```sql
CREATE TABLE membres (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  prenom text NOT NULL,
  ville_depart text NOT NULL,
  heure_depart text NOT NULL,
  heure_arrivee text NOT NULL,
  numero_train text,
  statut text DEFAULT 'pas_parti',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE membres ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public_all" ON membres
  FOR ALL USING (true) WITH CHECK (true);
```

4. Va dans **Project Settings → API** et copie :
   - **Project URL** → `SUPABASE_URL`
   - **anon / public key** → `SUPABASE_KEY`

5. Colle ces valeurs dans `.streamlit/secrets.toml`

---

## Étape 2 — Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

L'app s'ouvre sur http://localhost:8501

---

## Étape 3 — Déployer en ligne (Streamlit Community Cloud)

C'est gratuit et ça prend 5 minutes.

1. Pousse le projet sur GitHub :
```bash
git init
git add .
git commit -m "Nice dashboard"
gh repo create nice-dashboard --public --push
```

2. Va sur https://share.streamlit.io
3. Clique **New app**, sélectionne ton repo, branche `main`, fichier `app.py`
4. Dans **Advanced settings → Secrets**, colle le contenu de ton `secrets.toml`
5. Clique **Deploy**

Tu obtiens un lien du type `https://nice-dashboard-xxxx.streamlit.app` à partager au groupe.

---

## Plus tard : API SNCF pour les retards en temps réel

Quand tu veux brancher l'API SNCF :

1. Inscris-toi sur https://data.sncf.com et génère une clé API
2. Ajoute `SNCF_API_KEY` dans `secrets.toml`
3. Utilise l'endpoint :
   ```
   https://api.sncf.com/v1/coverage/sncf/vehicle_journeys?headsign=<NUMERO_TRAIN>
   ```
4. Claude peut générer ce code pour toi quand tu es prêt
