# Guide d'utilisation - Fine-tuning Qwen 3B pour produits de transport

## 🎓 Guide pas à pas pour débutants

Ce guide vous accompagne de A à Z pour entraîner votre propre modèle IA capable de convertir des descriptions de produits de transport en JSON.

---

## 📋 Prérequis

- ✅ Un compte Google (pour Google Colab gratuit)
- ✅ Python 3.8+ installé sur votre ordinateur (pour l'utilisation locale)
- ✅ Environ 5 GB d'espace disque libre
- ✅ Connexion internet

**Aucune carte graphique requise !** Le modèle final fonctionne sur CPU.

---

## 🚀 Étape 1: Préparation du dataset (Local - 5 min)

### 1.1 Télécharger les fichiers

Clonez ou téléchargez ce projet sur votre ordinateur.

### 1.2 Générer le dataset d'entraînement

Ouvrez un terminal dans le dossier du projet et exécutez:

```bash
python generate_training_dataset.py
```

**Que fait ce script ?**
- Génère 200 exemples variés de descriptions → JSON
- Couvre différents types de produits (abonnements, carnets, passes groupe, etc.)
- Sauvegarde dans `training_dataset.json`

**Sortie attendue:**
```
🔄 Génération du dataset d'entraînement...
✓ 200 exemples générés
✓ Dataset sauvegardé dans 'training_dataset.json'

=============================================================
EXEMPLES GÉNÉRÉS:
=============================================================

--- Exemple 1 ---
Input: Je veux un abonnement mensuel pour bus et métro
Output: {...}
```

### 1.3 Vérifier le dataset (optionnel)

Ouvrez `training_dataset.json` pour voir les exemples générés:

```json
[
  {
    "input": "Je veux un abonnement mensuel pour bus et métro",
    "output": {
      "product_name": "mensuel bus et métro",
      "characteristics": [...]
    }
  },
  ...
]
```

**💡 Personnalisation:**
Vous pouvez modifier `generate_training_dataset.py` pour ajouter:
- Vos propres templates de descriptions
- De nouveaux modes de transport
- Des contraintes spécifiques à votre domaine

---

## ☁️ Étape 2: Entraînement sur Google Colab (Gratuit - 30 min)

### 2.1 Accéder à Google Colab

1. Allez sur [https://colab.research.google.com/](https://colab.research.google.com/)
2. Connectez-vous avec votre compte Google

### 2.2 Importer le notebook

**Méthode 1: Upload direct**
1. Cliquez sur **Fichier** → **Importer le notebook**
2. Onglet **Upload**
3. Sélectionnez `transport_product_finetuning.ipynb`

**Méthode 2: Depuis GitHub**
1. **Fichier** → **Importer le notebook**
2. Onglet **GitHub**
3. Collez l'URL de votre repository

### 2.3 Configurer le GPU gratuit

1. Dans Colab, cliquez sur **Runtime** → **Change runtime type**
2. **Hardware accelerator**: Sélectionnez **T4 GPU**
3. Cliquez sur **Save**

**🎁 C'est gratuit !** Google offre accès aux GPU T4 gratuitement.

### 2.4 Upload du dataset

1. Dans le notebook, trouvez la section "4. Génération du dataset"
2. Cliquez sur l'icône 📁 (Files) dans la barre latérale
3. Cliquez sur l'icône ⬆️ (Upload)
4. Sélectionnez `training_dataset.json`

### 2.5 Exécuter l'entraînement

**IMPORTANT:** Exécutez les cellules dans l'ordre !

Cliquez sur **Runtime** → **Run all** ou exécutez cellule par cellule:

#### Cellule 1: Installation (2-3 min)
```python
!pip install -q "unsloth[colab-new] @ git+..."
```
Attendez que l'installation se termine.

#### Cellule 2-3: Imports et configuration
Exécution rapide (<10 sec).

#### Cellule 4: Chargement dataset
```python
dataset = Dataset.from_list(formatted_data)
```

#### Cellule 5: Chargement Qwen 3B (2-3 min)
```python
model, tokenizer = FastLanguageModel.from_pretrained(...)
```
Le modèle de 3 milliards de paramètres se télécharge.

#### Cellule 6-7: Configuration LoRA
Exécution rapide.

#### Cellule 8-9: **ENTRAÎNEMENT** (15-30 min)
```python
trainer_stats = trainer.train()
```

**Pendant l'entraînement, vous verrez:**
```
🚀 Démarrage de l'entraînement...

Step 10/100 | Loss: 2.341
Step 20/100 | Loss: 1.892
Step 30/100 | Loss: 1.456
...
Step 100/100 | Loss: 0.234

✓ Entraînement terminé !
```

**💡 Astuce:** Vous pouvez fermer l'onglet Colab pendant l'entraînement, il continuera en arrière-plan.

#### Cellule 10: Test du modèle
```python
test_input = "Je veux un pass mensuel pour le métro et le tramway..."
```
Vérifiez que le modèle génère du JSON cohérent.

#### Cellule 11: Validation
Calcule le score de qualité du JSON généré.

#### Cellule 12: **EXPORT GGUF** (5-10 min)
```python
model.save_pretrained_gguf(...)
```

**3 formats sont créés:**
- LoRA adapters (petit, nécessite le modèle de base)
- Merged 16-bit (gros, qualité maximale)
- **GGUF Q4/Q8** (optimal pour CPU) ⭐

#### Cellule 13: Téléchargement

**Option A: Download direct**
```python
!zip -r qwen3b_transport_gguf.zip qwen3b_transport_gguf/
```
1. Cliquez sur 📁 Files
2. Clic droit sur `qwen3b_transport_gguf.zip`
3. **Download**

**Option B: Google Drive**
```python
from google.colab import drive
drive.mount('/content/drive')
!cp -r qwen3b_transport_gguf/ /content/drive/MyDrive/
```

### 2.6 Vérifier les fichiers téléchargés

Une fois téléchargé, décompressez `qwen3b_transport_gguf.zip`:

```
qwen3b_transport_gguf/
├── unsloth.Q4_K_M.gguf  (~2 GB - rapide)
└── unsloth.Q8_0.gguf    (~3.5 GB - précis)
```

---

## 💻 Étape 3: Utilisation locale sur CPU (5 min)

### 3.1 Installation des dépendances

Dans le dossier du projet:

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

**Note:** L'installation de `llama-cpp-python` peut prendre quelques minutes (compilation).

**Problèmes d'installation ?**
- Mac M1/M2:
  ```bash
  pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/metal
  ```
- Windows: Installez Visual Studio Build Tools

### 3.2 Placer le modèle

Copiez le dossier décompressé dans le projet:
```
Ftune/
├── qwen3b_transport_gguf/
│   ├── unsloth.Q4_K_M.gguf
│   └── unsloth.Q8_0.gguf
├── inference_cpu.py
└── ...
```

### 3.3 Premier test !

```bash
python inference_cpu.py "Je veux un abonnement mensuel pour le métro"
```

**Sortie attendue:**
```
🔄 Chargement du modèle depuis qwen3b_transport_gguf/unsloth.Q4_K_M.gguf...
✓ Modèle chargé avec succès

🤖 Génération en cours...

============================================================
RÉSULTAT
============================================================

📝 Description: Je veux un abonnement mensuel pour le métro

✓ JSON valide

📦 JSON généré:
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
    ...
  ]
}

============================================================
```

**🎉 Ça marche !** Vous avez entraîné et utilisé votre propre modèle IA !

### 3.4 Mode interactif

Pour tester plusieurs descriptions:

```bash
python inference_cpu.py
```

Puis entrez vos descriptions:
```
Mode interactif - Générateur de produits de transport
============================================================
Chemin vers le modèle GGUF [qwen3b_transport_gguf/unsloth.Q4_K_M.gguf]:

✓ Prêt ! Entrez vos descriptions (Ctrl+C pour quitter)

📝 Description: Carnet de 10 tickets bus
✓ JSON valide
{...}

📝 Description: Pass 24h groupe 5 personnes
✓ JSON valide
{...}
```

---

## 🎯 Étape 4: Amélioration et personnalisation

### 4.1 Améliorer la qualité

**Augmenter le dataset:**
```python
# Dans generate_training_dataset.py
dataset = generate_full_dataset(1000)  # au lieu de 200
```

**Augmenter l'entraînement:**
```python
# Dans le notebook Colab, cellule 8
training_args = TrainingArguments(
    max_steps=500,     # au lieu de 100
    learning_rate=1e-4,  # apprentissage plus fin
)
```

### 4.2 Ajouter vos propres données

Créez un fichier `my_examples.json`:

```json
[
  {
    "input": "Votre description personnalisée",
    "output": {
      "product_name": "Votre produit",
      "characteristics": [...]
    }
  }
]
```

Dans le notebook, remplacez la cellule 4 par:
```python
import json
with open('my_examples.json', 'r') as f:
    training_data = json.load(f)
```

### 4.3 Optimiser pour votre cas d'usage

**Plus de précision (Q8):**
```bash
python inference_cpu.py \
  --model qwen3b_transport_gguf/unsloth.Q8_0.gguf \
  "description"
```

**Plus de créativité:**
```bash
python inference_cpu.py \
  --temperature 0.3 \
  "description"
```

**Plus déterministe:**
```bash
python inference_cpu.py \
  --temperature 0.01 \
  "description"
```

---

## 🐛 Problèmes fréquents

### ❌ "Modèle introuvable"

**Cause:** Le fichier GGUF n'est pas au bon endroit.

**Solution:**
```bash
# Vérifier l'emplacement
ls qwen3b_transport_gguf/

# Si absent, vérifiez que vous avez bien téléchargé depuis Colab
```

### ❌ "llama-cpp-python installation failed"

**Cause:** Compilation nécessaire.

**Solutions:**
- **Windows:** Installez Visual Studio Build Tools
- **Mac:** Installez Xcode Command Line Tools
- **Linux:** `sudo apt-get install build-essential`

### ❌ "Out of memory"

**Cause:** Modèle trop gros pour votre RAM.

**Solution:** Utilisez Q4_K_M au lieu de Q8:
```bash
python inference_cpu.py --model qwen3b_transport_gguf/unsloth.Q4_K_M.gguf
```

### ❌ "JSON invalide généré"

**Causes possibles:**
1. Modèle pas assez entraîné
2. Description trop ambiguë
3. Température trop élevée

**Solutions:**
1. Augmenter `max_steps` dans le notebook
2. Reformuler la description plus clairement
3. Réduire `--temperature 0.05`

### ❌ "Colab disconnected"

**Cause:** Inactivité ou temps limite dépassé.

**Solution:**
- Colab gratuit: ~12h max par session
- Colab Pro: sessions plus longues
- Astuce: Exécutez dans un seul bloc "Run all"

---

## 📊 Comprendre les métriques

### Loss (perte)

**Pendant l'entraînement:**
```
Step 10/100 | Loss: 2.341  ← Début (élevé)
Step 50/100 | Loss: 0.892  ← Milieu (descend)
Step 100/100 | Loss: 0.234 ← Fin (faible) ✓
```

**Bon signe:** Loss qui diminue régulièrement
**Mauvais signe:** Loss qui stagne ou augmente

### Reward Score

```
📊 REWARD SCORE: 0.85/1.00
📝 Feedback: ✓ product_name présent | ✓ characteristics présent | ✗ Schéma JSON invalide
```

- **1.00** = Parfait ✅
- **0.70-0.99** = Bon, quelques erreurs mineures
- **<0.70** = Nécessite amélioration

---

## 🎓 Aller plus loin

### Intégrer dans une application

```python
# app.py
from inference_cpu import TransportProductGenerator
from flask import Flask, request, jsonify

app = Flask(__name__)
generator = TransportProductGenerator("qwen3b_transport_gguf/unsloth.Q4_K_M.gguf")

@app.route('/generate', methods=['POST'])
def generate():
    description = request.json['description']
    result = generator.generate(description)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

### Utiliser avec Ollama

```bash
# Importer le modèle dans Ollama
ollama create transport-model -f qwen3b_transport_gguf/unsloth.Q4_K_M.gguf

# Utiliser
ollama run transport-model "Je veux un pass mensuel métro"
```

### Déployer en production

Pour une utilisation en production, considérez:
- **llama.cpp server** (API REST)
- **Ollama** (gestion facilitée)
- **vLLM** (haute performance)
- **Hugging Face Inference Endpoints**

---

## 📚 Ressources supplémentaires

- [Tutoriel Unsloth](https://github.com/unslothai/unsloth)
- [Documentation llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Qwen 2.5 Model Card](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
- [Fine-tuning best practices](https://www.databricks.com/blog/efficient-fine-tuning-lora-guide-llms)

---

## ✅ Checklist de réussite

- [ ] Dataset généré (200+ exemples)
- [ ] Notebook Colab importé
- [ ] GPU T4 activé
- [ ] Entraînement terminé (loss < 0.5)
- [ ] Modèle GGUF téléchargé
- [ ] Test local réussi
- [ ] JSON valides générés

**Félicitations ! Vous maîtrisez le fine-tuning de LLM !** 🎉

---

**Besoin d'aide ?** Ouvrez une issue sur GitHub avec:
- Votre système d'exploitation
- La commande exacte exécutée
- Le message d'erreur complet
