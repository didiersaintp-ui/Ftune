"""
Générateur de dataset d'entraînement pour la conversion
descriptions → JSON de produits de transport

Ce script génère un dataset synthétique varié pour entraîner
le modèle à reconnaître différentes formulations en français.
"""

import json
import random
from typing import List, Dict, Any

# Templates de descriptions en français
TEMPLATES = [
    # Abonnements temporels
    "Je veux un abonnement {duration} pour {modes}",
    "Créer un titre de transport valable {duration} sur {modes}",
    "Besoin d'un pass {duration} utilisable en {modes}",
    "Forfait {duration} {modes}",

    # Multi-déplacements
    "Carnet de {trips} tickets pour {modes}",
    "Je voudrais {trips} voyages sur {modes}",
    "{trips} déplacements valables {duration} en {modes}",

    # Groupes
    "Billet pour {people} personnes en {modes}",
    "Titre de groupe pour {people} passagers, {modes}",
    "Pass groupe jusqu'à {people} personnes sur {modes}",

    # Contraintes horaires
    "Abonnement {duration} valable {timerange} en {modes}",
    "Pass {duration} utilisable seulement {timerange}, {modes}",

    # Zones et lignes
    "Forfait {duration} pour les lignes {lines}",
    "Abonnement zones {zones}, {duration}",
    "Pass {duration} valable sur {lines} uniquement",

    # Combinaisons complexes
    "Je veux un {duration} avec {trips} déplacements max, utilisable {timerange} sur {modes}",
    "Créer un titre {duration} pour {people} personnes, {modes}, lignes {lines}",
    "Pass {duration} rechargeable, {trips} voyages, {modes}",
]

# Vocabulaire
DURATIONS = {
    "1 jour": {"7_02": "D", "7_03": 1},
    "24 heures": {"7_02": "H", "7_03": 24},
    "3 jours": {"7_02": "D", "7_03": 3},
    "1 semaine": {"7_02": "W", "7_03": 1},
    "1 mois": {"7_02": "M", "7_03": 1},
    "1 an": {"7_02": "M", "7_03": 12},
    "mensuel": {"7_02": "M", "7_03": 1},
    "hebdomadaire": {"7_02": "W", "7_03": 1},
    "annuel": {"7_02": "M", "7_03": 12},
}

MODES = {
    "bus": ["Bus urbain"],
    "métro": ["Métro"],
    "tramway": ["Tramway"],
    "train": ["Train"],
    "bus et métro": ["Bus urbain", "Métro"],
    "métro et tramway": ["Métro", "Tramway"],
    "bus, métro et tramway": ["Bus urbain", "Métro", "Tramway"],
    "tous modes": ["Bus urbain", "Métro", "Tramway", "Train"],
}

TIMERANGES = {
    "en semaine": {"days": "Lundi-Vendredi", "start": "00:00", "end": "23:59"},
    "le week-end": {"days": "Samedi-Dimanche", "start": "00:00", "end": "23:59"},
    "de 9h à 17h": {"days": "Lundi-Dimanche", "start": "09:00", "end": "17:00"},
    "heures de pointe": {"days": "Lundi-Vendredi", "start": "07:00", "end": "09:00"},
    "après 19h": {"days": "Lundi-Dimanche", "start": "19:00", "end": "23:59"},
}

def generate_product_name(params: Dict[str, Any]) -> str:
    """Génère un nom de produit cohérent"""
    parts = []

    if "duration" in params:
        parts.append(params["duration"])
    if "trips" in params:
        parts.append(f"{params['trips']} voyages")
    if "modes" in params:
        parts.append(params["modes"])
    if "people" in params:
        parts.append(f"Groupe {params['people']}p")

    return " ".join(parts) if parts else "Produit de transport"

def create_validity_characteristic(duration_key: str, rechargeable: bool = False) -> Dict:
    """Crée la caractéristique 7 (DDV et DEV)"""
    duration = DURATIONS[duration_key]

    return {
        "number": 7,
        "parameters": {
            "7_01": random.choice([0, 2, 4, 8]),  # Nature de validité
            "7_02": duration["7_02"],
            "7_03": duration["7_03"],
            "7_04": rechargeable,
            "7_05": rechargeable,
        }
    }

def create_trips_characteristic(trips: int, multi_user: bool = False) -> Dict:
    """Crée la caractéristique 22 ou 21 (multi-déplacements)"""
    if multi_user:
        return {
            "number": 21,
            "parameters": {
                "21_01": trips,
                "21_02": trips,
                "21_03": 0,
                "21_04": False
            }
        }
    else:
        return {
            "number": 22,
            "parameters": {
                "22_01": trips,
                "22_02": trips,
                "22_03": False
            }
        }

def create_modes_characteristic(modes_key: str, authorized: bool = True) -> Dict:
    """Crée la caractéristique 14 (modes de transport)"""
    modes = MODES[modes_key]

    return {
        "number": 14,
        "parameters": {
            "14_01": modes,
            "14_02": "Autorisée" if authorized else "Interdite"
        }
    }

def create_group_characteristic(people: int) -> Dict:
    """Crée la caractéristique 2 (groupe)"""
    return {
        "number": 2,
        "parameters": {
            "2_01": people
        }
    }

def create_timerange_characteristic(timerange_key: str) -> Dict:
    """Crée la caractéristique 9 (tranches horaires)"""
    timerange = TIMERANGES[timerange_key]

    return {
        "number": 9,
        "parameters": {
            "9_01": [timerange]
        }
    }

def create_lines_characteristic(lines: List[str]) -> Dict:
    """Crée la caractéristique 3 (lignes)"""
    return {
        "number": 3,
        "parameters": {
            "3_01": lines,
            "3_02": "Autorisée"
        }
    }

def generate_dataset_entry() -> Dict[str, Any]:
    """Génère une entrée aléatoire du dataset"""
    # Choix aléatoire des paramètres
    params = {}
    characteristics = []

    # 1. Durée (obligatoire)
    duration_key = random.choice(list(DURATIONS.keys()))
    params["duration"] = duration_key
    rechargeable = random.choice([True, False])
    characteristics.append(create_validity_characteristic(duration_key, rechargeable))

    # 2. Modes de transport (80% de chance)
    if random.random() < 0.8:
        modes_key = random.choice(list(MODES.keys()))
        params["modes"] = modes_key
        characteristics.append(create_modes_characteristic(modes_key))

    # 3. Nombre de déplacements (40% de chance)
    if random.random() < 0.4:
        trips = random.choice([1, 2, 5, 10, 20, 50])
        params["trips"] = trips
        multi_user = random.choice([True, False])
        characteristics.append(create_trips_characteristic(trips, multi_user))

    # 4. Groupe (20% de chance)
    if random.random() < 0.2:
        people = random.choice([2, 3, 4, 5, 10])
        params["people"] = people
        characteristics.append(create_group_characteristic(people))

    # 5. Tranche horaire (30% de chance)
    if random.random() < 0.3:
        timerange_key = random.choice(list(TIMERANGES.keys()))
        params["timerange"] = timerange_key
        characteristics.append(create_timerange_characteristic(timerange_key))

    # 6. Lignes (20% de chance)
    if random.random() < 0.2:
        num_lines = random.randint(1, 5)
        lines = [f"Ligne {i}" for i in random.sample(range(1, 20), num_lines)]
        params["lines"] = ", ".join(lines)
        characteristics.append(create_lines_characteristic(lines))

    # Génération de la description
    template = random.choice(TEMPLATES)
    description = template

    for key, value in params.items():
        if f"{{{key}}}" in description:
            description = description.replace(f"{{{key}}}", str(value))

    # Nettoyage de la description (suppression des placeholders non remplacés)
    import re
    description = re.sub(r'\{[^}]+\}', '', description)
    description = re.sub(r'\s+', ' ', description).strip()
    description = re.sub(r',\s*,', ',', description)

    # Génération du JSON de sortie
    output = {
        "product_name": generate_product_name(params),
        "characteristics": characteristics
    }

    return {
        "input": description,
        "output": output
    }

def generate_full_dataset(num_samples: int = 100) -> List[Dict]:
    """Génère un dataset complet"""
    dataset = []

    for _ in range(num_samples):
        try:
            entry = generate_dataset_entry()
            dataset.append(entry)
        except Exception as e:
            print(f"Erreur génération: {e}")
            continue

    return dataset

if __name__ == "__main__":
    # Génération du dataset
    print("🔄 Génération du dataset d'entraînement...")

    dataset = generate_full_dataset(200)

    print(f"✓ {len(dataset)} exemples générés")

    # Sauvegarde
    with open("training_dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print("✓ Dataset sauvegardé dans 'training_dataset.json'")

    # Affichage d'exemples
    print("\n" + "="*60)
    print("EXEMPLES GÉNÉRÉS:")
    print("="*60)

    for i, example in enumerate(dataset[:3], 1):
        print(f"\n--- Exemple {i} ---")
        print(f"Input: {example['input']}")
        print(f"Output: {json.dumps(example['output'], ensure_ascii=False, indent=2)}")
