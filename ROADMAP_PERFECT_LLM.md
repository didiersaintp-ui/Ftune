# 🎯 Roadmap pour un LLM Fine-tuné Parfait

## 📊 État actuel vs Objectif

| Critère | Actuel | Objectif Parfait |
|---------|--------|------------------|
| Exemples dataset | ~10 | 1000 |
| CAR couvertes | 16/29 (55%) | 29/29 (100%) |
| Natures validité | 3/8 (37%) | 8/8 (100%) |
| Modes transport | 3/7 (43%) | 7/7 (100%) |
| Taux réussite | 60-70% | 95-98% |
| Steps entraînement | 800 | 1500-2000 |

---

## 🎯 PHASE 1 : Quick Win (1-2 jours) - **PRIORITAIRE**

### Objectif : Passer de 55% à 80% de couverture

### Actions immédiates :

#### A. Ajouter 50 exemples pour les 13 CAR manquantes

**Caractéristiques critiques à couvrir** :

1. **CAR_3 - Lignes autorisées/interdites** (5 exemples)
```json
{
  "instruction": "Abonnement mensuel valable uniquement sur ligne 1 et 2.",
  "response": "🧠 Raisonnement : Abonnement avec restriction par lignes spécifiques...",
  "metadata": {"cars": [7, 3]}
}
```

2. **CAR_10 - Limitation par sous-période** (5 exemples)
```json
{
  "instruction": "Forfait mensuel limité à 2 déplacements par semaine.",
  "response": "🧠 Raisonnement : Limitation hebdomadaire avec CAR_10...",
  "metadata": {"cars": [7, 10]}
}
```

3. **CAR_102 - Tacite reconduction** (10 exemples - IMPORTANT)
```json
{
  "instruction": "Créer un abonnement mensuel à tacite reconduction avec prélèvement automatique.",
  "response": "🧠 Raisonnement : Abonnement TRDI (tacite reconduction durée illimitée)...",
  "metadata": {"cars": [7, 102], "type": "creation", "topic": "abonnement_tacite"}
}
```

4. **CAR_87 - Lignes déterminées à la vente** (5 exemples)

5. **CAR_38 - Groupe saisie à la vente** (5 exemples)

6. **CAR_105 - Multi-validation** (5 exemples)

7. **CAR_97 - Remboursement** (3 exemples)

8. **CAR_23 - Fidélité** (3 exemples)

9. **CAR_8, CAR_11, CAR_107, CAR_73, CAR_91** (2 exemples chacun)

#### B. Ajouter 30 exemples de cas edge

**Durées variées** :
```json
- "Abonnement 24 mois tous modes"
- "Pass 72 heures touriste"
- "Forfait hebdomadaire (7 jours)"
- "Abonnement semestriel (6 mois)"
- "Pass 30 minutes bus centre-ville"
```

**Modes variés** :
```json
- "Forfait Train+Bus interurbain"
- "Pass Parking+Vélo mensuel"
- "Ticket unitaire tous modes sauf parking"
```

**Prix variés** :
```json
- "Ticket social 0.50€"
- "Abonnement premium 250€"
- "Carnet étudiant 12€"
```

#### C. Ajouter 20 exemples d'incompatibilités

```json
- CAR_22 ⊗ CAR_21 (mono vs multi usager)
- CAR_2 ⊗ CAR_38 (passagers fixe vs variable)
- CAR_3 ⊗ CAR_87 (lignes paramétrées vs vente)
- CAR_4 ⊗ CAR_121 (zones paramétrées vs vente)
- Support BSC incompatible avec CAR_10, CAR_102, etc.
```

#### D. Augmenter les steps à 1200

```python
MAX_STEPS = 1200  # Au lieu de 800
```

### Résultat attendu Phase 1 :
- **Exemples** : 110 (10 → 110)
- **Couverture CAR** : 80% (23/29)
- **Taux réussite** : 75-80%

---

## 🚀 PHASE 2 : Production Ready (1 semaine)

### Objectif : Passer à 90% couverture, dataset robuste

### A. Dataset structuré de 300 exemples

**Répartition recommandée** :

| Catégorie | Nombre | Exemples |
|-----------|--------|----------|
| **Créations simples** (1-2 CAR) | 80 | "Ticket 1h bus", "Abonnement mensuel" |
| **Créations moyennes** (3-4 CAR) | 60 | "Carnet 10 voyages bus+métro zones 1-2" |
| **Créations complexes** (5+ CAR) | 40 | "Abonnement OD avec limitation horaire" |
| **Détections d'erreurs** | 40 | Incompatibilités, paramètres invalides |
| **Explications** | 40 | 1-2 exemples par CAR (29 CAR) |
| **Comparaisons** | 15 | Produit A vs B |
| **Recommandations** | 15 | Profil usager → produit adapté |
| **Multi-turn** | 10 | Conversations 2-3 tours |

### B. Générateur de données synthétiques

Créer un script Python qui génère automatiquement des variations :

```python
# dataset_generator.py

TEMPLATES = {
    "abonnement_simple": {
        "pattern": "Je veux un abonnement {durée} {mode} à {prix}€.",
        "variations": {
            "durée": ["mensuel", "annuel", "hebdomadaire", "semestriel"],
            "mode": ["métro", "bus", "tous modes", "bus+métro"],
            "prix": [30, 50, 75, 100]
        },
        "cars": [7, 14],
        "response_template": "..."
    },
    "carnet_tickets": {
        "pattern": "Carnet de {nombre} tickets {mode} valable {durée}.",
        "variations": {
            "nombre": [5, 10, 20, 30],
            "mode": ["bus", "métro", "tramway", "tous modes"],
            "durée": ["1 mois", "3 mois", "6 mois"]
        },
        "cars": [7, 22, 14]
    }
    # ... 15-20 templates
}

def generate_synthetic_examples(count=200):
    """Génère des exemples synthétiques variés"""
    pass
```

### C. Tests automatisés

```python
# tests/test_model_coverage.py

def test_all_cars_covered():
    """Vérifie que les 29 CAR sont testées"""
    for car_id in range(1, 30):
        if car_id in EXISTING_CARS:
            assert test_car(car_id) == True

def test_all_validity_natures():
    """Teste les 8 natures de validité"""
    for nature in [0, 2, 4, 6, 8, 14, 20, 21]:
        assert test_nature(nature) == True

def test_incompatibilities():
    """Teste toutes les incompatibilités documentées"""
    assert test_incompatibility("CAR_14", "CAR_74") == "error_detected"
    assert test_incompatibility("CAR_6", "CAR_21") == "error_detected"
    assert test_incompatibility("CAR_22", "CAR_21") == "error_detected"
```

### D. Configuration entraînement optimisée

```python
# Pour 300 exemples
MAX_STEPS = 1500
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 4
LEARNING_RATE = 2e-4
WARMUP_STEPS = 75

# Epochs estimés : ~40
```

### Résultat attendu Phase 2 :
- **Exemples** : 300
- **Couverture CAR** : 90% (26/29)
- **Taux réussite** : 85-90%
- **Tests automatisés** : Coverage complet

---

## 🏆 PHASE 3 : Excellence (2-3 semaines)

### Objectif : LLM parfait, 95%+ de réussite

### A. Dataset massif de 1000 exemples

**Composition** :

1. **Base manuelle** : 300 exemples (Phase 2)
2. **Synthétique** : 500 exemples générés
3. **Cas réels métier** : 100 exemples de vrais produits TCL, RATP, etc.
4. **Edge cases** : 100 exemples limites

### B. Toutes les natures de validité (8)

**Créer 10 exemples pour chaque nature** :

```json
// Nature 0 : Dates fixes
{
  "instruction": "Billet pour concert le 15 juin 2025, valable de 18h à minuit.",
  "response": "🧠 Raisonnement : DDV et DEV à dates fixes (nature 0)...",
  "metadata": {"cars": [7], "nature_validite": 0}
}

// Nature 6 : Modifiables à la vente
{
  "instruction": "Forfait dont l'acheteur peut choisir les dates de début et fin.",
  "response": "🧠 Raisonnement : Nature 6 avec modification à la vente...",
  "metadata": {"cars": [7], "nature_validite": 6}
}

// Nature 8 : DEV glissante avec DDV saisie
{
  "instruction": "Pass 7 jours démarrant le 20 mai.",
  "response": "🧠 Raisonnement : DDV saisie, DEV = DDV + 7 jours (nature 8)...",
  "metadata": {"cars": [7], "nature_validite": 8}
}
```

### C. Tous les modes de transport

**Exemples avec chaque mode** :
- Bus interurbain : "Forfait cars régionaux mensuel"
- Train : "Abonnement TER domicile-travail"
- Parking : "Abonnement parking P+R"
- Vélo : "Pass VLS annuel"
- Combinaisons : "Pass intermodal Train+Bus+Vélo"

### D. Produits complexes réels

**Exemples inspirés de vraies offres** :

```json
{
  "instruction": "Créer le « Forfait Liberté » TCL : abonnement mensuel tacite reconduction, zones 1-2-3, tous modes sauf train, avec 3 mois offerts pour 12 mois payés.",
  "response": "🧠 Raisonnement : Produit complexe multi-caractéristiques...",
  "metadata": {
    "type": "creation",
    "topic": "produit_reel_complexe",
    "cars": [7, 102, 107, 4, 14],
    "complexity": "very_high"
  }
}

{
  "instruction": "Pass Navigo annuel zones 1-5 avec option parking.",
  "response": "...",
  "metadata": {"cars": [7, 4, 8], "real_product": "Navigo"}
}

{
  "instruction": "Abonnement domicile-travail avec OD La Défense-Châtelet, 5j/7, heures de pointe uniquement.",
  "response": "...",
  "metadata": {"cars": [7, 86, 9], "real_product": "domicile_travail"}
}
```

### E. Active Learning

```python
# Entraîner → Tester → Identifier erreurs → Ajouter exemples ciblés

def active_learning_loop(iterations=5):
    for i in range(iterations):
        # 1. Entraîner le modèle
        train_model()

        # 2. Tester sur test set
        errors = test_model()

        # 3. Analyser les erreurs
        error_patterns = analyze_errors(errors)

        # 4. Générer exemples ciblés
        new_examples = generate_targeted_examples(error_patterns)

        # 5. Ajouter au dataset
        dataset.extend(new_examples)

        print(f"Iteration {i+1}: Added {len(new_examples)} examples")
```

### F. Reward Model

Entraîner un modèle de validation qui vérifie :
- Conformité au schéma JSON
- Respect des incompatibilités
- Cohérence des paramètres
- Format de réponse (🧠 ➡️ ✅)

```python
def reward_model(generated_output, expected_output):
    score = 0.0

    # Validité JSON
    score += 0.3 * validate_json_schema(generated_output)

    # Incompatibilités
    score += 0.2 * check_incompatibilities(generated_output)

    # Caractéristiques correctes
    score += 0.3 * compare_cars(generated_output, expected_output)

    # Format réponse
    score += 0.2 * validate_response_format(generated_output)

    return score
```

### G. Configuration finale

```python
# Pour 1000 exemples
MAX_STEPS = 2000
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 4
LEARNING_RATE = 2e-4
WARMUP_STEPS = 100
WEIGHT_DECAY = 0.01
LR_SCHEDULER = "cosine"

# Epochs estimés : ~16
```

### Résultat attendu Phase 3 :
- **Exemples** : 1000
- **Couverture CAR** : 100% (29/29)
- **Taux réussite** : 95-98%
- **Production ready** : OUI

---

## 📈 MÉTRIQUES DE SUCCÈS

### Tests obligatoires :

1. **Coverage Test** : 29/29 CAR avec ≥3 exemples chacune ✅
2. **Accuracy Test** : ≥95% sur test set de 100 exemples ✅
3. **Incompatibility Test** : 100% détection des incompatibilités documentées ✅
4. **Edge Case Test** : ≥90% sur 50 cas limites ✅
5. **Multi-turn Test** : ≥85% sur conversations ✅
6. **Real Product Test** : ≥90% sur 20 produits réels ✅

---

## 🛠️ OUTILS À CRÉER

### 1. Générateur de datasets
```bash
python tools/generate_synthetic_dataset.py --count 500 --output dataset/synthetic.json
```

### 2. Validateur de datasets
```bash
python tools/validate_dataset.py --input dataset/*.json --check-coverage
```

### 3. Testeur automatique
```bash
python tools/test_model.py --model qwen3b_transport_ultra_2_gguf --tests all
```

### 4. Analyseur d'erreurs
```bash
python tools/analyze_errors.py --test-results results.json --generate-examples
```

---

## 📅 TIMELINE

| Phase | Durée | Effort | Résultat |
|-------|-------|--------|----------|
| Phase 1 | 1-2 jours | 6h | 80% couverture, 75% précision |
| Phase 2 | 1 semaine | 20h | 90% couverture, 85% précision |
| Phase 3 | 2-3 semaines | 60h | 100% couverture, 95% précision |

---

## 🎯 PRIORITÉS IMMÉDIATES

**À faire MAINTENANT** :

1. ✅ Créer 10 exemples pour CAR_102 (tacite reconduction) - CRITIQUE
2. ✅ Créer 10 exemples pour CAR_10 (limitation sous-période)
3. ✅ Créer 10 exemples pour CAR_3 (lignes)
4. ✅ Ajouter 20 cas edge (durées variées, modes variés)
5. ✅ Augmenter MAX_STEPS à 1200

**Cette semaine** :

1. Script générateur de données synthétiques
2. Dataset de 150 exemples (110 actuels + 40 synthétiques)
3. Tests automatisés de base
4. Nouvel entraînement avec 1200 steps

**Ce mois-ci** :

1. Dataset de 300 exemples
2. Suite complète de tests
3. Active learning (1 itération)
4. Documentation complète

---

## 💡 NOTES IMPORTANTES

### Risques actuels :
1. **Overfitting** : Avec 10 exemples, le modèle mémorise sans généraliser
2. **Biais** : Surreprésentation CAR_7, CAR_14, CAR_22
3. **Hallucinations** : Va inventer des CAR non documentées
4. **Incompatibilités manquées** : Seulement 2 incompatibilités couvertes

### Pourquoi 1000 exemples ?
- **LLMs ont besoin de volume** : Fine-tuning = montrer des patterns
- **29 CAR × 10 exemples** = 290 minimum
- **8 natures × 10 exemples** = 80
- **Combinaisons** : 29×28/2 = 406 paires possibles
- **Edge cases, multi-turn, etc.** : +200
- **Total théorique** : ~1000 exemples pour couverture complète

### Pourquoi 2000 steps ?
- **Rule of thumb** : 2-3 epochs sur tout le dataset
- **1000 exemples, batch 8** : 125 steps/epoch
- **16 epochs** : 2000 steps
- **Équilibre** : Ni underfit, ni overfit

---

## 🎓 RESSOURCES

### Templates à utiliser :
- `/dataset/README.md` : Format et structure
- `/dataset/exemples_base.json` : 8 exemples de référence

### Documentation de référence :
- `/Modelisation produit de transport.pdf` : Source de vérité
- Pages 1-21 : Toutes les 29 caractéristiques

### Outils existants :
- `transport_finetuning_ULTRA_2.ipynb` : Notebook prêt
- Fonction de chargement dynamique des datasets

---

**🚀 Commence par la Phase 1 (Quick Win) pour voir une amélioration immédiate !**
