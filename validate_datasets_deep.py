#!/usr/bin/env python3
"""
Validation approfondie des datasets JSONL
Vérifie:
- Structure des métadonnées
- Cohérence des valeurs dans les métadonnées
- Types de données attendus
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any

def deep_analyze_jsonl(filepath: Path) -> Dict[str, Any]:
    """Analyse approfondie d'un fichier JSONL."""

    results = {
        'filepath': str(filepath),
        'filename': filepath.name,
        'total_lines': 0,
        'metadata_analysis': {
            'all_fields': Counter(),
            'field_values': defaultdict(Counter),
            'missing_fields': defaultdict(list),
            'unexpected_types': [],
            'issues': []
        },
        'expected_structure': {
            'instruction': 'string',
            'response': 'string',
            'metadata': 'object'
        },
        'metadata_expected_fields': {
            'type': ['string', ['explication', 'creation', 'clarification', 'verification',
                               'error_detection', 'update', 'search', 'delete', 'comparison',
                               'advanced_reasoning']],
            'topic': ['string', None],  # Any string value
            'expected_action': ['string', ['none', 'create_product', 'update_product',
                                           'delete_product', 'ask_questions', 'ask_choice',
                                           'ask_correction', 'ask_confirmation', 'propose_fix',
                                           'display_results', 'display_result', 'display_analysis',
                                           'suspend_product', 'propose_alternative', 'reject']],
            'turns': ['integer', None],
            'cars': ['list', None]
        }
    }

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            results['total_lines'] += 1

            try:
                data = json.loads(line)

                # Check top-level structure
                for field in results['expected_structure']:
                    if field not in data:
                        results['metadata_analysis']['missing_fields'][field].append(line_num)
                    else:
                        # Check type
                        expected_type = results['expected_structure'][field]
                        actual_type = type(data[field]).__name__

                        if expected_type == 'string' and actual_type != 'str':
                            results['metadata_analysis']['unexpected_types'].append({
                                'line': line_num,
                                'field': field,
                                'expected': expected_type,
                                'got': actual_type,
                                'value': str(data[field])[:50]
                            })
                        elif expected_type == 'object' and actual_type != 'dict':
                            results['metadata_analysis']['unexpected_types'].append({
                                'line': line_num,
                                'field': field,
                                'expected': expected_type,
                                'got': actual_type,
                                'value': str(data[field])[:50]
                            })

                # Analyze metadata if present
                if 'metadata' in data and isinstance(data['metadata'], dict):
                    metadata = data['metadata']

                    # Track all fields
                    for field in metadata:
                        results['metadata_analysis']['all_fields'][field] += 1

                    # Check expected fields
                    for field, (expected_type, allowed_values) in results['metadata_expected_fields'].items():
                        if field not in metadata:
                            results['metadata_analysis']['missing_fields'][f'metadata.{field}'].append(line_num)
                        else:
                            value = metadata[field]
                            results['metadata_analysis']['field_values'][field][str(value)] += 1

                            # Type check
                            actual_type = type(value).__name__

                            if expected_type == 'string' and actual_type != 'str':
                                results['metadata_analysis']['unexpected_types'].append({
                                    'line': line_num,
                                    'field': f'metadata.{field}',
                                    'expected': expected_type,
                                    'got': actual_type,
                                    'value': str(value)[:50]
                                })
                            elif expected_type == 'integer' and actual_type != 'int':
                                results['metadata_analysis']['unexpected_types'].append({
                                    'line': line_num,
                                    'field': f'metadata.{field}',
                                    'expected': expected_type,
                                    'got': actual_type,
                                    'value': str(value)[:50]
                                })
                            elif expected_type == 'list' and actual_type != 'list':
                                results['metadata_analysis']['unexpected_types'].append({
                                    'line': line_num,
                                    'field': f'metadata.{field}',
                                    'expected': expected_type,
                                    'got': actual_type,
                                    'value': str(value)[:50]
                                })

                            # Value check (if allowed_values is specified)
                            if allowed_values is not None and value not in allowed_values:
                                results['metadata_analysis']['issues'].append({
                                    'line': line_num,
                                    'type': 'unexpected_value',
                                    'field': field,
                                    'value': value,
                                    'allowed_values': allowed_values
                                })

            except json.JSONDecodeError as e:
                pass  # Already caught in first pass

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

    print("=" * 80)
    print("VALIDATION APPROFONDIE DES MÉTADONNÉES")
    print("=" * 80)
    print()

    all_results = []
    files_with_issues = []

    for filename in files_to_check:
        filepath = dataset_dir / filename

        if not filepath.exists():
            continue

        print(f"📂 {filename}")
        print("-" * 80)

        results = deep_analyze_jsonl(filepath)
        all_results.append(results)

        # Check for issues
        has_issues = False

        if results['metadata_analysis']['missing_fields']:
            has_issues = True
            print("⚠️  Champs manquants détectés:")
            for field, lines in results['metadata_analysis']['missing_fields'].items():
                if lines:  # Only show if there are actual missing instances
                    print(f"   - {field}: manquant sur {len(lines)} ligne(s): {lines[:5]}")

        if results['metadata_analysis']['unexpected_types']:
            has_issues = True
            print("⚠️  Types inattendus détectés:")
            for issue in results['metadata_analysis']['unexpected_types'][:5]:
                print(f"   - Ligne {issue['line']}: {issue['field']} (attendu: {issue['expected']}, reçu: {issue['got']})")

        if results['metadata_analysis']['issues']:
            has_issues = True
            print("⚠️  Valeurs inattendues détectées:")
            for issue in results['metadata_analysis']['issues'][:5]:
                print(f"   - Ligne {issue['line']}: {issue['field']} = '{issue['value']}' (non dans: {issue['allowed_values'][:5]}...)")

        if has_issues:
            files_with_issues.append(results)
            print()
        else:
            print("✅ Aucun problème détecté")
            print()

        # Show metadata field distribution
        print("📊 Distribution des champs metadata:")
        for field, count in sorted(results['metadata_analysis']['all_fields'].items()):
            coverage = (count / results['total_lines']) * 100
            print(f"   {field}: {count}/{results['total_lines']} ({coverage:.1f}%)")

        print()

    # Global summary
    print("=" * 80)
    print("RÉSUMÉ GLOBAL")
    print("=" * 80)
    print()

    # Aggregate field values across all files
    all_types = Counter()
    all_topics = Counter()
    all_actions = Counter()

    for results in all_results:
        for value, count in results['metadata_analysis']['field_values']['type'].items():
            all_types[value] += count
        for value, count in results['metadata_analysis']['field_values']['topic'].items():
            all_topics[value] += count
        for value, count in results['metadata_analysis']['field_values']['expected_action'].items():
            all_actions[value] += count

    print("📊 Valeurs de 'type' trouvées dans tous les fichiers:")
    for value, count in all_types.most_common():
        print(f"   {value}: {count}")
    print()

    print("📊 Valeurs de 'expected_action' trouvées dans tous les fichiers:")
    for value, count in all_actions.most_common():
        print(f"   {value}: {count}")
    print()

    print("📊 Top 20 'topic' trouvés dans tous les fichiers:")
    for value, count in all_topics.most_common(20):
        print(f"   {value}: {count}")
    print()

    if files_with_issues:
        print(f"⚠️  {len(files_with_issues)} fichier(s) avec des problèmes potentiels")
        for result in files_with_issues:
            print(f"   - {result['filename']}")
    else:
        print("✅ Aucun problème détecté dans les métadonnées")

    print()

if __name__ == '__main__':
    main()
