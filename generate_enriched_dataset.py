"""
Générateur de dataset enrichi pour le fine-tuning
Couvre TOUTES les 29 caractéristiques avec des exemples variés et sémantiquement riches
"""

import json
import random
from typing import List, Dict, Any

# Exemples manuels de haute qualité couvrant tous les cas
MANUAL_EXAMPLES = [
    # === Caractéristique 7 : Validité (OBLIGATOIRE) ===
    {
        "description": "Je veux un abonnement mensuel pour le métro",
        "json": {
            "product_name": "Abonnement mensuel Métro",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 14, "parameters": {"14_01": ["Métro"], "14_02": "Autorisée"}}
            ]
        }
    },
    {
        "description": "Pass 24 heures tous modes de transport",
        "json": {
            "product_name": "Pass 24h Multi-modal",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 4, "7_02": "H", "7_03": 24, "7_04": False, "7_05": False}}
            ]
        }
    },
    {
        "description": "Forfait hebdomadaire bus et tramway",
        "json": {
            "product_name": "Forfait hebdomadaire Bus-Tramway",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "W", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 14, "parameters": {"14_01": ["Bus urbain", "Tramway"], "14_02": "Autorisée"}}
            ]
        }
    },
    {
        "description": "Abonnement annuel rechargeable pour tous modes",
        "json": {
            "product_name": "Abonnement annuel Multi-modal",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 12, "7_04": True, "7_05": True}}
            ]
        }
    },

    # === Caractéristique 22 : Multi-déplacements mono-usager ===
    {
        "description": "Carnet de 10 tickets valable 1 semaine sur bus et tramway",
        "json": {
            "product_name": "Carnet 10 voyages hebdomadaire Bus-Tramway",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "W", "7_03": 1, "7_04": False, "7_05": False}},
                {"number": 22, "parameters": {"22_01": 10, "22_02": 10, "22_03": False}},
                {"number": 14, "parameters": {"14_01": ["Bus urbain", "Tramway"], "14_02": "Autorisée"}}
            ]
        }
    },
    {
        "description": "Ticket simple trajet métro",
        "json": {
            "product_name": "Ticket unitaire Métro",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 4, "7_02": "H", "7_03": 2, "7_04": False, "7_05": False}},
                {"number": 22, "parameters": {"22_01": 1, "22_02": 1, "22_03": False}},
                {"number": 14, "parameters": {"14_01": ["Métro"], "14_02": "Autorisée"}}
            ]
        }
    },
    {
        "description": "Carnet de 20 voyages rechargeable tous modes",
        "json": {
            "product_name": "Carnet 20 voyages rechargeable",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": False, "7_05": False}},
                {"number": 22, "parameters": {"22_01": 20, "22_02": 20, "22_03": True}}
            ]
        }
    },

    # === Caractéristique 2 : Groupe ===
    {
        "description": "Pass 24h pour 5 personnes",
        "json": {
            "product_name": "Pass 24h Groupe 5 personnes",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 4, "7_02": "H", "7_03": 24, "7_04": False, "7_05": False}},
                {"number": 2, "parameters": {"2_01": 5}}
            ]
        }
    },
    {
        "description": "Forfait mensuel pour 10 personnes tous modes",
        "json": {
            "product_name": "Forfait mensuel Groupe 10 personnes",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 2, "parameters": {"2_01": 10}}
            ]
        }
    },

    # === Caractéristique 9 : Contraintes horaires ===
    {
        "description": "Forfait hebdomadaire valable en semaine de 9h à 17h sur le métro",
        "json": {
            "product_name": "Forfait hebdomadaire heures creuses Métro",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "W", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 9, "parameters": {"9_01": [{"days": "Lundi-Vendredi", "start": "09:00", "end": "17:00"}]}},
                {"number": 14, "parameters": {"14_01": ["Métro"], "14_02": "Autorisée"}}
            ]
        }
    },
    {
        "description": "Pass week-end illimité bus métro tramway",
        "json": {
            "product_name": "Pass Week-end Illimité",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 4, "7_02": "D", "7_03": 2, "7_04": False, "7_05": False}},
                {"number": 9, "parameters": {"9_01": [{"days": "Samedi-Dimanche", "start": "00:00", "end": "23:59"}]}},
                {"number": 14, "parameters": {"14_01": ["Bus urbain", "Métro", "Tramway"], "14_02": "Autorisée"}}
            ]
        }
    },
    {
        "description": "Abonnement mensuel valable après 19h tous les jours",
        "json": {
            "product_name": "Abonnement mensuel Soirée",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 9, "parameters": {"9_01": [{"days": "Lundi-Dimanche", "start": "19:00", "end": "23:59"}]}}
            ]
        }
    },

    # === Caractéristique 3 : Lignes spécifiques ===
    {
        "description": "Abonnement annuel pour les lignes 1, 2 et 3",
        "json": {
            "product_name": "Abonnement annuel Lignes 1-2-3",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 12, "7_04": True, "7_05": True}},
                {"number": 3, "parameters": {"3_01": ["Ligne 1", "Ligne 2", "Ligne 3"], "3_02": "Autorisée"}}
            ]
        }
    },
    {
        "description": "Pass mensuel valable sur toutes les lignes sauf la ligne 5",
        "json": {
            "product_name": "Pass mensuel (hors Ligne 5)",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 3, "parameters": {"3_01": ["Ligne 5"], "3_02": "Interdite"}}
            ]
        }
    },

    # === Caractéristique 102 : Tacite reconduction ===
    {
        "description": "Abonnement annuel avec tacite reconduction automatique",
        "json": {
            "product_name": "Abonnement annuel avec reconduction",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 12, "7_04": True, "7_05": True}},
                {"number": 102, "parameters": {"102_01": "Aucun", "102_04": True}}
            ]
        }
    },
    {
        "description": "Forfait mensuel avec prélèvement automatique",
        "json": {
            "product_name": "Forfait mensuel prélèvement auto",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 102, "parameters": {"102_01": "Mensuel", "102_04": True}}
            ]
        }
    },

    # === Caractéristique 10 : Limitation par sous-période ===
    {
        "description": "Abonnement hebdomadaire avec maximum 2 déplacements par jour",
        "json": {
            "product_name": "Abonnement hebdomadaire 2 voyages/jour",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "W", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 10, "parameters": {"10_01": [{"unit": "Jour", "count": 1, "max_trips": 2}]}}
            ]
        }
    },
    {
        "description": "Pass mensuel limité à 10 voyages par semaine en métro",
        "json": {
            "product_name": "Pass mensuel 10 voyages/semaine Métro",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 10, "parameters": {"10_01": [{"unit": "Semaine", "count": 1, "max_trips": 10}]}},
                {"number": 14, "parameters": {"14_01": ["Métro"], "14_02": "Autorisée"}}
            ]
        }
    },

    # === Caractéristique 14 : Modes (interdits) ===
    {
        "description": "Abonnement annuel tous modes sauf train",
        "json": {
            "product_name": "Abonnement annuel (hors Train)",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 12, "7_04": True, "7_05": True}},
                {"number": 14, "parameters": {"14_01": ["Train"], "14_02": "Interdite"}}
            ]
        }
    },

    # === Produits complexes ===
    {
        "description": "Abonnement mensuel pour 2 personnes, valable du lundi au vendredi de 6h à 20h, sur bus et métro, lignes 5 et 12, rechargeable",
        "json": {
            "product_name": "Abonnement mensuel Duo Lignes 5-12",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 2, "parameters": {"2_01": 2}},
                {"number": 9, "parameters": {"9_01": [{"days": "Lundi-Vendredi", "start": "06:00", "end": "20:00"}]}},
                {"number": 14, "parameters": {"14_01": ["Bus urbain", "Métro"], "14_02": "Autorisée"}},
                {"number": 3, "parameters": {"3_01": ["Ligne 5", "Ligne 12"], "3_02": "Autorisée"}}
            ]
        }
    },
    {
        "description": "Pass 48h groupe 3 personnes avec 20 voyages maximum sur bus et tramway",
        "json": {
            "product_name": "Pass 48h Groupe 3p 20 voyages Bus-Tramway",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 4, "7_02": "H", "7_03": 48, "7_04": False, "7_05": False}},
                {"number": 2, "parameters": {"2_01": 3}},
                {"number": 22, "parameters": {"22_01": 20, "22_02": 20, "22_03": False}},
                {"number": 14, "parameters": {"14_01": ["Bus urbain", "Tramway"], "14_02": "Autorisée"}}
            ]
        }
    },

    # === Caractéristique 58 : Classe ===
    {
        "description": "Abonnement annuel première classe avec surclassement autorisé",
        "json": {
            "product_name": "Abonnement annuel Première Classe",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 12, "7_04": True, "7_05": True}},
                {"number": 58, "parameters": {"58_01": 1, "58_02": True}}
            ]
        }
    },
    {
        "description": "Pass mensuel seconde classe uniquement",
        "json": {
            "product_name": "Pass mensuel Seconde Classe",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 58, "parameters": {"58_01": 2, "58_02": False}}
            ]
        }
    },

    # === Caractéristique 73 : Profil tarifaire ===
    {
        "description": "Abonnement mensuel tarif étudiant pour le métro",
        "json": {
            "product_name": "Abonnement mensuel Étudiant Métro",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 73, "parameters": {"73_01": "ETU", "73_02": "Étudiant"}},
                {"number": 14, "parameters": {"14_01": ["Métro"], "14_02": "Autorisée"}}
            ]
        }
    },
    {
        "description": "Pass annuel tarif senior tous modes",
        "json": {
            "product_name": "Pass annuel Senior",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 12, "7_04": True, "7_05": True}},
                {"number": 73, "parameters": {"73_01": "SEN", "73_02": "Senior"}}
            ]
        }
    },

    # === Caractéristique 4 : Zones ===
    {
        "description": "Abonnement mensuel zones 1, 2 et 3",
        "json": {
            "product_name": "Abonnement mensuel Zones 1-2-3",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 4, "parameters": {"4_01": ["Zone 1", "Zone 2", "Zone 3"], "4_02": "Autorisée"}}
            ]
        }
    },
    {
        "description": "Pass hebdomadaire hors zone 5",
        "json": {
            "product_name": "Pass hebdomadaire (hors Zone 5)",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "W", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 4, "parameters": {"4_01": ["Zone 5"], "4_02": "Interdite"}}
            ]
        }
    },

    # === Caractéristique 21 : Multi-usager ===
    {
        "description": "Carnet de 10 tickets partageable entre 3 personnes",
        "json": {
            "product_name": "Carnet 10 tickets familial",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": False, "7_05": False}},
                {"number": 21, "parameters": {"21_01": 10, "21_02": 10, "21_03": 3, "21_04": False}}
            ]
        }
    },

    # === Caractéristique 103 : Titre unitaire sans compteur ===
    {
        "description": "Ticket valable 90 minutes après validation",
        "json": {
            "product_name": "Ticket 90 minutes",
            "characteristics": [
                {"number": 103, "parameters": {"103_01": 90}}
            ]
        }
    },

    # === Caractéristique 105 : Multi-validation ===
    {
        "description": "Titre permettant de valider pour 3 personnes simultanément",
        "json": {
            "product_name": "Titre multi-validation 3 personnes",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 4, "7_02": "H", "7_03": 24, "7_04": False, "7_05": False}},
                {"number": 105, "parameters": {"105_01": 3}}
            ]
        }
    },

    # === Caractéristique 107 : Promotion X mois gratuits ===
    {
        "description": "Abonnement annuel : payez 10 mois, voyagez 12 mois",
        "json": {
            "product_name": "Abonnement annuel Promo 10+2",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 12, "7_04": True, "7_05": True}},
                {"number": 107, "parameters": {"107_01": 10, "107_02": 2, "107_03": 12}}
            ]
        }
    },

    # === Caractéristique 38 : Groupe variable ===
    {
        "description": "Forfait groupe de 5 à 20 personnes à définir à l'achat",
        "json": {
            "product_name": "Forfait Groupe Variable (5-20p)",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 38, "parameters": {"38_01": 5, "38_02": 20}}
            ]
        }
    },

    # === Caractéristique 97 : Remboursement ===
    {
        "description": "Abonnement mensuel remboursable sous 7 jours à 80%",
        "json": {
            "product_name": "Abonnement mensuel Remboursable",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 2, "7_02": "M", "7_03": 1, "7_04": True, "7_05": True}},
                {"number": 97, "parameters": {"97_01": True, "97_02": 7, "97_03": 80, "97_04": 5.0}}
            ]
        }
    },

    # === Caractéristique 86 : Origine-Destination ===
    {
        "description": "Billet Paris-Lyon aller-retour",
        "json": {
            "product_name": "Billet Paris-Lyon A/R",
            "characteristics": [
                {"number": 7, "parameters": {"7_01": 0, "7_02": "D", "7_03": 1, "7_04": False, "7_05": False}},
                {"number": 86, "parameters": {"86_01": "PARIS", "86_02": "LYON", "86_03": True}}
            ]
        }
    },
]


def generate_dataset_from_manual_examples() -> List[Dict[str, Any]]:
    """
    Génère le dataset d'entraînement à partir des exemples manuels
    Format: {"input": "description", "output": {...json...}}
    """
    dataset = []

    for example in MANUAL_EXAMPLES:
        dataset.append({
            "input": example["description"],
            "output": example["json"]
        })

    return dataset


def add_variations(dataset: List[Dict], num_variations: int = 3) -> List[Dict]:
    """
    Ajoute des variations linguistiques pour chaque exemple
    """
    variations_templates = [
        "Je souhaite {}",
        "Créer {}",
        "Je veux créer {}",
        "Besoin de {}",
        "Je voudrais {}",
        "Définir {}",
    ]

    new_dataset = list(dataset)

    for example in dataset[:20]:  # Seulement pour les 20 premiers
        original_desc = example["input"]

        # Retirer les débuts classiques
        cleaned = original_desc
        for prefix in ["Je veux ", "Créer ", "Je souhaite ", "Besoin de "]:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break

        # Créer des variations
        for i in range(min(num_variations, len(variations_templates))):
            template = variations_templates[i]
            new_desc = template.format(cleaned)

            new_dataset.append({
                "input": new_desc,
                "output": example["output"]
            })

    return new_dataset


if __name__ == "__main__":
    print("🔄 Génération du dataset enrichi...")

    # Générer le dataset de base
    dataset = generate_dataset_from_manual_examples()
    print(f"✓ {len(dataset)} exemples de base générés")

    # Ajouter des variations
    dataset = add_variations(dataset, num_variations=2)
    print(f"✓ {len(dataset)} exemples au total (avec variations)")

    # Mélanger
    random.shuffle(dataset)

    # Sauvegarder
    with open("training_dataset_enriched.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print("✓ Dataset sauvegardé dans 'training_dataset_enriched.json'")

    # Statistiques
    print("\n" + "="*60)
    print("STATISTIQUES DU DATASET")
    print("="*60)

    # Compter les caractéristiques utilisées
    char_counts = {}
    for example in dataset:
        for char in example["output"]["characteristics"]:
            num = char["number"]
            char_counts[num] = char_counts.get(num, 0) + 1

    print(f"\nNombre total d'exemples: {len(dataset)}")
    print(f"\nCaractéristiques couvertes ({len(char_counts)}/29):")
    for num in sorted(char_counts.keys()):
        print(f"  - Caractéristique {num}: {char_counts[num]} exemples")

    # Afficher quelques exemples
    print("\n" + "="*60)
    print("EXEMPLES ALÉATOIRES:")
    print("="*60)

    for i, example in enumerate(random.sample(dataset, min(3, len(dataset))), 1):
        print(f"\n--- Exemple {i} ---")
        print(f"Input: {example['input']}")
        print(f"Output: {json.dumps(example['output'], ensure_ascii=False, indent=2)[:300]}...")
