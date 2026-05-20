# AssurGuinée 360 — Documentation Complète du Projet Power BI
# Pilotage Assurance 360 : Performance, Sinistres, Rentabilité et Renouvellement en Guinée
# Alpha Data Solutions (ADS) — Projet Portfolio
---

================================================================================
SECTION 1 — RELATIONS À CRÉER DANS POWER BI
================================================================================

## Schéma en étoile recommandé

### Relations actives (à activer dans Power BI Desktop)

| Table Source   | Colonne Source  | Table Cible | Colonne Cible | Cardinalité | Direction filtre |
|----------------|-----------------|-------------|---------------|-------------|-----------------|
| Contrats       | ID Client       | Clients     | ID Client     | N:1         | Unique (→)      |
| Contrats       | ID Produit      | Produits    | ID Produit    | N:1         | Unique (→)      |
| Contrats       | ID Agence       | Agences     | ID Agence     | N:1         | Unique (→)      |
| Contrats       | ID Agent        | Agents      | ID Agent      | N:1         | Unique (→)      |
| Sinistres      | ID Contrat      | Contrats    | ID Contrat    | N:1         | Unique (→)      |
| Contrats       | Date Début      | Calendrier  | Date          | N:1         | Unique (→)      |
| Objectifs      | ID Agence       | Agences     | ID Agence     | N:1         | Unique (→)      |
| Objectifs      | ID Produit      | Produits    | ID Produit    | N:1         | Unique (→)      |

### Relations inactives (à gérer via USERELATIONSHIP en DAX)

| Table Source | Colonne Source   | Table Cible | Colonne Cible | Raison                              |
|--------------|------------------|-------------|---------------|-------------------------------------|
| Contrats     | Date Fin         | Calendrier  | Date          | Évite conflit avec Date Début       |
| Sinistres    | Date Sinistre    | Calendrier  | Date          | Conflit : Calendrier déjà lié       |
| Sinistres    | Date Règlement   | Calendrier  | Date          | Troisième relation sur même table   |
| Objectifs    | Année + Mois     | Calendrier  | —             | Jointure via colonne calculée       |

### Explication des choix
- La relation active Calendrier → Contrats utilise "Date Début" : c'est la date de souscription,
  la plus utilisée pour suivre la production.
- Pour analyser les sinistres par date de survenance, utilisez USERELATIONSHIP(Sinistres[Date Sinistre], Calendrier[Date]).
- Pour les objectifs, créez une colonne calculée dans Objectifs :
  Date Objectif = DATE([Année], [Mois], 1)
  puis reliez-la à Calendrier[Date] (relation inactive, activée via USERELATIONSHIP).
- Agents → Agences : relation active N:1 (chaque agent appartient à une agence).
  Ne pas activer les filtres bidirectionnels pour éviter les ambiguïtés.


================================================================================
SECTION 2 — MESURES DAX EN FRANÇAIS
================================================================================

-- ============================================================
-- TABLE : _Mesures AssurGuinée 360
-- ============================================================

-- ─── PRIMES & CONTRATS ───────────────────────────────────────

Total Primes =
    SUM( Contrats[Montant Prime] )

Nombre Contrats =
    COUNTROWS( Contrats )

Contrats Actifs =
    CALCULATE(
        COUNTROWS( Contrats ),
        Contrats[Statut Contrat] = "Actif"
    )

Contrats Résiliés =
    CALCULATE(
        COUNTROWS( Contrats ),
        Contrats[Statut Contrat] = "Résilié"
    )

Prime Moyenne par Contrat =
    DIVIDE(
        [Total Primes],
        [Nombre Contrats],
        0
    )

Nombre Nouveaux Contrats =
    CALCULATE(
        COUNTROWS( Contrats ),
        USERELATIONSHIP( Contrats[Date Début], Calendrier[Date] )
    )

-- ─── SINISTRES ───────────────────────────────────────────────

Nombre Sinistres =
    COUNTROWS( Sinistres )

Montant Réclamé Total =
    SUM( Sinistres[Montant Réclamé] )

Total Sinistres Réglés =
    CALCULATE(
        SUM( Sinistres[Montant Réglé] ),
        Sinistres[Statut Sinistre] = "Réglé"
    )

Ratio Sinistres Primes =
    DIVIDE(
        [Total Sinistres Réglés],
        [Total Primes],
        0
    )

Délai Moyen de Règlement =
    CALCULATE(
        AVERAGE( Sinistres[Délai Règlement Jours] ),
        Sinistres[Statut Sinistre] = "Réglé"
    )

Taux Sinistres Réglés =
    DIVIDE(
        CALCULATE( COUNTROWS( Sinistres ), Sinistres[Statut Sinistre] = "Réglé" ),
        COUNTROWS( Sinistres ),
        0
    )

Taux Sinistres Rejetés =
    DIVIDE(
        CALCULATE( COUNTROWS( Sinistres ), Sinistres[Statut Sinistre] = "Rejeté" ),
        COUNTROWS( Sinistres ),
        0
    )

-- ─── COMMISSIONS & RENTABILITÉ ────────────────────────────────

Total Commissions =
    SUM( Contrats[Montant Commission] )

Marge Estimée =
    [Total Primes]
    - [Total Sinistres Réglés]
    - [Total Commissions]

Taux Marge Estimée =
    DIVIDE(
        [Marge Estimée],
        [Total Primes],
        0
    )

-- ─── RENOUVELLEMENT ──────────────────────────────────────────

Contrats Renouvelés =
    CALCULATE(
        COUNTROWS( Contrats ),
        Contrats[Renouvelé] = "Oui"
    )

Taux Renouvellement =
    DIVIDE(
        [Contrats Renouvelés],
        [Nombre Contrats],
        0
    )

-- ─── OBJECTIFS & ÉCARTS ──────────────────────────────────────

Objectif Primes =
    SUM( Objectifs[Objectif Primes] )

Écart Objectif Primes =
    [Total Primes] - [Objectif Primes]

Taux Atteinte Objectif Primes =
    DIVIDE(
        [Total Primes],
        [Objectif Primes],
        0
    )

Objectif Nouveaux Contrats =
    SUM( Objectifs[Objectif Nouveaux Contrats] )

Écart Nouveaux Contrats =
    [Nombre Nouveaux Contrats] - [Objectif Nouveaux Contrats]

-- ─── MESURES COMPLÉMENTAIRES (couleur dynamique) ─────────────

Couleur Ratio Sinistres =
    IF( [Ratio Sinistres Primes] > 0.65, "#C0392B",
        IF( [Ratio Sinistres Primes] > 0.50, "#F2C94C", "#2E7D32" )
    )

Couleur Taux Atteinte =
    IF( [Taux Atteinte Objectif Primes] >= 1, "#2E7D32",
        IF( [Taux Atteinte Objectif Primes] >= 0.85, "#F2C94C", "#C0392B" )
    )


================================================================================
SECTION 3 — PAGES POWER BI PROPOSÉES
================================================================================

────────────────────────────────────────────────────────
PAGE 1 — VUE DIRECTION
────────────────────────────────────────────────────────
Objectif business :
  Offrir au Directeur Général une vision synthétique de la santé du portefeuille.
  Un coup d'œil = une décision.

KPIs principaux :
  • Total Primes (GNF)           • Marge Estimée (GNF & %)
  • Nombre Contrats Actifs       • Ratio Sinistres/Primes
  • Taux Renouvellement          • Taux Atteinte Objectif Primes

Visuels recommandés :
  • 6 cartes KPI avec variation M-1 (flèche + couleur RAG)
  • Courbe de primes mensuelles (2023–2025) avec trait objectif
  • Graphique à barres : Top 5 agences par primes
  • Anneau : Répartition primes par produit
  • Jauge : Taux atteinte objectif global

Filtres utiles :
  Année | Trimestre | Région | Produit

Message clé :
  "AssurGuinée 360 croît, mais le ratio sinistres dépasse 55% sur les produits Auto et Santé."

────────────────────────────────────────────────────────
PAGE 2 — ANALYSE DES PRODUITS
────────────────────────────────────────────────────────
Objectif business :
  Identifier les produits les plus rentables et les plus risqués.

KPIs principaux :
  • Total Primes par produit
  • Ratio Sinistres/Primes par produit
  • Marge Estimée par produit
  • Nombre de contrats par produit

Visuels recommandés :
  • Matrice : Produit × (Primes / Sinistres / Marge / Ratio)
  • Scatter plot : Primes vs Ratio Sinistres/Primes (bulle = volume contrats)
  • Barres empilées : Primes vs Sinistres réglés par catégorie
  • Indicateur de Niveau Risque (table filtrée)

Filtres utiles :
  Année | Agence | Région | Segment Client

Message clé :
  "Vie et Entreprise affichent les meilleures marges.
   Auto et Santé génèrent le plus de volume mais aussi le plus de sinistres."

────────────────────────────────────────────────────────
PAGE 3 — ANALYSE DES SINISTRES
────────────────────────────────────────────────────────
Objectif business :
  Piloter la sinistralité, détecter les zones à risque et optimiser les délais de traitement.

KPIs principaux :
  • Nombre Sinistres             • Montant Réclamé Total
  • Total Sinistres Réglés       • Délai Moyen de Règlement (jours)
  • Taux Sinistres Réglés        • Taux Sinistres Rejetés

Visuels recommandés :
  • Courbe mensuelle : Sinistres ouverts vs réglés
  • Barres : Sinistres par type (Accident, Maladie, Vol…)
  • Carte géographique : Ratio sinistres/primes par région
  • Histogramme : Distribution des délais de règlement
  • Matrice : Gravité × Statut (avec comptage)
  • Anneau : Répartition des statuts sinistres

Filtres utiles :
  Année | Produit | Agence | Gravité | Type Sinistre

Message clé :
  "Guinée Forestière et Haute Guinée affichent un ratio sinistres/primes supérieur à 60%.
   Le délai moyen de règlement dépasse 40 jours sur les sinistres critiques."

────────────────────────────────────────────────────────
PAGE 4 — ANALYSE CLIENTS
────────────────────────────────────────────────────────
Objectif business :
  Comprendre la structure du portefeuille clients pour orienter la stratégie commerciale.

KPIs principaux :
  • Nombre Clients               • Prime Moyenne par Contrat
  • Répartition par Segment      • Taux de Clients Actifs
  • Canaux d'acquisition les plus performants

Visuels recommandés :
  • Anneau : Répartition par segment (Particulier / Pro / PME / GE)
  • Barres horizontales : Prime moyenne par segment
  • Histogramme : Distribution par âge (tranches de 10 ans)
  • Carte géographique : Clients par ville/région
  • Barres : Nombre de contrats par canal d'acquisition
  • Tableau : Top 20 clients par prime totale

Filtres utiles :
  Segment | Ville | Genre | Canal Acquisition | Année

Message clé :
  "Les Particuliers représentent 55% des clients mais génèrent une prime moyenne 3× inférieure
   aux PME. Le canal Partenaire bancaire performe mieux sur les produits Vie."

────────────────────────────────────────────────────────
PAGE 5 — PERFORMANCE AGENCES ET AGENTS
────────────────────────────────────────────────────────
Objectif business :
  Comparer la performance des agences et des agents pour orienter le management commercial.

KPIs principaux :
  • Total Primes par agence       • Nombre Contrats par agent
  • Commission moyenne par agent  • Taux Atteinte Objectif par agence
  • Ratio Sinistres par agence

Visuels recommandés :
  • Barres : Classement agences par primes (avec objectif)
  • Barres horizontales : Top 15 agents par primes générées
  • Carte : Performance agences sur carte Guinée
  • Matrice : Agence × (Primes / Contrats / Sinistres / Marge)
  • Nuage de points : Agent (Primes vs Nombre Contrats)

Filtres utiles :
  Région | Type Agence | Niveau Expérience | Canal Vente | Année

Message clé :
  "Conakry Kaloum (siège) génère 18% du volume total. Certaines agences régionales
   dépassent leurs objectifs grâce à un meilleur mix produit."

────────────────────────────────────────────────────────
PAGE 6 — RENOUVELLEMENT
────────────────────────────────────────────────────────
Objectif business :
  Analyser la fidélisation client et anticiper les risques de non-renouvellement.

KPIs principaux :
  • Taux Renouvellement global     • Contrats Expirant dans 90 jours
  • Taux Renouvellement par segment • Taux Renouvellement par produit

Visuels recommandés :
  • Jauge : Taux de renouvellement global vs objectif (70%)
  • Barres : Taux de renouvellement par segment
  • Barres horizontales : Taux de renouvellement par produit
  • Courbe : Évolution mensuelle du taux de renouvellement
  • Table : Contrats expirant dans les 90 prochains jours (avec client + produit + agence)

Filtres utiles :
  Produit | Segment | Agence | Canal Vente | Année

Message clé :
  "Les PME et Grandes Entreprises renouvellent à 72–78%.
   Les Particuliers souscrits via Campagne digitale renouvellent à seulement 45%."

────────────────────────────────────────────────────────
PAGE 7 — OBJECTIFS VS RÉALISÉ
────────────────────────────────────────────────────────
Objectif business :
  Mesurer l'écart entre les objectifs fixés et les résultats obtenus par agence et produit.

KPIs principaux :
  • Taux Atteinte Objectif Primes  • Écart Objectif Primes
  • Taux Atteinte Nouveaux Contrats • Écart Nouveaux Contrats

Visuels recommandés :
  • Barres groupées : Réalisé vs Objectif par agence
  • Barres avec ligne d'objectif : Primes mensuelles vs objectif
  • Matrice : Agence × Produit × Taux Atteinte (couleur conditionnelle RAG)
  • Anneau : % agences ayant atteint l'objectif ce mois

Filtres utiles :
  Année | Mois | Agence | Produit | Région

Message clé :
  "En 2024, seulement 60% des agences ont atteint leur objectif de primes.
   Les produits Vie et Entreprise dépassent leurs objectifs dans les agences de Conakry."

────────────────────────────────────────────────────────
PAGE 8 — RECOMMANDATIONS
────────────────────────────────────────────────────────
Objectif business :
  Synthétiser les insights et proposer des actions concrètes à la direction.

Structure recommandée :
  • Tableau de bord des alertes RAG (3–5 indicateurs clés)
  • 3 à 5 cartes de recommandation avec :
      - Problème détecté
      - Donnée support
      - Action recommandée
      - Impact estimé

Exemples de recommandations :
  1. Réduire la sinistralité Auto → Réviser les critères de souscription en Guinée Forestière.
  2. Booster le renouvellement Particuliers → Programme de fidélisation via Mobile Money.
  3. Développer le canal Partenaire bancaire → Focus sur produits Vie (marge +35%).
  4. Accélérer les règlements → Objectif : délai < 30 jours pour sinistres Faible/Moyenne.

Visuels recommandés :
  • Boutons de navigation vers les pages de détail
  • Tableau de synthèse exécutive
  • Graphique waterfall : Décomposition de la marge


================================================================================
SECTION 4 — THÈME JSON POWER BI
================================================================================

EXPLICATION DES COULEURS :
  • #0B1F3A  Bleu profond    → Confiance, rigueur, professionnalisme (éléments principaux)
  • #1F4E79  Bleu secondaire → Hiérarchie visuelle, en-têtes, titres de sections
  • #2E7D32  Vert croissance → KPIs positifs, marge, renouvellement, performances satisfaisantes
  • #F2C94C  Jaune/or        → Alerte attention, objectif moyen, inspiré du drapeau guinéen
  • #C0392B  Rouge alerte    → KPIs critiques, sinistres graves, objectifs non atteints
  • #F5F7FA  Gris fond       → Arrière-plans neutres, zones de contenu secondaire
  • #2C3E50  Gris texte      → Corps de texte, labels, annotations
  • #FFFFFF  Blanc           → Textes sur fond sombre, cartes, valeurs KPI

```json
{
  "name": "AssurGuinée 360",
  "dataColors": [
    "#0B1F3A",
    "#2E7D32",
    "#F2C94C",
    "#1F4E79",
    "#C0392B",
    "#5D8AA8",
    "#85C17E",
    "#F7DC6F",
    "#A9CCE3",
    "#E74C3C"
  ],
  "background": "#F5F7FA",
  "foreground": "#2C3E50",
  "tableAccent": "#1F4E79",
  "good": "#2E7D32",
  "neutral": "#F2C94C",
  "bad": "#C0392B",
  "maximum": "#0B1F3A",
  "center": "#F2C94C",
  "minimum": "#C0392B",
  "null": "#BDC3C7",
  "visualStyles": {
    "*": {
      "*": {
        "fontFamily": [{ "value": "Segoe UI" }],
        "fontSize": [{ "value": 11 }],
        "color": [{ "solid": { "color": "#2C3E50" } }]
      }
    },
    "card": {
      "*": {
        "background": [{ "solid": { "color": "#FFFFFF" } }],
        "border": [{ "solid": { "color": "#E0E4EA" } }],
        "calloutValue": [
          {
            "fontSize": [{ "value": 28 }],
            "fontFamily": [{ "value": "Segoe UI Semibold" }],
            "color": [{ "solid": { "color": "#0B1F3A" } }]
          }
        ],
        "label": [
          {
            "fontSize": [{ "value": 11 }],
            "color": [{ "solid": { "color": "#5D6D7E" } }]
          }
        ]
      }
    },
    "columnChart": {
      "*": {
        "dataPoint": [{ "fill": { "solid": { "color": "#0B1F3A" } } }],
        "dataLabels": [
          {
            "show": [{ "value": true }],
            "fontSize": [{ "value": 10 }],
            "color": [{ "solid": { "color": "#2C3E50" } }]
          }
        ],
        "xAxis": [
          {
            "gridlineColor": [{ "solid": { "color": "#E0E4EA" } }],
            "labelColor": [{ "solid": { "color": "#5D6D7E" } }],
            "fontSize": [{ "value": 10 }]
          }
        ],
        "yAxis": [
          {
            "gridlineColor": [{ "solid": { "color": "#E0E4EA" } }],
            "labelColor": [{ "solid": { "color": "#5D6D7E" } }],
            "fontSize": [{ "value": 10 }]
          }
        ]
      }
    },
    "lineChart": {
      "*": {
        "lineStyles": [
          {
            "strokeWidth": [{ "value": 2 }]
          }
        ],
        "markers": [
          {
            "show": [{ "value": true }],
            "size": [{ "value": 5 }]
          }
        ]
      }
    },
    "tableEx": {
      "*": {
        "header": [
          {
            "fontColor": [{ "solid": { "color": "#FFFFFF" } }],
            "backColor": [{ "solid": { "color": "#0B1F3A" } }],
            "fontSize": [{ "value": 11 }],
            "fontFamily": [{ "value": "Segoe UI Semibold" }]
          }
        ],
        "values": [
          {
            "fontColor": [{ "solid": { "color": "#2C3E50" } }],
            "backColor": [{ "solid": { "color": "#FFFFFF" } }],
            "fontSize": [{ "value": 10 }],
            "fontFamily": [{ "value": "Segoe UI" }]
          }
        ],
        "gridHorizontal": [{ "gridlineColor": [{ "solid": { "color": "#E8ECF0" } }] }]
      }
    },
    "pivotTable": {
      "*": {
        "columnHeaders": [
          {
            "fontColor": [{ "solid": { "color": "#FFFFFF" } }],
            "backColor": [{ "solid": { "color": "#1F4E79" } }],
            "fontSize": [{ "value": 10 }]
          }
        ],
        "rowHeaders": [
          {
            "fontColor": [{ "solid": { "color": "#0B1F3A" } }],
            "backColor": [{ "solid": { "color": "#EBF0F7" } }],
            "fontSize": [{ "value": 10 }]
          }
        ],
        "values": [
          {
            "fontSize": [{ "value": 10 }],
            "fontColor": [{ "solid": { "color": "#2C3E50" } }]
          }
        ],
        "totals": [
          {
            "fontColor": [{ "solid": { "color": "#FFFFFF" } }],
            "backColor": [{ "solid": { "color": "#0B1F3A" } }],
            "fontFamily": [{ "value": "Segoe UI Semibold" }]
          }
        ]
      }
    },
    "title": {
      "*": {
        "background": [{ "solid": { "color": "#0B1F3A" } }],
        "fontColor": [{ "solid": { "color": "#FFFFFF" } }],
        "fontSize": [{ "value": 14 }],
        "fontFamily": [{ "value": "Segoe UI Semibold" }]
      }
    },
    "gauge": {
      "*": {
        "data": [{ "fill": { "solid": { "color": "#2E7D32" } } }],
        "target": [{ "fill": { "solid": { "color": "#0B1F3A" } } }]
      }
    },
    "donutChart": {
      "*": {
        "legend": [{ "position": [{ "value": "Right" }] }]
      }
    }
  },
  "textClasses": {
    "callout": {
      "fontSize": 45,
      "fontFace": "DIN",
      "color": "#0B1F3A"
    },
    "title": {
      "fontSize": 16,
      "fontFace": "Segoe UI Semibold",
      "color": "#0B1F3A"
    },
    "header": {
      "fontSize": 12,
      "fontFace": "Segoe UI Semibold",
      "color": "#1F4E79"
    },
    "label": {
      "fontSize": 10,
      "fontFace": "Segoe UI",
      "color": "#5D6D7E"
    }
  }
}
```


================================================================================
SECTION 5 — PROMPT LOGO OREATE
================================================================================

## VERSION LONGUE (prompt complet)

Crée un logo professionnel pour une entreprise d'assurance africaine appelée
"AssurGuinée 360" avec le slogan "Protéger aujourd'hui, piloter demain".

Secteur : assurance, analyse de données, pilotage de performance business.
Marché cible : Guinée et Afrique francophone, décideurs d'entreprise.

Style : moderne, épuré, premium, rassurant, sobre mais distinctif.
Évite : les logos trop chargés, les clichés afro-génériques, les formes trop complexes.

Symbolique à intégrer (choisir 1 à 2 éléments maximum) :
  - Un bouclier stylisé évoquant la protection
  - Un cercle ou arc de cercle 360° évoquant la vision globale et le pilotage
  - Une courbe ascendante ou flèche subtile évoquant la croissance
  - Des points de données ou un réseau discret suggérant l'analyse BI

Palette de couleurs :
  - Bleu profond principal : #0B1F3A (confiance, rigueur)
  - Vert accent : #2E7D32 (croissance, sécurité)
  - Touche jaune/or : #F2C94C (énergie, drapeau guinéen — usage très discret)
  - Fond clair : #F5F7FA

Typographie :
  - Nom "AssurGuinée 360" : police sans-serif, géométrique, forte, lisible
  - Slogan : police fine, légère, en dessous du nom
  - Aucune police manuscrite ou serif classique

Déclinaisons requises :
  1. Version horizontale : icône à gauche + nom + slogan à droite
  2. Version icône seule : symbole seul, utilisable comme favicon ou avatar
  3. Version fond clair (standard)
  4. Version fond sombre (#0B1F3A ou noir) pour dashboards Power BI

Format de rendu : vectoriel, haute résolution, fond transparent.
Lisible à toutes tailles : dashboard, PowerPoint, carte de visite, site web.

---

## VERSION COURTE (si limitation de caractères)

Logo "AssurGuinée 360" — assurance & BI, Guinée.
Slogan : "Protéger aujourd'hui, piloter demain".
Style : moderne, épuré, premium. Symboles : bouclier + cercle 360.
Couleurs : bleu #0B1F3A, vert #2E7D32, or discret #F2C94C.
Typo géométrique sans-serif. Version horizontale + icône seule.
Fond clair ET fond sombre. Format vectoriel, fond transparent.


================================================================================
SECTION 6 — STRUCTURE GITHUB
================================================================================

pilotage-assurance-360-guinee/
│
├── README.md                          ← Description complète du projet (voir Section 7)
│
├── donnees/
│   ├── Clients.csv
│   ├── Produits.csv
│   ├── Agences.csv
│   ├── Agents.csv
│   ├── Contrats.csv
│   ├── Sinistres.csv
│   ├── Objectifs.csv
│   ├── Calendrier.csv
│   └── Dictionnaire_Donnees.csv
│   → Contient tous les fichiers CSV générés par le script Python.
│     Encodage UTF-8-SIG, prêts à importer dans Power BI ou Excel.
│
├── scripts/
│   └── generate_assurguinee_360.py
│   → Script Python commenté qui génère l'intégralité du dataset.
│     Exécutable directement avec Python 3.8+.
│     Dépendances : pandas, numpy (pip install pandas numpy).
│
├── powerbi/
│   └── AssurGuinee_360.pbix
│   → Fichier Power BI principal contenant les tables, le modèle de données,
│     toutes les mesures DAX, les relations et les 8 pages du dashboard.
│     À ouvrir avec Power BI Desktop (version juin 2024 ou supérieure).
│
├── theme/
│   └── AssurGuinee360_Theme.json
│   → Fichier thème Power BI à importer via :
│     Affichage → Thèmes → Parcourir les thèmes.
│     Inclut les couleurs, typographies et styles de visuels.
│
├── logo/
│   ├── assurguinee360_logo_horizontal_fond_clair.png
│   ├── assurguinee360_logo_horizontal_fond_sombre.png
│   ├── assurguinee360_icone_fond_clair.png
│   └── assurguinee360_icone_fond_sombre.png
│   → Déclinaisons du logo pour usage dans le dashboard, les slides et documents.
│
├── captures_ecran/
│   ├── page1_vue_direction.png
│   ├── page2_analyse_produits.png
│   ├── page3_analyse_sinistres.png
│   ├── page4_analyse_clients.png
│   ├── page5_performance_agences.png
│   ├── page6_renouvellement.png
│   ├── page7_objectifs_vs_realise.png
│   └── page8_recommandations.png
│   → Captures d'écran haute résolution de chaque page du dashboard.
│     Utilisées dans le README et la présentation PowerPoint.
│
├── presentation/
│   └── AssurGuinee360_Presentation_Portfolio.pptx
│   → Présentation storytelling 8 slides (voir Section 8).
│     Destinée à des recruteurs, clients ou jurys de soutenance.
│
└── documentation/
    ├── modele_de_donnees.png          ← Capture du schéma de données Power BI
    ├── mesures_dax.md                 ← Toutes les mesures DAX documentées
    └── dictionnaire_donnees.md        ← Description de chaque colonne


================================================================================
SECTION 7 — README.md COMPLET
================================================================================

# 🛡️ Pilotage Assurance 360 — AssurGuinée 360

> **Tableau de bord Power BI de pilotage de la performance, des sinistres, de la rentabilité
> et du renouvellement d'un portefeuille d'assurance en Guinée.**

---

## 🏢 Contexte Business

AssurGuinée 360 est une compagnie d'assurance fictive basée à Conakry, Guinée.
Elle opère dans 8 villes principales à travers 12 agences couvrant les 5 régions du pays.

La Direction Générale souhaite disposer d'un outil de pilotage centralisé pour :
- Suivre les primes encaissées et la rentabilité estimée par agence et par produit.
- Analyser la sinistralité et détecter les zones à risque.
- Piloter les renouvellements de contrats par segment client.
- Mesurer l'atteinte des objectifs commerciaux mensuels.

---

## 🎯 Objectif du Projet

Créer un dashboard Power BI professionnel permettant à la direction de prendre
des décisions basées sur les données, structuré autour de 8 pages analytiques
couvrant l'ensemble du cycle de vie du contrat d'assurance.

---

## ❓ Questions Business Auxquelles Répond ce Dashboard

1. Quels produits génèrent les meilleures marges ?
2. Quelles agences surperforment ou sous-performent leurs objectifs ?
3. Quel est le profil des sinistres les plus coûteux ?
4. Quelles régions présentent un ratio sinistres/primes préoccupant ?
5. Quels segments clients renouvellent le mieux leurs contrats ?
6. Quel canal d'acquisition est le plus rentable ?
7. Comment évoluent les primes d'une année à l'autre ?
8. Quels agents commerciaux performent le mieux ?

---

## 📊 Données Utilisées

| Fichier                  | Lignes  | Description                              |
|--------------------------|---------|------------------------------------------|
| Clients.csv              | 1 000   | Portefeuille clients avec segments        |
| Produits.csv             | 8       | Catalogue des produits d'assurance        |
| Agences.csv              | 12      | Réseau d'agences en Guinée                |
| Agents.csv               | 60      | Agents commerciaux par agence             |
| Contrats.csv             | 5 000   | Contrats souscrits (2023–2025)            |
| Sinistres.csv            | ~1 500  | Déclarations de sinistres avec statuts    |
| Objectifs.csv            | ~3 456  | Objectifs mensuels agence × produit       |
| Calendrier.csv           | 1 096   | Table calendrier 2023–2025                |
| Dictionnaire_Donnees.csv | —       | Description de toutes les colonnes        |

> ⚠️ **Ces données sont entièrement fictives**, générées via un script Python
> à des fins de démonstration et de portfolio. Elles ne représentent aucune
> entreprise réelle.

---

## 🗂️ Modèle de Données

Schéma en étoile centré sur la table **Contrats** :

- Contrats → Clients (N:1)
- Contrats → Produits (N:1)
- Contrats → Agences (N:1)
- Contrats → Agents (N:1)
- Sinistres → Contrats (N:1)
- Contrats → Calendrier via Date Début (relation active)
- Sinistres → Calendrier via Date Sinistre (relation inactive, USERELATIONSHIP)
- Objectifs → Agences (N:1)
- Objectifs → Produits (N:1)

> Voir `documentation/modele_de_donnees.png` pour le schéma visuel complet.

---

## 🛠️ Outils Utilisés

| Outil              | Usage                                      |
|--------------------|--------------------------------------------|
| Python 3.10        | Génération du dataset (pandas, numpy)      |
| Power BI Desktop   | Modèle de données, DAX, dashboard          |
| DAX                | 23 mesures métier documentées              |
| Power Query (M)    | Transformations et typage des données      |
| JSON               | Thème Power BI personnalisé                |

---

## 📄 Pages du Dashboard

| Page | Titre                     | Audience principale      |
|------|---------------------------|--------------------------|
| 1    | Vue Direction             | DG, Comité de direction  |
| 2    | Analyse des Produits      | Directeur technique       |
| 3    | Analyse des Sinistres     | Responsable sinistres     |
| 4    | Analyse Clients           | Directeur commercial      |
| 5    | Performance Agences/Agents| Directeur réseau          |
| 6    | Renouvellement            | Directeur commercial      |
| 7    | Objectifs vs Réalisé      | Direction générale        |
| 8    | Recommandations           | Comité de direction       |

---

## 📈 KPIs Principaux

- Total Primes (GNF)
- Marge Estimée (GNF & %)
- Ratio Sinistres/Primes
- Taux de Renouvellement
- Taux d'Atteinte des Objectifs
- Délai Moyen de Règlement (jours)
- Prime Moyenne par Contrat

---

## 💡 Insights (à compléter après analyse)

> *À remplir après exploration du dashboard.*

- [ ] Insight 1 : Le produit le plus rentable est…
- [ ] Insight 2 : L'agence avec le meilleur ratio est…
- [ ] Insight 3 : Le segment client qui renouvelle le plus est…
- [ ] Insight 4 : La région avec le ratio sinistres/primes le plus élevé est…

---

## ✅ Recommandations (à compléter)

> *À remplir après analyse.*

- [ ] Recommandation 1 :
- [ ] Recommandation 2 :
- [ ] Recommandation 3 :

---

## 📸 Captures d'Écran

> *À ajouter après finalisation du dashboard.*

| Page | Aperçu |
|------|--------|
| Vue Direction | *(à venir)* |
| Sinistres | *(à venir)* |

---

## 🚀 Prochaines Améliorations

- [ ] Intégration d'une page de prévision (forecasting) via analytics Power BI
- [ ] Ajout d'un modèle de scoring de risque client
- [ ] Publication sur Power BI Service avec accès partagé
- [ ] Ajout de la sécurité au niveau des lignes (RLS) par agence
- [ ] Version mobile du dashboard

---

## 👤 Auteur

**Ousmane Tawel CAMARA** | Fondateur, Alpha Data Solutions (ADS)
Consultant Business Intelligence & Data — Conakry, Guinée
[LinkedIn](#) | infos@alphadatasolution.com

---

*Projet réalisé à des fins de démonstration portfolio. Données 100% fictives.*


================================================================================
SECTION 8 — STORYTELLING POWERPOINT (8 SLIDES)
================================================================================

────────────────────────────────────────────────────────
SLIDE 1 — LE PROBLÈME BUSINESS
────────────────────────────────────────────────────────
Titre orienté conclusion :
  "AssurGuinée 360 pilote son portefeuille à l'aveugle — et ça coûte cher."

Message principal :
  Sans tableau de bord unifié, la direction ne peut pas distinguer les produits
  rentables des produits à risque, ni anticiper les vagues de sinistres.
  Les décisions se prennent sur intuition, pas sur données.

Visuels à utiliser :
  • Icônes représentant : perte de rentabilité, sinistres non maîtrisés, churn client
  • Citation fictive : "On découvre les sinistres critiques 2 mois après qu'ils arrivent."
  • Chiffres-chocs : X% de ratio sinistres/primes non mesuré, Y contrats résiliés sans signal

Points à dire à l'oral :
  "Imaginez piloter une compagnie d'assurance sans savoir lesquels de vos produits
   vous font perdre de l'argent. C'est exactement le problème qu'on a résolu ici."

────────────────────────────────────────────────────────
SLIDE 2 — DONNÉES ET MÉTHODE
────────────────────────────────────────────────────────
Titre orienté conclusion :
  "9 tables, 8 500+ lignes, 1 modèle de données structuré comme un pro."

Message principal :
  Un dataset fictif mais réaliste, généré en Python, modélisé en schéma étoile
  dans Power BI, avec 23 mesures DAX et 8 pages analytiques.

Visuels à utiliser :
  • Schéma simplifié du modèle de données (Contrats au centre)
  • Pipeline : Python → CSV → Power BI → Dashboard
  • Tableau : 9 tables avec nb de lignes et description en 5 mots

Points à dire à l'oral :
  "J'ai commencé par modéliser le métier avant de toucher à Power BI.
   Le schéma en étoile centré sur les contrats est la colonne vertébrale du projet."

────────────────────────────────────────────────────────
SLIDE 3 — SYNTHÈSE EXÉCUTIVE
────────────────────────────────────────────────────────
Titre orienté conclusion :
  "Le portefeuille est rentable — mais 3 signaux d'alerte exigent une action immédiate."

Message principal :
  Vue d'ensemble : primes totales, marge estimée, taux de renouvellement global,
  et les 3 alertes clés identifiées dans l'analyse.

Visuels à utiliser :
  • 4 KPI cards : Total Primes / Marge Estimée / Taux Renouvellement / Ratio Sinistres
  • 3 icônes d'alerte colorées (rouge/orange) avec label court
  • Flèche de tendance mensuelle (2023→2025)

Points à dire à l'oral :
  "Le portfolio génère X milliards GNF de primes sur 3 ans, avec une marge estimée de Y%.
   Mais 3 signaux nécessitent une intervention : sinistralité Auto, churn Particuliers,
   et 2 agences régionales en sous-performance chronique."

────────────────────────────────────────────────────────
SLIDE 4 — PERFORMANCE DU PORTEFEUILLE
────────────────────────────────────────────────────────
Titre orienté conclusion :
  "Conakry concentre 46% des primes — les agences régionales ont un potentiel sous-exploité."

Message principal :
  Répartition du volume par agence, région et produit.
  Tendance de croissance interannuelle visible sur 3 ans.

Visuels à utiliser :
  • Carte Guinée avec performance agences (bulles proportionnelles aux primes)
  • Barres horizontales : Top 5 agences
  • Courbe de primes mensuelles 2023–2025

Points à dire à l'oral :
  "Le siège de Kaloum génère presque 1/5 du volume. Mais regardez Boké et Labé :
   des marchés en croissance avec un taux d'atteinte objectif supérieur à 80%."

────────────────────────────────────────────────────────
SLIDE 5 — PRODUITS RENTABLES ET PRODUITS À RISQUE
────────────────────────────────────────────────────────
Titre orienté conclusion :
  "Vie et Entreprise financent les pertes de l'Auto. Il faut rééquilibrer le mix."

Message principal :
  Matrice rentabilité vs sinistralité : identifier les 2 produits moteurs et les 2 produits
  à surveiller. Recommandation sur l'évolution du mix produit.

Visuels à utiliser :
  • Scatter plot : Primes (axe X) vs Ratio Sinistres (axe Y), bulle = volume
  • Tableau : 8 produits × (Primes / Sinistres / Marge / Ratio) avec couleurs RAG
  • Indicateurs de niveau de risque

Points à dire à l'oral :
  "Ce scatter plot dit tout. Les produits en haut à gauche sont les plus dangereux :
   beaucoup de sinistres pour peu de primes. Ceux en bas à droite sont les pépites."

────────────────────────────────────────────────────────
SLIDE 6 — ANALYSE DES SINISTRES
────────────────────────────────────────────────────────
Titre orienté conclusion :
  "40 jours en moyenne pour régler un sinistre critique — c'est 2× trop long."

Message principal :
  Les sinistres sont concentrés sur Auto et Santé. La Guinée Forestière affiche
  un ratio 20% supérieur à la moyenne nationale. Les délais de règlement pénalisent
  la satisfaction client.

Visuels à utiliser :
  • Histogramme des délais de règlement (distribution)
  • Carte : Ratio sinistres/primes par région (dégradé vert → rouge)
  • Anneau : Répartition des statuts (Réglé / En cours / Rejeté / Ouvert)
  • Barre : Top 5 types de sinistres par montant réglé

Points à dire à l'oral :
  "La question n'est pas 'combien de sinistres' mais 'combien ça coûte et combien de temps
   on met à les régler'. Ces deux métriques définissent l'expérience client."

────────────────────────────────────────────────────────
SLIDE 7 — RENOUVELLEMENT ET OPPORTUNITÉS COMMERCIALES
────────────────────────────────────────────────────────
Titre orienté conclusion :
  "72% des PME renouvellent — mais seulement 45% des Particuliers digitaux. L'écart est stratégique."

Message principal :
  Le taux de renouvellement varie fortement selon le segment et le canal d'acquisition.
  Les Particuliers acquis via Campagne digitale sont les moins fidèles.
  Les Partenaires bancaires performent mieux sur Vie et Entreprise.

Visuels à utiliser :
  • Barres : Taux de renouvellement par segment (avec ligne objectif)
  • Matrice : Canal Acquisition × Taux Renouvellement
  • Table : Contrats expirant dans 90 jours (opportunité pipeline)

Points à dire à l'oral :
  "Chaque contrat renouvelé, c'est zéro coût d'acquisition. Identifier les profils
   à risque de non-renouvellement avant l'échéance, c'est de la rétention proactive."

────────────────────────────────────────────────────────
SLIDE 8 — RECOMMANDATIONS
────────────────────────────────────────────────────────
Titre orienté conclusion :
  "4 actions concrètes pour +15% de marge estimée d'ici 12 mois."

Message principal :
  Synthèse des recommandations prioritaires, chiffrées, actionnables,
  avec l'impact attendu et le responsable suggéré.

Visuels à utiliser :
  • Tableau 4 lignes : Action / Problème ciblé / Impact estimé / Responsable
  • Icônes de priorité (🔴 Urgent / 🟡 Important / 🟢 À planifier)
  • Waterfall : Décomposition de l'amélioration de marge possible

Points à dire à l'oral :
  "Ce dashboard n'est pas une fin en soi. C'est un système d'alerte précoce.
   Ces 4 recommandations découlent directement des données.
   La prochaine étape : les intégrer dans le plan d'action trimestriel de la direction."

Recommandations à présenter :
  1. 🔴 Revoir les critères de souscription Auto en Guinée Forestière
     → Réduire le ratio sinistres de 20% dans la région
     → Responsable : Directeur Technique

  2. 🔴 Accélérer les délais de règlement (objectif < 30 jours pour gravité Faible/Moyenne)
     → Améliorer le NPS et réduire les litiges
     → Responsable : Responsable Sinistres

  3. 🟡 Développer le canal Partenaire bancaire sur les produits Vie et Entreprise
     → +35% de marge estimée vs canal Agence sur ces produits
     → Responsable : Directeur Commercial

  4. 🟢 Lancer un programme de fidélisation ciblant les Particuliers digitaux
     → Objectif : porter le taux de renouvellement de 45% à 60% en 12 mois
     → Responsable : Marketing

---

FIN DE LA DOCUMENTATION — AssurGuinée 360 × Alpha Data Solutions (ADS)
