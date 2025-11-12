# 📂 Dataset pour Fine-tuning - Format et Instructions

Ce dossier contient les datasets d'entraînement pour le modèle de produits de transport.

## 📋 Format attendu

Le notebook `transport_finetuning_ULTRA_2.ipynb` charge **automatiquement tous les fichiers** JSON et JSONL de ce dossier.

### Format JSON (fichiers .json)

```json
[
  {
    "instruction": "Votre question ou demande ici",
    "response": "La réponse formatée avec emojis et structure",
    "metadata": {
      "type": "creation|error_detection|explication|comparison|etc.",
      "topic": "produit_transport|incompatibilite|caracteristique|etc.",
      "expected_action": "create_product|ask_correction|none|etc.",
      "turns": 1,
      "cars": [7, 14, 22]
    }
  },
  {
    "instruction": "Autre exemple...",
    "response": "Autre réponse...",
    "metadata": {...}
  }
]
```

### Format JSONL (fichiers .jsonl)

Un objet JSON par ligne :

```jsonl
{"instruction":"Question 1","response":"Réponse 1","metadata":{...}}
{"instruction":"Question 2","response":"Réponse 2","metadata":{...}}
{"instruction":"Question 3","response":"Réponse 3","metadata":{...}}
```

## 🎯 Structure de la réponse

Toutes les réponses doivent suivre ce format structuré :

```
🧠 Raisonnement : [Explication du contexte et de l'analyse]

➡️ Plan/Réponse : [La solution ou l'information demandée]

✅ Confirmation : [Question de validation si nécessaire]
```

### Exemples par type :

#### 1. Création de produit (type: "creation")

```json
{
  "instruction": "Je veux un abonnement mensuel métro à 50€.",
  "response": "🧠 Raisonnement : Abonnement mensuel simple avec mode métro.\n\n➡️ Plan de création :\n```json\n{\n  \"nom\": \"Abonnement Mensuel Métro\",\n  \"famille\": \"Abonnement\",\n  \"caracteristiques\": [7, 14],\n  \"parametres\": {...}\n}\n```\n\n✅ Confirmez-vous cette création ?",
  "metadata": {
    "type": "creation",
    "topic": "produit_transport",
    "expected_action": "create_product",
    "turns": 1,
    "cars": [7, 14]
  }
}
```

#### 2. Détection d'erreur (type: "error_detection")

```json
{
  "instruction": "Produit CAR_14 (modes liste) ET CAR_74 (mode codé) bus.",
  "response": "🧠 Raisonnement : Incompatibilité classique détectée.\n\n⚠️ **ERREUR : INCOMPATIBILITÉ CAR_14 ⊗ CAR_74**\n\n❌ Impossible de combiner les deux systèmes\n\n💡 **Solution** : Choisir UNE approche\n\nQuelle option choisissez-vous?",
  "metadata": {
    "type": "error_detection",
    "topic": "incompatibilite",
    "incompatibility": ["CAR_14", "CAR_74"],
    "expected_action": "ask_choice",
    "turns": 1
  }
}
```

#### 3. Explication (type: "explication")

```json
{
  "instruction": "Qu'est-ce que CAR_7?",
  "response": "🧠 Raisonnement : CAR_7 définit la période de validité.\n\n➡️ Réponse : CAR_7 - Période de validité - définit quand le produit est valide.\n\n📋 Paramètres :\n- nature_validite : type de validité\n- unite_duree : heures/jours/mois\n- duree : nombre d'unités",
  "metadata": {
    "type": "explication",
    "topic": "caracteristique",
    "caracteristique_id": 7,
    "expected_action": "none",
    "turns": 1
  }
}
```

## 📊 Types de metadata

### type
- `creation` : Création de produit
- `error_detection` : Détection d'erreur/incompatibilité
- `explication` : Explication de concept
- `comparison` : Comparaison de produits
- `update` : Mise à jour de produit
- `delete` : Suppression de produit
- `advanced_reasoning` : Raisonnement complexe

### topic
- `produit_transport` : Produit général
- `incompatibilite` : Incompatibilité de caractéristiques
- `caracteristique` : Explication de CAR_X
- `valeur_invalide` : Validation de paramètres
- `comparaison_produits` : Comparaison
- `edge_case` : Cas limite

### expected_action
- `create_product` : Créer un produit
- `ask_correction` : Demander correction
- `ask_choice` : Demander un choix
- `none` : Pas d'action
- `display_analysis` : Afficher analyse

### cars (optionnel)
Liste des numéros de caractéristiques impliquées : `[7, 14, 22]`

## 🔄 Multi-turn conversations

Pour des conversations multi-tours, utilisez `"turns": 2` ou plus et incluez le contexte dans l'instruction :

```json
{
  "instruction": "Option B, je veux limiter les correspondances. 10 voyages, max 3 correspondances, Bus+Métro, CSC, 18€.",
  "response": "🧠 Raisonnement : L'utilisateur choisit option B (mono-usager + limitation)...",
  "metadata": {
    "type": "creation",
    "topic": "produit_transport",
    "expected_action": "create_product",
    "turns": 2,
    "cars": [22, 6, 14],
    "resolved_incompatibility": true
  }
}
```

## 📁 Organisation recommandée

Vous pouvez organiser vos fichiers par thème :

```
dataset/
├── README.md                           (ce fichier)
├── produits_base.json                  (créations simples)
├── incompatibilites.json              (détection d'erreurs)
├── explications_cars.json             (explications CAR_X)
├── cas_avances.json                   (raisonnement complexe)
├── multi_turn.jsonl                   (conversations)
└── edge_cases.jsonl                   (cas limites)
```

## ✅ Bonnes pratiques

1. **Utilisez des emojis** pour la lisibilité : 🧠 ➡️ ✅ ⚠️ ❌ 💡 📋 📊
2. **Structurez toujours** avec Raisonnement → Plan/Réponse → Confirmation
3. **Incluez le JSON** pour les créations de produits
4. **Signalez clairement** les incompatibilités avec ⚠️ et ❌
5. **Ajoutez des metadata** complètes pour l'analyse
6. **Variez les exemples** : simples, complexes, erreurs, cas limites

## 🚀 Utilisation

Le notebook charge automatiquement tous les fichiers :

```python
training_data = load_all_datasets("dataset")
# → Charge tous les .json et .jsonl du dossier
```

Les statistiques sont affichées automatiquement :
- Nombre d'exemples par fichier
- Distribution des types
- Topics couverts
- Exemple d'entrée

---

**💡 Astuce** : Commencez avec des exemples simples, puis ajoutez progressivement des cas plus complexes pour améliorer le modèle.
