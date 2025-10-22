"""
Script de test automatique pour valider le modèle GGUF entraîné
Usage: python test_model_gguf.py [--model path/to/model.gguf]
"""

import json
import sys
import argparse
from typing import List, Dict, Tuple

try:
    from llama_cpp import Llama
except ImportError:
    print("❌ llama-cpp-python n'est pas installé")
    print("   Installation: pip install llama-cpp-python")
    sys.exit(1)

# Charger le schéma
try:
    with open("transport_schema_complete.json", "r", encoding="utf-8") as f:
        SCHEMA = json.load(f)
except FileNotFoundError:
    print("❌ Fichier transport_schema_complete.json introuvable")
    sys.exit(1)

# Charger la fonction de reward
try:
    from reward_function_improved import (
        calculate_reward_improved,
        extract_json_from_output,
        validate_json_schema
    )
except ImportError:
    print("❌ reward_function_improved.py introuvable")
    sys.exit(1)


# Cas de test
TEST_CASES = [
    {
        "name": "Abonnement mensuel simple",
        "input": "Je veux un abonnement mensuel pour le métro",
        "expected": {
            "product_name": "Abonnement mensuel Métro",
            "characteristics": [
                {
                    "number": 7,
                    "parameters": {
                        "7_01": 2,
                        "7_02": "M",
                        "7_03": 1,
                        "7_04": True,
                        "7_05": True
                    }
                },
                {
                    "number": 14,
                    "parameters": {
                        "14_01": ["Métro"],
                        "14_02": "Autorisée"
                    }
                }
            ]
        }
    },
    {
        "name": "Carnet de tickets",
        "input": "Carnet de 10 tickets valable 1 semaine sur bus et tramway",
        "expected": {
            "product_name": "Carnet 10 voyages hebdomadaire Bus-Tramway",
            "characteristics": [
                {
                    "number": 7,
                    "parameters": {
                        "7_01": 2,
                        "7_02": "W",
                        "7_03": 1,
                        "7_04": False,
                        "7_05": False
                    }
                },
                {
                    "number": 22,
                    "parameters": {
                        "22_01": 10,
                        "22_02": 10,
                        "22_03": False
                    }
                },
                {
                    "number": 14,
                    "parameters": {
                        "14_01": ["Bus urbain", "Tramway"],
                        "14_02": "Autorisée"
                    }
                }
            ]
        }
    },
    {
        "name": "Pass groupe",
        "input": "Pass 24h pour 5 personnes",
        "expected": {
            "product_name": "Pass 24h Groupe 5 personnes",
            "characteristics": [
                {
                    "number": 7,
                    "parameters": {
                        "7_01": 4,
                        "7_02": "H",
                        "7_03": 24,
                        "7_04": False,
                        "7_05": False
                    }
                },
                {
                    "number": 2,
                    "parameters": {
                        "2_01": 5
                    }
                }
            ]
        }
    },
    {
        "name": "Contraintes horaires",
        "input": "Forfait hebdomadaire valable en semaine de 9h à 17h",
        "expected": {
            "product_name": "Forfait hebdomadaire heures creuses",
            "characteristics": [
                {
                    "number": 7,
                    "parameters": {
                        "7_01": 2,
                        "7_02": "W",
                        "7_03": 1,
                        "7_04": True,
                        "7_05": True
                    }
                },
                {
                    "number": 9,
                    "parameters": {
                        "9_01": [
                            {
                                "days": "Lundi-Vendredi",
                                "start": "09:00",
                                "end": "17:00"
                            }
                        ]
                    }
                }
            ]
        }
    },
    {
        "name": "Exclusion de mode",
        "input": "Abonnement annuel tous modes sauf train",
        "expected": {
            "product_name": "Abonnement annuel (hors Train)",
            "characteristics": [
                {
                    "number": 7,
                    "parameters": {
                        "7_01": 2,
                        "7_02": "M",
                        "7_03": 12,
                        "7_04": True,
                        "7_05": True
                    }
                },
                {
                    "number": 14,
                    "parameters": {
                        "14_01": ["Train"],
                        "14_02": "Interdite"
                    }
                }
            ]
        }
    },
    {
        "name": "Produit complexe",
        "input": "Abonnement mensuel pour 2 personnes, valable du lundi au vendredi de 6h à 20h, sur bus et métro, lignes 5 et 12",
        "expected": {
            "product_name": "Abonnement mensuel Duo Lignes 5-12",
            "characteristics": [
                {
                    "number": 7,
                    "parameters": {
                        "7_01": 2,
                        "7_02": "M",
                        "7_03": 1,
                        "7_04": True,
                        "7_05": True
                    }
                },
                {
                    "number": 2,
                    "parameters": {
                        "2_01": 2
                    }
                },
                {
                    "number": 9,
                    "parameters": {
                        "9_01": [
                            {
                                "days": "Lundi-Vendredi",
                                "start": "06:00",
                                "end": "20:00"
                            }
                        ]
                    }
                },
                {
                    "number": 14,
                    "parameters": {
                        "14_01": ["Bus urbain", "Métro"],
                        "14_02": "Autorisée"
                    }
                },
                {
                    "number": 3,
                    "parameters": {
                        "3_01": ["Ligne 5", "Ligne 12"],
                        "3_02": "Autorisée"
                    }
                }
            ]
        }
    }
]


def format_prompt(input_text: str) -> str:
    """Format du prompt pour le modèle"""
    system = """Tu es un assistant expert pour créer des produits de transport en JSON.

Règles OBLIGATOIRES:
1. TOUJOURS inclure caractéristique 7 (période de validité)
2. "Abonnement mensuel" → 7_01:2, 7_02:"M", 7_03:1, rechargeable (7_04:true, 7_05:true)
3. "Pass 24h" → 7_01:4, 7_02:"H", 7_03:24, NON rechargeable (7_04:false, 7_05:false)
4. "Carnet de X tickets" → carac. 22 avec X déplacements, NON rechargeable
5. "Pour Y personnes" → carac. 2 avec Y passagers
6. "Métro/Bus/Tramway" → carac. 14 avec modes autorisés
7. "Tous modes sauf X" → carac. 14 avec X interdit
8. Illimité = PAS de carac. 22

Format JSON requis:
{
  "product_name": "...",
  "characteristics": [{"number": X, "parameters": {...}}]
}"""

    return f"""{system}

### Description:
{input_text}

### JSON:
"""


def test_model(model_path: str, verbose: bool = True) -> Tuple[int, int, List[Dict]]:
    """
    Teste le modèle sur tous les cas de test

    Returns:
        (success_count, total_count, detailed_results)
    """
    print("🤖 Chargement du modèle...")
    try:
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )
        print("✅ Modèle chargé\n")
    except Exception as e:
        print(f"❌ Erreur de chargement: {e}")
        sys.exit(1)

    results = []
    success_count = 0

    for i, test_case in enumerate(TEST_CASES, 1):
        if verbose:
            print(f"{'='*70}")
            print(f"Test {i}/{len(TEST_CASES)}: {test_case['name']}")
            print(f"{'='*70}")
            print(f"📝 Input: {test_case['input']}")

        # Générer
        prompt = format_prompt(test_case['input'])

        try:
            output = llm(
                prompt,
                max_tokens=512,
                temperature=0.1,
                top_p=0.9,
                stop=["###", "\n\n\n"],
                echo=False
            )

            response_text = output['choices'][0]['text']
            full_output = prompt + response_text

            # Extraire le JSON
            json_obj = extract_json_from_output(full_output)

            if json_obj:
                # Calculer le reward avec la fonction améliorée
                score, details = calculate_reward_improved(
                    full_output,
                    test_case['expected'],
                    SCHEMA,
                    verbose=False
                )

                # Valider le schéma
                is_valid = validate_json_schema(json_obj, SCHEMA)

                # Vérifier les caractéristiques
                found_chars = sorted([c["number"] for c in json_obj.get("characteristics", [])])
                expected_chars = sorted([c["number"] for c in test_case['expected']["characteristics"]])

                success = score >= 0.8 and is_valid

                if verbose:
                    print(f"\n✅ JSON généré:")
                    print(json.dumps(json_obj, ensure_ascii=False, indent=2))
                    print(f"\n📊 Reward score: {score:.2f}/1.00")
                    print(f"✅ Schéma valide: {is_valid}")
                    print(f"✅ Caractéristiques trouvées: {found_chars}")
                    print(f"✅ Caractéristiques attendues: {expected_chars}")
                    print(f"\n{'✅ TEST RÉUSSI' if success else '⚠️  TEST PARTIELLEMENT RÉUSSI'}")

                results.append({
                    "name": test_case["name"],
                    "success": success,
                    "score": score,
                    "valid_schema": is_valid,
                    "chars_found": found_chars,
                    "chars_expected": expected_chars
                })

                if success:
                    success_count += 1

            else:
                if verbose:
                    print(f"\n❌ JSON invalide ou non trouvé")
                    print(f"❌ TEST ÉCHOUÉ")

                results.append({
                    "name": test_case["name"],
                    "success": False,
                    "score": 0.0,
                    "valid_schema": False,
                    "chars_found": [],
                    "chars_expected": expected_chars
                })

        except Exception as e:
            if verbose:
                print(f"\n❌ Erreur: {e}")
                print(f"❌ TEST ÉCHOUÉ")

            results.append({
                "name": test_case["name"],
                "success": False,
                "score": 0.0,
                "error": str(e)
            })

        if verbose:
            print()

    return success_count, len(TEST_CASES), results


def print_summary(success_count: int, total_count: int, results: List[Dict]):
    """Affiche un résumé des tests"""
    print("="*70)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*70)

    success_rate = (success_count / total_count) * 100

    print(f"\nTests réussis: {success_count}/{total_count} ({success_rate:.1f}%)")
    print()

    for result in results:
        status = "✅" if result["success"] else "❌"
        score_str = f" (score: {result['score']:.2f})" if "score" in result else ""
        print(f"  {status} {result['name']}{score_str}")

    print()

    if success_rate >= 90:
        print("🎉 EXCELLENT ! Modèle validé avec succès.")
    elif success_rate >= 75:
        print("✅ BON ! Le modèle fonctionne bien.")
    elif success_rate >= 60:
        print("⚠️  ACCEPTABLE. Le modèle peut être amélioré.")
    else:
        print("❌ INSUFFISANT. Réentraîner avec plus de steps recommandé.")

    print("="*70)


def main():
    parser = argparse.ArgumentParser(description="Test automatique du modèle GGUF")
    parser.add_argument(
        "--model",
        type=str,
        default="qwen3b_transport_gguf/unsloth.Q4_K_M.gguf",
        help="Chemin vers le modèle GGUF"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Mode silencieux (afficher seulement le résumé)"
    )

    args = parser.parse_args()

    print("🧪 TEST AUTOMATIQUE DU MODÈLE GGUF")
    print("="*70)
    print(f"Modèle: {args.model}")
    print(f"Tests: {len(TEST_CASES)} cas")
    print("="*70)
    print()

    success_count, total_count, results = test_model(
        args.model,
        verbose=not args.quiet
    )

    print_summary(success_count, total_count, results)

    # Code de sortie
    success_rate = (success_count / total_count) * 100
    if success_rate >= 75:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
