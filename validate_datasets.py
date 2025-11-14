#!/usr/bin/env python3
"""
Script de validation des fichiers dataset JSONL
Vérifie:
- JSON valide sur chaque ligne
- Consistance des clés entre lignes
- Incohérences dans les structures
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Any

def analyze_jsonl_file(filepath: Path) -> Dict[str, Any]:
    """Analyse un fichier JSONL et retourne les statistiques et incohérences."""

    results = {
        'filepath': str(filepath),
        'filename': filepath.name,
        'total_lines': 0,
        'valid_json_lines': 0,
        'invalid_json_lines': [],
        'key_structures': defaultdict(list),  # {frozenset(keys): [line_numbers]}
        'inconsistencies': [],
        'sample_structures': {},
        'is_consistent': True
    }

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            results['total_lines'] += 1

            try:
                data = json.loads(line)
                results['valid_json_lines'] += 1

                # Extract keys
                keys = frozenset(data.keys())
                results['key_structures'][keys].append(line_num)

                # Store sample for each structure
                if keys not in results['sample_structures']:
                    results['sample_structures'][keys] = {
                        'line_number': line_num,
                        'data': data,
                        'keys': sorted(list(keys))
                    }

            except json.JSONDecodeError as e:
                results['invalid_json_lines'].append({
                    'line_number': line_num,
                    'error': str(e),
                    'content': line[:100] + '...' if len(line) > 100 else line
                })

    # Check consistency
    if len(results['key_structures']) > 1:
        results['is_consistent'] = False

        # Identify inconsistencies
        structures = list(results['key_structures'].items())
        base_keys = structures[0][0]
        base_lines = structures[0][1]

        results['inconsistencies'].append({
            'type': 'different_key_structures',
            'num_different_structures': len(structures),
            'details': []
        })

        for i, (keys, lines) in enumerate(structures):
            missing_keys = base_keys - keys
            extra_keys = keys - base_keys

            results['inconsistencies'][0]['details'].append({
                'structure_id': i + 1,
                'line_count': len(lines),
                'line_numbers': lines[:5],  # First 5 lines with this structure
                'total_affected_lines': len(lines),
                'keys': sorted(list(keys)),
                'missing_compared_to_structure_1': sorted(list(missing_keys)) if i > 0 else [],
                'extra_compared_to_structure_1': sorted(list(extra_keys)) if i > 0 else []
            })

    return results

def main():
    dataset_dir = Path('/home/user/Ftune/dataset')

    files_to_check = [
        '01_explications_cars.jsonl',
        '02_creation_produits_simples.jsonl',
        '03_clarifications_multi_tours.jsonl',
        '04_erreurs_incompatibilites.jsonl',
        '05_produits_complexes_raisonnement.jsonl',
        '06_creations_variees_supplementaires.jsonl',
        '07_explications_cars_supplementaires.jsonl',
        '08_verifications_updates_recherches.jsonl',
        '09_edge_cases_erreurs_avancees.jsonl'
    ]

    all_results = []
    problematic_files = []

    print("=" * 80)
    print("VALIDATION DES FICHIERS DATASET JSONL")
    print("=" * 80)
    print()

    for filename in files_to_check:
        filepath = dataset_dir / filename

        if not filepath.exists():
            print(f"❌ FICHIER NON TROUVÉ: {filename}")
            print()
            continue

        print(f"📂 Analyse de: {filename}")
        print("-" * 80)

        results = analyze_jsonl_file(filepath)
        all_results.append(results)

        # Summary
        print(f"   Total lignes: {results['total_lines']}")
        print(f"   JSON valides: {results['valid_json_lines']}")
        print(f"   JSON invalides: {len(results['invalid_json_lines'])}")
        print(f"   Structures différentes: {len(results['key_structures'])}")
        print(f"   Consistant: {'✅ OUI' if results['is_consistent'] else '❌ NON'}")

        if not results['is_consistent']:
            problematic_files.append(results)
            print()
            print("   ⚠️  INCOHÉRENCES DÉTECTÉES!")

        print()

    # Detailed report for problematic files
    if problematic_files:
        print()
        print("=" * 80)
        print("RAPPORT DÉTAILLÉ DES FICHIERS PROBLÉMATIQUES")
        print("=" * 80)
        print()

        for result in problematic_files:
            print(f"🔴 FICHIER: {result['filename']}")
            print("=" * 80)
            print()

            if result['invalid_json_lines']:
                print("❌ LIGNES AVEC JSON INVALIDE:")
                for invalid in result['invalid_json_lines']:
                    print(f"   Ligne {invalid['line_number']}: {invalid['error']}")
                    print(f"   Contenu: {invalid['content']}")
                print()

            if result['inconsistencies']:
                for incons in result['inconsistencies']:
                    print(f"⚠️  TYPE: {incons['type']}")
                    print(f"   Nombre de structures différentes: {incons['num_different_structures']}")
                    print()

                    for detail in incons['details']:
                        print(f"   📊 STRUCTURE #{detail['structure_id']}:")
                        print(f"      Lignes affectées: {detail['total_affected_lines']}")
                        print(f"      Exemples de lignes: {detail['line_numbers']}")
                        print(f"      Clés présentes: {detail['keys']}")

                        if detail['structure_id'] > 1:
                            if detail['missing_compared_to_structure_1']:
                                print(f"      ❌ Clés manquantes vs Structure #1: {detail['missing_compared_to_structure_1']}")
                            if detail['extra_compared_to_structure_1']:
                                print(f"      ➕ Clés supplémentaires vs Structure #1: {detail['extra_compared_to_structure_1']}")

                        # Show sample
                        keys = frozenset(detail['keys'])
                        if keys in result['sample_structures']:
                            sample = result['sample_structures'][keys]
                            print(f"      Exemple (ligne {sample['line_number']}):")
                            print(f"      {json.dumps(sample['data'], ensure_ascii=False, indent=8)}")

                        print()

            print()

    # Summary
    print()
    print("=" * 80)
    print("RÉSUMÉ FINAL")
    print("=" * 80)
    print()
    print(f"Fichiers analysés: {len(all_results)}")
    print(f"Fichiers sans problème: {len(all_results) - len(problematic_files)} ✅")
    print(f"Fichiers avec problèmes: {len(problematic_files)} ❌")
    print()

    if problematic_files:
        print("FICHIERS PROBLÉMATIQUES:")
        for result in problematic_files:
            print(f"   - {result['filename']}")
        print()

        print("ACTIONS RECOMMANDÉES:")
        print("1. Examiner les structures de clés identifiées ci-dessus")
        print("2. Décider quelle structure est la référence correcte")
        print("3. Corriger les lignes incohérentes pour uniformiser le format")
        print("4. Re-valider après correction")
    else:
        print("🎉 TOUS LES FICHIERS SONT COHÉRENTS!")

    print()

if __name__ == '__main__':
    main()
