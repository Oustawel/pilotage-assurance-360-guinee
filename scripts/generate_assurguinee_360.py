"""
=============================================================================
AssurGuinée 360 — Générateur de Dataset Fictif
Projet : Pilotage Assurance 360 — Performance, Sinistres, Rentabilité, Renouvellement
Auteur : Alpha Data Solutions (ADS)
Devise  : Franc guinéen (GNF)
Période : 01/01/2023 — 31/12/2025
=============================================================================
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date

# Reproductibilité
random.seed(42)
np.random.seed(42)

# ─── Dossier de sortie ────────────────────────────────────────────────────────
OUTPUT_DIR = "dataset_pilotage_assurance_360_guinee"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Constantes ───────────────────────────────────────────────────────────────
START_DATE = date(2023, 1, 1)
END_DATE   = date(2025, 12, 31)

VILLES = [
    "Conakry", "Kindia", "Labé", "Kankan", "Nzérékoré",
    "Boké", "Mamou", "Faranah", "Siguiri", "Guéckédou",
    "Kissidougou", "Dubréka"
]

VILLE_REGION = {
    "Conakry": "Conakry",
    "Dubréka": "Basse Guinée",
    "Kindia": "Basse Guinée",
    "Boké": "Basse Guinée",
    "Labé": "Moyenne Guinée",
    "Mamou": "Moyenne Guinée",
    "Kankan": "Haute Guinée",
    "Siguiri": "Haute Guinée",
    "Faranah": "Haute Guinée",
    "Nzérékoré": "Guinée Forestière",
    "Guéckédou": "Guinée Forestière",
    "Kissidougou": "Guinée Forestière",
}

CANAUX_ACQUISITION = [
    "Recommandation", "Agence", "Courtier",
    "Campagne digitale", "Partenaire bancaire", "Prospection commerciale"
]

SEGMENTS = ["Particulier", "Professionnel", "PME", "Grande Entreprise"]

PRENOMS_M = [
    "Mamadou", "Ibrahima", "Alpha", "Oumar", "Mohamed", "Thierno", "Abdoulaye",
    "Sekou", "Amadou", "Lansana", "Fodé", "Bangaly", "Boubacar", "Daouda",
    "Elhadj", "Fatoumata", "Mariama", "Aissatou", "Kadiatou", "Aminata"
]
PRENOMS_F = [
    "Fatoumata", "Mariama", "Aissatou", "Kadiatou", "Aminata",
    "Hawa", "Oumou", "Binta", "Nene", "Rabi"
]
NOMS = [
    "Diallo", "Bah", "Barry", "Camara", "Sylla", "Konaté", "Traoré",
    "Condé", "Doumbouya", "Kouyaté", "Soumah", "Guilavogui", "Millimono",
    "Bangoura", "Tolno", "Cissé", "Keita", "Sow", "Baldé", "Fofana"
]

MOIS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
]

JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def nom_aleatoire(genre: str) -> str:
    prenom = random.choice(PRENOMS_F if genre == "Féminin" else PRENOMS_M)
    nom    = random.choice(NOMS)
    return f"{prenom} {nom}"

def arrondi_gnf(val: float) -> int:
    """Arrondi au millier le plus proche."""
    return int(round(val / 1000) * 1000)

# =============================================================================
# 1. TABLE PRODUITS
# =============================================================================
produits_data = [
    # (ID, Nom, Catégorie, Type Couverture, Niveau Risque, Taux Commission %)
    ("PRD-001", "Assurance Auto Essentielle",          "Auto",                     "Tous risques partiels",  "Élevé",   8),
    ("PRD-002", "Assurance Auto Premium",               "Auto",                     "Tous risques complets",  "Élevé",   10),
    ("PRD-003", "Assurance Santé Famille",              "Santé",                    "Hospitalisation + soins","Élevé",   9),
    ("PRD-004", "Assurance Habitation Confort",         "Habitation",               "Multirisque habitation", "Moyen",   7),
    ("PRD-005", "Assurance Voyage Afrique",             "Voyage",                   "Assistance voyage",      "Faible",  6),
    ("PRD-006", "Assurance Vie Épargne",                "Vie",                      "Capital + épargne",      "Faible",  11),
    ("PRD-007", "Assurance Entreprise PME",             "Entreprise",               "Risques professionnels", "Moyen",   12),
    ("PRD-008", "Assurance Multirisque Professionnelle","Multirisque Professionnelle","Risques multiples pro", "Moyen",   13),
]

# Plages de primes par produit (min, max) en GNF
PRIME_RANGES = {
    "PRD-001": (1_500_000,  5_000_000),
    "PRD-002": (4_000_000, 12_000_000),
    "PRD-003": (3_000_000, 15_000_000),
    "PRD-004": (2_000_000,  9_000_000),
    "PRD-005": (  300_000,  2_500_000),
    "PRD-006": (5_000_000, 25_000_000),
    "PRD-007": (10_000_000,60_000_000),
    "PRD-008": (15_000_000,90_000_000),
}

# Pondération sinistres : produits Auto et Santé ont plus de sinistres
SINISTRE_PROB = {
    "PRD-001": 0.42,
    "PRD-002": 0.38,
    "PRD-003": 0.40,
    "PRD-004": 0.22,
    "PRD-005": 0.18,
    "PRD-006": 0.10,
    "PRD-007": 0.14,
    "PRD-008": 0.16,
}

df_produits = pd.DataFrame(produits_data, columns=[
    "ID Produit", "Nom Produit", "Catégorie Produit",
    "Type Couverture", "Niveau Risque", "Taux Commission Standard"
])

# =============================================================================
# 2. TABLE AGENCES
# =============================================================================
agences_data = [
    ("AGC-001", "Agence Conakry Kaloum",   "Conakry",    "Conakry",          "Guinée", "Siège"),
    ("AGC-002", "Agence Conakry Ratoma",    "Conakry",    "Conakry",          "Guinée", "Agence principale"),
    ("AGC-003", "Agence Conakry Matoto",    "Conakry",    "Conakry",          "Guinée", "Agence principale"),
    ("AGC-004", "Agence Kindia Centre",     "Kindia",     "Basse Guinée",     "Guinée", "Agence régionale"),
    ("AGC-005", "Agence Labé Centre",       "Labé",       "Moyenne Guinée",   "Guinée", "Agence régionale"),
    ("AGC-006", "Agence Kankan Centre",     "Kankan",     "Haute Guinée",     "Guinée", "Agence régionale"),
    ("AGC-007", "Agence Nzérékoré Centre",  "Nzérékoré",  "Guinée Forestière","Guinée", "Agence régionale"),
    ("AGC-008", "Agence Boké Centre",       "Boké",       "Basse Guinée",     "Guinée", "Agence régionale"),
    ("AGC-009", "Agence Mamou Centre",      "Mamou",      "Moyenne Guinée",   "Guinée", "Point de service"),
    ("AGC-010", "Agence Faranah Centre",    "Faranah",    "Haute Guinée",     "Guinée", "Point de service"),
    ("AGC-011", "Agence Siguiri",           "Siguiri",    "Haute Guinée",     "Guinée", "Point de service"),
    ("AGC-012", "Agence Guéckédou",         "Guéckédou",  "Guinée Forestière","Guinée", "Point de service"),
]

df_agences = pd.DataFrame(agences_data, columns=[
    "ID Agence", "Nom Agence", "Ville Agence",
    "Région Agence", "Pays", "Type Agence"
])

IDS_AGENCES    = df_agences["ID Agence"].tolist()
IDS_AGENCES_CKY = ["AGC-001", "AGC-002", "AGC-003"]

# Poids volume agences (Conakry domine)
AGENCE_POIDS = {
    "AGC-001": 0.18, "AGC-002": 0.15, "AGC-003": 0.13,
    "AGC-004": 0.08, "AGC-005": 0.08, "AGC-006": 0.07,
    "AGC-007": 0.07, "AGC-008": 0.06, "AGC-009": 0.05,
    "AGC-010": 0.05, "AGC-011": 0.04, "AGC-012": 0.04,
}

# =============================================================================
# 3. TABLE AGENTS
# =============================================================================
CANAUX_VENTE  = ["Agence", "Courtier", "En ligne", "Télévente", "Partenaire bancaire"]
NIVEAUX_EXP   = ["Junior", "Confirmé", "Senior", "Expert"]
EXP_POIDS     = [0.35, 0.35, 0.20, 0.10]

# Nombre d'agents par agence (≈ 60 au total)
NB_AGENTS_PAR_AGENCE = {
    "AGC-001": 9, "AGC-002": 8, "AGC-003": 7,
    "AGC-004": 5, "AGC-005": 5, "AGC-006": 5,
    "AGC-007": 5, "AGC-008": 4, "AGC-009": 4,
    "AGC-010": 3, "AGC-011": 3, "AGC-012": 2,
}

agents_rows = []
agent_counter = 1
for id_agence, nb in NB_AGENTS_PAR_AGENCE.items():
    for _ in range(nb):
        id_agent   = f"AGT-{agent_counter:03d}"
        genre      = random.choice(["Masculin", "Féminin"])
        nom        = nom_aleatoire(genre)
        canal      = random.choice(CANAUX_VENTE)
        date_recru = rand_date(date(2018, 1, 1), date(2023, 6, 30))
        niveau     = random.choices(NIVEAUX_EXP, weights=EXP_POIDS)[0]
        agents_rows.append([id_agent, nom, id_agence, canal, date_recru.strftime("%Y-%m-%d"), niveau])
        agent_counter += 1

df_agents = pd.DataFrame(agents_rows, columns=[
    "ID Agent", "Nom Agent", "ID Agence",
    "Canal Vente", "Date Recrutement", "Niveau Expérience"
])

IDS_AGENTS = df_agents["ID Agent"].tolist()

# =============================================================================
# 4. TABLE CLIENTS
# =============================================================================
STATUTS_CLIENT = ["Actif", "Inactif", "Résilié"]

clients_rows = []
# Distribution segments : Particuliers >> reste
SEGMENT_POIDS = [0.55, 0.20, 0.15, 0.10]

for i in range(1, 1001):
    id_client   = f"CLT-{i:04d}"
    genre       = random.choice(["Masculin", "Féminin"])
    nom         = nom_aleatoire(genre)
    age         = random.randint(22, 68)
    segment     = random.choices(SEGMENTS, weights=SEGMENT_POIDS)[0]

    # Segments Entreprise/PME → plutôt Conakry
    if segment in ("PME", "Grande Entreprise"):
        ville = random.choices(
            VILLES,
            weights=[0.40, 0.10, 0.08, 0.08, 0.07, 0.07, 0.05, 0.05, 0.04, 0.02, 0.02, 0.02]
        )[0]
    else:
        ville = random.choices(VILLES, weights=[
            0.25, 0.10, 0.09, 0.09, 0.08, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04
        ])[0]

    region      = VILLE_REGION[ville]
    date_ins    = rand_date(date(2020, 1, 1), date(2025, 6, 30))
    canal_acq   = random.choice(CANAUX_ACQUISITION)
    statut      = random.choices(["Actif", "Inactif", "Résilié"], weights=[0.75, 0.15, 0.10])[0]

    clients_rows.append([
        id_client, nom, genre, age, segment,
        ville, region, "Guinée",
        date_ins.strftime("%Y-%m-%d"), canal_acq, statut
    ])

df_clients = pd.DataFrame(clients_rows, columns=[
    "ID Client", "Nom Client", "Genre", "Âge", "Segment Client",
    "Ville", "Région", "Pays", "Date Inscription", "Canal Acquisition", "Statut Client"
])

IDS_CLIENTS = df_clients["ID Client"].tolist()

# =============================================================================
# 5. TABLE CONTRATS
# =============================================================================
IDS_PRODUITS = [p[0] for p in produits_data]
PROD_POIDS   = [0.18, 0.14, 0.16, 0.12, 0.10, 0.10, 0.10, 0.10]  # Auto + Santé dominants

STATUTS_CONTRAT   = ["Actif", "Expiré", "Résilié"]
FREQUENCES_PAIEM  = ["Mensuelle", "Trimestrielle", "Semestrielle", "Annuelle"]
MODES_PAIEM       = ["Espèces", "Mobile Money", "Virement bancaire", "Carte bancaire", "Chèque"]

# Taux de renouvellement selon segment et produit
RENOUVELLEMENT_SEG = {
    "Particulier": 0.55, "Professionnel": 0.68, "PME": 0.72, "Grande Entreprise": 0.78
}
RENOUVELLEMENT_PROD = {
    "PRD-001": 0.60, "PRD-002": 0.65, "PRD-003": 0.58,
    "PRD-004": 0.62, "PRD-005": 0.45, "PRD-006": 0.75,
    "PRD-007": 0.78, "PRD-008": 0.76,
}

contrats_rows = []
for i in range(1, 5001):
    id_contrat  = f"CTR-{i:05d}"
    id_client   = random.choice(IDS_CLIENTS)
    id_produit  = random.choices(IDS_PRODUITS, weights=PROD_POIDS)[0]

    # Choix agence pondéré
    id_agence   = random.choices(IDS_AGENCES, weights=list(AGENCE_POIDS.values()))[0]
    # Agent appartenant à cette agence
    agents_agence = df_agents[df_agents["ID Agence"] == id_agence]["ID Agent"].tolist()
    id_agent    = random.choice(agents_agence)

    # Dates
    date_debut  = rand_date(START_DATE, date(2025, 6, 30))
    duree_mois  = random.choices([12, 24, 36], weights=[0.60, 0.30, 0.10])[0]
    date_fin    = date_debut + timedelta(days=duree_mois * 30)

    # Statut
    if date_fin < END_DATE:
        statut = random.choices(["Expiré", "Résilié"], weights=[0.80, 0.20])[0]
    else:
        statut = "Actif"

    # Prime
    pmin, pmax  = PRIME_RANGES[id_produit]
    # Segments PME/GE → primes plus élevées
    segment_cl  = df_clients.loc[df_clients["ID Client"] == id_client, "Segment Client"].values[0]
    if segment_cl == "Grande Entreprise":
        pmin = int(pmin * 1.8); pmax = int(pmax * 1.5)
    elif segment_cl == "PME":
        pmin = int(pmin * 1.3); pmax = int(pmax * 1.2)
    montant_prime = arrondi_gnf(random.uniform(pmin, pmax))

    # Commission
    taux_comm   = df_produits.loc[df_produits["ID Produit"] == id_produit, "Taux Commission Standard"].values[0]
    montant_comm = arrondi_gnf(montant_prime * taux_comm / 100)

    # Renouvellement
    tx_renouv   = RENOUVELLEMENT_SEG.get(segment_cl, 0.60) * RENOUVELLEMENT_PROD.get(id_produit, 0.65)
    # Contrats résiliés → rarement renouvelés
    if statut == "Résilié":
        tx_renouv *= 0.15
    renouvelé   = "Oui" if (statut != "Résilié" and random.random() < tx_renouv) else "Non"

    freq_paiem  = random.choices(
        FREQUENCES_PAIEM, weights=[0.30, 0.25, 0.20, 0.25]
    )[0]
    mode_paiem  = random.choices(
        MODES_PAIEM, weights=[0.20, 0.35, 0.20, 0.15, 0.10]
    )[0]

    contrats_rows.append([
        id_contrat, id_client, id_produit, id_agent, id_agence,
        date_debut.strftime("%Y-%m-%d"), date_fin.strftime("%Y-%m-%d"),
        statut, montant_prime, montant_comm,
        freq_paiem, renouvelé, mode_paiem, duree_mois
    ])

df_contrats = pd.DataFrame(contrats_rows, columns=[
    "ID Contrat", "ID Client", "ID Produit", "ID Agent", "ID Agence",
    "Date Début", "Date Fin", "Statut Contrat",
    "Montant Prime", "Montant Commission",
    "Fréquence Paiement", "Renouvelé", "Mode Paiement", "Durée Contrat Mois"
])

IDS_CONTRATS = df_contrats["ID Contrat"].tolist()

# =============================================================================
# 6. TABLE SINISTRES
# =============================================================================
TYPES_SINISTRE = [
    "Accident", "Maladie", "Vol", "Incendie", "Dégât des eaux",
    "Annulation voyage", "Responsabilité civile", "Dommage matériel", "Hospitalisation"
]

# Types de sinistres par produit
TYPE_SINISTRE_PROD = {
    "PRD-001": ["Accident", "Vol", "Dommage matériel", "Responsabilité civile"],
    "PRD-002": ["Accident", "Vol", "Dommage matériel", "Responsabilité civile"],
    "PRD-003": ["Maladie", "Hospitalisation", "Accident"],
    "PRD-004": ["Incendie", "Dégât des eaux", "Vol"],
    "PRD-005": ["Annulation voyage", "Accident", "Maladie"],
    "PRD-006": ["Accident", "Maladie"],
    "PRD-007": ["Incendie", "Vol", "Dommage matériel", "Responsabilité civile"],
    "PRD-008": ["Incendie", "Vol", "Dommage matériel", "Responsabilité civile", "Dégât des eaux"],
}

STATUTS_SINISTRE = ["Ouvert", "En cours", "Réglé", "Rejeté"]
GRAVITES         = ["Faible", "Moyenne", "Élevée", "Critique"]

sinistres_rows = []
sinistre_counter = 1

for _, contrat in df_contrats.iterrows():
    id_produit  = contrat["ID Produit"]
    prob        = SINISTRE_PROB[id_produit]

    # Région impacte aussi la probabilité
    id_agence   = contrat["ID Agence"]
    region_agc  = df_agences.loc[df_agences["ID Agence"] == id_agence, "Région Agence"].values[0]
    if region_agc in ("Guinée Forestière", "Haute Guinée"):
        prob *= 1.20  # ratio sinistres/primes plus élevé

    # Nombre de sinistres pour ce contrat
    nb_sin = 0
    if random.random() < prob:
        nb_sin = random.choices([1, 2, 3], weights=[0.70, 0.22, 0.08])[0]

    date_debut_ct = datetime.strptime(contrat["Date Début"], "%Y-%m-%d").date()
    date_fin_ct   = datetime.strptime(contrat["Date Fin"],   "%Y-%m-%d").date()
    date_fin_ct   = min(date_fin_ct, END_DATE)

    for _ in range(nb_sin):
        id_sinistre = f"SIN-{sinistre_counter:05d}"

        date_sin    = rand_date(date_debut_ct, date_fin_ct)
        type_sin    = random.choice(TYPE_SINISTRE_PROD.get(id_produit, TYPES_SINISTRE))
        gravite     = random.choices(GRAVITES, weights=[0.35, 0.35, 0.20, 0.10])[0]

        # Montant réclamé : fraction de la prime (réaliste)
        prime       = contrat["Montant Prime"]
        mult        = {"Faible": 0.15, "Moyenne": 0.40, "Élevée": 0.80, "Critique": 1.40}[gravite]
        montant_rec = arrondi_gnf(prime * mult * random.uniform(0.6, 1.2))

        # Statut sinistre
        statut_sin  = random.choices(
            STATUTS_SINISTRE, weights=[0.12, 0.18, 0.55, 0.15]
        )[0]

        # Montant réglé & date règlement
        if statut_sin == "Réglé":
            delai_reglem = random.randint(5, 90)
            date_reglem  = date_sin + timedelta(days=delai_reglem)
            if date_reglem > END_DATE:
                date_reglem = END_DATE
            # Parfois on règle moins que réclamé
            taux_reglem  = random.uniform(0.70, 1.00)
            montant_regle = arrondi_gnf(montant_rec * taux_reglem)
            date_reglem_str = date_reglem.strftime("%Y-%m-%d")
        elif statut_sin == "Rejeté":
            delai_reglem    = random.randint(10, 60)
            montant_regle   = 0  # rejeté → pas de règlement ou symbolique
            date_reglem_str = None
            delai_reglem    = None
        elif statut_sin in ("Ouvert", "En cours"):
            montant_regle   = 0
            date_reglem_str = None
            delai_reglem    = None
        else:
            montant_regle   = 0
            date_reglem_str = None
            delai_reglem    = None

        sinistres_rows.append([
            id_sinistre, contrat["ID Contrat"],
            date_sin.strftime("%Y-%m-%d"), type_sin,
            montant_rec, montant_regle,
            statut_sin, date_reglem_str, delai_reglem, gravite
        ])
        sinistre_counter += 1

df_sinistres = pd.DataFrame(sinistres_rows, columns=[
    "ID Sinistre", "ID Contrat", "Date Sinistre", "Type Sinistre",
    "Montant Réclamé", "Montant Réglé",
    "Statut Sinistre", "Date Règlement", "Délai Règlement Jours", "Gravité Sinistre"
])

# =============================================================================
# 7. TABLE OBJECTIFS
# =============================================================================
objectifs_rows = []
obj_counter    = 1

for annee in [2023, 2024, 2025]:
    for mois in range(1, 13):
        for id_agence in IDS_AGENCES:
            for id_produit in IDS_PRODUITS:
                # Volume de base selon agence
                is_ckry = id_agence in IDS_AGENCES_CKY
                base_prime = random.randint(
                    800_000_000 if is_ckry else 200_000_000,
                    1_800_000_000 if is_ckry else 600_000_000
                )
                # Ajustement par produit
                if id_produit in ("PRD-007", "PRD-008"):
                    base_prime = int(base_prime * 2.5)
                elif id_produit in ("PRD-005",):
                    base_prime = int(base_prime * 0.5)

                # Objectif contrats nouveaux
                obj_contrats = random.randint(
                    15 if is_ckry else 4,
                    50 if is_ckry else 18
                )

                # Taux renouvellement objectif
                obj_renouv  = round(random.uniform(0.60, 0.80), 2)

                # Objectif ratio sinistres/primes
                obj_ratio   = round(random.uniform(0.40, 0.65), 2)

                # Croissance interannuelle légère
                facteur_an  = 1.0 if annee == 2023 else (1.10 if annee == 2024 else 1.18)
                obj_primes  = arrondi_gnf(base_prime * facteur_an)

                objectifs_rows.append([
                    f"OBJ-{obj_counter:05d}",
                    annee, mois, id_agence, id_produit,
                    obj_primes, obj_contrats, obj_renouv, obj_ratio
                ])
                obj_counter += 1

df_objectifs = pd.DataFrame(objectifs_rows, columns=[
    "ID Objectif", "Année", "Mois", "ID Agence", "ID Produit",
    "Objectif Primes", "Objectif Nouveaux Contrats",
    "Objectif Taux Renouvellement", "Objectif Ratio Sinistres Primes"
])

# =============================================================================
# 8. TABLE CALENDRIER
# =============================================================================
calendrier_rows = []
cur = START_DATE
while cur <= END_DATE:
    trimestre   = f"T{((cur.month - 1) // 3) + 1}"
    nom_mois    = MOIS_FR[cur.month - 1]
    annee_mois  = cur.strftime("%Y-%m")
    debut_mois  = cur.replace(day=1)
    # Fin de mois
    if cur.month == 12:
        fin_mois = date(cur.year + 1, 1, 1) - timedelta(days=1)
    else:
        fin_mois = date(cur.year, cur.month + 1, 1) - timedelta(days=1)
    nom_jour    = JOURS_FR[cur.weekday()]
    num_semaine = cur.isocalendar()[1]

    calendrier_rows.append([
        cur.strftime("%Y-%m-%d"),
        cur.year, trimestre, cur.month, nom_mois,
        annee_mois,
        debut_mois.strftime("%Y-%m-%d"),
        fin_mois.strftime("%Y-%m-%d"),
        nom_jour, num_semaine
    ])
    cur += timedelta(days=1)

df_calendrier = pd.DataFrame(calendrier_rows, columns=[
    "Date", "Année", "Trimestre", "Mois Numéro", "Mois",
    "Année-Mois", "Début Mois", "Fin Mois", "Nom Jour", "Numéro Semaine"
])

# =============================================================================
# 9. TABLE DICTIONNAIRE_DONNEES
# =============================================================================
dict_data = [
    # Clients
    ("Clients", "ID Client",        "Identifiant unique du client",              "Texte",  "CLT-0001"),
    ("Clients", "Nom Client",       "Nom complet du client",                     "Texte",  "Mamadou Diallo"),
    ("Clients", "Genre",            "Genre du client",                           "Texte",  "Masculin"),
    ("Clients", "Âge",              "Âge du client en années",                   "Entier", "35"),
    ("Clients", "Segment Client",   "Segment commercial du client",              "Texte",  "PME"),
    ("Clients", "Ville",            "Ville de résidence ou d'activité",          "Texte",  "Conakry"),
    ("Clients", "Région",           "Région administrative de Guinée",           "Texte",  "Conakry"),
    ("Clients", "Pays",             "Pays du client",                            "Texte",  "Guinée"),
    ("Clients", "Date Inscription", "Date d'entrée en relation avec AssurGuinée","Date",   "2023-03-15"),
    ("Clients", "Canal Acquisition","Canal par lequel le client a été acquis",   "Texte",  "Agence"),
    ("Clients", "Statut Client",    "Statut actuel du client",                   "Texte",  "Actif"),
    # Produits
    ("Produits","ID Produit",       "Identifiant unique du produit",             "Texte",  "PRD-001"),
    ("Produits","Nom Produit",      "Nom commercial du produit",                 "Texte",  "Assurance Auto Essentielle"),
    ("Produits","Catégorie Produit","Catégorie métier du produit",               "Texte",  "Auto"),
    ("Produits","Type Couverture",  "Description de la couverture proposée",     "Texte",  "Tous risques partiels"),
    ("Produits","Niveau Risque",    "Niveau de risque estimé du produit",        "Texte",  "Élevé"),
    ("Produits","Taux Commission Standard","Taux de commission standard en %",   "Décimal","8"),
    # Agences
    ("Agences", "ID Agence",        "Identifiant unique de l'agence",            "Texte",  "AGC-001"),
    ("Agences", "Nom Agence",       "Nom de l'agence",                           "Texte",  "Agence Conakry Kaloum"),
    ("Agences", "Ville Agence",     "Ville de l'agence",                         "Texte",  "Conakry"),
    ("Agences", "Région Agence",    "Région de l'agence",                        "Texte",  "Conakry"),
    ("Agences", "Pays",             "Pays de l'agence",                          "Texte",  "Guinée"),
    ("Agences", "Type Agence",      "Catégorie de l'agence",                     "Texte",  "Siège"),
    # Agents
    ("Agents",  "ID Agent",         "Identifiant unique de l'agent",             "Texte",  "AGT-001"),
    ("Agents",  "Nom Agent",        "Nom complet de l'agent",                    "Texte",  "Ibrahima Bah"),
    ("Agents",  "ID Agence",        "Agence de rattachement de l'agent",         "Texte",  "AGC-001"),
    ("Agents",  "Canal Vente",      "Canal de vente principal de l'agent",       "Texte",  "Agence"),
    ("Agents",  "Date Recrutement", "Date d'entrée de l'agent",                  "Date",   "2021-06-01"),
    ("Agents",  "Niveau Expérience","Niveau d'expérience de l'agent",            "Texte",  "Confirmé"),
    # Contrats
    ("Contrats","ID Contrat",       "Identifiant unique du contrat",             "Texte",  "CTR-00001"),
    ("Contrats","ID Client",        "Client souscripteur du contrat",            "Texte",  "CLT-0001"),
    ("Contrats","ID Produit",       "Produit souscrit",                          "Texte",  "PRD-001"),
    ("Contrats","ID Agent",         "Agent ayant souscrit le contrat",           "Texte",  "AGT-001"),
    ("Contrats","ID Agence",        "Agence émettrice du contrat",               "Texte",  "AGC-001"),
    ("Contrats","Date Début",       "Date de début de couverture",               "Date",   "2023-01-15"),
    ("Contrats","Date Fin",         "Date de fin de couverture",                 "Date",   "2024-01-15"),
    ("Contrats","Statut Contrat",   "Statut actuel du contrat",                  "Texte",  "Actif"),
    ("Contrats","Montant Prime",    "Montant annuel de la prime en GNF",         "Entier", "3500000"),
    ("Contrats","Montant Commission","Commission versée à l'agent en GNF",       "Entier", "280000"),
    ("Contrats","Fréquence Paiement","Fréquence de paiement de la prime",        "Texte",  "Mensuelle"),
    ("Contrats","Renouvelé",        "Le contrat a-t-il été renouvelé ?",         "Texte",  "Oui"),
    ("Contrats","Mode Paiement",    "Mode de paiement utilisé",                  "Texte",  "Mobile Money"),
    ("Contrats","Durée Contrat Mois","Durée du contrat en mois",                 "Entier", "12"),
    # Sinistres
    ("Sinistres","ID Sinistre",     "Identifiant unique du sinistre",            "Texte",  "SIN-00001"),
    ("Sinistres","ID Contrat",      "Contrat associé au sinistre",               "Texte",  "CTR-00001"),
    ("Sinistres","Date Sinistre",   "Date de survenance du sinistre",            "Date",   "2023-06-10"),
    ("Sinistres","Type Sinistre",   "Nature du sinistre déclaré",                "Texte",  "Accident"),
    ("Sinistres","Montant Réclamé", "Montant réclamé par l'assuré en GNF",       "Entier", "1200000"),
    ("Sinistres","Montant Réglé",   "Montant effectivement réglé en GNF",        "Entier", "950000"),
    ("Sinistres","Statut Sinistre", "Statut de traitement du sinistre",          "Texte",  "Réglé"),
    ("Sinistres","Date Règlement",  "Date de règlement du sinistre",             "Date",   "2023-07-05"),
    ("Sinistres","Délai Règlement Jours","Délai en jours entre sinistre et règlement","Entier","25"),
    ("Sinistres","Gravité Sinistre","Niveau de gravité du sinistre",             "Texte",  "Moyenne"),
    # Objectifs
    ("Objectifs","ID Objectif",     "Identifiant unique de l'objectif",          "Texte",  "OBJ-00001"),
    ("Objectifs","Année",           "Année de l'objectif",                       "Entier", "2024"),
    ("Objectifs","Mois",            "Numéro du mois de l'objectif",              "Entier", "3"),
    ("Objectifs","ID Agence",       "Agence concernée",                          "Texte",  "AGC-001"),
    ("Objectifs","ID Produit",      "Produit concerné",                          "Texte",  "PRD-001"),
    ("Objectifs","Objectif Primes", "Objectif mensuel de primes en GNF",         "Entier", "500000000"),
    ("Objectifs","Objectif Nouveaux Contrats","Nombre de nouveaux contrats visés","Entier","30"),
    ("Objectifs","Objectif Taux Renouvellement","Taux de renouvellement cible",  "Décimal","0.70"),
    ("Objectifs","Objectif Ratio Sinistres Primes","Ratio sinistres/primes cible","Décimal","0.55"),
    # Calendrier
    ("Calendrier","Date",           "Date complète",                             "Date",   "2023-01-01"),
    ("Calendrier","Année",          "Année civile",                              "Entier", "2023"),
    ("Calendrier","Trimestre",      "Trimestre (T1 à T4)",                       "Texte",  "T1"),
    ("Calendrier","Mois Numéro",    "Numéro du mois (1–12)",                     "Entier", "1"),
    ("Calendrier","Mois",           "Nom du mois en français",                   "Texte",  "Janvier"),
    ("Calendrier","Année-Mois",     "Clé combinée année-mois",                   "Texte",  "2023-01"),
    ("Calendrier","Début Mois",     "Premier jour du mois",                      "Date",   "2023-01-01"),
    ("Calendrier","Fin Mois",       "Dernier jour du mois",                      "Date",   "2023-01-31"),
    ("Calendrier","Nom Jour",       "Nom du jour de la semaine en français",     "Texte",  "Dimanche"),
    ("Calendrier","Numéro Semaine", "Numéro de semaine ISO",                     "Entier", "1"),
]

df_dico = pd.DataFrame(dict_data, columns=[
    "Table", "Colonne", "Description", "Type Donnée", "Exemple"
])

# =============================================================================
# EXPORT CSV
# =============================================================================
exports = {
    "Clients.csv":               df_clients,
    "Produits.csv":              df_produits,
    "Agences.csv":               df_agences,
    "Agents.csv":                df_agents,
    "Contrats.csv":              df_contrats,
    "Sinistres.csv":             df_sinistres,
    "Objectifs.csv":             df_objectifs,
    "Calendrier.csv":            df_calendrier,
    "Dictionnaire_Donnees.csv":  df_dico,
}

for filename, df in exports.items():
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  ✔ {filename:35s} — {len(df):>6} lignes")

# =============================================================================
# CONTRÔLE QUALITÉ
# =============================================================================
print("\n" + "="*60)
print("  RAPPORT DE CONTRÔLE QUALITÉ")
print("="*60)

# Clés étrangères
orphelins_ct_cli = df_contrats[~df_contrats["ID Client"].isin(IDS_CLIENTS)]
orphelins_ct_prd = df_contrats[~df_contrats["ID Produit"].isin(IDS_PRODUITS)]
orphelins_ct_agt = df_contrats[~df_contrats["ID Agent"].isin(IDS_AGENTS)]
orphelins_ct_agc = df_contrats[~df_contrats["ID Agence"].isin(IDS_AGENCES)]
orphelins_sin    = df_sinistres[~df_sinistres["ID Contrat"].isin(IDS_CONTRATS)]

print(f"\n  Clés étrangères :")
print(f"    Contrats → Clients   orphelins : {len(orphelins_ct_cli)}")
print(f"    Contrats → Produits  orphelins : {len(orphelins_ct_prd)}")
print(f"    Contrats → Agents    orphelins : {len(orphelins_ct_agt)}")
print(f"    Contrats → Agences   orphelins : {len(orphelins_ct_agc)}")
print(f"    Sinistres → Contrats orphelins : {len(orphelins_sin)}")

# Montants négatifs
neg_primes  = (df_contrats["Montant Prime"] < 0).sum()
neg_sin_rec = (df_sinistres["Montant Réclamé"] < 0).sum()
neg_sin_reg = (df_sinistres["Montant Réglé"] < 0).sum()
print(f"\n  Montants négatifs :")
print(f"    Primes négatives         : {neg_primes}")
print(f"    Montants réclamés négatifs : {neg_sin_rec}")
print(f"    Montants réglés négatifs   : {neg_sin_reg}")

# Dates manquantes
dates_manq_c  = df_contrats[["Date Début","Date Fin"]].isnull().sum().sum()
dates_manq_s  = df_sinistres["Date Sinistre"].isnull().sum()
print(f"\n  Dates manquantes :")
print(f"    Contrats (Début/Fin)  : {dates_manq_c}")
print(f"    Sinistres (Survenance): {dates_manq_s}")

# Résumés financiers
total_primes     = df_contrats["Montant Prime"].sum()
total_sin_regle  = df_sinistres["Montant Réglé"].sum()
total_commissions= df_contrats["Montant Commission"].sum()
marge_estimee    = total_primes - total_sin_regle - total_commissions
ratio_glob       = total_sin_regle / total_primes if total_primes > 0 else 0
taux_marge       = marge_estimee / total_primes if total_primes > 0 else 0

print(f"\n  RÉSUMÉ FINANCIER (GNF) :")
print(f"    Total Primes           : {total_primes:>25,.0f} GNF")
print(f"    Total Sinistres Réglés : {total_sin_regle:>25,.0f} GNF")
print(f"    Total Commissions      : {total_commissions:>25,.0f} GNF")
print(f"    Marge Estimée          : {marge_estimee:>25,.0f} GNF")
print(f"    Ratio Sinistres/Primes : {ratio_glob:>25.2%}")
print(f"    Taux Marge Estimée     : {taux_marge:>25.2%}")
print(f"\n  Dossier créé : ./{OUTPUT_DIR}/")
print("="*60)
