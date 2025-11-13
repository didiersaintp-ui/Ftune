# 🔍 Analyse des Problèmes d'Entraînement - Assistant Billettique

**Date**: 2025-01-12
**Auteur**: Claude Code
**Objectif**: Identifier et résoudre les problèmes critiques de l'assistant billettique

---

## 🚨 Problèmes Identifiés

### 1. **Connaissance Inexacte des Concepts**

#### Erreurs observées dans les tests Ollama :
```
>>> qu'est ce que la caractéristique 7 ?
Réponse: "Multi-déplacements" ❌
```

**Réalité** : CAR_7 = "DDV et DEV contrat" (période de validité)

#### Invention de caractéristiques :
- **CAR_48** n'existe pas ❌ (confusion avec CAR_48 = "Produit à post-paiement")
- **CAR_107** existe mais mal utilisé ✓ (= "X mois gratuits pour Y mois payés")

**Cause racine** :
- Le dataset ne contient PAS les définitions exactes des caractéristiques
- Le system prompt contient des règles mais pas les définitions du PDF
- Le modèle "invente" basé sur des patterns vus à l'entraînement

---

### 2. **JSON Mal Formés**

#### Erreurs de syntaxe :
```json
{
  "nom": "Abonnement Mensuel Métro",
  19: 50.00,  ❌ Clé non quotée
  "caracteristiques": [...]
}
```

#### Schéma incohérent :
- Parfois `"cars": [...]`
- Parfois `"caracteristiques": [...]`
- Parfois `"characteristics": [...]`

**Cause racine** :
- Le dataset d'entraînement utilise uniquement `"characteristics"` en anglais
- Le modèle n'a pas appris qu'il faut TOUJOURS respecter cette structure

---

### 3. **Absence de Capacité Conversationnelle**

#### Ce qui manque :
1. **Poser des questions** quand des paramètres manquent
2. **Détecter les incompatibilités** (ex: CAR_14 vs CAR_74)
3. **Clarifier les ambiguïtés** ("abonnement mensuel" = rechargeable ou non?)
4. **Guider l'utilisateur** dans la création du produit

#### Exemple attendu mais absent :
```
User: Je veux un abonnement mensuel pour le métro
Assistant:
🧠 Raisonnement: Un abonnement mensuel nécessite:
   - CAR_7 pour la validité (1 mois)
   - CAR_14 pour le mode (métro)

❓ Questions avant de générer:
   1. Prix du produit ?
   2. Rechargeable automatiquement ?
   3. Sur quel support ? (CSC ou BSC)
   4. Profil tarifaire ? (Plein tarif, étudiant, senior...)

➡️ Pouvez-vous préciser ces éléments ?
```

**Ce que fait le modèle actuel** : Génère directement du JSON sans poser de questions ❌

---

### 4. **Pas de Détection d'Incompatibilités**

#### Incompatibilités non détectées :
- **CAR_14** (liste de modes) + **CAR_74** (mode codé) = INCOMPATIBLE ⚠️
- **CAR_22** (mono-usager) + **CAR_21** (multi-usager) = INCOMPATIBLE ⚠️
- **CAR_3** (lignes par paramétrage) + **CAR_87** (lignes codées vente) = INCOMPATIBLE ⚠️

**Test échoué** :
```
>>> Produit CAR_14 (modes liste) ET CAR_74 (mode codé) bus.
Réponse: Génère un JSON avec les deux ❌
Attendu: ⚠️ INCOMPATIBILITÉ détectée : CAR_14 et CAR_74 ne peuvent pas coexister
```

---

### 5. **Manque de Raisonnement Adaptatif**

#### Problème : Le modèle ne "comprend" pas la logique métier

**Exemple 1 - Ticket 1h à 32,10€** :
```json
{
  "id": "4",  ❌ Pas dans le schéma
  "prix_centimes": 3210,  ✓
  "support": ["BSC"],  ✓
  "validite": {
    "nature": "glissante_validation",  ❌ Doit être un code (4)
    "duree": 60,  ❌ En heures pas minutes
    "unit": "heures"  ❌ Doit être "H"
  }
}
```

**Ce qu'il aurait dû générer** :
```json
{
  "product_name": "Ticket 1h",
  "price_cents": 3210,
  "support": ["BSC"],
  "characteristics": [
    {
      "number": 7,
      "parameters": {
        "7_01": 4,
        "7_02": "H",
        "7_03": 1,
        "7_04": false,
        "7_05": false
      }
    }
  ]
}
```

---

## 📊 Analyse du Dataset Actuel

### Forces ✅
1. **Structure JSON correcte** pour la génération basique
2. **Exemples variés** (abonnements, carnets, pass, tickets)
3. **System prompt détaillé** avec règles claires

### Faiblesses ❌
1. **Aucun exemple conversationnel** avec questions/réponses
2. **Pas de définitions des concepts** (DDV, DEV, TRDI, TRDD, etc.)
3. **Pas d'exemples d'incompatibilités** détectées
4. **Pas de structure de raisonnement** (🧠 Raisonnement → ❓ Questions → ✅ JSON)
5. **Vocabulaire incomplet** (termes métier non définis)

---

## 🎯 Objectifs d'Amélioration

### Objectif Principal
**Transformer le modèle d'un "générateur de JSON" en un "assistant conversationnel expert"**

### Objectifs Spécifiques
1. ✅ **Maîtrise des concepts** : Connaître exactement chaque caractéristique
2. ✅ **JSON parfaits** : Syntaxe et schéma toujours corrects
3. ✅ **Conversation fluide** : Poser les bonnes questions
4. ✅ **Détection d'erreurs** : Identifier les incompatibilités
5. ✅ **Raisonnement métier** : Comprendre la logique billettique

---

## 💡 Solutions Proposées

### Solution 1 : **Dataset Enrichi avec Définitions**

#### Catégorie A : Définitions des Caractéristiques (150+ exemples)
```json
{
  "instruction": "Qu'est-ce que la caractéristique 7 ?",
  "response": "🧠 Définition:\n\nLa **caractéristique 7** (DDV et DEV contrat) permet de définir la période de validité d'un produit.\n\n📋 Paramètres:\n- **7_01**: Nature de validité (0, 2, 4, 6, 8, 14, 20, 21)\n- **7_02**: Unité de durée (D=Jour, W=Semaine, M=Mois, H=Heure)\n- **7_03**: Durée de validité (integer)\n- **7_04**: Rechargement par prorogation (true/false)\n- **7_05**: Autorisation de rechargement (true/false)\n\n💡 Exemples:\n- Abonnement mensuel: 7_01=2, 7_02=\"M\", 7_03=1\n- Pass 24h: 7_01=4, 7_02=\"H\", 7_03=24",
  "metadata": {
    "type": "definition",
    "topic": "caracteristiques",
    "car_number": 7
  }
}
```

#### Catégorie B : Exemples Conversationnels (100+ exemples)
```json
{
  "instruction": "Je veux un abonnement mensuel pour le métro",
  "response": "🧠 Raisonnement:\n\nPour un abonnement mensuel métro, j'ai besoin de:\n- CAR_7: Validité 1 mois (7_01=2, 7_02=\"M\", 7_03=1)\n- CAR_14: Mode métro autorisé\n- Prix et support manquants\n\n❓ Questions:\n\n1. **Prix** : Quel est le tarif mensuel ?\n2. **Support** : Sur quel support ? (CSC ou BSC)\n3. **Rechargement** : Tacite reconduction automatique ?\n4. **Profil** : Plein tarif ou tarif réduit (étudiant, senior) ?\n\n➡️ Une fois ces informations fournies, je pourrai générer le JSON complet.\n\n✅ Confirmez-vous ces besoins ?",
  "metadata": {
    "type": "conversational",
    "topic": "missing_parameters"
  }
}
```

#### Catégorie C : Détection d'Incompatibilités (50+ exemples)
```json
{
  "instruction": "Créé un produit avec CAR_14 (modes liste) ET CAR_74 (mode codé)",
  "response": "⚠️ INCOMPATIBILITÉ DÉTECTÉE\n\n🔍 Analyse:\n\n**CAR_14** (Modes de transport autorisés ou interdits):\n- Définit une LISTE de modes au niveau du paramétrage\n- Support: BSC et AB\n\n**CAR_74** (Mode de transport autorisé par produit):\n- Définit UN SEUL mode codé sur le support\n- Support: AB uniquement\n\n❌ **Conflit**: Ces deux caractéristiques servent le même objectif mais de manière différente. Elles ne peuvent PAS coexister.\n\n✅ Solution:\n- Si vous voulez plusieurs modes: Utilisez **CAR_14** uniquement\n- Si vous voulez un mode unique codé sur le support: Utilisez **CAR_74** uniquement\n\nQuelle approche préférez-vous ?",
  "metadata": {
    "type": "incompatibility",
    "topic": "car_14_vs_car_74",
    "incompatible_cars": [14, 74]
  }
}
```

#### Catégorie D : Concepts Métier (80+ exemples)
```json
{
  "instruction": "C'est quoi un TRDI ?",
  "response": "📖 Définition:\n\n**TRDI** = Tacite Reconduction à Durée Illimitée\n\n🔍 Caractéristiques:\n- Abonnement qui se renouvelle automatiquement\n- Durée indéterminée (tant que l'usager ne résilie pas)\n- Prélèvement automatique mensuel/annuel\n- Nécessite CAR_102 avec 102_04=true\n\n💡 Exemple:\n\"Abonnement mensuel avec prélèvement automatique, résiliable à tout moment\"\n\n📋 Structure JSON:\n```json\n{\n  \"characteristics\": [\n    {\n      \"number\": 7,\n      \"parameters\": {\"7_01\": 2, \"7_02\": \"M\", \"7_03\": 1, ...}\n    },\n    {\n      \"number\": 102,\n      \"parameters\": {\"102_01\": \"Aucun\", \"102_04\": true}\n    }\n  ]\n}\n```\n\n🔗 Voir aussi: TRDD (Tacite Reconduction à Durée Déterminée)",
  "metadata": {
    "type": "concept",
    "topic": "trdi"
  }
}
```

---

### Solution 2 : **System Prompt Amélioré avec Structure Stricte**

#### Nouveau Format de Réponse Obligatoire
```markdown
## Structure de Réponse OBLIGATOIRE

Toutes vos réponses doivent suivre cette structure:

### 1. 🧠 Raisonnement
Analysez la demande et identifiez:
- Les caractéristiques nécessaires
- Les paramètres manquants
- Les éventuelles ambiguïtés

### 2. ❓ Questions (si besoin)
Si des informations manquent, posez des questions précises.

### 3. ➡️ Réponse / JSON
Fournissez le JSON demandé OU des recommandations.

### 4. ✅ Confirmation
Demandez validation à l'utilisateur.

### Exemple:
```
🧠 Raisonnement:
Pour un abonnement mensuel, je détecte:
- CAR_7 nécessaire (validité 1 mois)
- Prix non spécifié
- Support non spécifié

❓ Questions:
1. Prix mensuel ?
2. Support (CSC ou BSC) ?
3. Rechargement automatique ?

➡️ En attente de vos précisions pour générer le JSON.

✅ Confirmez-vous ces besoins ?
```
```

---

### Solution 3 : **Techniques d'Entraînement Avancées**

#### 1. **DPO (Direct Preference Optimization)**

**Principe** : Apprendre à préférer les bonnes réponses aux mauvaises

**Exemples de paires** :
```json
{
  "prompt": "Créé un ticket métro 2h à 2,50€",
  "chosen": {
    "response": "🧠 Raisonnement: [...]\n➡️ JSON: {...correct...}"
  },
  "rejected": {
    "response": "{\n  19: 250,  // ❌ Syntaxe invalide\n  ...\n}"
  }
}
```

**Avantages** :
- Améliore la qualité des réponses
- Réduit les hallucinations
- Renforce les patterns corrects

#### 2. **RLHF (Reinforcement Learning from Human Feedback)**

**Principe** : Récompenser les bonnes réponses, pénaliser les mauvaises

**Reward Function** :
```python
def reward_function(output):
    score = 0

    # +10 : JSON syntaxiquement correct
    if is_valid_json(output):
        score += 10

    # +20 : Contient raisonnement (🧠)
    if "🧠" in output:
        score += 20

    # +15 : Pose des questions si paramètres manquants
    if has_missing_params(input) and "❓" in output:
        score += 15

    # +25 : Utilise les bonnes caractéristiques
    if correct_characteristics(output):
        score += 25

    # -50 : Invente des caractéristiques
    if invents_characteristics(output):
        score -= 50

    # +10 : Demande confirmation
    if "✅" in output:
        score += 10

    return score
```

#### 3. **Few-Shot Learning avec Exemples de Haute Qualité**

**Principe** : Inclure 3-5 exemples parfaits dans le prompt

**Exemple de prompt amélioré** :
```markdown
Tu es un assistant expert en billettique. Voici des exemples:

### Exemple 1 : Réponse avec questions
User: Abonnement mensuel métro
Assistant:
🧠 Pour un abonnement mensuel, j'ai besoin de:
   - CAR_7: Validité 1 mois
   - CAR_14: Mode métro

❓ Questions:
1. Prix ?
2. Support (CSC/BSC) ?
3. Rechargement auto ?

✅ Confirmez ?

### Exemple 2 : Détection d'incompatibilité
User: Produit CAR_14 et CAR_74
Assistant:
⚠️ INCOMPATIBILITÉ: CAR_14 (liste modes) et CAR_74 (mode codé)
   ne peuvent pas coexister.

➡️ Choisissez une seule approche.

### Exemple 3 : JSON complet
User: Ticket 1h métro à 2€ sur CSC
Assistant:
🧠 Ticket unitaire 1h:
   - CAR_7: Nature 4 (validation), 1 heure
   - CAR_14: Métro uniquement
   - CAR_22: 1 voyage

➡️ JSON:
```json
{
  "product_name": "Ticket 1h Métro",
  "price_cents": 200,
  "support": ["CSC"],
  "characteristics": [...]
}
```

✅ Validez-vous ?
```

#### 4. **Chain-of-Thought Prompting**

**Principe** : Forcer le modèle à "réfléchir à voix haute"

**Prompt COT** :
```markdown
Avant de répondre, tu DOIS:

1. **Analyser** la demande pas à pas
2. **Identifier** les caractéristiques nécessaires
3. **Vérifier** les compatibilités
4. **Lister** les informations manquantes
5. **Générer** la réponse structurée

❌ NE JAMAIS sauter directement à la réponse
✅ TOUJOURS montrer ton raisonnement
```

---

### Solution 4 : **Hyperparamètres d'Entraînement Optimisés**

#### Configuration Recommandée

```python
# Dataset
TOTAL_EXAMPLES = 6000  # ⬆️ Augmenté de 4090 à 6000
- Définitions: 800 exemples
- Conversations: 1500 exemples
- Incompatibilités: 500 exemples
- Concepts: 500 exemples
- JSON complets: 2700 exemples

# LoRA
LORA_RANK = 64  # ⬆️ Augmenté de 32 à 64 (capacité max)
LORA_ALPHA = 64
LORA_DROPOUT = 0.05  # ⬆️ Ajouté pour réduction overfitting

# Training
MAX_STEPS = 1500  # ⬆️ Augmenté de 766 à 1500
LEARNING_RATE = 1e-4  # ⬇️ Réduit de 2e-4 à 1e-4 (plus stable)
WARMUP_STEPS = 150  # 10% des steps
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 8  # Effective batch = 16

# Epochs
ESTIMATED_EPOCHS = (1500 * 16) / 6000 = 4 epochs

# Regularization
WEIGHT_DECAY = 0.01
LR_SCHEDULER = "cosine_with_restarts"  # Meilleure convergence
```

#### Justification des Changements

1. **LoRA Rank 64** : Capacité maximale pour apprendre des patterns complexes
2. **Dropout 0.05** : Prévention de l'overfitting sur les exemples répétitifs
3. **Learning Rate 1e-4** : Plus stable, moins de fluctuations
4. **1500 steps** : ~4 epochs pour bien intégrer les 6000 exemples
5. **Cosine with restarts** : Permet au modèle de "sortir" des minimums locaux

---

## 📈 Métriques d'Évaluation

### Métriques à Suivre

1. **Exactitude des Définitions** (Target: >95%)
   - % de bonnes réponses aux questions "Qu'est-ce que CAR_X ?"

2. **Qualité des JSON** (Target: >98%)
   - % de JSON syntaxiquement corrects
   - % de JSON avec schéma valide

3. **Détection d'Incompatibilités** (Target: >90%)
   - % d'incompatibilités détectées correctement

4. **Qualité Conversationnelle** (Target: >85%)
   - % de cas où le modèle pose des questions appropriées
   - % de cas où le modèle structure sa réponse correctement

5. **Hallucinations** (Target: <5%)
   - % de réponses avec caractéristiques inventées

---

## 🚀 Plan d'Action

### Phase 1 : Création du Dataset Enrichi (3-4h)
1. ✅ Générer 800 définitions de caractéristiques
2. ✅ Créer 1500 exemples conversationnels
3. ✅ Ajouter 500 exemples d'incompatibilités
4. ✅ Enrichir avec 500 concepts métier
5. ✅ Valider le dataset (format, diversité)

### Phase 2 : Amélioration du System Prompt (1h)
1. ✅ Ajouter structure obligatoire (🧠➡️✅)
2. ✅ Inclure définitions clés du PDF
3. ✅ Ajouter exemples few-shot
4. ✅ Forcer Chain-of-Thought

### Phase 3 : Entraînement Optimisé (2-3h sur T4)
1. ✅ Mettre à jour hyperparamètres
2. ✅ Lancer entraînement avec nouveau dataset
3. ✅ Monitorer métriques en temps réel
4. ✅ Ajuster si nécessaire

### Phase 4 : Validation et Tests (1h)
1. ✅ Tester sur cas d'usage réels
2. ✅ Vérifier détection d'incompatibilités
3. ✅ Valider capacité conversationnelle
4. ✅ Mesurer taux d'hallucination

### Phase 5 : Déploiement (30min)
1. ✅ Conversion GGUF Q4_K_M
2. ✅ Tests avec Ollama
3. ✅ Documentation utilisateur
4. ✅ Push sur repository

**Durée totale estimée** : 7-9 heures

---

## 📚 Références

### Documents Sources
- `Modelisation produit de transport.pdf` : Spécification complète
- `system_prompt.md` : Prompt actuel (à améliorer)
- `training_dataset.json` : Dataset actuel (4090 exemples)
- `examples.json` : Exemples de base

### Outils et Frameworks
- **Unsloth** : Fine-tuning optimisé
- **LoRA** : Efficient parameter adaptation
- **Qwen 2.5 3B** : Modèle de base
- **llama.cpp** : Conversion GGUF
- **Ollama** : Déploiement local

---

## ✅ Critères de Succès

Le projet sera considéré comme réussi si:

1. ✅ **Zéro hallucination** sur les caractéristiques (<2% acceptable)
2. ✅ **100% JSON valides** (syntaxe et schéma)
3. ✅ **90%+ détection d'incompatibilités**
4. ✅ **85%+ questions appropriées** quand infos manquantes
5. ✅ **Raisonnement structuré** dans 95%+ des réponses
6. ✅ **Conversations naturelles** avec guidage utilisateur

---

**Prochaine étape** : Commencer Phase 1 - Création du Dataset Enrichi
