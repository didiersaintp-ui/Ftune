# 🚫 Incompatibilités et Règles Métier - Billettique TCL

Documentation exhaustive de toutes les incompatibilités entre caractéristiques, supports et paramètres dans le système de billettique Atlas.

## 📋 Vue d'Ensemble

Cette documentation liste **TOUTES** les incompatibilités connues qui doivent être détectées et signalées par l'assistant.

**Criticité** : 🔴 BLOQUANT - L'assistant DOIT refuser de créer un produit avec des caractéristiques incompatibles.

## 🔴 Incompatibilités entre Caractéristiques

### 1. CAR_14 ⊗ CAR_74 : Modes de Transport
**Raison** : Ces deux caractéristiques servent le même objectif mais de manière incompatible.

- **CAR_14** : Liste paramétrable de modes autorisés/interdits
- **CAR_74** : Mode unique codé sur le support (OBSOLÈTE)

**Règle** : Utiliser UNIQUEMENT CAR_14 (CAR_74 est deprecated)

**Exemple d'erreur** :
```json
{
  "characteristics": [
    {"number": 14, "parameters": {"14_01": ["Bus urbain", "Métro"]}},
    {"number": 74, "parameters": {"74_01": "Bus"}}  // ❌ INTERDIT
  ]
}
```

**Réponse attendue** :
```
⚠️ **INCOMPATIBILITÉ DÉTECTÉE**

CAR_14 et CAR_74 ne peuvent pas coexister car elles définissent toutes deux les modes de transport autorisés.

✅ **Solution** : Utiliser uniquement CAR_14
```

---

### 2. CAR_22 ⊗ CAR_21 : Mono-usager vs Multi-usager
**Raison** : Un carnet ne peut être à la fois mono-usager ET multi-usager.

- **CAR_22** : Multi-déplacements pour UNE seule personne
- **CAR_21** : Multi-déplacements partageable entre PLUSIEURS personnes

**Règle** : Choisir l'une OU l'autre, jamais les deux

**Exemple d'erreur** :
```json
{
  "characteristics": [
    {"number": 22, "parameters": {"22_01": 10}},  // Mono-usager
    {"number": 21, "parameters": {"21_01": 10, "21_03": 3}}  // ❌ Multi-usager
  ]
}
```

**Réponse attendue** :
```
⚠️ **INCOMPATIBILITÉ DÉTECTÉE**

CAR_22 (mono-usager) et CAR_21 (multi-usager) sont mutuellement exclusives.

❓ **Question** : Le carnet est-il pour une seule personne ou partageable ?
- Si mono-usager → CAR_22
- Si multi-usager → CAR_21
```

---

### 3. CAR_2 ⊗ CAR_38 : Groupe Fixe vs Variable
**Raison** : Le nombre de passagers ne peut être à la fois fixe ET variable.

- **CAR_2** : Nombre de passagers FIXE au paramétrage
- **CAR_38** : Nombre de passagers VARIABLE, saisi à la vente

**Règle** : Choisir l'une OU l'autre

**Exemple d'erreur** :
```json
{
  "characteristics": [
    {"number": 2, "parameters": {"2_01": 5}},  // 5 passagers fixes
    {"number": 38, "parameters": {"38_01": 3, "38_02": 10}}  // ❌ Variable 3-10
  ]
}
```

**Réponse attendue** :
```
⚠️ **INCOMPATIBILITÉ DÉTECTÉE**

CAR_2 (groupe fixe) et CAR_38 (groupe variable) sont incompatibles.

✅ **Solution** :
- Si le nombre est connu à l'avance → CAR_2
- Si le nombre varie à la vente → CAR_38
```

---

### 4. CAR_3 ⊗ CAR_87 : Lignes Paramétrées vs Codées à la Vente
**Raison** : Les lignes ne peuvent être à la fois paramétrées ET saisies à la vente.

- **CAR_3** : Lignes définies dans le paramétrage du produit
- **CAR_87** : Lignes choisies et codées à la vente sur le support

**Règle** : Choisir l'une OU l'autre

**Exemple d'erreur** :
```json
{
  "characteristics": [
    {"number": 3, "parameters": {"3_01": ["Ligne 1", "Ligne 2"], "3_02": "Autorisée"}},
    {"number": 87, "parameters": {"87_01": ["Ligne 3"], "87_02": false}}  // ❌
  ]
}
```

**Réponse attendue** :
```
⚠️ **INCOMPATIBILITÉ DÉTECTÉE**

CAR_3 (lignes paramétrées) et CAR_87 (lignes à la vente) sont incompatibles.

❓ **Question** : Les lignes sont-elles :
- Connues à l'avance → CAR_3
- Choisies à l'achat → CAR_87
```

---

### 5. CAR_4 ⊗ CAR_121 : Zones Paramétrées vs Saisies à la Vente
**Raison** : Les zones tarifaires ne peuvent être à la fois paramétrées ET saisies à la vente.

- **CAR_4** : Zones définies dans le paramétrage
- **CAR_121** : Zones choisies à la vente pour un réseau spécifique

**Règle** : Choisir l'une OU l'autre

**Exemple d'erreur** :
```json
{
  "characteristics": [
    {"number": 4, "parameters": {"4_01": ["Zone 1", "Zone 2"], "4_02": "Autorisée"}},
    {"number": 121, "parameters": {"121_01": "LYON", "121_02": ["Zone 3"]}}  // ❌
  ]
}
```

**Réponse attendue** :
```
⚠️ **INCOMPATIBILITÉ DÉTECTÉE**

CAR_4 (zones paramétrées) et CAR_121 (zones à la vente) sont incompatibles.

✅ **Solution** :
- Zones fixes → CAR_4
- Zones choisies à l'achat → CAR_121
```

---

### 6. CAR_6 ⊗ CAR_21 : Validation par Déplacement vs Multi-usager
**Raison** : La validation multiple par déplacement (entrée-sortie) est incompatible avec les carnets multi-usagers.

- **CAR_6** : Nombre de validations requises par déplacement (ex: entrée + sortie)
- **CAR_21** : Carnet partageable entre usagers

**Règle** : CAR_6 ne peut être utilisée qu'avec des produits mono-usager

**Impact** : Si CAR_21 → ne pas utiliser CAR_6

---

## 🔴 Incompatibilités Support BSC

### Support BSC (Billet Sans Contact)
Le support **BSC** (billet papier, QR code, NFC temporaire) a des limitations techniques importantes.

#### Caractéristiques INCOMPATIBLES avec BSC :

1. **CAR_10** : Limitation des déplacements par sous-période
   - **Raison** : Le BSC ne peut pas stocker de compteur dynamique
   - **Incompatible** : "Maximum 2 voyages par jour"

2. **CAR_102** : Tacite reconduction
   - **Raison** : Le BSC n'est pas rechargeable automatiquement
   - **Incompatible** : Abonnements avec prélèvement automatique

3. **CAR_23** : Points de fidélité
   - **Raison** : Le BSC ne peut pas mettre à jour un compteur de points
   - **Incompatible** : Programmes de fidélité

4. **CAR_48** : Post-paiement
   - **Raison** : Le BSC ne permet pas de tracking pour facturation différée
   - **Incompatible** : Facturation mensuelle après utilisation

5. **CAR_98** : Inhibition du blocage de contrat
   - **Raison** : Le BSC n'a pas de mécanisme de blocage/déblocage
   - **Incompatible** : Déblocage automatique après fraude

6. **CAR_105** : Multi-validation
   - **Raison** : Le BSC est à usage unique, ne peut pas valider pour plusieurs personnes
   - **Incompatible** : "Valider pour 3 personnes"

7. **Rechargement par prorogation** (7_04: true)
   - **Raison** : Le BSC n'est pas rechargeable
   - **Règle** : Si support = BSC → 7_04 doit être false

8. **Rechargement autorisé** (7_05: true)
   - **Raison** : Le BSC n'est pas rechargeable
   - **Règle** : Si support = BSC → 7_05 doit être false

#### Exemple d'erreur BSC :
```json
{
  "product_name": "Abonnement Mensuel",
  "support": ["BSC"],  // ❌ IMPOSSIBLE
  "characteristics": [
    {
      "number": 7,
      "parameters": {
        "7_01": 2,
        "7_02": "M",
        "7_03": 1,
        "7_04": true,  // ❌ Rechargeable = impossible sur BSC
        "7_05": true
      }
    }
  ]
}
```

**Réponse attendue** :
```
⚠️ **INCOMPATIBILITÉ SUPPORT DÉTECTÉE**

Les abonnements mensuels rechargeables ne peuvent PAS être sur support BSC.

✅ **Solutions** :
1. Utiliser support CSC (Carte Sans Contact) ou AB (Application)
2. OU créer un ticket mensuel non-rechargeable (mais peu pratique)

❓ Sur quel support souhaitez-vous ce produit ?
- CSC (carte rechargeable)
- AB (application mobile)
```

---

## 🔴 Incompatibilités Support CSC vs AB

### Support CSC (Carte Sans Contact)
- ✅ Rechargeable
- ✅ Tacite reconduction
- ✅ Fidélité
- ✅ Multi-validation
- ❌ Dématérialisé

### Support AB (Application Billettique)
- ✅ Rechargeable
- ✅ Tacite reconduction
- ✅ Fidélité
- ✅ Multi-validation
- ✅ Dématérialisé
- ✅ Géolocalisation possible

**Note** : AB et CSC sont généralement compatibles avec les mêmes caractéristiques, mais AB offre plus de fonctionnalités (notifications, géolocalisation, paiement intégré).

---

## 🟡 Incompatibilités Logiques de Paramètres

### 1. Durée de Validité Incohérente
**Règle** : La durée doit être cohérente avec l'unité

```json
// ❌ ERREUR
{
  "number": 7,
  "parameters": {
    "7_02": "M",  // Mois
    "7_03": 0     // ❌ Durée = 0
  }
}

// ✅ CORRECT
{
  "number": 7,
  "parameters": {
    "7_02": "M",
    "7_03": 1  // Au moins 1 mois
  }
}
```

---

### 2. Nature de Validité Incohérente
**Règle** : Certaines natures nécessitent des paramètres spécifiques

**Nature 0** (dates fixes) : Nécessite DDV et DEV fixes (pas dans CAR_7, mais dans le système)
**Nature 2** (glissant au chargement) : Standard pour abonnements
**Nature 4** (glissant à validation) : Standard pour pass temporels
**Nature 8** (DEV glissante avec DDV saisie) : Nécessite interaction à la vente

---

### 3. Multi-déplacements Incohérent
**Règle** : Le nombre de déplacements doit être > 0

```json
// ❌ ERREUR
{
  "number": 22,
  "parameters": {
    "22_01": 0,  // ❌ Impossible
    "22_02": 0
  }
}

// ✅ CORRECT
{
  "number": 22,
  "parameters": {
    "22_01": 10,
    "22_02": 10
  }
}
```

---

### 4. Zones Vides
**Règle** : Si CAR_4 est présente, la liste de zones ne peut pas être vide

```json
// ❌ ERREUR
{
  "number": 4,
  "parameters": {
    "4_01": [],  // ❌ Liste vide
    "4_02": "Autorisée"
  }
}

// ✅ CORRECT
{
  "number": 4,
  "parameters": {
    "4_01": ["Zone 1", "Zone 2"],
    "4_02": "Autorisée"
  }
}
```

---

### 5. Modes Vides
**Règle** : Si CAR_14 est présente, la liste de modes ne peut pas être vide

```json
// ❌ ERREUR
{
  "number": 14,
  "parameters": {
    "14_01": [],  // ❌ Liste vide
    "14_02": "Autorisée"
  }
}

// ✅ CORRECT : Ne pas inclure CAR_14 si tous modes autorisés
// OU
{
  "number": 14,
  "parameters": {
    "14_01": ["Bus urbain", "Métro", "Tramway"],
    "14_02": "Autorisée"
  }
}
```

---

## 🟡 Règles Métier TCL Spécifiques

### 1. Produits TCL Lyon Standards

#### Ticket Unité
- Prix : 2.00€
- Durée : 1 heure
- Modes : Bus urbain, Métro, Tramway, Funiculaire
- Support : BSC, AB
- Voyages : 1
- **CAR requises** : 7, 14, 22

#### Abonnement Mensuel (Plein tarif)
- Prix : 67.00€
- Durée : 1 mois
- Modes : Bus urbain, Métro, Tramway, Funiculaire
- Support : CSC, AB
- Voyages : Illimité
- **CAR requises** : 7, 14

#### Abonnement Jeune (-26 ans)
- Prix : 34.00€
- Durée : 1 mois
- Modes : Bus urbain, Métro, Tramway, Funiculaire
- Support : CSC, AB
- Voyages : Illimité
- **CAR requises** : 7, 14
- **Profil** : Jeune

---

### 2. Zones Tarifaires TCL
Lyon a **5 zones tarifaires** :
- Zone 1 : Lyon centre
- Zone 2 : Proche banlieue
- Zone 3 : Banlieue
- Zone 4 : Périphérie
- Zone 5 : Extérieur

**Règle** : Les zones doivent être contiguës (pas de "trou")
- ✅ Zones 1-2-3
- ❌ Zones 1-3 (manque zone 2)

---

### 3. Modes de Transport TCL
- **Bus urbain** : Réseau urbain Lyon
- **Métro** : 4 lignes (A, B, C, D)
- **Tramway** : 7 lignes (T1-T7)
- **Funiculaire** : 2 lignes (Fourvière, Croix-Rousse)
- **Bus interurbain** : Cars régionaux (hors TCL standard)

**Règle** : Le Funiculaire est généralement inclus avec le pack "tous modes TCL"

---

### 4. Prix Cohérence
**Règle** : Le prix doit être cohérent avec le produit

Exemples de fourchettes TCL :
- Ticket unitaire : 1.50€ - 3.00€
- Carnet 10 tickets : 15.00€ - 25.00€
- Abonnement mensuel : 30.00€ - 80.00€
- Abonnement annuel : 300.00€ - 900.00€

**Alerte** si prix hors fourchette

---

## 📊 Matrice de Compatibilité Complète

| CAR | 2 | 3 | 4 | 6 | 7 | 10 | 14 | 21 | 22 | 38 | 87 | 102 | 121 |
|-----|---|---|---|---|---|----|----|----|----|----|----|----|-----|
| **2** | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **3** | ✅ | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **4** | ✅ | ✅ | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **6** | ✅ | ✅ | ✅ | - | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **7** | ✅ | ✅ | ✅ | ✅ | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **14** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **21** | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | - | ❌ | ✅ | ✅ | ✅ | ✅ |
| **22** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | - | ✅ | ✅ | ✅ | ✅ |
| **38** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ | ✅ | ✅ |
| **87** | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ | ✅ |
| **102** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ |
| **121** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - |

**Légende** :
- ✅ Compatible
- ❌ Incompatible
- - (diagonale) = même caractéristique

---

## 🎯 Tests de Validation

### Checklist pour Chaque Produit

1. ✅ Vérifier qu'aucune paire incompatible n'est présente
2. ✅ Vérifier que le support est compatible avec toutes les CAR
3. ✅ Vérifier que les paramètres sont cohérents (pas de 0, pas de listes vides)
4. ✅ Vérifier que CAR_7 est toujours présente
5. ✅ Vérifier que le prix est dans une fourchette raisonnable
6. ✅ Vérifier que les zones sont contiguës (TCL)
7. ✅ Si BSC → 7_04 et 7_05 doivent être false

---

## 📝 Exemples de Détection

### Exemple 1 : Détection CAR_14 + CAR_74
**Input** : "Créer un produit avec CAR_14 et CAR_74"

**Output attendu** :
```
⚠️ **INCOMPATIBILITÉ DÉTECTÉE**

CAR_14 et CAR_74 ne peuvent pas coexister car elles définissent toutes deux les modes de transport.

✅ **Solution** : Utiliser uniquement CAR_14 (CAR_74 est obsolète)
```

---

### Exemple 2 : Détection BSC + Rechargement
**Input** : "Abonnement mensuel sur support BSC"

**Output attendu** :
```
⚠️ **INCOMPATIBILITÉ SUPPORT**

Un abonnement mensuel ne peut PAS être sur support BSC car :
- Les abonnements sont rechargeables
- Le BSC (billet) n'est pas rechargeable

✅ **Solutions** :
1. Utiliser support CSC (Carte Sans Contact) → Rechargeable
2. Utiliser support AB (Application) → Rechargeable
3. OU créer un "Pass mensuel" sur BSC → Non rechargeable (moins pratique)

❓ Quel support préférez-vous ?
```

---

### Exemple 3 : Détection CAR_22 + CAR_21
**Input** : "Carnet de 10 tickets mono et multi-usager"

**Output attendu** :
```
⚠️ **INCOMPATIBILITÉ DÉTECTÉE**

Un carnet ne peut pas être à la fois mono-usager (CAR_22) et multi-usager (CAR_21).

❓ **Question** : Le carnet est-il :
1. Pour UNE seule personne → CAR_22
2. Partageable entre plusieurs personnes → CAR_21

Merci de préciser.
```

---

## 🚀 Implémentation dans l'Assistant

### Priorité de Détection
1. **🔴 P1 - Incompatibilités CAR** : Détection immédiate, refus de génération
2. **🔴 P2 - Incompatibilités Support** : Détection immédiate, proposition alternatives
3. **🟡 P3 - Incohérences Paramètres** : Alerte, correction suggérée
4. **🟢 P4 - Règles Métier TCL** : Warning, validation demandée

### Format de Réponse Standard
```
⚠️ **INCOMPATIBILITÉ DÉTECTÉE**

[Description du problème]

❌ **Conflit** : [Explication technique]

✅ **Solution(s)** :
1. [Option 1]
2. [Option 2]

❓ **Question** : [Demande de clarification si nécessaire]
```

---

**Dernière mise à jour** : 2025-01-16
**Version** : 1.0
**Status** : ✅ COMPLET - Production Ready
