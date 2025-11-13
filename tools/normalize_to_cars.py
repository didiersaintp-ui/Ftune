#!/usr/bin/env python3
"""
Script de normalisation COMPLÈTE des champs CAR
Uniformise TOUS les champs vers "cars": [...]

Transformations:
- "car": 48                    → "cars": [48]
- "caracteristiques": [7, 14]  → "cars": [7, 14]
- "caracteristique_id": 8      → "cars": [8]
- Pas de champ CAR             → "cars": []
- "incompatibility": [...]     → reste inchangé (concept différent)
"""

import json
import sys
import os
import glob
from pathlib import Path

def normalize_metadata_to_cars(metadata):
    """
    Normalise tous les champs CAR vers "cars": [...]

    Règles:
    1. Si "cars" existe déjà → le garder (déjà liste)
    2. Si "car" existe → convertir en liste et renommer vers "cars"
    3. Si "caracteristiques" existe → renommer vers "cars"
    4. Si "caracteristique_id" existe → convertir en liste et renommer vers "cars"
    5. Si aucun champ → ajouter "cars": []
    6. "incompatibility" reste inchangé
    """
    normalized = metadata.copy()

    # Cas 1: "cars" existe déjà (rien à faire, déjà normalisé)
    if "cars" in normalized:
        # Vérifier que c'est bien une liste
        if not isinstance(normalized["cars"], list):
            normalized["cars"] = [normalized["cars"]]
        return normalized

    # Cas 2: "caracteristiques" existe → renommer vers "cars"
    if "caracteristiques" in normalized:
        normalized["cars"] = normalized["caracteristiques"]
        del normalized["caracteristiques"]
        # Vérifier que c'est une liste
        if not isinstance(normalized["cars"], list):
            normalized["cars"] = [normalized["cars"]]
        return normalized

    # Cas 3: "car" existe (singulier) → convertir en liste et renommer
    if "car" in normalized:
        normalized["cars"] = [normalized["car"]]
        del normalized["car"]
        return normalized

    # Cas 4: "caracteristique_id" existe → convertir en liste et renommer
    if "caracteristique_id" in normalized:
        normalized["cars"] = [normalized["caracteristique_id"]]
        del normalized["caracteristique_id"]
        return normalized

    # Cas 5: Aucun champ CAR → ajouter "cars": []
    normalized["cars"] = []

    return normalized

def process_file(input_path, output_path):
    """
    Traite un fichier JSON/JSONL et normalise tous les metadata vers "cars"

    Returns:
        tuple: (total_lines, normalized_lines)
    """
    total_lines = 0
    normalized_lines = 0

    # Lire toutes les lignes d'abord
    lines = []

    if input_path.endswith('.jsonl'):
        # Format JSONL
        with open(input_path, 'r', encoding='utf-8') as fin:
            for line in fin:
                if line.strip():
                    lines.append(line)

        # Traiter et écrire
        with open(output_path, 'w', encoding='utf-8') as fout:
            for line in lines:
                total_lines += 1
                data = json.loads(line)

                if 'metadata' in data:
                    original_metadata = json.dumps(data['metadata'], sort_keys=True)
                    data['metadata'] = normalize_metadata_to_cars(data['metadata'])
                    new_metadata = json.dumps(data['metadata'], sort_keys=True)

                    if original_metadata != new_metadata:
                        normalized_lines += 1

                fout.write(json.dumps(data, ensure_ascii=False) + '\n')

    else:
        # Format JSON
        with open(input_path, 'r', encoding='utf-8') as fin:
            data = json.load(fin)

        if isinstance(data, list):
            for item in data:
                total_lines += 1
                if 'metadata' in item:
                    original_metadata = json.dumps(item['metadata'], sort_keys=True)
                    item['metadata'] = normalize_metadata_to_cars(item['metadata'])
                    new_metadata = json.dumps(item['metadata'], sort_keys=True)

                    if original_metadata != new_metadata:
                        normalized_lines += 1

        with open(output_path, 'w', encoding='utf-8') as fout:
            json.dump(data, fout, ensure_ascii=False, indent=2)

    return total_lines, normalized_lines

def main():
    print("🔄 NORMALISATION COMPLÈTE VERS 'cars': [...]")
    print("=" * 70)
    print("Transformations:")
    print("  • 'car': 48                   → 'cars': [48]")
    print("  • 'caracteristiques': [7,14]  → 'cars': [7,14]")
    print("  • 'caracteristique_id': 8     → 'cars': [8]")
    print("  • Aucun champ                 → 'cars': []")
    print("  • 'incompatibility'           → inchangé")
    print("=" * 70)
    print()

    # Déterminer le répertoire dataset
    if len(sys.argv) > 1:
        dataset_dir = sys.argv[1]
    else:
        dataset_dir = "dataset"

    if not os.path.exists(dataset_dir):
        print(f"❌ Erreur: répertoire '{dataset_dir}' introuvable")
        sys.exit(1)

    # Trouver tous les fichiers JSON/JSONL
    os.chdir(dataset_dir)
    files_to_normalize = sorted(glob.glob("*.jsonl")) + sorted(glob.glob("*.json"))

    # Exclure les backups et README
    files_to_normalize = [f for f in files_to_normalize if "backup" not in f.lower() and "readme" not in f.lower()]

    print(f"Fichiers à traiter: {len(files_to_normalize)}")
    print("=" * 70)
    print()

    total_all = 0
    normalized_all = 0

    for filename in files_to_normalize:
        print(f"📝 {filename}...")

        # Créer un backup
        backup_name = f"{filename}.backup_prenorm"
        if not os.path.exists(backup_name):
            import shutil
            shutil.copy2(filename, backup_name)

        # Traiter le fichier
        total, normalized = process_file(filename, filename)

        total_all += total
        normalized_all += normalized

        if normalized > 0:
            print(f"   ✅ {normalized}/{total} entrées normalisées")
        else:
            print(f"   ⏭️  {total} entrées (déjà normalisées)")
        print()

    print("=" * 70)
    print(f"🎉 TERMINÉ: {normalized_all}/{total_all} entrées normalisées")
    print(f"💾 Backups créés: *.backup_prenorm")
    print("=" * 70)

    # Validation finale
    print()
    print("🔍 VALIDATION FINALE")
    print("=" * 70)

    validation_errors = 0
    entries_without_cars = 0

    for filename in files_to_normalize:
        with open(filename, 'r', encoding='utf-8') as f:
            if filename.endswith('.jsonl'):
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        data = json.loads(line)
                        if 'metadata' in data:
                            # Vérifier que "cars" existe
                            if "cars" not in data['metadata']:
                                validation_errors += 1
                                print(f"❌ {filename}:{line_num} - Pas de champ 'cars'")
                                entries_without_cars += 1
                            else:
                                # Vérifier que "cars" est une liste
                                if not isinstance(data['metadata']['cars'], list):
                                    validation_errors += 1
                                    print(f"❌ {filename}:{line_num} - 'cars' n'est pas une liste")
                                # Vérifier que tous les éléments sont des entiers
                                for car in data['metadata']['cars']:
                                    if not isinstance(car, int):
                                        validation_errors += 1
                                        print(f"❌ {filename}:{line_num} - 'cars' contient non-entier: {car}")

                            # Vérifier qu'il n'y a plus de champs anciens
                            for old_field in ['car', 'caracteristiques', 'caracteristique_id']:
                                if old_field in data['metadata']:
                                    validation_errors += 1
                                    print(f"❌ {filename}:{line_num} - Ancien champ '{old_field}' encore présent")
            else:
                data = json.load(f)
                if isinstance(data, list):
                    for i, item in enumerate(data, 1):
                        if 'metadata' in item:
                            if "cars" not in item['metadata']:
                                validation_errors += 1
                                print(f"❌ {filename}:{i} - Pas de champ 'cars'")
                                entries_without_cars += 1
                            else:
                                if not isinstance(item['metadata']['cars'], list):
                                    validation_errors += 1
                                    print(f"❌ {filename}:{i} - 'cars' n'est pas une liste")
                                for car in item['metadata']['cars']:
                                    if not isinstance(car, int):
                                        validation_errors += 1
                                        print(f"❌ {filename}:{i} - 'cars' contient non-entier: {car}")

                            for old_field in ['car', 'caracteristiques', 'caracteristique_id']:
                                if old_field in item['metadata']:
                                    validation_errors += 1
                                    print(f"❌ {filename}:{i} - Ancien champ '{old_field}' encore présent")

    if validation_errors == 0:
        print(f"✅ PARFAIT: Tous les {total_all} exemples ont 'cars': [...]")
        print(f"✅ Entrées avec 'cars': [] (sans CAR): {entries_without_cars}")
    else:
        print(f"⚠️ {validation_errors} erreurs de validation détectées")

    print("=" * 70)

if __name__ == "__main__":
    main()
