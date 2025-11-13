#!/usr/bin/env python3
"""
Validateur JSON Avancé et Reward Function pour RLHF
Assistant Billettique - TCL Lyon

Ce module fournit :
1. Validateur JSON avec schéma strict
2. Détecteur d'incompatibilités entre caractéristiques
3. Reward function pour RLHF (Reinforcement Learning from Human Feedback)
4. Vérificateur de cohérence métier
"""

import json
import re
from typing import Dict, List, Tuple, Any, Optional
from jsonschema import validate, ValidationError, Draft7Validator

# ============================================================================
# SCHÉMA JSON STRICT
# ============================================================================

PRODUCT_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["product_name", "characteristics"],
    "properties": {
        "product_name": {
            "type": "string",
            "minLength": 3,
            "maxLength": 100
        },
        "price_cents": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100000
        },
        "support": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["BSC", "AB", "CSC"]
            },
            "minItems": 1,
            "uniqueItems": True
        },
        "profile": {
            "type": "string",
            "enum": ["Plein tarif", "Jeune", "Senior", "Étudiant", "Employeur", "Solidarité"]
        },
        "characteristics": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["number", "parameters"],
                "properties": {
                    "number": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 200
                    },
                    "parameters": {
                        "type": "object"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    "additionalProperties": False
}

# ============================================================================
# INCOMPATIBILITÉS CONNUES
# ============================================================================

INCOMPATIBILITIES = {
    (14, 74): {
        "reason": "CAR_14 (liste de modes par paramétrage) et CAR_74 (mode unique codé) servent le même objectif de manière incompatible",
        "severity": "critical",
        "solution": "Utiliser CAR_14 pour plusieurs modes OU CAR_74 pour un mode unique"
    },
    (22, 21): {
        "reason": "CAR_22 (mono-usager) et CAR_21 (multi-usager) s'excluent mutuellement",
        "severity": "critical",
        "solution": "Choisir CAR_22 pour un seul usager OU CAR_21 pour plusieurs usagers"
    },
    (3, 87): {
        "reason": "CAR_3 (lignes par paramétrage) et CAR_87 (lignes codées à la vente) sont incompatibles",
        "severity": "critical",
        "solution": "Utiliser CAR_3 pour lignes fixes OU CAR_87 pour lignes déterminées à la vente"
    },
    (2, 38): {
        "reason": "CAR_2 (nombre fixe de passagers) et CAR_38 (nombre saisi à la vente) s'excluent",
        "severity": "critical",
        "solution": "Utiliser CAR_2 pour nombre fixe OU CAR_38 pour nombre variable"
    },
    (4, 121): {
        "reason": "CAR_4 (zones par paramétrage) et CAR_121 (zones déterminées à la vente) peuvent créer des conflits",
        "severity": "warning",
        "solution": "Préférer CAR_4 pour zones fixes OU CAR_121 pour trajet zonal défini à la vente"
    },
    (22, 6): {
        "reason": "CAR_22 (multi-déplacements) limite déjà le nombre de voyages, CAR_6 (validations par déplacement) peut créer une double limitation",
        "severity": "warning",
        "solution": "Vérifier que les deux limitations sont cohérentes"
    }
}

# Caractéristiques mutuellement exclusives par groupe
EXCLUSIVE_GROUPS = [
    [22, 21],  # Mono-usager vs Multi-usager
    [14, 74],  # Modes liste vs Mode unique
    [3, 87],   # Lignes paramétrées vs Lignes vente
    [2, 38],   # Groupe fixe vs Groupe variable
]

# ============================================================================
# RÈGLES MÉTIER
# ============================================================================

BUSINESS_RULES = {
    "car_7_mandatory": {
        "description": "La caractéristique 7 (DDV/DEV) est OBLIGATOIRE pour tous les produits",
        "severity": "critical"
    },
    "nature_validite_valid": {
        "description": "Le paramètre 7_01 doit être dans [0, 2, 4, 6, 8, 14, 20, 21]",
        "severity": "critical",
        "valid_values": [0, 2, 4, 6, 8, 14, 20, 21]
    },
    "duree_unit_valid": {
        "description": "Le paramètre 7_02 doit être D, W, M ou H",
        "severity": "critical",
        "valid_values": ["D", "W", "M", "H"]
    },
    "duree_positive": {
        "description": "Le paramètre 7_03 doit être un entier positif",
        "severity": "critical"
    },
    "rechargement_boolean": {
        "description": "Les paramètres 7_04 et 7_05 doivent être des booléens (true/false)",
        "severity": "critical"
    },
    "voyages_coherence": {
        "description": "Si CAR_22, alors 22_01 <= 22_02 (voyages <= max)",
        "severity": "error"
    },
    "groupe_coherence": {
        "description": "Si CAR_38, alors 38_01 <= 38_02 (min <= max passagers)",
        "severity": "error"
    },
    "modes_non_vides": {
        "description": "Si CAR_14, la liste 14_01 ne doit pas être vide",
        "severity": "error"
    },
    "lignes_non_vides": {
        "description": "Si CAR_3, la liste 3_01 ne doit pas être vide",
        "severity": "error"
    }
}

# ============================================================================
# VALIDATEUR JSON
# ============================================================================

class ProductJSONValidator:
    """Validateur JSON avancé pour produits de transport"""

    def __init__(self):
        self.validator = Draft7Validator(PRODUCT_JSON_SCHEMA)

    def validate(self, json_data: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Valide un JSON de produit

        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # 1. Validation du schéma JSON
        schema_errors = self._validate_schema(json_data)
        errors.extend(schema_errors)

        # 2. Validation syntaxique
        syntax_errors = self._validate_syntax(json_data)
        errors.extend(syntax_errors)

        # 3. Détection d'incompatibilités
        incomp_errors, incomp_warnings = self._detect_incompatibilities(json_data)
        errors.extend(incomp_errors)
        warnings.extend(incomp_warnings)

        # 4. Validation des règles métier
        business_errors, business_warnings = self._validate_business_rules(json_data)
        errors.extend(business_errors)
        warnings.extend(business_warnings)

        is_valid = len(errors) == 0

        return is_valid, errors, warnings

    def _validate_schema(self, json_data: Dict) -> List[str]:
        """Valide contre le schéma JSON"""
        errors = []
        try:
            validate(instance=json_data, schema=PRODUCT_JSON_SCHEMA)
        except ValidationError as e:
            errors.append(f"Erreur de schéma : {e.message}")
        return errors

    def _validate_syntax(self, json_data: Any) -> List[str]:
        """Valide la syntaxe JSON"""
        errors = []

        # Vérifier que c'est un dict
        if not isinstance(json_data, dict):
            errors.append("Le JSON doit être un objet (dictionnaire)")
            return errors

        # Vérifier les clés obligatoires
        if "characteristics" not in json_data:
            errors.append("Clé 'characteristics' manquante")
            return errors

        # Vérifier la structure des caractéristiques
        chars = json_data.get("characteristics", [])
        if not isinstance(chars, list):
            errors.append("'characteristics' doit être une liste")
            return errors

        for i, char in enumerate(chars):
            if not isinstance(char, dict):
                errors.append(f"Caractéristique {i} doit être un objet")
                continue

            if "number" not in char:
                errors.append(f"Caractéristique {i} : clé 'number' manquante")

            if "parameters" not in char:
                errors.append(f"Caractéristique {i} : clé 'parameters' manquante")
            elif not isinstance(char["parameters"], dict):
                errors.append(f"Caractéristique {i} : 'parameters' doit être un objet")

        return errors

    def _detect_incompatibilities(self, json_data: Dict) -> Tuple[List[str], List[str]]:
        """Détecte les incompatibilités entre caractéristiques"""
        errors = []
        warnings = []

        chars = json_data.get("characteristics", [])
        char_numbers = [c.get("number") for c in chars if "number" in c]

        # Vérifier les incompatibilités connues
        for (car1, car2), incomp_data in INCOMPATIBILITIES.items():
            if car1 in char_numbers and car2 in char_numbers:
                message = f"Incompatibilité CAR_{car1}/CAR_{car2} : {incomp_data['reason']}"
                if incomp_data['severity'] == 'critical':
                    errors.append(message)
                else:
                    warnings.append(message)

        # Vérifier les groupes mutuellement exclusifs
        for exclusive_group in EXCLUSIVE_GROUPS:
            present = [car for car in exclusive_group if car in char_numbers]
            if len(present) > 1:
                errors.append(f"Caractéristiques mutuellement exclusives présentes : {present}")

        return errors, warnings

    def _validate_business_rules(self, json_data: Dict) -> Tuple[List[str], List[str]]:
        """Valide les règles métier"""
        errors = []
        warnings = []

        chars = json_data.get("characteristics", [])
        char_dict = {c.get("number"): c.get("parameters", {}) for c in chars if "number" in c}

        # Règle 1 : CAR_7 obligatoire
        if 7 not in char_dict:
            errors.append("CRITIQUE : La caractéristique 7 (DDV/DEV) est OBLIGATOIRE")
            return errors, warnings

        # Règle 2 : Valider CAR_7
        car_7_params = char_dict[7]

        if "7_01" in car_7_params:
            if car_7_params["7_01"] not in [0, 2, 4, 6, 8, 14, 20, 21]:
                errors.append(f"CAR_7 : Nature de validité invalide ({car_7_params['7_01']}). Doit être dans [0, 2, 4, 6, 8, 14, 20, 21]")

        if "7_02" in car_7_params:
            if car_7_params["7_02"] not in ["D", "W", "M", "H"]:
                errors.append(f"CAR_7 : Unité invalide ({car_7_params['7_02']}). Doit être D, W, M ou H")

        if "7_03" in car_7_params:
            if not isinstance(car_7_params["7_03"], int) or car_7_params["7_03"] <= 0:
                errors.append(f"CAR_7 : Durée invalide ({car_7_params['7_03']}). Doit être un entier positif")

        if "7_04" in car_7_params:
            if not isinstance(car_7_params["7_04"], bool):
                errors.append(f"CAR_7 : Paramètre 7_04 doit être un booléen (true/false)")

        if "7_05" in car_7_params:
            if not isinstance(car_7_params["7_05"], bool):
                errors.append(f"CAR_7 : Paramètre 7_05 doit être un booléen (true/false)")

        # Règle 3 : Cohérence CAR_22
        if 22 in char_dict:
            car_22_params = char_dict[22]
            voyages = car_22_params.get("22_01", 0)
            max_voyages = car_22_params.get("22_02", 0)

            if voyages > max_voyages:
                errors.append(f"CAR_22 : Incohérence : voyages ({voyages}) > max ({max_voyages})")

        # Règle 4 : Cohérence CAR_38
        if 38 in char_dict:
            car_38_params = char_dict[38]
            min_pass = car_38_params.get("38_01", 0)
            max_pass = car_38_params.get("38_02", 0)

            if min_pass > max_pass:
                errors.append(f"CAR_38 : Incohérence : min ({min_pass}) > max ({max_pass})")

        # Règle 5 : Listes non vides
        if 14 in char_dict:
            modes = char_dict[14].get("14_01", [])
            if not modes or len(modes) == 0:
                errors.append("CAR_14 : La liste des modes ne peut pas être vide")

        if 3 in char_dict:
            lignes = char_dict[3].get("3_01", [])
            if not lignes or len(lignes) == 0:
                errors.append("CAR_3 : La liste des lignes ne peut pas être vide")

        return errors, warnings

# ============================================================================
# REWARD FUNCTION POUR RLHF
# ============================================================================

class RewardFunction:
    """Fonction de récompense pour RLHF"""

    def __init__(self):
        self.validator = ProductJSONValidator()

    def calculate_reward(self, output: str, expected_structure: bool = True) -> float:
        """
        Calcule la récompense pour une sortie du modèle

        Args:
            output: La sortie du modèle
            expected_structure: Si True, vérifie la structure 🧠→❓→➡️→✅

        Returns:
            float: Score de récompense (0-100)
        """
        score = 0.0

        # 1. Structure de réponse (+25 points)
        structure_score = self._check_structure(output, expected_structure)
        score += structure_score

        # 2. JSON valide (+30 points)
        json_score = self._check_json_validity(output)
        score += json_score

        # 3. Pas d'hallucinations (+20 points)
        hallucination_penalty = self._check_hallucinations(output)
        score -= hallucination_penalty

        # 4. Qualité conversationnelle (+15 points)
        conversational_score = self._check_conversational_quality(output)
        score += conversational_score

        # 5. Cohérence métier (+10 points)
        business_score = self._check_business_coherence(output)
        score += business_score

        return max(0.0, min(100.0, score))

    def _check_structure(self, output: str, expected: bool) -> float:
        """Vérifie la structure 🧠→❓→➡️→✅"""
        if not expected:
            return 25.0  # Pas de structure attendue

        score = 0.0

        # Vérifier présence des marqueurs
        has_reasoning = "🧠" in output or "Raisonnement" in output
        has_questions = "❓" in output or "Questions" in output
        has_response = "➡️" in output or "Réponse" in output or "JSON" in output
        has_confirmation = "✅" in output or "Confirmez" in output or "Validez" in output

        if has_reasoning:
            score += 8.0
        if has_response:
            score += 10.0
        if has_confirmation:
            score += 7.0

        # Bonus si questions pertinentes (quand approprié)
        if has_questions:
            # Vérifier si les questions sont pertinentes
            if any(keyword in output.lower() for keyword in ["prix", "support", "mode", "durée", "profil"]):
                score += 5.0

        return score

    def _check_json_validity(self, output: str) -> float:
        """Vérifie la validité du JSON"""
        score = 0.0

        # Extraire le JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', output, re.DOTALL)
        if not json_match:
            # Pas de JSON trouvé, peut être normal si questions posées
            if "❓" in output and "Questions" in output:
                return 15.0  # Score partiel si conversation
            return 0.0

        json_str = json_match.group(1)

        try:
            # 1. Syntaxe JSON valide (+10 points)
            json_data = json.loads(json_str)
            score += 10.0

            # 2. Validation avec notre validateur (+20 points)
            is_valid, errors, warnings = self.validator.validate(json_data)

            if is_valid:
                score += 20.0
            else:
                # Pénalités graduelles
                if len(errors) == 0:
                    score += 18.0  # Seulement des warnings
                elif len(errors) <= 2:
                    score += 10.0  # Quelques erreurs mineures
                else:
                    score += 5.0   # Plusieurs erreurs

        except json.JSONDecodeError:
            # Syntaxe JSON invalide
            score = 0.0

        return score

    def _check_hallucinations(self, output: str) -> float:
        """Détecte les hallucinations (caractéristiques inventées, etc.)"""
        penalty = 0.0

        # Caractéristiques valides (0-200)
        valid_cars = list(range(201))

        # Rechercher mentions de CAR_X
        car_mentions = re.findall(r'CAR[_ ](\d+)', output)

        for car_num_str in car_mentions:
            car_num = int(car_num_str)
            if car_num not in valid_cars:
                penalty += 10.0  # Grosse pénalité pour caractéristique inventée

        # Rechercher définitions incorrectes
        hallucination_patterns = [
            (r'CAR[_ ]7.*[Mm]ulti[- ]déplacement', 20.0),  # CAR_7 n'est PAS multi-déplacements
            (r'CAR[_ ]48.*[Mm]ulti[- ]déplacement', 20.0),  # CAR_48 n'est PAS multi-déplacements
            (r'CAR[_ ]107.*[Rr]econduction', 0.0),  # CAR_107 est bien "X mois gratuits"
        ]

        for pattern, penalty_value in hallucination_patterns:
            if re.search(pattern, output):
                penalty += penalty_value

        return penalty

    def _check_conversational_quality(self, output: str) -> float:
        """Évalue la qualité conversationnelle"""
        score = 0.0

        # 1. Pose des questions appropriées (+8 points)
        if "❓" in output:
            questions = re.findall(r'[?？]', output)
            if len(questions) >= 2:
                score += 8.0
            elif len(questions) == 1:
                score += 4.0

        # 2. Ton professionnel et aidant (+4 points)
        helpful_markers = ["Voulez-vous", "Confirmez", "Une fois", "je pourrai", "je peux"]
        if any(marker in output for marker in helpful_markers):
            score += 4.0

        # 3. Pas de répétitions inutiles (+3 points)
        # Détection simple : vérifier si le même mot apparaît trop souvent
        words = output.lower().split()
        word_counts = {}
        for word in words:
            if len(word) > 4:  # Ignorer les petits mots
                word_counts[word] = word_counts.get(word, 0) + 1

        max_repetitions = max(word_counts.values()) if word_counts else 0
        if max_repetitions <= 5:
            score += 3.0
        elif max_repetitions <= 8:
            score += 1.5

        return score

    def _check_business_coherence(self, output: str) -> float:
        """Vérifie la cohérence métier"""
        score = 10.0  # Score de base

        # Extraire le JSON si présent
        json_match = re.search(r'```json\s*(.*?)\s*```', output, re.DOTALL)
        if not json_match:
            return 5.0  # Score partiel si pas de JSON

        try:
            json_data = json.loads(json_match.group(1))

            # Vérifier cohérence prix (si présent)
            if "price_cents" in json_data:
                price = json_data["price_cents"]
                if price < 0 or price > 100000:
                    score -= 5.0  # Prix incohérent

            # Vérifier cohérence nom produit
            if "product_name" in json_data:
                name = json_data["product_name"]
                if len(name) < 3:
                    score -= 3.0  # Nom trop court

        except:
            pass

        return max(0.0, score)

# ============================================================================
# FONCTION DE TEST
# ============================================================================

def test_validator():
    """Teste le validateur avec des exemples"""
    validator = ProductJSONValidator()
    reward_func = RewardFunction()

    # Test 1 : JSON correct
    good_json = {
        "product_name": "Ticket Métro 1h",
        "price_cents": 200,
        "support": ["BSC"],
        "characteristics": [
            {
                "number": 7,
                "parameters": {
                    "7_01": 4,
                    "7_02": "H",
                    "7_03": 1,
                    "7_04": False,
                    "7_05": False
                }
            }
        ]
    }

    is_valid, errors, warnings = validator.validate(good_json)
    print(f"Test 1 (JSON correct) : {'✅ VALIDE' if is_valid else '❌ INVALIDE'}")
    if errors:
        print(f"  Erreurs : {errors}")
    if warnings:
        print(f"  Warnings : {warnings}")

    # Test 2 : JSON avec incompatibilité
    bad_json = {
        "product_name": "Produit test",
        "characteristics": [
            {"number": 7, "parameters": {"7_01": 4, "7_02": "H", "7_03": 1, "7_04": False, "7_05": False}},
            {"number": 14, "parameters": {"14_01": ["Métro"], "14_02": "Autorisée"}},
            {"number": 74, "parameters": {"74_01": 3, "74_02": True}}
        ]
    }

    is_valid, errors, warnings = validator.validate(bad_json)
    print(f"\nTest 2 (avec incompatibilité) : {'✅ VALIDE' if is_valid else '❌ INVALIDE'}")
    if errors:
        print(f"  Erreurs : {errors}")
    if warnings:
        print(f"  Warnings : {warnings}")

    # Test 3 : Reward function
    good_output = """🧠 **Raisonnement** :

Ticket métro 1h valide.

➡️ **JSON** :

```json
{
  "product_name": "Ticket Métro",
  "characteristics": [
    {"number": 7, "parameters": {"7_01": 4, "7_02": "H", "7_03": 1, "7_04": false, "7_05": false}}
  ]
}
```

✅ Validez-vous ?"""

    reward = reward_func.calculate_reward(good_output)
    print(f"\nTest 3 (reward) : Score = {reward:.1f}/100")

if __name__ == "__main__":
    print("🧪 Test du validateur et de la reward function\n")
    print("="*70)
    test_validator()
    print("="*70)
    print("\n✅ Tests terminés")
