# Glossaire complet des caractéristiques de produits de transport

Ce document définit TOUTES les 29 caractéristiques utilisables dans les produits de transport, avec leur sémantique complète pour l'apprentissage du LLM.

## Caractéristiques principales

### Caractéristique 2 : Groupe avec nombre de passagers par produit
**Utilisation** : Définit un produit de groupe avec un nombre fixe de passagers
**Paramètres** :
- `2_01` : Nombre maximum de passagers autorisés (integer, minimum 1)

**Exemples d'utilisation** :
- "Pass pour 5 personnes" → `2_01: 5`
- "Titre de groupe 10 passagers" → `2_01: 10`

**Règle métier** : À utiliser quand le produit est explicitement pour un groupe

---

### Caractéristique 3 : Lignes autorisées ou interdites par produit
**Utilisation** : Restreint ou autorise l'utilisation à certaines lignes spécifiques
**Paramètres** :
- `3_01` : Liste des lignes (array de strings)
- `3_02` : Type d'utilisation ("Autorisée" ou "Interdite")

**Exemples d'utilisation** :
- "Valable sur lignes 1, 2, 3" → `3_01: ["Ligne 1", "Ligne 2", "Ligne 3"], 3_02: "Autorisée"`
- "Sauf ligne 5" → `3_01: ["Ligne 5"], 3_02: "Interdite"`

**Règle métier** : N'utiliser que si des lignes spécifiques sont mentionnées

---

### Caractéristique 4 : Zones de tarification autorisées/interdites
**Utilisation** : Définit les zones tarifaires où le produit est valable
**Paramètres** :
- `4_01` : Liste des zones (array de strings ou integers)
- `4_02` : Type ("Autorisée" ou "Interdite")

**Exemples d'utilisation** :
- "Zones 1-2-3" → `4_01: ["Zone 1", "Zone 2", "Zone 3"], 4_02: "Autorisée"`
- "Hors zone 5" → `4_01: ["Zone 5"], 4_02: "Interdite"`

---

### Caractéristique 6 : Nombre de validations par déplacement
**Utilisation** : Définit combien de fois on doit valider pour un déplacement
**Paramètres** :
- `6_01` : Nombre de validations requises (integer, minimum 1)
- `6_02` : Type de validation ("Entrée", "Sortie", "Entrée-Sortie")

**Exemples d'utilisation** :
- "Validation à l'entrée et à la sortie" → `6_01: 2, 6_02: "Entrée-Sortie"`
- "Une seule validation" → `6_01: 1, 6_02: "Entrée"`

---

### Caractéristique 7 : DDV et DEV contrat - Période de validité
**Utilisation** : OBLIGATOIRE - Définit la durée de validité du produit
**Paramètres** :
- `7_01` : Nature de validité (integer) - CRITIQUE pour la compréhension
  - `0` = DDV et DEV à dates fixes (ex: "du 1er janvier au 31 décembre")
  - `2` = DDV et DEV glissantes au chargement (ex: "valable 1 mois à partir de l'achat")
  - `4` = DEV glissante à la validation (ex: "24h à partir de la première validation")
  - `6` = DDV et DEV déterminées au chargement et modifiables à la vente
  - `8` = DEV glissante avec DDV saisie à la vente
  - `14` = DDV saisie à la vente et DEV limitée par profil ou support
  - `20` = DDV début mois suivant, DEV limitée par profil ou support
  - `21` = DDV et DEV calendaires avec date pivot
- `7_02` : Unité de la durée ("D"=Jour, "W"=Semaine, "M"=Mois, "H"=Heure)
- `7_03` : Durée de validité (integer, minimum 1)
- `7_04` : Rechargement par prorogation (boolean) - vrai si le produit est renouvelable
- `7_05` : Autorisation de rechargement (boolean) - vrai si rechargeable

**Exemples d'utilisation** :
- "Abonnement mensuel rechargeable" → `7_01: 2, 7_02: "M", 7_03: 1, 7_04: true, 7_05: true`
- "Pass 24h" → `7_01: 4, 7_02: "H", 7_03: 24, 7_04: false, 7_05: false`
- "Valable 1 semaine" → `7_01: 2, 7_02: "W", 7_03: 1, 7_04: false, 7_05: false`
- "Abonnement annuel" → `7_01: 2, 7_02: "M", 7_03: 12, 7_04: true, 7_05: true`

**Règles de choix pour 7_01** :
- Utiliser `7_01: 2` pour les abonnements classiques (mensuel, hebdomadaire, annuel)
- Utiliser `7_01: 4` pour les pass/tickets à durée limitée (24h, 48h, etc.)
- Utiliser `7_01: 0` pour les produits avec dates fixes

---

### Caractéristique 8 : Calendrier d'autorisation ou de refus en validation
**Utilisation** : Définit un calendrier de jours où le produit est valable/invalide
**Paramètres** :
- `8_01` : Liste de dates ou périodes (array)
- `8_02` : Type ("Autorisé" ou "Interdit")

**Exemples d'utilisation** :
- "Valable pendant les vacances scolaires" → calendrier spécifique
- "Sauf jours fériés" → liste des jours fériés avec type "Interdit"

---

### Caractéristique 9 : Autorisation de déplacement par type de jour et tranche horaire
**Utilisation** : Restreint l'utilisation à certains jours et/ou heures
**Paramètres** :
- `9_01` : Table de validité (array d'objets avec `days`, `start`, `end`)
  - `days` : Type de jour (ex: "Lundi-Vendredi", "Samedi-Dimanche", "Lundi-Dimanche")
  - `start` : Heure de début au format "HH:MM"
  - `end` : Heure de fin au format "HH:MM"

**Exemples d'utilisation** :
- "Valable en semaine de 9h à 17h" → `9_01: [{days: "Lundi-Vendredi", start: "09:00", end: "17:00"}]`
- "Week-end uniquement" → `9_01: [{days: "Samedi-Dimanche", start: "00:00", end: "23:59"}]`
- "Après 19h" → `9_01: [{days: "Lundi-Dimanche", start: "19:00", end: "23:59"}]`

---

### Caractéristique 10 : Limitation des déplacements par sous-période
**Utilisation** : Limite le nombre de déplacements sur une période (jour, semaine, etc.)
**Paramètres** :
- `10_01` : Liste de limitations (array d'objets)
  - `unit` : Unité de temps ("Jour", "Semaine", "Mois", "Heure")
  - `count` : Nombre d'unités (integer)
  - `max_trips` : Nombre maximum de déplacements (integer)

**Exemples d'utilisation** :
- "Maximum 2 voyages par jour" → `10_01: [{unit: "Jour", count: 1, max_trips: 2}]`
- "10 déplacements par semaine" → `10_01: [{unit: "Semaine", count: 1, max_trips: 10}]`

---

### Caractéristique 11 : Interdiction de retour sur une même ligne
**Utilisation** : Empêche de revenir en arrière sur la même ligne pendant un certain temps
**Paramètres** :
- `11_01` : Durée d'interdiction en minutes (integer)
- `11_02` : Applicable à toutes les lignes (boolean)

**Exemples d'utilisation** :
- "Pas de retour dans les 90 minutes" → `11_01: 90, 11_02: true`

---

### Caractéristique 14 : Modes de transport autorisés ou interdits
**Utilisation** : Définit sur quels modes de transport le produit est valable
**Paramètres** :
- `14_01` : Liste des modes (array) - valeurs possibles :
  - "Bus urbain"
  - "Bus interurbain"
  - "Métro"
  - "Tramway"
  - "Train"
  - "Parking"
  - "Vélo"
- `14_02` : Type ("Autorisée" ou "Interdite")

**Exemples d'utilisation** :
- "Pour le métro" → `14_01: ["Métro"], 14_02: "Autorisée"`
- "Bus et tramway" → `14_01: ["Bus urbain", "Tramway"], 14_02: "Autorisée"`
- "Tous modes sauf train" → `14_01: ["Train"], 14_02: "Interdite"`
- "Tous modes" → omettre la caractéristique OU `14_01: ["Bus urbain", "Métro", "Tramway", "Train"], 14_02: "Autorisée"`

**Règle métier** : Si mode non spécifié, ne pas inclure cette caractéristique

---

### Caractéristique 21 : Multi-déplacement, Multi-usager
**Utilisation** : Carnet partageable entre plusieurs personnes
**Paramètres** :
- `21_01` : Nombre de déplacements du produit (integer)
- `21_02` : Nombre maximum de déplacements (integer)
- `21_03` : Nombre d'usagers simultanés maximum (integer)
- `21_04` : Rechargement par surcharge (boolean)

**Exemples d'utilisation** :
- "Carnet de 10 tickets partageable" → `21_01: 10, 21_02: 10, 21_03: 3, 21_04: false`

**Différence avec carac. 22** : 21 = multi-usager, 22 = mono-usager

---

### Caractéristique 22 : Multi-déplacements Mono-usager
**Utilisation** : Carnet de tickets pour UNE seule personne
**Paramètres** :
- `22_01` : Nombre de déplacements du produit (integer, minimum 1)
- `22_02` : Nombre maximum de déplacements du contrat (integer, minimum 1)
- `22_03` : Rechargement par surcharge (boolean)

**Exemples d'utilisation** :
- "Carnet de 10 tickets" → `22_01: 10, 22_02: 10, 22_03: false`
- "1 voyage" → `22_01: 1, 22_02: 1, 22_03: false`
- "Carnet rechargeable de 20 tickets" → `22_01: 20, 22_02: 20, 22_03: true`

**Règle métier** : Utiliser pour tout produit avec nombre de voyages limité (pas illimité)

---

### Caractéristique 23 : Points de fidélité à la validation
**Utilisation** : Crédite des points de fidélité à chaque validation
**Paramètres** :
- `23_01` : Nombre de points par validation (integer)
- `23_02` : Programme de fidélité (string)

**Exemples d'utilisation** :
- "2 points par voyage" → `23_01: 2, 23_02: "Programme standard"`

---

### Caractéristique 38 : Groupe avec nombre de passagers saisi à la vente
**Utilisation** : Le nombre de passagers est variable et saisi au moment de l'achat
**Paramètres** :
- `38_01` : Nombre minimum de passagers (integer)
- `38_02` : Nombre maximum de passagers (integer)

**Exemples d'utilisation** :
- "Groupe de 5 à 20 personnes" → `38_01: 5, 38_02: 20`

**Différence avec carac. 2** : 38 = nombre variable à la vente, 2 = nombre fixe

---

### Caractéristique 48 : Produit à post-paiement
**Utilisation** : Le paiement s'effectue après utilisation
**Paramètres** :
- `48_01` : Mode de facturation ("Mensuel", "Trimestriel", "Annuel")
- `48_02` : Délai de paiement en jours (integer)

**Exemples d'utilisation** :
- "Facturation mensuelle" → `48_01: "Mensuel", 48_02: 30`

---

### Caractéristique 58 : Classe autorisée par produit
**Utilisation** : Définit la classe de voyage autorisée
**Paramètres** :
- `58_01` : Numéro de classe (integer) - 1=Première classe, 2=Seconde classe
- `58_02` : Surclassement autorisé (boolean)

**Exemples d'utilisation** :
- "Première classe" → `58_01: 1, 58_02: true`
- "Seconde classe uniquement" → `58_01: 2, 58_02: false`

---

### Caractéristique 73 : Encodage du pointeur sur profil
**Utilisation** : Lie le produit à un profil spécifique (étudiant, senior, etc.)
**Paramètres** :
- `73_01` : Code profil (string ou integer)
- `73_02` : Description du profil (string)

**Exemples d'utilisation** :
- "Tarif étudiant" → `73_01: "ETU", 73_02: "Étudiant"`
- "Tarif senior" → `73_01: "SEN", 73_02: "Senior"`

---

### Caractéristique 74 : Mode de transport autorisé par produit
**Utilisation** : DEPRECATED - Utiliser caractéristique 14 à la place
**Note** : Cette caractéristique est obsolète, préférer la caractéristique 14

---

### Caractéristique 86 : OD sélectionnée à la vente
**Utilisation** : Origine-Destination définie au moment de l'achat
**Paramètres** :
- `86_01` : Code origine (string)
- `86_02` : Code destination (string)
- `86_03` : Trajet aller-retour (boolean)

**Exemples d'utilisation** :
- "Paris-Lyon aller simple" → `86_01: "PARIS", 86_02: "LYON", 86_03: false`
- "Paris-Lyon aller-retour" → `86_01: "PARIS", 86_02: "LYON", 86_03: true`

---

### Caractéristique 87 : Lignes déterminées à la vente et codées sur le support
**Utilisation** : Les lignes sont choisies à l'achat et gravées sur le support
**Paramètres** :
- `87_01` : Liste des lignes sélectionnées (array de strings)
- `87_02` : Modifiable après achat (boolean)

**Exemples d'utilisation** :
- "Lignes 1 et 2 fixées à l'achat" → `87_01: ["Ligne 1", "Ligne 2"], 87_02: false`

---

### Caractéristique 90 : Champ de zones
**Utilisation** : Définit un ensemble de zones tarifaires
**Paramètres** :
- `90_01` : Zones incluses (array)
- `90_02` : Type de champ ("Circulaire", "Rectangulaire", "Libre")

---

### Caractéristique 91 : Encodage de prestations
**Utilisation** : Services additionnels inclus dans le produit
**Paramètres** :
- `91_01` : Liste des prestations (array de strings)

**Exemples** :
- "Accès WiFi + Prise électrique" → `91_01: ["WiFi", "Prise électrique"]`

---

### Caractéristique 97 : Gestion du remboursement
**Utilisation** : Définit les conditions de remboursement
**Paramètres** :
- `97_01` : Remboursable (boolean)
- `97_02` : Délai de remboursement en jours (integer)
- `97_03` : Pourcentage de remboursement (integer, 0-100)
- `97_04` : Frais de remboursement (number)

**Exemples d'utilisation** :
- "Remboursable sous 7 jours à 80%" → `97_01: true, 97_02: 7, 97_03: 80, 97_04: 5.00`
- "Non remboursable" → `97_01: false`

---

### Caractéristique 98 : Mécanisme d'inhibition du blocage de contrat
**Utilisation** : Gère le déblocage automatique du contrat
**Paramètres** :
- `98_01` : Déblocage automatique (boolean)
- `98_02` : Délai avant déblocage en heures (integer)

**Exemples d'utilisation** :
- "Déblocage auto après 24h" → `98_01: true, 98_02: 24`

---

### Caractéristique 102 : Abonnement à tacite reconduction avec prélèvements automatiques
**Utilisation** : Renouvellement automatique de l'abonnement
**Paramètres** :
- `102_01` : Type de prélèvement ("Aucun", "Mensuel", "Trimestriel", "Annuel")
- `102_04` : Tacite reconduction activée (boolean)

**Exemples d'utilisation** :
- "Abonnement avec tacite reconduction" → `102_01: "Aucun", 102_04: true`
- "Prélèvement mensuel automatique" → `102_01: "Mensuel", 102_04: true`
- "Sans reconduction" → `102_01: "Aucun", 102_04: false`

**Règle métier** : À utiliser pour les abonnements renouvelables automatiquement

---

### Caractéristique 103 : Titre unitaire sans compteur
**Utilisation** : Titre à usage unique sans décompte
**Paramètres** :
- `103_01` : Durée de validité après validation (integer, en minutes)

**Exemples d'utilisation** :
- "Ticket valable 90 minutes" → `103_01: 90`

---

### Caractéristique 105 : Multi-validation
**Utilisation** : Permet de valider pour plusieurs personnes en une fois
**Paramètres** :
- `105_01` : Nombre maximum de validations simultanées (integer)

**Exemples d'utilisation** :
- "Validation pour 3 personnes max" → `105_01: 3`

---

### Caractéristique 107 : X mois gratuits pour Y mois payés
**Utilisation** : Promotion type "payez 10 mois, voyagez 12 mois"
**Paramètres** :
- `107_01` : Mois payés (integer)
- `107_02` : Mois gratuits (integer)
- `107_03` : Mois total (integer)

**Exemples d'utilisation** :
- "10 mois payés = 12 mois de voyage" → `107_01: 10, 107_02: 2, 107_03: 12`

---

### Caractéristique 121 : Zones autorisées sur un des réseaux locaux déterminées à la vente
**Utilisation** : Zones choisies au moment de l'achat pour un réseau spécifique
**Paramètres** :
- `121_01` : Code réseau (string)
- `121_02` : Zones sélectionnées (array)

**Exemples d'utilisation** :
- "Réseau Paris zones 1-2-3" → `121_01: "PARIS", 121_02: ["Zone 1", "Zone 2", "Zone 3"]`

---

## Règles de combinaison des caractéristiques

### Caractéristique 7 (validité) : TOUJOURS OBLIGATOIRE
Tous les produits DOIVENT avoir une caractéristique 7.

### Choix entre 21 et 22 (multi-déplacements)
- Utiliser **22** si le produit est pour UNE personne
- Utiliser **21** si le carnet peut être partagé entre plusieurs personnes

### Choix entre 2 et 38 (groupe)
- Utiliser **2** si le nombre de passagers est FIXE
- Utiliser **38** si le nombre est VARIABLE et saisi à la vente

### Abonnements rechargeables
Pour un abonnement rechargeable, utiliser :
- Caractéristique 7 avec `7_04: true` et `7_05: true`
- Optionnellement caractéristique 102 si tacite reconduction

### Restrictions horaires vs restrictions calendaires
- Utiliser **9** pour restrictions par jour de semaine et tranches horaires
- Utiliser **8** pour restrictions par dates spécifiques (calendrier)

---

## Inférences importantes pour le LLM

### Déduction de la nature de validité (7_01)
- "Abonnement mensuel/annuel" → `7_01: 2` (glissant au chargement)
- "Pass 24h/48h" → `7_01: 4` (glissant à la validation)
- "Valable du 1er au 31 janvier" → `7_01: 0` (dates fixes)

### Déduction du rechargement (7_04, 7_05)
- "Abonnement mensuel" → probablement rechargeable → `7_04: true, 7_05: true`
- "Carnet de tickets" → probablement non rechargeable → `7_04: false, 7_05: false`
- "Pass 24h" → non rechargeable → `7_04: false, 7_05: false`

### Déduction de multi-déplacements
- "Illimité" → PAS de caractéristique 22 ou 21
- "10 tickets" ou "10 voyages" → caractéristique 22 avec `22_01: 10, 22_02: 10`
- "1 trajet" ou "ticket simple" → caractéristique 22 avec `22_01: 1, 22_02: 1`

### Déduction des modes
- "Métro" → `14_01: ["Métro"], 14_02: "Autorisée"`
- "Bus et tramway" → `14_01: ["Bus urbain", "Tramway"], 14_02: "Autorisée"`
- "Tous modes sauf train" → `14_01: ["Train"], 14_02: "Interdite"`
- "Tous modes" ou "multi-modal" → ne pas inclure la caractéristique 14

### Déduction des contraintes horaires
- "Week-end" → caractéristique 9 avec `days: "Samedi-Dimanche", start: "00:00", end: "23:59"`
- "En semaine" → `days: "Lundi-Vendredi", start: "00:00", end: "23:59"`
- "Heures creuses" ou "9h-17h" → `days: "Lundi-Vendredi", start: "09:00", end: "17:00"`
- "Après 19h" → `days: "Lundi-Dimanche", start: "19:00", end: "23:59"`

---

## Exemples complets avec raisonnement

### Exemple 1 : "Je veux un abonnement mensuel pour le métro"

**Raisonnement** :
1. "abonnement mensuel" → caractéristique 7 avec durée 1 mois, rechargeable
2. "pour le métro" → caractéristique 14 avec métro autorisé
3. Pas de limitation de voyages → PAS de caractéristique 22

**JSON** :
```json
{
  "product_name": "Abonnement mensuel Métro",
  "characteristics": [
    {
      "number": 7,
      "parameters": {
        "7_01": 2,
        "7_02": "M",
        "7_03": 1,
        "7_04": true,
        "7_05": true
      }
    },
    {
      "number": 14,
      "parameters": {
        "14_01": ["Métro"],
        "14_02": "Autorisée"
      }
    }
  ]
}
```

### Exemple 2 : "Carnet de 10 tickets valable 1 semaine sur bus et tramway"

**Raisonnement** :
1. "valable 1 semaine" → caractéristique 7 avec durée 1 semaine
2. "10 tickets" → caractéristique 22 avec 10 déplacements
3. "sur bus et tramway" → caractéristique 14 avec ces 2 modes
4. "carnet" = non rechargeable → `7_04: false, 7_05: false`

**JSON** :
```json
{
  "product_name": "Carnet 10 voyages hebdomadaire Bus-Tramway",
  "characteristics": [
    {
      "number": 7,
      "parameters": {
        "7_01": 2,
        "7_02": "W",
        "7_03": 1,
        "7_04": false,
        "7_05": false
      }
    },
    {
      "number": 22,
      "parameters": {
        "22_01": 10,
        "22_02": 10,
        "22_03": false
      }
    },
    {
      "number": 14,
      "parameters": {
        "14_01": ["Bus urbain", "Tramway"],
        "14_02": "Autorisée"
      }
    }
  ]
}
```

### Exemple 3 : "Pass 24h pour 5 personnes, tous modes"

**Raisonnement** :
1. "Pass 24h" → caractéristique 7 avec durée 24 heures, nature 4 (glissant à validation)
2. "pour 5 personnes" → caractéristique 2 avec 5 passagers
3. "tous modes" → PAS de caractéristique 14 (ou tous les modes en autorisé)
4. "pass" = non rechargeable → `7_04: false, 7_05: false`

**JSON** :
```json
{
  "product_name": "Pass 24h Groupe 5 personnes",
  "characteristics": [
    {
      "number": 7,
      "parameters": {
        "7_01": 4,
        "7_02": "H",
        "7_03": 24,
        "7_04": false,
        "7_05": false
      }
    },
    {
      "number": 2,
      "parameters": {
        "2_01": 5
      }
    }
  ]
}
```

---

## Notes importantes pour l'entraînement

1. **Toujours inclure la caractéristique 7** - C'est obligatoire
2. **Ne pas sur-spécifier** - Si "tous modes", ne pas inclure caractéristique 14
3. **Inférer le rechargement** - Les abonnements sont généralement rechargeables
4. **Comprendre la sémantique** - "Carnet" ≠ "Abonnement" ≠ "Pass"
5. **Attention aux exclusions** - "Sauf train" → mode Train en Interdit, pas les autres en Autorisé
