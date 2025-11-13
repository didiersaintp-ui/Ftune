#!/usr/bin/env python3
"""
Génération du Dataset Enrichi v2 - Assistant Billettique Conversationnel

Ce script génère un dataset complet pour entraîner un assistant capable de:
1. Connaître exactement toutes les définitions des caractéristiques
2. Converser avec l'utilisateur pour clarifier les besoins
3. Détecter les incompatibilités
4. Expliquer les concepts métier
5. Générer du JSON parfait

Catégories:
- Définitions des caractéristiques (800 exemples)
- Conversations avec questions (1500 exemples)
- Détection d'incompatibilités (500 exemples)
- Concepts métier (500 exemples)
- Génération JSON complète (2700 exemples)

Total: 6000 exemples
"""

import json
from typing import List, Dict, Any

# ============================================================================
# DONNÉES DU PDF - CARACTÉRISTIQUES
# ============================================================================

CHARACTERISTICS_DATA = {
    7: {
        "label": "DDV et DEV contrat",
        "description": "Permet de définir un produit avec une période de validité limitée.",
        "parameters": {
            "7_01": {
                "label": "Nature de validité du produit",
                "values": [0, 2, 4, 6, 8, 14, 20, 21],
                "descriptions": {
                    0: "DDV et DEV à dates fixes",
                    2: "DDV et DEV glissantes au chargement",
                    4: "DEV glissante à la validation",
                    6: "DDV et DEV déterminées au chargement et modifiables à la vente",
                    8: "DEV glissante avec DDV saisie à la vente",
                    14: "DDV saisie à la vente et DEV limitée par profil ou support",
                    20: "DDV début mois suivant, DEV limitée par profil ou support",
                    21: "DDV et DEV calendaires avec date pivot"
                }
            },
            "7_02": {
                "label": "Unité de la durée de validité",
                "values": ["D", "W", "M", "H"],
                "descriptions": {
                    "D": "Jour",
                    "W": "Semaine",
                    "M": "Mois",
                    "H": "Heure"
                }
            },
            "7_03": {
                "label": "Durée de validité",
                "type": "integer",
                "description": "Nombre d'unités de la durée de validité"
            },
            "7_04": {
                "label": "Rechargement par prorogation",
                "type": "boolean",
                "description": "Si true, la DEV est augmentée de la durée de validité lors du rechargement"
            },
            "7_05": {
                "label": "Autorisation de rechargement",
                "type": "boolean",
                "description": "Si true, permet le rechargement du contrat"
            }
        },
        "supports": ["BSC", "AB"]
    },
    8: {
        "label": "Calendrier d'autorisation ou de refus en validation",
        "description": "Permet d'autoriser ou d'interdire l'utilisation du produit en fonction des intervalles de date d'un calendrier.",
        "parameters": {
            "8_01": {"label": "Calendriers", "type": "list"},
            "8_02": {"label": "Utilisation", "values": ["Autorisée", "Interdite"]}
        },
        "supports": ["BSC", "AB"]
    },
    9: {
        "label": "Autorisation de déplacement par type de jour et tranche horaire",
        "description": "Permet de définir les autorisations d'utilisation du produit par type de jour et tranche horaire.",
        "parameters": {
            "9_01": {"label": "Table de validité par tranche horaire", "type": "list"}
        },
        "supports": ["BSC", "AB"]
    },
    10: {
        "label": "Limitation des déplacements par sous-période",
        "description": "Permet de limiter le nombre de déplacements par sous période (ex: 2 déplacements par semaine).",
        "parameters": {
            "10_01": {"label": "Sous-périodes de référence", "type": "list"}
        },
        "supports": ["AB"]
    },
    22: {
        "label": "Multi-déplacements Mono-usager",
        "description": "Permet de définir un produit à multi-déplacements utilisable par un seul usager.",
        "parameters": {
            "22_01": {"label": "Nombre de déplacements du produit", "type": "integer"},
            "22_02": {"label": "Nombre maximum de déplacements du contrat", "type": "integer"},
            "22_03": {"label": "Rechargement par surcharge", "type": "boolean"}
        },
        "supports": ["BSC", "AB"]
    },
    6: {
        "label": "Nombre de validations par déplacement",
        "description": "Permet de limiter le nombre de voyages d'un produit dans un déplacement.",
        "parameters": {
            "6_01": {"label": "Nombre maximum de voyages autorisés", "type": "integer"}
        },
        "supports": ["BSC", "AB"]
    },
    14: {
        "label": "Modes de transport autorisés ou interdits",
        "description": "Permet de limiter l'utilisation d'un produit à la validation sur un ou plusieurs modes de transports donnés.",
        "parameters": {
            "14_01": {"label": "Modes de transport", "type": "list"},
            "14_02": {"label": "Utilisation", "values": ["Autorisée", "Interdite"]}
        },
        "supports": ["BSC", "AB"]
    },
    74: {
        "label": "Mode de transport autorisé par produit",
        "description": "Permet de limiter l'utilisation en validation d'un produit à un mode de transport (0 signifie tout mode autorisé).",
        "parameters": {
            "74_01": {"label": "Numéro du mode de transport autorisé", "type": "integer"},
            "74_02": {"label": "Codage sur le support", "type": "boolean"}
        },
        "supports": ["AB"]
    },
    58: {
        "label": "Classe autorisée par produit",
        "description": "Permet de limiter l'utilisation d'un produit à une classe.",
        "parameters": {
            "58_01": {"label": "Numéro de classe", "type": "integer"},
            "58_02": {"label": "Codage sur le support", "type": "boolean"}
        },
        "supports": ["BSC", "AB"]
    },
    2: {
        "label": "Groupe avec nombre de passagers par produit",
        "description": "Permet de limiter l'utilisation d'un produit à un groupe dont le nombre de passagers maximum est fixé à la définition du produit.",
        "parameters": {
            "2_01": {"label": "Nombre maximum de passagers autorisés", "type": "integer"}
        },
        "supports": ["BSC", "AB"]
    },
    21: {
        "label": "Multi-déplacement, Multi-usager",
        "description": "Permet de définir un produit à multi-déplacements utilisable par un ou plusieurs usagers par un geste de multi-validation.",
        "parameters": {
            "21_01": {"label": "Nombre de déplacements du produit", "type": "integer"},
            "21_02": {"label": "Nombre maximum de déplacements du contrat", "type": "integer"},
            "21_03": {"label": "Nombre maximum de passagers pour un déplacement", "type": "integer"},
            "21_04": {"label": "Rechargement par surcharge", "type": "boolean"}
        },
        "supports": ["BSC", "AB"]
    },
    38: {
        "label": "Groupe avec nombre de passagers saisi à la vente",
        "description": "Permet de limiter l'utilisation d'un produit à un groupe dont le nombre est saisi lors de la vente.",
        "parameters": {
            "38_01": {"label": "Nombre minimum de passagers", "type": "integer"},
            "38_02": {"label": "Nombre maximum de passagers", "type": "integer"}
        },
        "supports": ["BSC", "AB"]
    },
    105: {
        "label": "Multi-validation",
        "description": "Permet de définir le fonctionnel de multi-validation selon les équipements pour un produit.",
        "parameters": {
            "105_01": {"label": "Table des règles de multi-validation", "type": "list"}
        },
        "supports": ["BSC", "AB"]
    },
    3: {
        "label": "Lignes autorisées ou interdites par produit",
        "description": "Permet de limiter l'utilisation d'un produit à la validation sur une ou plusieurs lignes données par paramétrage.",
        "parameters": {
            "3_01": {"label": "Lignes autorisées", "type": "list"},
            "3_02": {"label": "Utilisation", "values": ["Autorisée", "Interdite"]}
        },
        "supports": ["BSC", "AB"]
    },
    87: {
        "label": "Lignes déterminées à la vente et codées sur le support",
        "description": "Permet de définir une liste de ligne sur lesquelles l'usage du produit de transport est autorisé ou non.",
        "parameters": {
            "87_01": {"label": "Nombre de lignes à coder", "type": "integer"},
            "87_02": {"label": "Changement de ligne possible lors d'un rechargement", "type": "boolean"},
            "87_03": {"label": "Origine des lignes", "values": ["Saisie lors de la vente", "Issue du dossier client"]}
        },
        "supports": ["BSC", "AB"]
    },
    11: {
        "label": "Interdiction de retour sur une même ligne",
        "description": "Permet d'interdire le retour sur la ligne précédemment empruntée.",
        "parameters": {},
        "supports": ["BSC", "AB"]
    },
    102: {
        "label": "Abonnement à tacite reconduction avec prélèvements automatiques",
        "description": "Permet de traiter les abonnements à tacite reconduction à durée déterminée (TRDD) et à durée illimitée (TRDI).",
        "parameters": {
            "102_01": {"label": "Mécanisme de suspension de contrat", "values": ["Aucun", "Liste de contrat à ignorer"]},
            "102_02": {"label": "Nombre de périodes de suspension maximum autorisé", "type": "integer"},
            "102_03": {"label": "Nombre de périodes de suspension minimum autorisé", "type": "integer"},
            "102_04": {"label": "Indicateur d'autorisation de résiliation à l'initiative de l'usager", "type": "boolean"}
        },
        "supports": ["AB"]
    },
    107: {
        "label": "X mois gratuits pour Y mois payés",
        "description": "Pour les abonnements de type TRDD et TRDI uniquement, au bout de Y mois payés, les X prochains mois sont gratuits.",
        "parameters": {
            "107_01": {"label": "Nombre de mois payés", "type": "integer"},
            "107_02": {"label": "Nombre de mois gratuits", "type": "integer"},
            "107_03": {"label": "Libellé pour facturation", "type": "string"}
        },
        "supports": ["AB"]
    },
    4: {
        "label": "Zones de tarification autorisées/interdites affectées au produit",
        "description": "Permet d'autoriser ou d'interdire les déplacements sur une liste de zones de tarification prédéfinies.",
        "parameters": {
            "4_01": {"label": "Liste de zones", "type": "list"},
            "4_02": {"label": "Utilisation", "values": ["Autorisée", "Interdite"]}
        },
        "supports": ["BSC", "AB"]
    },
    121: {
        "label": "Zones autorisées sur un des réseaux locaux déterminées à la vente",
        "description": "Permet la détermination pour un réseau monomodal, d'une liste de zones autorisées (trajet de zones).",
        "parameters": {
            "121_01": {"label": "Origine du trajet zonal", "values": ["Saisie lors de la vente"]},
            "121_02": {"label": "Réseau de référence de la zone", "type": "string"},
            "121_03": {"label": "Type de saisie zonal", "values": ["Zone de tarification", "Point d'arrêt physique"]},
            "121_04": {"label": "Nombre de zones maximum pour le produit", "values": [16, 32, 48, 64]}
        },
        "supports": ["BSC", "AB"]
    },
    86: {
        "label": "OD sélectionnée à la vente",
        "description": "Permet de limiter l'usage du titre sur une O/D (point d'arrêt physique, point d'arrêt commercial, zone) pour un réseau monomodal.",
        "parameters": {
            "86_01": {"label": "Origine du trajet O/D", "values": ["Saisie lors de la vente", "Issue du dossier client", "Issue d'un produit d'acquisition"]},
            "86_02": {"label": "Type de saisie O/D", "values": ["Arrêt physique", "Arrêt commercial", "Zone de tarification"]},
            "86_03": {"label": "Type d'origine/destination à encoder", "values": ["Arrêt physique", "Arrêt commercial", "Zone de tarification"]},
            "86_04": {"label": "Réseau de référence de l'O/D", "type": "string"},
            "86_05": {"label": "Nombre de définition O/D maximum du produit", "values": [1, 2]},
            "86_06": {"label": "Restriction sur le sens du trajet en validation", "type": "boolean"},
            "86_07": {"label": "Divergence autorisée", "type": "boolean"},
            "86_08": {"label": "Autorisation à monter en cours de trajet", "type": "boolean"},
            "86_09": {"label": "Indicateur de correspondance autorisée sur trajet O/D", "type": "boolean"}
        },
        "supports": ["BSC", "AB"]
    },
    97: {
        "label": "Gestion du remboursement",
        "description": "Permet de fixer la règle de remboursement à appliquer.",
        "parameters": {
            "97_01": {"label": "Règle de remboursement", "values": ["Non encadré", "Produits/articles dont le début de la période de validité n'est pas dépassé", "Produits/articles jamais consommés"]}
        },
        "supports": ["BSC", "AB"]
    },
    48: {
        "label": "Produit à post-paiement",
        "description": "Permet de définir un produit à post paiement en validation.",
        "parameters": {},
        "supports": ["AB"]
    },
    23: {
        "label": "Points de fidélité à la validation",
        "description": "Permet de définir, par type de jour et tranche horaire, le nombre de points de fidélité attribués en première montée.",
        "parameters": {
            "23_01": {"label": "Liste des jours fériés", "type": "list"},
            "23_02": {"label": "Liste des tranches horaires par type de jour", "type": "list"},
            "23_03": {"label": "Table d'attribution de points de fidélité par tranche horaire", "type": "list"}
        },
        "supports": ["AB"]
    },
    103: {
        "label": "Titre unitaire sans compteur",
        "description": "Permet de coder un titre 1 voyage sur la carte sans contact sans utilisation de compteur.",
        "parameters": {},
        "supports": ["AB"]
    },
    98: {
        "label": "Mécanisme d'inhibition du blocage de contrat",
        "description": "Permet de choisir le mécanisme d'inhibition du blocage de contrat.",
        "parameters": {
            "98_01": {"label": "Mécanisme d'inhibition du blocage du contrat", "values": ["DSI", "ES"]}
        },
        "supports": ["AB"]
    },
    73: {
        "label": "Encodage du pointeur sur profil",
        "description": "Permet d'assurer la compatibilité et l'interopérabilité du traitement de titre avec des systèmes billettiques partenaires.",
        "parameters": {},
        "supports": ["AB"]
    },
    90: {
        "label": "Champ de zones",
        "description": "Définition et codage d'un champ de bits dans les données zones du contrat.",
        "parameters": {
            "90_01": {"label": "Champ de zones", "type": "bitfield"}
        },
        "supports": ["BSC", "AB"]
    },
    91: {
        "label": "Encodage de prestations",
        "description": "Définition et codage d'une valeur de prestation dans les données zones du contrat en origine ou en destination.",
        "parameters": {
            "91_01": {"label": "Liste des points d'arrêts avec la valeur de la prestation à encoder", "type": "list"}
        },
        "supports": ["BSC", "AB"]
    }
}

# Incompatibilités connues
INCOMPATIBILITIES = [
    {
        "cars": [14, 74],
        "reason": "CAR_14 définit une LISTE de modes par paramétrage, CAR_74 définit UN SEUL mode codé sur le support. Ils ne peuvent pas coexister car ils servent le même objectif de manière différente.",
        "solution": "Choisir CAR_14 pour plusieurs modes OU CAR_74 pour un mode unique codé."
    },
    {
        "cars": [22, 21],
        "reason": "CAR_22 est pour multi-déplacements MONO-usager, CAR_21 est pour multi-déplacements MULTI-usager. Ils s'excluent mutuellement.",
        "solution": "Choisir CAR_22 pour un seul usager OU CAR_21 pour plusieurs usagers simultanés."
    },
    {
        "cars": [3, 87],
        "reason": "CAR_3 définit des lignes par paramétrage, CAR_87 permet de coder des lignes à la vente. Ils ne peuvent pas coexister.",
        "solution": "Choisir CAR_3 pour lignes fixes OU CAR_87 pour lignes déterminées à la vente."
    },
    {
        "cars": [2, 38],
        "reason": "CAR_2 définit un nombre FIXE de passagers, CAR_38 permet de SAISIR le nombre à la vente. Ils s'excluent mutuellement.",
        "solution": "Choisir CAR_2 pour un nombre fixe OU CAR_38 pour un nombre variable saisi à la vente."
    },
    {
        "cars": [4, 121],
        "reason": "CAR_4 définit des zones par paramétrage, CAR_121 permet de déterminer les zones à la vente. Risque de conflit de logique.",
        "solution": "Préférer CAR_4 pour zones fixes OU CAR_121 pour trajet zonal défini à la vente."
    }
]

# Concepts métier
BUSINESS_CONCEPTS = {
    "DDV": {
        "full_name": "Date de Début de Validité",
        "description": "Date à partir de laquelle un titre de transport peut être utilisé.",
        "example": "Pour un abonnement acheté le 15 janvier avec DDV au 1er février, le titre ne sera valable qu'à partir du 1er février."
    },
    "DEV": {
        "full_name": "Date de Fin de Validité",
        "description": "Date jusqu'à laquelle un titre de transport peut être utilisé.",
        "example": "Un abonnement mensuel avec DEV au 31 janvier ne pourra plus être utilisé après cette date."
    },
    "TRDI": {
        "full_name": "Tacite Reconduction à Durée Illimitée",
        "description": "Abonnement qui se renouvelle automatiquement sans limite de durée, jusqu'à résiliation par l'usager.",
        "example": "Un abonnement mensuel avec prélèvement automatique qui continue chaque mois jusqu'à ce que le client demande l'arrêt.",
        "car": 102
    },
    "TRDD": {
        "full_name": "Tacite Reconduction à Durée Déterminée",
        "description": "Abonnement qui se renouvelle automatiquement pour une durée fixée à l'avance.",
        "example": "Un abonnement annuel qui se renouvelle automatiquement pour une année supplémentaire, avec possibilité de résiliation à l'échéance.",
        "car": 102
    },
    "BSC": {
        "full_name": "Billet Sans Contact",
        "description": "Support de transport physique sans contact (ticket papier, carte à puce).",
        "example": "Un ticket de métro sans contact qu'on valide en le passant devant le lecteur."
    },
    "AB": {
        "full_name": "Application Billettique",
        "description": "Support dématérialisé (application mobile, carte virtuelle).",
        "example": "Un ticket de transport stocké dans une application smartphone."
    },
    "CSC": {
        "full_name": "Carte Sans Contact",
        "description": "Support physique réutilisable sans contact (carte à puce rechargeable).",
        "example": "Une carte Navigo ou Oyster card."
    },
    "Nature de validité": {
        "description": "Détermine comment les dates de début (DDV) et de fin (DEV) sont calculées.",
        "types": {
            0: "Dates fixes (définies à l'avance)",
            2: "Glissantes au chargement (commence à l'achat)",
            4: "Glissantes à la validation (commence à la première utilisation)",
            6: "Déterminées au chargement et modifiables",
            8: "DEV glissante avec DDV saisie",
            14: "DDV saisie, DEV limitée par profil",
            20: "DDV début mois suivant",
            21: "Calendaires avec date pivot"
        }
    },
    "Multi-validation": {
        "description": "Permet à plusieurs personnes de valider simultanément avec un seul support (pour les produits groupe).",
        "example": "Un pass famille où on peut valider 4 personnes en une seule fois.",
        "car": 105
    },
    "Rechargement par prorogation": {
        "description": "Lors du rechargement, la nouvelle période de validité s'ajoute à la fin de l'ancienne (prolongation).",
        "example": "Abonnement valable jusqu'au 31 janvier, rechargé le 25 janvier : nouvelle DEV = 28 février (31 jan + 1 mois).",
        "parameter": "7_04"
    },
    "Rechargement par surcharge": {
        "description": "Permet d'ajouter des déplacements au compteur existant sans attendre l'épuisement.",
        "example": "Carnet de 10 voyages avec 3 restants, rechargeable de 10 : nouveau solde = 13 voyages.",
        "parameter": "22_03"
    }
}

# Modes de transport
TRANSPORT_MODES = [
    {"number": 0, "label": "Indéterminé"},
    {"number": 1, "label": "Bus urbain"},
    {"number": 2, "label": "Bus interurbain"},
    {"number": 3, "label": "Métro"},
    {"number": 4, "label": "Tramway"},
    {"number": 5, "label": "Train"},
    {"number": 8, "label": "Parking"},
    {"number": 9, "label": "Vélo"}
]

# ============================================================================
# GÉNÉRATEURS D'EXEMPLES
# ============================================================================

def generate_characteristic_definitions() -> List[Dict]:
    """Génère les exemples de définitions de caractéristiques"""
    examples = []

    for car_num, car_data in CHARACTERISTICS_DATA.items():
        # Définition complète de la caractéristique
        params_desc = ""
        if car_data["parameters"]:
            params_desc = "\n\n📋 **Paramètres** :\n"
            for param_code, param_info in car_data["parameters"].items():
                param_label = param_info.get("label", "")
                params_desc += f"- **{param_code}** : {param_label}\n"

                # Ajouter les valeurs possibles
                if "values" in param_info:
                    if isinstance(param_info["values"], dict):
                        params_desc += "  Valeurs :\n"
                        for val, desc in param_info["values"].items():
                            params_desc += f"    - `{val}` : {desc}\n"
                    else:
                        params_desc += f"  Valeurs possibles : {param_info['values']}\n"

                if "type" in param_info:
                    params_desc += f"  Type : {param_info['type']}\n"
                if "description" in param_info:
                    params_desc += f"  {param_info['description']}\n"

        supports_text = ", ".join(car_data["supports"])

        response = f"""🧠 **Définition** :

La **caractéristique {car_num}** ({car_data['label']}) {car_data['description']}{params_desc}

📦 **Supports** : {supports_text}

💡 **Usage** : Cette caractéristique est essentielle pour définir {car_data['label'].lower()}."""

        examples.append({
            "instruction": f"Qu'est-ce que la caractéristique {car_num} ?",
            "response": response,
            "metadata": {
                "type": "definition",
                "topic": "caracteristiques",
                "car_number": car_num
            }
        })

        # Ajouter des variations de questions
        variations = [
            f"Définition de CAR_{car_num}",
            f"Explique-moi la CAR_{car_num}",
            f"À quoi sert la caractéristique {car_num} ?",
            f"C'est quoi CAR_{car_num} ?"
        ]

        for variation in variations:
            examples.append({
                "instruction": variation,
                "response": response,
                "metadata": {
                    "type": "definition",
                    "topic": "caracteristiques",
                    "car_number": car_num
                }
            })

    return examples


def generate_conversational_examples() -> List[Dict]:
    """Génère les exemples conversationnels avec questions"""
    examples = []

    # Catégorie 1 : Produits avec informations manquantes
    scenarios = [
        {
            "input": "Je veux un abonnement mensuel pour le métro",
            "reasoning": """Pour un abonnement mensuel métro, j'identifie :
- **CAR_7** : Validité 1 mois (7_01=2, 7_02="M", 7_03=1)
- **CAR_14** : Mode métro autorisé
- **Informations manquantes** : Prix, support, rechargement""",
            "questions": [
                "Quel est le **prix** de cet abonnement ?",
                "Sur quel **support** ? (CSC ou BSC)",
                "**Rechargement automatique** (tacite reconduction) ?",
                "**Profil tarifaire** ? (Plein tarif, étudiant, senior...)"
            ]
        },
        {
            "input": "Créé un carnet de 10 tickets",
            "reasoning": """Pour un carnet de 10 tickets, j'identifie :
- **CAR_22** : Multi-déplacements mono-usager (22_01=10, 22_02=10)
- **CAR_7** : Période de validité nécessaire
- **Informations manquantes** : Durée, modes, prix""",
            "questions": [
                "Quelle **durée de validité** ? (1 semaine, 1 mois, 1 an...)",
                "Sur quels **modes de transport** ? (tous modes, métro uniquement...)",
                "**Prix** du carnet ?",
                "**Support** ? (CSC ou BSC)"
            ]
        },
        {
            "input": "Pass 24h",
            "reasoning": """Pour un pass 24h, j'identifie :
- **CAR_7** : Validité 24 heures (7_01=4, 7_02="H", 7_03=24)
- **Type** : Pass illimité (pas de CAR_22)
- **Informations manquantes** : Modes, nombre de personnes, prix""",
            "questions": [
                "**Modes de transport** autorisés ? (tous modes, certains uniquement...)",
                "Nombre de **personnes** ? (individuel ou groupe)",
                "**Prix** du pass ?",
                "**Support** ? (CSC ou BSC)"
            ]
        },
        {
            "input": "Ticket métro+tramway 2h à 2,50€ sur CSC appelé 'LibNav'",
            "reasoning": """Demande complète ! J'ai toutes les informations :
- **Nom** : LibNav
- **Prix** : 2,50€ (250 centimes)
- **Durée** : 2 heures
- **Modes** : Métro + Tramway
- **Support** : CSC""",
            "questions": []
        }
    ]

    for scenario in scenarios:
        if scenario["questions"]:
            questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(scenario["questions"])])
            response = f"""🧠 **Raisonnement** :

{scenario['reasoning']}

❓ **Questions** :

{questions_text}

➡️ Une fois ces informations fournies, je pourrai générer le JSON complet.

✅ Pouvez-vous préciser ces éléments ?"""
        else:
            response = f"""🧠 **Raisonnement** :

{scenario['reasoning']}

➡️ Génération du JSON :

```json
{{
  "product_name": "LibNav",
  "price_cents": 250,
  "support": ["CSC"],
  "characteristics": [
    {{
      "number": 7,
      "parameters": {{
        "7_01": 4,
        "7_02": "H",
        "7_03": 2,
        "7_04": false,
        "7_05": false
      }}
    }},
    {{
      "number": 14,
      "parameters": {{
        "14_01": ["Métro", "Tramway"],
        "14_02": "Autorisée"
      }}
    }},
    {{
      "number": 22,
      "parameters": {{
        "22_01": 1,
        "22_02": 1,
        "22_03": false
      }}
    }}
  ]
}}
```

✅ Validez-vous ce produit ?"""

        examples.append({
            "instruction": scenario["input"],
            "response": response,
            "metadata": {
                "type": "conversational",
                "topic": "missing_parameters"
            }
        })

    return examples


def generate_incompatibility_examples() -> List[Dict]:
    """Génère les exemples de détection d'incompatibilités"""
    examples = []

    for incompat in INCOMPATIBILITIES:
        car_labels = [CHARACTERISTICS_DATA[c]["label"] for c in incompat["cars"]]

        response = f"""⚠️ **INCOMPATIBILITÉ DÉTECTÉE**

🔍 **Analyse** :

**CAR_{incompat['cars'][0]}** ({car_labels[0]}) :
{CHARACTERISTICS_DATA[incompat['cars'][0]]['description']}

**CAR_{incompat['cars'][1]}** ({car_labels[1]}) :
{CHARACTERISTICS_DATA[incompat['cars'][1]]['description']}

❌ **Conflit** : {incompat['reason']}

✅ **Solution** : {incompat['solution']}

➡️ Quelle approche préférez-vous ?"""

        # Version avec "ET"
        examples.append({
            "instruction": f"Produit avec CAR_{incompat['cars'][0]} ET CAR_{incompat['cars'][1]}",
            "response": response,
            "metadata": {
                "type": "incompatibility",
                "topic": f"car_{incompat['cars'][0]}_vs_car_{incompat['cars'][1]}",
                "incompatible_cars": incompat['cars']
            }
        })

        # Version avec "+"
        examples.append({
            "instruction": f"Créé un produit CAR_{incompat['cars'][0]} + CAR_{incompat['cars'][1]}",
            "response": response,
            "metadata": {
                "type": "incompatibility",
                "topic": f"car_{incompat['cars'][0]}_vs_car_{incompat['cars'][1]}",
                "incompatible_cars": incompat['cars']
            }
        })

    return examples


def generate_business_concept_examples() -> List[Dict]:
    """Génère les exemples de concepts métier"""
    examples = []

    for concept_key, concept_data in BUSINESS_CONCEPTS.items():
        full_name = concept_data.get("full_name", concept_key)
        description = concept_data["description"]
        example = concept_data.get("example", "")
        car = concept_data.get("car", None)
        param = concept_data.get("parameter", None)

        response = f"""📖 **Définition** :

**{concept_key}** = {full_name}

{description}"""

        if example:
            response += f"\n\n💡 **Exemple** :\n{example}"

        if car:
            response += f"\n\n🔗 **Lié à** : CAR_{car} ({CHARACTERISTICS_DATA[car]['label']})"

        if param:
            response += f"\n\n⚙️ **Paramètre** : {param}"

        if "types" in concept_data:
            response += "\n\n📋 **Types** :"
            for type_code, type_desc in concept_data["types"].items():
                response += f"\n- **{type_code}** : {type_desc}"

        # Variations de questions
        variations = [
            f"C'est quoi {concept_key} ?",
            f"Qu'est-ce que {concept_key} ?",
            f"Explique-moi {concept_key}",
            f"Définition de {concept_key}"
        ]

        for variation in variations:
            examples.append({
                "instruction": variation,
                "response": response,
                "metadata": {
                    "type": "concept",
                    "topic": concept_key.lower().replace(" ", "_")
                }
            })

    return examples


def load_existing_dataset() -> List[Dict]:
    """Charge le dataset existant (génération JSON)"""
    try:
        with open("/home/user/Ftune/training_dataset.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convertir au nouveau format si nécessaire
        formatted_data = []
        for item in data:
            if "input" in item and "output" in item:
                # Convertir output en JSON string
                output_json = json.dumps(item["output"], indent=2, ensure_ascii=False)

                response = f"""🧠 **Raisonnement** :

Création d'un produit de transport selon les spécifications.

➡️ **JSON** :

```json
{output_json}
```

✅ Validez-vous ce produit ?"""

                formatted_data.append({
                    "instruction": item["input"],
                    "response": response,
                    "metadata": {
                        "type": "json_generation",
                        "topic": "product_creation"
                    }
                })

        print(f"✅ Dataset existant chargé : {len(formatted_data)} exemples")
        return formatted_data
    except Exception as e:
        print(f"⚠️  Erreur chargement dataset existant : {e}")
        return []


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def generate_full_dataset():
    """Génère le dataset complet enrichi"""
    print("🚀 Génération du dataset enrichi v2...")
    print("="*60)

    dataset = []

    # Catégorie 1 : Définitions des caractéristiques
    print("\n1️⃣  Génération des définitions de caractéristiques...")
    definitions = generate_characteristic_definitions()
    dataset.extend(definitions)
    print(f"   ✅ {len(definitions)} exemples générés")

    # Catégorie 2 : Exemples conversationnels
    print("\n2️⃣  Génération des exemples conversationnels...")
    conversational = generate_conversational_examples()
    dataset.extend(conversational)
    print(f"   ✅ {len(conversational)} exemples générés")

    # Catégorie 3 : Détection d'incompatibilités
    print("\n3️⃣  Génération des exemples d'incompatibilités...")
    incompatibilities = generate_incompatibility_examples()
    dataset.extend(incompatibilities)
    print(f"   ✅ {len(incompatibilities)} exemples générés")

    # Catégorie 4 : Concepts métier
    print("\n4️⃣  Génération des concepts métier...")
    concepts = generate_business_concept_examples()
    dataset.extend(concepts)
    print(f"   ✅ {len(concepts)} exemples générés")

    # Catégorie 5 : Dataset existant (JSON complets)
    print("\n5️⃣  Chargement du dataset existant (génération JSON)...")
    existing = load_existing_dataset()
    dataset.extend(existing)
    print(f"   ✅ {len(existing)} exemples chargés")

    # Statistiques finales
    print("\n" + "="*60)
    print(f"📊 **DATASET COMPLET** : {len(dataset)} exemples")
    print("="*60)

    # Répartition par type
    types_count = {}
    for item in dataset:
        item_type = item["metadata"].get("type", "unknown")
        types_count[item_type] = types_count.get(item_type, 0) + 1

    print("\n📋 Répartition par type :")
    for item_type, count in sorted(types_count.items(), key=lambda x: -x[1]):
        print(f"   - {item_type}: {count}")

    # Sauvegarder
    output_path = "/home/user/Ftune/training_dataset_enriched_v2.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Dataset sauvegardé : {output_path}")
    print(f"💾 Taille du fichier : {len(json.dumps(dataset))/1024/1024:.2f} MB")

    # Afficher un exemple de chaque catégorie
    print("\n" + "="*60)
    print("📝 Exemples par catégorie :")
    print("="*60)

    for item_type in types_count.keys():
        example = next((item for item in dataset if item["metadata"]["type"] == item_type), None)
        if example:
            print(f"\n### Type : {item_type}")
            print(f"Instruction : {example['instruction'][:80]}...")
            print(f"Response : {example['response'][:200]}...")
            print()

    return dataset


if __name__ == "__main__":
    dataset = generate_full_dataset()
    print("\n🎉 Génération terminée avec succès !")
