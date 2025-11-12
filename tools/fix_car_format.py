#!/usr/bin/env python3
"""
Script pour convertir les CAR_X en entiers dans les metadata
Corrige : "cars": ["CAR_7", "CAR_14"] → "cars": [7, 14]
"""

import json
import sys
import re
import os
from pathlib import Path

def convert_car_to_int(value):
    """Convertit 'CAR_X' en X (entier)"""
    if isinstance(value, str) and value.startswith("CAR_"):
        try:
            return int(value.replace("CAR_", ""))
        except ValueError:
            return value
    return value

def fix_metadata(metadata):
    """Fixe tous les champs cars/car/incompatibility dans metadata"""
    if not isinstance(metadata, dict):
        return metadata

    fixed = metadata.copy()

    # Fixer 'cars' (pluriel, liste)
    if "cars" in fixed and isinstance(fixed["cars"], list):
        fixed["cars"] = [convert_car_to_int(car) for car in fixed["cars"]]

    # Fixer 'car' (singulier, string)
    if "car" in fixed:
        fixed["car"] = convert_car_to_int(fixed["car"])

    # Fixer 'incompatibility'
    if "incompatibility" in fixed and isinstance(fixed["incompatibility"], list):
        fixed["incompatibility"] = [convert_car_to_int(car) for car in fixed["incompatibility"]]

    # Fixer 'caracteristique_id' (si string)
    if "caracteristique_id" in fixed:
        fixed["caracteristique_id"] = convert_car_to_int(fixed["caracteristique_id"])

    # Fixer 'caracteristiques' (si liste de strings)
    if "caracteristiques" in fixed and isinstance(fixed["caracteristiques"], list):
        fixed["caracteristiques"] = [convert_car_to_int(car) for car in fixed["caracteristiques"]]

    return fixed

def fix_jsonl_file(input_path, output_path):
    """Corrige un fichier JSONL"""
    fixed_count = 0
    total_count = 0

    # Lire toutes les lignes d'abord
    lines = []
    with open(input_path, 'r', encoding='utf-8') as fin:
        for line in fin:
            if line.strip():
                lines.append(line)

    # Écrire les lignes corrigées
    with open(output_path, 'w', encoding='utf-8') as fout:
        for line in lines:
            total_count += 1
            try:
                data = json.loads(line)

                # Fixer metadata si présent
                if "metadata" in data:
                    original_metadata = json.dumps(data["metadata"], sort_keys=True)
                    data["metadata"] = fix_metadata(data["metadata"])
                    new_metadata = json.dumps(data["metadata"], sort_keys=True)

                    if original_metadata != new_metadata:
                        fixed_count += 1

                # Écrire la ligne corrigée
                fout.write(json.dumps(data, ensure_ascii=False) + '\n')

            except json.JSONDecodeError as e:
                print(f"⚠️  Ligne {total_count} invalide: {e}", file=sys.stderr)
                fout.write(line)  # Garder la ligne originale si erreur

    return fixed_count, total_count

def fix_json_file(input_path, output_path):
    """Corrige un fichier JSON (liste)"""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        return 0, 0

    fixed_count = 0
    for item in data:
        if "metadata" in item:
            original_metadata = json.dumps(item["metadata"], sort_keys=True)
            item["metadata"] = fix_metadata(item["metadata"])
            new_metadata = json.dumps(item["metadata"], sort_keys=True)

            if original_metadata != new_metadata:
                fixed_count += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return fixed_count, len(data)

def main():
    dataset_dir = Path("/home/user/Ftune/dataset")

    # Trouver tous les fichiers JSON/JSONL
    import glob
    os.chdir(dataset_dir)
    files_to_fix = sorted(glob.glob("*.jsonl")) + sorted(glob.glob("*.json"))

    # Exclure les backups et README
    files_to_fix = [f for f in files_to_fix if "backup" not in f.lower() and "readme" not in f.lower()]

    print("🔧 CORRECTION DES FORMATS CAR_X → X (TOUS CHAMPS)")
    print("="*60)
    print(f"Fichiers à traiter: {len(files_to_fix)}")
    print("Champs corrigés: cars, car, incompatibility, caracteristique_id, caracteristiques")
    print("="*60)

    total_fixed = 0
    total_processed = 0

    for filename in files_to_fix:
        input_path = dataset_dir / filename
        if not input_path.exists():
            print(f"⚠️  {filename} non trouvé")
            continue

        # Créer un backup
        backup_path = dataset_dir / f"{filename}.backup"
        import shutil
        shutil.copy2(input_path, backup_path)

        # Fixer le fichier
        print(f"\n📝 {filename}...")

        if filename.endswith('.jsonl'):
            fixed, total = fix_jsonl_file(input_path, input_path)
        else:
            fixed, total = fix_json_file(input_path, input_path)

        if fixed > 0:
            print(f"   ✅ {fixed}/{total} lignes corrigées")
        else:
            print(f"   ⏭️  {total} lignes (déjà correctes)")

        total_fixed += fixed
        total_processed += total

    print("\n" + "="*60)
    print(f"🎉 TERMINÉ: {total_fixed}/{total_processed} lignes corrigées")
    print(f"💾 Backups créés: *.backup")
    print("="*60)

if __name__ == "__main__":
    main()
