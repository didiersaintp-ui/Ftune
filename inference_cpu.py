"""
Script d'inférence CPU pour le modèle de génération de produits de transport

Ce script utilise le modèle GGUF quantifié pour des inférences rapides sur CPU.
Compatible avec llama-cpp-python.

Installation:
    pip install llama-cpp-python jsonschema

Usage:
    python inference_cpu.py "Je veux un abonnement mensuel pour le métro"
"""

import json
import sys
import argparse
from typing import Dict, Optional
from pathlib import Path

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    print("⚠ llama-cpp-python non installé. Installez avec:")
    print("   pip install llama-cpp-python")

try:
    import jsonschema
    from jsonschema import validate
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("⚠ jsonschema non installé. Validation désactivée.")

# Schéma de validation (simplifié)
TRANSPORT_SCHEMA = {
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

class TransportProductGenerator:
    """Générateur de produits de transport basé sur GGUF"""

    def __init__(self, model_path: str, verbose: bool = False):
        """
        Initialise le générateur

        Args:
            model_path: Chemin vers le fichier GGUF
            verbose: Mode verbose pour débug
        """
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError("llama-cpp-python requis")

        self.verbose = verbose

        print(f"🔄 Chargement du modèle depuis {model_path}...")

        self.model = Llama(
            model_path=model_path,
            n_ctx=2048,  # Contexte
            n_threads=4,  # Threads CPU
            n_gpu_layers=0,  # CPU uniquement
            verbose=verbose
        )

        print("✓ Modèle chargé avec succès\n")

    def format_prompt(self, description: str) -> str:
        """Formate le prompt pour l'inférence"""
        return f"""Vous êtes un assistant spécialisé dans la création de produits de transport. Convertissez la description suivante en JSON structuré.

### Description:
{description}

### JSON:"""

    def extract_json(self, text: str) -> Optional[Dict]:
        """Extrait le JSON de la réponse"""
        try:
            # Chercher le JSON dans la réponse
            start = text.find("{")
            end = text.rfind("}") + 1

            if start != -1 and end > start:
                json_text = text[start:end]
                return json.loads(json_text)
        except Exception as e:
            if self.verbose:
                print(f"⚠ Erreur extraction JSON: {e}")

        return None

    def validate_json(self, json_obj: Dict) -> tuple[bool, str]:
        """
        Valide le JSON généré

        Returns:
            (valid, message)
        """
        if not JSONSCHEMA_AVAILABLE:
            return True, "Validation désactivée"

        try:
            validate(instance=json_obj, schema=TRANSPORT_SCHEMA)
            return True, "✓ JSON valide"
        except jsonschema.exceptions.ValidationError as e:
            return False, f"✗ Erreur validation: {e.message}"

    def generate(
        self,
        description: str,
        temperature: float = 0.1,
        max_tokens: int = 512,
        validate_output: bool = True
    ) -> Dict:
        """
        Génère un produit de transport depuis une description

        Args:
            description: Description en langage naturel
            temperature: Température de génération (0.0-1.0)
            max_tokens: Nombre max de tokens à générer
            validate_output: Valider le JSON de sortie

        Returns:
            Dictionnaire avec le résultat
        """
        prompt = self.format_prompt(description)

        if self.verbose:
            print(f"📝 Prompt:\n{prompt}\n")

        print("🤖 Génération en cours...")

        # Génération
        output = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["###", "\n\n\n"],
        )

        generated_text = output["choices"][0]["text"]

        if self.verbose:
            print(f"\n📄 Réponse brute:\n{generated_text}\n")

        # Extraction du JSON
        json_obj = self.extract_json(generated_text)

        result = {
            "description": description,
            "raw_output": generated_text,
            "json": json_obj,
            "valid": False,
            "validation_message": ""
        }

        if json_obj is None:
            result["validation_message"] = "✗ Impossible d'extraire le JSON"
            return result

        # Validation
        if validate_output:
            is_valid, msg = self.validate_json(json_obj)
            result["valid"] = is_valid
            result["validation_message"] = msg
        else:
            result["valid"] = True
            result["validation_message"] = "Validation ignorée"

        return result

def main():
    parser = argparse.ArgumentParser(
        description="Génération de produits de transport avec IA"
    )
    parser.add_argument(
        "description",
        type=str,
        help="Description du produit en langage naturel"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="qwen3b_transport_gguf/unsloth.Q4_K_M.gguf",
        help="Chemin vers le modèle GGUF"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Température de génération (0.0-1.0)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mode verbose"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Désactiver la validation"
    )

    args = parser.parse_args()

    # Vérification du modèle
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"❌ Modèle introuvable: {model_path}")
        print("\n💡 Assurez-vous d'avoir entraîné et exporté le modèle avec le notebook Colab")
        sys.exit(1)

    try:
        # Initialisation
        generator = TransportProductGenerator(
            model_path=str(model_path),
            verbose=args.verbose
        )

        # Génération
        result = generator.generate(
            description=args.description,
            temperature=args.temperature,
            validate_output=not args.no_validate
        )

        # Affichage des résultats
        print("\n" + "="*60)
        print("RÉSULTAT")
        print("="*60)

        print(f"\n📝 Description: {result['description']}")
        print(f"\n{result['validation_message']}")

        if result['json']:
            print(f"\n📦 JSON généré:")
            print(json.dumps(result['json'], ensure_ascii=False, indent=2))
        else:
            print(f"\n⚠ Aucun JSON valide trouvé")
            if args.verbose:
                print(f"\n📄 Sortie brute:\n{result['raw_output']}")

        print("\n" + "="*60)

        # Code de sortie
        sys.exit(0 if result['valid'] else 1)

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Mode interactif si aucun argument
        print("Mode interactif - Générateur de produits de transport")
        print("="*60)

        model_path = input("Chemin vers le modèle GGUF [qwen3b_transport_gguf/unsloth.Q4_K_M.gguf]: ").strip()
        if not model_path:
            model_path = "qwen3b_transport_gguf/unsloth.Q4_K_M.gguf"

        if not Path(model_path).exists():
            print(f"❌ Modèle introuvable: {model_path}")
            sys.exit(1)

        generator = TransportProductGenerator(model_path=model_path)

        print("\n✓ Prêt ! Entrez vos descriptions (Ctrl+C pour quitter)\n")

        while True:
            try:
                description = input("📝 Description: ").strip()
                if not description:
                    continue

                result = generator.generate(description)

                print(f"\n{result['validation_message']}")
                if result['json']:
                    print(json.dumps(result['json'], ensure_ascii=False, indent=2))
                else:
                    print("⚠ Aucun JSON généré")

                print()

            except KeyboardInterrupt:
                print("\n\n👋 Au revoir !")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}\n")
    else:
        main()
