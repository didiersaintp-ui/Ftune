"""
Fonction de reward ULTRA améliorée pour le fine-tuning
- Extraction JSON robuste (gère texte avant/après)
- Comparaison exacte avec JSON attendu
- Scoring pondéré optimisé
"""

import json
import re
from typing import Dict, Any, Tuple, Optional
import jsonschema
from jsonschema import validate


def extract_json_from_output(text: str) -> Optional[Dict[str, Any]]:
    """
    Extrait le JSON de la sortie du modèle de manière robuste
    Gère les cas où du texte est présent avant ou après le JSON
    """
    try:
        # Méthode 1 : Chercher le JSON entre accolades
        # Trouver tous les objets JSON potentiels
        brace_count = 0
        start_idx = -1

        for i, char in enumerate(text):
            if char == '{':
                if brace_count == 0:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    # On a trouvé un JSON complet
                    json_text = text[start_idx:i+1]
                    try:
                        parsed = json.loads(json_text)
                        # Vérifier que c'est bien un produit de transport
                        if "product_name" in parsed and "characteristics" in parsed:
                            return parsed
                    except json.JSONDecodeError:
                        # Ce n'était pas du JSON valide, continuer
                        continue

        # Méthode 2 : Utiliser regex pour trouver le JSON
        # Pattern pour capturer un objet JSON
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.finditer(json_pattern, text, re.DOTALL)

        for match in matches:
            try:
                json_text = match.group(0)
                parsed = json.loads(json_text)
                if "product_name" in parsed and "characteristics" in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue

        # Méthode 3 : Chercher après un marqueur spécifique
        markers = ["### JSON:", "```json", "Output:", "Réponse:"]
        for marker in markers:
            if marker in text:
                json_start = text.find(marker) + len(marker)
                json_text = text[json_start:].strip()

                # Nettoyer les backticks markdown si présents
                json_text = json_text.replace("```", "")

                # Trouver le premier { et le dernier }
                first_brace = json_text.find("{")
                if first_brace == -1:
                    continue

                # Compter les accolades pour trouver le JSON complet
                brace_count = 0
                end_idx = -1
                for i in range(first_brace, len(json_text)):
                    if json_text[i] == '{':
                        brace_count += 1
                    elif json_text[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break

                if end_idx != -1:
                    json_text = json_text[first_brace:end_idx]
                    try:
                        parsed = json.loads(json_text)
                        if "product_name" in parsed and "characteristics" in parsed:
                            return parsed
                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        print(f"⚠️  Erreur extraction JSON: {e}")

    return None


def validate_json_schema(json_obj: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Valide un JSON selon le schéma"""
    try:
        validate(instance=json_obj, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"⚠️  Erreur validation schéma: {e.message}")
        return False
    except Exception as e:
        print(f"⚠️  Erreur validation: {e}")
        return False


def compare_characteristics(
    generated: list,
    expected: list,
    strict: bool = True
) -> Tuple[float, Dict[str, Any]]:
    """
    Compare les caractéristiques générées avec celles attendues

    Args:
        generated: Liste des caractéristiques générées
        expected: Liste des caractéristiques attendues
        strict: Si True, pénalise les caractéristiques en trop

    Returns:
        score (0.0-1.0), détails de la comparaison
    """
    details = {
        "matched": [],
        "missing": [],
        "extra": [],
        "incorrect_params": []
    }

    score = 0.0
    total_expected = len(expected)

    if total_expected == 0:
        return 1.0 if len(generated) == 0 else 0.0, details

    # Créer un dict des caractéristiques par numéro
    expected_by_number = {char["number"]: char for char in expected}
    generated_by_number = {char["number"]: char for char in generated}

    # Vérifier chaque caractéristique attendue
    for exp_char in expected:
        char_num = exp_char["number"]

        if char_num not in generated_by_number:
            # Caractéristique manquante
            details["missing"].append(char_num)
            continue

        gen_char = generated_by_number[char_num]

        # Comparer les paramètres
        params_score = compare_parameters(
            gen_char.get("parameters", {}),
            exp_char.get("parameters", {})
        )

        if params_score == 1.0:
            # Correspondance parfaite
            details["matched"].append(char_num)
            score += 1.0
        else:
            # Paramètres incorrects
            details["incorrect_params"].append({
                "number": char_num,
                "score": params_score,
                "expected": exp_char.get("parameters", {}),
                "generated": gen_char.get("parameters", {})
            })
            score += params_score

    # Vérifier les caractéristiques en trop
    for gen_char in generated:
        char_num = gen_char["number"]
        if char_num not in expected_by_number:
            details["extra"].append(char_num)
            if strict:
                # Pénaliser les caractéristiques en trop en mode strict
                score -= 0.2

    # Normaliser le score
    final_score = max(0.0, min(1.0, score / total_expected))

    return final_score, details


def compare_parameters(generated: Dict, expected: Dict) -> float:
    """
    Compare les paramètres d'une caractéristique
    Retourne un score de 0.0 (aucune correspondance) à 1.0 (parfait)
    """
    if not expected:
        return 1.0 if not generated else 0.5

    total_params = len(expected)
    if total_params == 0:
        return 1.0

    score = 0.0

    for param_key, expected_value in expected.items():
        if param_key not in generated:
            # Paramètre manquant
            continue

        generated_value = generated[param_key]

        # Comparaison en fonction du type
        if isinstance(expected_value, list):
            # Listes : vérifier que les éléments correspondent
            if isinstance(generated_value, list):
                if sorted(expected_value) == sorted(generated_value):
                    score += 1.0
                else:
                    # Score partiel si certains éléments correspondent
                    matching = len(set(map(str, expected_value)) & set(map(str, generated_value)))
                    total = len(set(map(str, expected_value)) | set(map(str, generated_value)))
                    score += matching / total if total > 0 else 0.0
        elif isinstance(expected_value, dict):
            # Dictionnaires : récursion
            nested_score = compare_parameters(generated_value, expected_value)
            score += nested_score
        elif isinstance(expected_value, (list, tuple)) and all(isinstance(item, dict) for item in expected_value):
            # Liste de dictionnaires (ex: 9_01)
            if isinstance(generated_value, list) and len(generated_value) == len(expected_value):
                dict_scores = []
                for exp_dict, gen_dict in zip(expected_value, generated_value):
                    dict_scores.append(compare_parameters(gen_dict, exp_dict))
                score += sum(dict_scores) / len(dict_scores) if dict_scores else 0.0
            else:
                # Longueurs différentes ou type incorrect
                score += 0.0
        else:
            # Valeurs simples : comparaison directe
            if expected_value == generated_value:
                score += 1.0
            elif isinstance(expected_value, (int, float)) and isinstance(generated_value, (int, float)):
                # Pour les nombres, permettre une petite marge d'erreur
                if abs(expected_value - generated_value) / max(abs(expected_value), 1) < 0.01:
                    score += 0.9

    return score / total_params


def calculate_reward_improved(
    output_text: str,
    expected_json: Dict[str, Any],
    schema: Dict[str, Any],
    verbose: bool = False
) -> Tuple[float, Dict[str, Any]]:
    """
    Fonction de reward améliorée basée sur la comparaison avec le JSON attendu

    Args:
        output_text: Texte généré par le modèle
        expected_json: JSON attendu pour cette entrée
        schema: Schéma JSON de validation
        verbose: Afficher les détails

    Returns:
        score (0.0-1.0), détails de l'évaluation
    """
    result = {
        "score": 0.0,
        "valid_json": False,
        "valid_schema": False,
        "product_name_match": False,
        "characteristics_score": 0.0,
        "details": {}
    }

    # 1. Extraire le JSON généré
    generated_json = extract_json_from_output(output_text)

    if generated_json is None:
        result["details"]["error"] = "JSON invalide ou non trouvé"
        if verbose:
            print("❌ JSON invalide ou non trouvé")
        return 0.0, result

    result["valid_json"] = True

    # 2. Valider le schéma
    if validate_json_schema(generated_json, schema):
        result["valid_schema"] = True

    # 3. Comparer le product_name (tolérant)
    gen_name = generated_json.get("product_name", "").lower().strip()
    exp_name = expected_json.get("product_name", "").lower().strip()

    # Vérifier si les mots clés principaux sont présents
    exp_words = set(exp_name.split())
    gen_words = set(gen_name.split())

    # Calculer la similarité des noms
    if exp_words:
        name_similarity = len(exp_words & gen_words) / len(exp_words | gen_words)
        result["product_name_match"] = name_similarity > 0.5
        result["name_similarity"] = name_similarity

    # 4. Comparer les caractéristiques (le plus important !)
    gen_chars = generated_json.get("characteristics", [])
    exp_chars = expected_json.get("characteristics", [])

    char_score, char_details = compare_characteristics(gen_chars, exp_chars, strict=True)
    result["characteristics_score"] = char_score
    result["details"]["characteristics"] = char_details

    # 5. Calcul du score final pondéré
    # 80% pour les caractéristiques (le plus important)
    # 10% pour la validité du schéma
    # 10% pour la similarité du nom

    final_score = (
        0.80 * char_score +
        0.10 * (1.0 if result["valid_schema"] else 0.0) +
        0.10 * result.get("name_similarity", 0.0)
    )

    result["score"] = final_score

    if verbose:
        print("\n" + "="*60)
        print("REWARD DÉTAILLÉ")
        print("="*60)
        print(f"Score final: {final_score:.3f}")
        print(f"  - Caractéristiques: {char_score:.3f} (80%)")
        print(f"  - Schéma valide: {1.0 if result['valid_schema'] else 0.0} (10%)")
        print(f"  - Nom similaire: {result.get('name_similarity', 0.0):.3f} (10%)")
        print("\nDétails des caractéristiques:")
        print(f"  ✓ Correctes: {char_details['matched']}")
        print(f"  ✗ Manquantes: {char_details['missing']}")
        print(f"  ⚠ En trop: {char_details['extra']}")
        if char_details['incorrect_params']:
            print(f"  ⚠ Paramètres incorrects:")
            for item in char_details['incorrect_params']:
                print(f"    - Carac. {item['number']}: score {item['score']:.2f}")
        print("="*60)

    return final_score, result


# Test de la fonction
if __name__ == "__main__":
    # Test avec du texte supplémentaire après le JSON
    test_output = """Voici le produit demandé :

{
  "product_name": "Abonnement mensuel Métro",
  "characteristics": [
    {
      "number": 7,
      "parameters": {
        "7_01": 2,
        "7_02": "M",
        "7_03": 1,
        "7_04": true,
        "7_05": true
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

Ce produit est parfait pour vos besoins quotidiens."""

    expected = {
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

    schema = {
        "type": "object",
        "required": ["product_name", "characteristics"],
        "properties": {
            "product_name": {"type": "string"},
            "characteristics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["number", "parameters"],
                    "properties": {
                        "number": {"type": "integer"},
                        "parameters": {"type": "object"}
                    }
                }
            }
        }
    }

    print("🧪 Test de l'extraction JSON avec texte supplémentaire")
    print("="*60)

    extracted = extract_json_from_output(test_output)

    if extracted:
        print("✅ JSON extrait avec succès !")
        print(json.dumps(extracted, ensure_ascii=False, indent=2))

        score, details = calculate_reward_improved(test_output, expected, schema, verbose=True)
        print(f"\n📊 Score final: {score:.3f}")
    else:
        print("❌ Échec de l'extraction JSON")
