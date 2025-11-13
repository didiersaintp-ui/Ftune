#!/usr/bin/env python3
"""
Générateur de Dataset Ultra-Réaliste pour Assistant Billettique
Basé sur les vrais produits TCL Lyon + Techniques avancées (DPO, RLHF)

Ce script génère un dataset de 6000+ exemples ultra-réalistes comprenant :
1. Tous les produits TCL Lyon réels (tarifs 2024)
2. Variations conversationnelles naturelles
3. Paires DPO (bonnes vs mauvaises réponses)
4. Exemples d'incompatibilités détectées
5. Questions de clarification intelligentes
6. Concepts métier complets
"""

import json
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

# ============================================================================
# PRODUITS TCL LYON RÉELS (Tarifs 2024)
# ============================================================================

TCL_PRODUCTS = {
    "tickets_unitaires": [
        {
            "nom": "Ticket Unité",
            "description": "Ticket 1h tous modes",
            "prix": 2.00,
            "duree": {"value": 1, "unit": "H"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 4,  # Glissante à validation
            "rechargeable": False,
            "voyages": 1,
            "support": ["BSC", "AB"],
            "caracteristiques": [7, 14, 22]
        },
        {
            "nom": "Ticket 2h",
            "description": "Ticket 2h tous modes avec correspondances",
            "prix": 3.00,
            "duree": {"value": 2, "unit": "H"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 4,
            "rechargeable": False,
            "voyages": None,  # Illimité pendant 2h
            "support": ["BSC", "AB"],
            "caracteristiques": [7, 14]
        },
        {
            "nom": "Ticket Soirée",
            "description": "Valable après 19h jusqu'à fin de service",
            "prix": 3.20,
            "duree": {"value": 5, "unit": "H"},
            "modes": ["Bus urbain", "Métro", "Tramway"],
            "nature_validite": 4,
            "rechargeable": False,
            "horaires": {"debut": "19:00", "fin": "23:59"},
            "support": ["BSC", "AB"],
            "caracteristiques": [7, 9, 14]
        }
    ],
    "carnets": [
        {
            "nom": "Carnet 10 voyages",
            "description": "10 tickets valables 1 mois",
            "prix": 17.70,
            "duree": {"value": 1, "unit": "M"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 2,  # Glissante au chargement
            "rechargeable": False,
            "voyages": 10,
            "support": ["AB"],
            "caracteristiques": [7, 14, 22]
        },
        {
            "nom": "Carnet 20 voyages",
            "description": "20 tickets valables 2 mois",
            "prix": 33.00,
            "duree": {"value": 2, "unit": "M"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 2,
            "rechargeable": False,
            "voyages": 20,
            "support": ["AB"],
            "caracteristiques": [7, 14, 22]
        }
    ],
    "abonnements": [
        {
            "nom": "Abonnement Mensuel Liberté",
            "description": "Abonnement 1 mois tous modes",
            "prix": 68.00,
            "duree": {"value": 1, "unit": "M"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 20,  # DDV début mois suivant
            "rechargeable": True,
            "voyages": None,  # Illimité
            "support": ["CSC", "AB"],
            "caracteristiques": [7, 14]
        },
        {
            "nom": "Abonnement Annuel Liberté",
            "description": "Abonnement 12 mois tous modes",
            "prix": 680.00,
            "duree": {"value": 12, "unit": "M"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 2,
            "rechargeable": True,
            "voyages": None,
            "support": ["CSC", "AB"],
            "caracteristiques": [7, 14]
        },
        {
            "nom": "Abonnement Mensuel Entreprise",
            "description": "Abonnement employeur 1 mois",
            "prix": 39.70,
            "duree": {"value": 1, "unit": "M"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 20,
            "rechargeable": True,
            "voyages": None,
            "support": ["CSC", "AB"],
            "caracteristiques": [7, 14],
            "profil": "Employeur"
        },
        {
            "nom": "Abonnement Jeune (-26 ans)",
            "description": "Abonnement mensuel tarif réduit jeunes",
            "prix": 34.00,
            "duree": {"value": 1, "unit": "M"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 20,
            "rechargeable": True,
            "voyages": None,
            "support": ["CSC", "AB"],
            "caracteristiques": [7, 14],
            "profil": "Jeune"
        },
        {
            "nom": "Abonnement Senior (+65 ans)",
            "description": "Abonnement mensuel tarif réduit seniors",
            "prix": 34.00,
            "duree": {"value": 1, "unit": "M"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 20,
            "rechargeable": True,
            "voyages": None,
            "support": ["CSC", "AB"],
            "caracteristiques": [7, 14],
            "profil": "Senior"
        }
    ],
    "pass_journee": [
        {
            "nom": "Pass 1 jour",
            "description": "Pass illimité 24h",
            "prix": 6.50,
            "duree": {"value": 24, "unit": "H"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 4,
            "rechargeable": False,
            "voyages": None,
            "support": ["BSC", "AB"],
            "caracteristiques": [7, 14]
        },
        {
            "nom": "Pass 2 jours",
            "description": "Pass illimité 48h",
            "prix": 12.00,
            "duree": {"value": 48, "unit": "H"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 4,
            "rechargeable": False,
            "voyages": None,
            "support": ["BSC", "AB"],
            "caracteristiques": [7, 14]
        },
        {
            "nom": "Pass 3 jours",
            "description": "Pass illimité 72h",
            "prix": 17.00,
            "duree": {"value": 72, "unit": "H"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 4,
            "rechargeable": False,
            "voyages": None,
            "support": ["BSC", "AB"],
            "caracteristiques": [7, 14]
        }
    ],
    "produits_groupe": [
        {
            "nom": "Pass Groupe 10 personnes",
            "description": "Pass journée pour 10 personnes",
            "prix": 35.00,
            "duree": {"value": 24, "unit": "H"},
            "modes": ["Bus urbain", "Métro", "Tramway"],
            "nature_validite": 4,
            "rechargeable": False,
            "voyages": None,
            "nb_personnes": 10,
            "support": ["BSC"],
            "caracteristiques": [7, 14, 2]
        },
        {
            "nom": "Pass Famille Weekend",
            "description": "Pass weekend pour 2 adultes + 3 enfants",
            "prix": 15.00,
            "duree": {"value": 2, "unit": "D"},
            "modes": ["Bus urbain", "Métro", "Tramway", "Funiculaire"],
            "nature_validite": 4,
            "rechargeable": False,
            "voyages": None,
            "nb_personnes": 5,
            "horaires": {"jours": "Samedi-Dimanche"},
            "support": ["BSC", "AB"],
            "caracteristiques": [7, 9, 14, 2]
        }
    ],
    "produits_zones": [
        {
            "nom": "Abonnement Périurbain 2 zones",
            "description": "Abonnement mensuel zones 1-2",
            "prix": 85.00,
            "duree": {"value": 1, "unit": "M"},
            "modes": ["Bus urbain", "Bus interurbain", "Métro", "Tramway"],
            "nature_validite": 20,
            "rechargeable": True,
            "voyages": None,
            "zones": ["Zone 1", "Zone 2"],
            "support": ["CSC", "AB"],
            "caracteristiques": [7, 14, 4]
        },
        {
            "nom": "Abonnement Périurbain 4 zones",
            "description": "Abonnement mensuel zones 1-4",
            "prix": 125.00,
            "duree": {"value": 1, "unit": "M"},
            "modes": ["Bus urbain", "Bus interurbain", "Métro", "Tramway"],
            "nature_validite": 20,
            "rechargeable": True,
            "voyages": None,
            "zones": ["Zone 1", "Zone 2", "Zone 3", "Zone 4"],
            "support": ["CSC", "AB"],
            "caracteristiques": [7, 14, 4]
        }
    ]
}

# ============================================================================
# VARIATIONS CONVERSATIONNELLES NATURELLES
# ============================================================================

CONVERSATION_PATTERNS = {
    "demande_simple": [
        "Je veux {produit}",
        "J'ai besoin de {produit}",
        "Je voudrais acheter {produit}",
        "Il me faut {produit}",
        "Est-ce que vous avez {produit} ?",
        "Combien coûte {produit} ?",
        "Comment acheter {produit} ?"
    ],
    "demande_incomplete": [
        "Un abonnement mensuel",
        "Un ticket de métro",
        "Un pass pour le weekend",
        "Un carnet de tickets",
        "Quelque chose pour voyager 1 mois",
        "Un titre pour aller au travail tous les jours",
        "Un pass pour visiter Lyon 3 jours"
    ],
    "demande_avec_contexte": [
        "Je suis étudiant, je veux un abonnement pas cher",
        "J'ai 67 ans, quel abonnement pour moi ?",
        "Je travaille à Lyon, mon employeur paie une partie",
        "On est un groupe de 8 personnes pour une journée",
        "Je viens visiter Lyon ce weekend avec ma famille",
        "J'habite à Villeurbanne, je vais au centre tous les jours"
    ],
    "questions_clarification": [
        "C'est quoi la différence entre {produit1} et {produit2} ?",
        "Le {produit} est valable combien de temps ?",
        "Je peux recharger mon {produit} ?",
        "Ça marche sur tous les modes de transport ?",
        "C'est valable dans quelle zone ?",
        "Il faut quelle carte pour {produit} ?"
    ],
    "demandes_complexes": [
        "Je veux un abonnement pour aller de Part-Dieu à Vieux Lyon tous les jours en semaine",
        "Un pass pour 2 adultes et 3 enfants valable samedi et dimanche",
        "Abonnement mensuel métro uniquement, rechargeable automatiquement",
        "Carnet de 10 tickets valable 2 mois sur bus et tramway",
        "Pass 3 jours avec tous les modes sauf le train"
    ]
}

REFORMULATIONS = {
    "abonnement": ["forfait", "pass mensuel", "titre mensuel", "carte mensuelle"],
    "ticket": ["billet", "titre", "ticket unitaire"],
    "métro": ["le métro", "metro", "la ligne de métro"],
    "bus": ["le bus", "l'autobus", "les bus"],
    "tramway": ["le tram", "le tramway", "les tramways"],
    "1 heure": ["1h", "une heure", "60 minutes"],
    "1 mois": ["mensuel", "un mois", "30 jours"],
    "illimité": ["sans limite", "autant que je veux", "voyages illimités"]
}

# ============================================================================
# PAIRES DPO (CHOSEN vs REJECTED)
# ============================================================================

def generate_dpo_pairs() -> List[Dict]:
    """Génère des paires DPO pour l'apprentissage par préférence"""
    dpo_pairs = []

    # Exemple 1 : JSON syntaxe correcte vs incorrecte
    dpo_pairs.append({
        "prompt": "Créé un ticket métro 1h à 2€",
        "chosen": """🧠 **Raisonnement** :

Ticket unitaire métro 1 heure :
- CAR_7 : Validité 1h, glissante à validation (7_01=4)
- CAR_14 : Métro uniquement
- CAR_22 : 1 voyage
- Prix : 2€ (200 centimes)

➡️ **JSON** :

```json
{
  "product_name": "Ticket Métro 1h",
  "price_cents": 200,
  "support": ["BSC", "AB"],
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
    },
    {
      "number": 14,
      "parameters": {
        "14_01": ["Métro"],
        "14_02": "Autorisée"
      }
    },
    {
      "number": 22,
      "parameters": {
        "22_01": 1,
        "22_02": 1,
        "22_03": false
      }
    }
  ]
}
```

✅ Validez-vous ce produit ?""",
        "rejected": """```json
{
  19: 200,
  "nom": "Ticket Métro 1h",
  "caracteristiques": [
    {
      "number": 7,
      "params": {
        "nature": "glissante",
        "duree": 60,
        "unit": "minutes"
      }
    }
  ]
}
```""",
        "metadata": {"type": "dpo", "category": "json_syntax"}
    })

    # Exemple 2 : Définition correcte vs hallucination
    dpo_pairs.append({
        "prompt": "Qu'est-ce que la caractéristique 7 ?",
        "chosen": """🧠 **Définition** :

La **caractéristique 7** (DDV et DEV contrat) permet de définir un produit avec une période de validité limitée.

📋 **Paramètres** :
- **7_01** : Nature de validité du produit (0, 2, 4, 6, 8, 14, 20, 21)
- **7_02** : Unité de durée (D=Jour, W=Semaine, M=Mois, H=Heure)
- **7_03** : Durée de validité (nombre entier)
- **7_04** : Rechargement par prorogation (true/false)
- **7_05** : Autorisation de rechargement (true/false)

📦 **Supports** : BSC, AB

💡 **Usage** : Cette caractéristique est OBLIGATOIRE pour tous les produits de transport.""",
        "rejected": """La caractéristique 7 correspond à **Multi-déplacements** et est utilisée pour gérer le nombre de personnes pouvant utiliser un même produit simultanément.""",
        "metadata": {"type": "dpo", "category": "definition_accuracy"}
    })

    # Exemple 3 : Conversation avec questions vs génération sans réflexion
    dpo_pairs.append({
        "prompt": "Je veux un abonnement mensuel",
        "chosen": """🧠 **Raisonnement** :

Pour un abonnement mensuel, j'identifie :
- **CAR_7** : Validité 1 mois (7_01=20, 7_02="M", 7_03=1)
- **Informations manquantes** : Modes, prix, support, profil

❓ **Questions** :

1. Sur quels **modes de transport** ? (tous modes, métro uniquement, bus+tramway...)
2. Quel **profil tarifaire** ? (plein tarif 68€, jeune 34€, senior 34€, entreprise 39.70€)
3. Sur quel **support** ? (CSC ou Application mobile)
4. **Rechargement automatique** (tacite reconduction) ?

➡️ Une fois ces informations fournies, je pourrai générer le JSON complet.

✅ Pouvez-vous préciser ces éléments ?""",
        "rejected": """```json
{
  "product_name": "Abonnement mensuel",
  "characteristics": [
    {
      "number": 7,
      "parameters": {
        "7_01": 2,
        "7_02": "M",
        "7_03": 1
      }
    }
  ]
}
```""",
        "metadata": {"type": "dpo", "category": "conversational_quality"}
    })

    # Exemple 4 : Détection incompatibilité vs génération aveugle
    dpo_pairs.append({
        "prompt": "Créé un produit avec CAR_14 et CAR_74",
        "chosen": """⚠️ **INCOMPATIBILITÉ DÉTECTÉE**

🔍 **Analyse** :

**CAR_14** (Modes de transport autorisés ou interdits) :
Définit une LISTE de modes au niveau du paramétrage
Support : BSC et AB

**CAR_74** (Mode de transport autorisé par produit) :
Définit UN SEUL mode codé sur le support
Support : AB uniquement

❌ **Conflit** : Ces deux caractéristiques servent le même objectif (définir les modes autorisés) mais de manière incompatible. CAR_14 utilise une liste paramétrée, CAR_74 code un mode unique sur le support.

✅ **Solution** :
- Si vous voulez plusieurs modes → Utilisez **CAR_14** uniquement
- Si vous voulez un mode unique codé → Utilisez **CAR_74** uniquement (AB seulement)

➡️ Quelle approche préférez-vous ?""",
        "rejected": """```json
{
  "characteristics": [
    {
      "number": 14,
      "parameters": {
        "14_01": ["Bus urbain", "Métro"],
        "14_02": "Autorisée"
      }
    },
    {
      "number": 74,
      "parameters": {
        "74_01": 3,
        "74_02": true
      }
    }
  ]
}
```""",
        "metadata": {"type": "dpo", "category": "incompatibility_detection"}
    })

    return dpo_pairs

# ============================================================================
# GÉNÉRATEURS D'EXEMPLES RÉALISTES
# ============================================================================

def generate_realistic_product_examples() -> List[Dict]:
    """Génère des exemples réalistes basés sur les produits TCL"""
    examples = []

    for category, products in TCL_PRODUCTS.items():
        for product in products:
            # Variations de demandes pour chaque produit
            variations = generate_product_variations(product)
            examples.extend(variations)

    return examples

def generate_product_variations(product: Dict) -> List[Dict]:
    """Génère toutes les variations conversationnelles pour un produit"""
    variations = []

    # Variation 1 : Demande directe avec toutes les infos
    direct_request = generate_direct_request(product)
    variations.append(direct_request)

    # Variation 2 : Demande partielle nécessitant des questions
    partial_request = generate_partial_request(product)
    variations.append(partial_request)

    # Variation 3 : Question sur le prix
    price_question = generate_price_question(product)
    variations.append(price_question)

    # Variation 4 : Question sur la durée/validité
    validity_question = generate_validity_question(product)
    variations.append(validity_question)

    # Variation 5 : Demande avec reformulations
    reformulated = generate_reformulated_request(product)
    variations.append(reformulated)

    return variations

def generate_direct_request(product: Dict) -> Dict:
    """Génère une demande directe complète"""
    prix_str = f"{product['prix']:.2f}€"
    duree_str = f"{product['duree']['value']} {product['duree']['unit'].replace('H', 'heure').replace('M', 'mois').replace('D', 'jour')}"
    modes_str = " + ".join(product['modes'][:2]) if len(product['modes']) > 1 else product['modes'][0]

    instruction = f"Créé un {product['nom']} : {duree_str}, {modes_str}, {prix_str}"

    # Construire le JSON de réponse
    json_response = build_product_json(product)

    response = f"""🧠 **Raisonnement** :

{product['description']} - Toutes les informations sont fournies.

Caractéristiques nécessaires :
{format_required_characteristics(product)}

➡️ **JSON** :

```json
{json.dumps(json_response, indent=2, ensure_ascii=False)}
```

✅ Validez-vous ce produit ?"""

    return {
        "instruction": instruction,
        "response": response,
        "metadata": {
            "type": "product_generation",
            "product_name": product["nom"],
            "category": "complete_request"
        }
    }

def generate_partial_request(product: Dict) -> Dict:
    """Génère une demande partielle nécessitant des questions"""
    # Variantes de demandes incomplètes
    incomplete_patterns = [
        f"Je veux {product['nom'].lower()}",
        f"Un {product['nom'].lower()}",
        f"Combien coûte {product['nom'].lower()} ?",
        f"C'est quoi {product['nom'].lower()} ?"
    ]

    instruction = random.choice(incomplete_patterns)

    # Identifier ce qui manque
    questions = []
    if "profil" in product:
        questions.append(f"Confirmez-vous le **profil {product['profil']}** ?")
    if len(product.get("support", [])) > 1:
        questions.append(f"Sur quel **support** ? ({' ou '.join(product['support'])})")
    if product.get("rechargeable"):
        questions.append("**Rechargement automatique** souhaité ?")

    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

    response = f"""🧠 **Raisonnement** :

{product['description']}

Informations identifiées :
- **Prix** : {product['prix']:.2f}€
- **Durée** : {product['duree']['value']} {product['duree']['unit']}
- **Modes** : {', '.join(product['modes'])}

❓ **Questions de clarification** :

{questions_text if questions else "Toutes les informations sont présentes."}

➡️ {"Une fois confirmé, je génèrerai le JSON complet." if questions else "Génération du JSON :"}

✅ Confirmez-vous ces paramètres ?"""

    return {
        "instruction": instruction,
        "response": response,
        "metadata": {
            "type": "conversational",
            "product_name": product["nom"],
            "category": "partial_request"
        }
    }

def generate_price_question(product: Dict) -> Dict:
    """Génère une question sur le prix"""
    instruction = f"Quel est le prix de {product['nom'].lower()} ?"

    voyages_text = "Illimité" if product.get('voyages') is None else f"{product.get('voyages', 'Illimité')} voyage(s)"

    response = f"""🧠 **Information tarifaire** :

Le **{product['nom']}** coûte **{product['prix']:.2f}€**.

📋 **Caractéristiques** :
- Durée : {product['duree']['value']} {product['duree']['unit'].replace('H', 'heure(s)').replace('M', 'mois').replace('D', 'jour(s)')}
- Modes : {', '.join(product['modes'])}
- Voyages : {voyages_text}
- Rechargeable : {"Oui" if product.get('rechargeable', False) else "Non"}

💡 {product['description']}

✅ Voulez-vous créer ce produit ?"""

    return {
        "instruction": instruction,
        "response": response,
        "metadata": {
            "type": "information",
            "product_name": product["nom"],
            "category": "price_inquiry"
        }
    }

def generate_validity_question(product: Dict) -> Dict:
    """Génère une question sur la validité"""
    instruction = f"{product['nom']} est valable combien de temps ?"

    duree_humaine = format_duration_human(product['duree'])
    nature_desc = get_validity_nature_description(product['nature_validite'])

    response = f"""🧠 **Informations de validité** :

Le **{product['nom']}** est valable **{duree_humaine}**.

📅 **Nature de validité** : {nature_desc}

💡 **En pratique** :
{get_practical_validity_example(product)}

✅ D'autres questions ?"""

    return {
        "instruction": instruction,
        "response": response,
        "metadata": {
            "type": "information",
            "product_name": product["nom"],
            "category": "validity_inquiry"
        }
    }

def generate_reformulated_request(product: Dict) -> Dict:
    """Génère une demande avec reformulations naturelles"""
    # Reformuler le nom du produit
    reformulations_nom = {
        "Ticket": ["billet", "titre"],
        "Abonnement": ["forfait", "pass"],
        "Pass": ["ticket", "forfait"],
        "Carnet": ["pack"]
    }

    nom_reformule = product['nom']
    for key, alternatives in reformulations_nom.items():
        if key in product['nom']:
            nom_reformule = product['nom'].replace(key, random.choice(alternatives))

    instruction = f"Je voudrais {nom_reformule.lower()}"

    json_response = build_product_json(product)

    response = f"""🧠 **Raisonnement** :

Vous souhaitez : **{product['nom']}**

{product['description']}

➡️ **JSON** :

```json
{json.dumps(json_response, indent=2, ensure_ascii=False)}
```

✅ Confirmez-vous ?"""

    return {
        "instruction": instruction,
        "response": response,
        "metadata": {
            "type": "product_generation",
            "product_name": product["nom"],
            "category": "reformulated_request"
        }
    }

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def build_product_json(product: Dict) -> Dict:
    """Construit le JSON complet d'un produit"""
    characteristics = []

    # CAR_7 : Validité (OBLIGATOIRE)
    car_7 = {
        "number": 7,
        "parameters": {
            "7_01": product['nature_validite'],
            "7_02": product['duree']['unit'],
            "7_03": product['duree']['value'],
            "7_04": product.get('rechargeable', False),
            "7_05": product.get('rechargeable', False)
        }
    }
    characteristics.append(car_7)

    # CAR_14 : Modes de transport (si spécifiques)
    if 'modes' in product and product['modes']:
        car_14 = {
            "number": 14,
            "parameters": {
                "14_01": product['modes'],
                "14_02": "Autorisée"
            }
        }
        characteristics.append(car_14)

    # CAR_22 : Multi-déplacements (si limité)
    if product.get('voyages') is not None:
        car_22 = {
            "number": 22,
            "parameters": {
                "22_01": product['voyages'],
                "22_02": product['voyages'],
                "22_03": False
            }
        }
        characteristics.append(car_22)

    # CAR_2 : Groupe (si applicable)
    if 'nb_personnes' in product:
        car_2 = {
            "number": 2,
            "parameters": {
                "2_01": product['nb_personnes']
            }
        }
        characteristics.append(car_2)

    # CAR_9 : Horaires (si restrictions)
    if 'horaires' in product:
        horaires_data = product['horaires']
        car_9 = {
            "number": 9,
            "parameters": {
                "9_01": [
                    {
                        "days": horaires_data.get("jours", "Lundi-Dimanche"),
                        "start": horaires_data.get("debut", "00:00"),
                        "end": horaires_data.get("fin", "23:59")
                    }
                ]
            }
        }
        characteristics.append(car_9)

    # CAR_4 : Zones (si applicable)
    if 'zones' in product:
        car_4 = {
            "number": 4,
            "parameters": {
                "4_01": product['zones'],
                "4_02": "Autorisée"
            }
        }
        characteristics.append(car_4)

    result = {
        "product_name": product['nom'],
        "price_cents": int(product['prix'] * 100),
        "support": product['support'],
        "characteristics": characteristics
    }

    if 'profil' in product:
        result['profile'] = product['profil']

    return result

def format_required_characteristics(product: Dict) -> str:
    """Formate la liste des caractéristiques nécessaires"""
    cars = []
    cars.append(f"- **CAR_7** : Période de validité ({product['duree']['value']} {product['duree']['unit']})")

    if 'modes' in product and product['modes']:
        cars.append(f"- **CAR_14** : Modes autorisés ({', '.join(product['modes'][:2])}...)")

    if product.get('voyages') is not None:
        cars.append(f"- **CAR_22** : Nombre de voyages ({product['voyages']})")

    if 'nb_personnes' in product:
        cars.append(f"- **CAR_2** : Nombre de personnes ({product['nb_personnes']})")

    if 'horaires' in product:
        cars.append(f"- **CAR_9** : Restrictions horaires")

    if 'zones' in product:
        cars.append(f"- **CAR_4** : Zones tarifaires ({len(product['zones'])} zones)")

    return "\n".join(cars)

def format_duration_human(duree: Dict) -> str:
    """Formate la durée en langage naturel"""
    value = duree['value']
    unit = duree['unit']

    unit_map = {
        'H': 'heure' if value == 1 else 'heures',
        'D': 'jour' if value == 1 else 'jours',
        'W': 'semaine' if value == 1 else 'semaines',
        'M': 'mois'
    }

    return f"{value} {unit_map.get(unit, unit)}"

def get_validity_nature_description(nature: int) -> str:
    """Retourne la description de la nature de validité"""
    descriptions = {
        0: "Dates fixes (DDV et DEV définies à l'avance)",
        2: "Glissante au chargement (commence à l'achat)",
        4: "Glissante à la validation (commence à la première utilisation)",
        6: "Déterminée au chargement et modifiable à la vente",
        8: "DEV glissante avec DDV saisie à la vente",
        14: "DDV saisie à la vente, DEV limitée par profil",
        20: "DDV début du mois suivant",
        21: "Calendaire avec date pivot"
    }
    return descriptions.get(nature, f"Nature {nature}")

def get_practical_validity_example(product: Dict) -> str:
    """Génère un exemple pratique de validité"""
    nature = product['nature_validite']
    duree = format_duration_human(product['duree'])

    examples = {
        2: f"Si vous l'achetez aujourd'hui, il est valable {duree} à partir d'aujourd'hui.",
        4: f"Il devient valable dès votre première validation et reste actif pendant {duree}.",
        20: f"Si vous l'achetez aujourd'hui, il sera valable à partir du 1er jour du mois prochain pour {duree}."
    }

    return examples.get(nature, f"Validité de {duree} selon la nature {nature}.")

# ============================================================================
# GÉNÉRATION COMPLÈTE DU DATASET
# ============================================================================

def generate_complete_dataset() -> List[Dict]:
    """Génère le dataset complet ultra-réaliste"""
    print("🚀 Génération du dataset ultra-réaliste TCL Lyon...")
    print("="*70)

    all_examples = []

    # 1. Exemples de produits réalistes TCL
    print("\n1️⃣  Génération des produits TCL Lyon...")
    tcl_examples = generate_realistic_product_examples()
    all_examples.extend(tcl_examples)
    print(f"   ✅ {len(tcl_examples)} exemples générés")

    # 2. Paires DPO
    print("\n2️⃣  Génération des paires DPO...")
    dpo_examples = generate_dpo_pairs()
    all_examples.extend(dpo_examples)
    print(f"   ✅ {len(dpo_examples)} paires générées")

    # 3. Charger les exemples existants (définitions, concepts, incompatibilités)
    print("\n3️⃣  Chargement des exemples existants...")
    try:
        with open("/home/user/Ftune/training_dataset_enriched_v2.json", "r", encoding="utf-8") as f:
            existing = json.load(f)
        all_examples.extend(existing)
        print(f"   ✅ {len(existing)} exemples chargés")
    except Exception as e:
        print(f"   ⚠️  Impossible de charger : {e}")

    # Statistiques
    print("\n" + "="*70)
    print(f"📊 **DATASET COMPLET** : {len(all_examples)} exemples")
    print("="*70)

    # Répartition par type
    types_count = {}
    for item in all_examples:
        item_type = item.get("metadata", {}).get("type", "unknown")
        types_count[item_type] = types_count.get(item_type, 0) + 1

    print("\n📋 Répartition par type :")
    for item_type, count in sorted(types_count.items(), key=lambda x: -x[1]):
        print(f"   - {item_type}: {count}")

    return all_examples

if __name__ == "__main__":
    dataset = generate_complete_dataset()

    # Sauvegarder
    output_path = "/home/user/Ftune/training_dataset_ultra_realistic.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Dataset sauvegardé : {output_path}")
    print(f"💾 Taille : {len(json.dumps(dataset))/1024/1024:.2f} MB")
    print("\n🎉 Génération terminée !")
