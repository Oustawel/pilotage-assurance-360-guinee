<p align="center">
  <img src="logo/assurguinee360_horizontal_fond_sombre.png" width="320" alt="Logo AssurGuinée 360">
</p>

# Pilotage Assurance 360 — Tableau de bord Power BI pour le secteur assurance en Guinée


## Contexte du projet

Ce projet est un cas fictif de Business Intelligence appliqué au secteur de l’assurance en Guinée.

L’objectif est de construire un tableau de bord Power BI permettant à une compagnie d’assurance de suivre la performance de son portefeuille à travers les primes, les contrats, les sinistres, les clients, les produits, les agences et les canaux de vente.

Les données utilisées sont fictives et ont été générées pour un projet portfolio.

---

## Objectif business

Le projet répond à la question suivante :

**Comment une compagnie d’assurance peut-elle identifier ses moteurs de croissance, ses zones de risque et ses leviers d’amélioration commerciale à partir de ses données ?**

Le dashboard permet notamment de suivre :

- les primes générées ;
- le nombre de contrats ;
- les contrats actifs ;
- les sinistres réglés ;
- le ratio sinistres/primes ;
- la marge estimée ;
- le taux de renouvellement ;
- la performance des produits ;
- la segmentation client ;
- la performance des agences et des canaux de vente.

---

## Outils utilisés

- Power BI
- Power Query
- DAX
- Python
- GitHub
- PowerPoint

---

## Structure du projet

```text
Pilotage Assurance 360_AssurGuinée 360/
│
├── donnees/
│   ├── Agences.csv
│   ├── Agents.csv
│   ├── Calendrier.csv
│   ├── Clients.csv
│   ├── Contrats.csv
│   ├── Dictionnaire_Donnees.csv
│   ├── Objectifs.csv
│   ├── Produits.csv
│   └── Sinistres.csv
│
├── powerbi/
│   └── Pilotage Assurance 360_AssurGuinée 360.pbix
│
├── scripts/
│   └── generate_assurguinee_360.py
│
├── documentation/
│   ├── insights_business.md
│   └── AssurGuinee360_Documentation_Complete.md
│
├── captures_ecran/
│   ├── 01_vue_direction.png
│   ├── 02_analyse_produits.png
│   ├── 03_analyse_sinistres.png
│   ├── 04_analyse_clients.png
│   └── 05_performance_agences.png
│
├── presentation/
│   └── pilotage_assurance_360_presentation.pptx
│
└── README.md