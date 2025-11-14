# 🚀 Fine-tuning Ministral 3B pour TCL Lyon

Guide complet pour utiliser les notebooks de fine-tuning avec **Ministral 3B** (Mistral AI).

## 📋 Vue d'ensemble

Ce repository contient 2 notebooks pour un workflow de training en 2 phases avec Ministral 3B:

1. **`transport_finetuning_Ministral_SFT.ipynb`** - Phase 1: Supervised Fine-Tuning (SFT)
2. **`transport_finetuning_Ministral_DPO.ipynb`** - Phase 2: Direct Preference Optimization (DPO)

## ⚠️ Pré-requis IMPORTANTS

### 1. Vérifier la disponibilité de Ministral 3B

**Ministral 3B** est un modèle récent (octobre 2024) de Mistral AI. Avant d'exécuter:

```python
# Vérifiez sur HuggingFace que le modèle existe:
# - https://huggingface.co/mistralai/Ministral-3B-Instruct-2410
# - https://huggingface.co/unsloth/Ministral-3B-Instruct (si disponible)
```

### 2. Support Unsloth

- GitHub Issue #1677 demande le support de Ministral 3B dans Unsloth
- Status: À vérifier avant d'exécuter
- Fallback: Utilisez les notebooks Qwen si Ministral n'est pas encore supporté

### 3. Noms de modèles possibles

Les notebooks essaient dans cet ordre:
1. `unsloth/Ministral-3B-Instruct` (préféré)
2. `mistralai/Ministral-3B-Instruct-2410`
3. `mistralai/Ministral-3B-2410`

**Ajustez le nom dans la cellule 12 du notebook SFT si nécessaire.**

## 🎯 Ministral 3B - Caractéristiques

- **Paramètres**: 3 milliards
- **Context**: Jusqu'à 128k tokens (32k sur vLLM)
- **Performance**: Surpasse Mistral 7B sur la plupart des benchmarks
- **Optimisé pour**: Edge computing, on-device inference
- **Langues**: Support multilingue natif

## 📚 Workflow en 2 Phases

### Phase 1: SFT (Supervised Fine-Tuning)
**Notebook**: `transport_finetuning_Ministral_SFT.ipynb`

- **Dataset**: 7492 exemples (SFT + DPO combinés)
- **Durée**: ~120-150 minutes sur T4 GPU
- **Objectif**: Apprendre les patterns, formats, règles TCL
- **Output**: Modèle de base sauvegardé sur Google Drive

**Exécution**:
1. Ouvrir le notebook dans Google Colab
2. Sélectionner GPU Runtime (T4 recommandé)
3. Exécuter toutes les cellules
4. Le modèle sera sauvegardé dans `/content/drive/MyDrive/Ftune_Models_Ministral/`

### Phase 2: DPO (Direct Preference Optimization)
**Notebook**: `transport_finetuning_Ministral_DPO.ipynb`

- **Dataset**: 1004 paires DPO pures (chosen/rejected)
- **Durée**: ~30-40 minutes sur T4 GPU
- **Objectif**: Affiner les préférences et la qualité
- **Input**: Modèle SFT de la Phase 1
- **Output**: Modèle final optimisé

**Exécution**:
1. **Pré-requis**: Avoir complété la Phase 1
2. Ouvrir le notebook dans Google Colab
3. Le notebook chargera automatiquement le modèle SFT depuis Google Drive
4. Exécuter toutes les cellules

## 🔧 Configuration

Les notebooks utilisent les mêmes hyperparamètres que Qwen 3B (taille similaire):

### Phase 1 (SFT):
```python
MAX_SEQ_LENGTH = 2048
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 8  # Effective batch = 16
MAX_STEPS = 3000  # ~6.4 epochs sur 7492 exemples
LEARNING_RATE = 1e-4
LORA_RANK = 64
LORA_ALPHA = 128  # 2×rank
```

### Phase 2 (DPO):
```python
MAX_SEQ_LENGTH = 2048
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 8
MAX_STEPS = 500  # ~8 epochs sur 1004 paires
LEARNING_RATE = 5e-5  # Plus bas pour DPO
DPO_BETA = 0.1  # KL penalty
```

## 🐛 Dépannage

### Erreur: "Model not found"

```python
# Dans la cellule 12 du notebook SFT, changez:
MODEL_NAME = "mistralai/Ministral-3B-Instruct-2410"  # Essayez ce nom
```

### Erreur: "Unsloth doesn't support this model"

- Vérifiez l'issue GitHub #1677 pour les mises à jour
- En attendant le support officiel, utilisez les notebooks Qwen:
  - `transport_finetuning_ULTRA_2.ipynb` (SFT)
  - `transport_finetuning_DPO_REAL.ipynb` (DPO)

### Mémoire insuffisante

- Réduisez `BATCH_SIZE` à 1
- Réduisez `MAX_SEQ_LENGTH` à 1024
- Utilisez Google Colab Pro pour plus de RAM

## 📊 Résultats Attendus

Après Phase 1 + Phase 2:
- **Structure**: 100% (appris en SFT)
- **JSON valide**: >98% (appris en SFT)
- **Qualité des réponses**: >95% (amélioré par DPO)
- **Détection incompatibilités**: >92% (affiné par DPO)
- **Préférences bonnes pratiques**: ✅ (DPO)

## 🔄 Comparaison avec Qwen 3B

| Aspect | Qwen 2.5 3B | Ministral 3B |
|--------|-------------|--------------|
| Paramètres | 3B | 3B |
| Context | 32k | 128k (32k vLLM) |
| Support Unsloth | ✅ Officiel | ⚠️ À vérifier |
| Optimisé pour | Général | Edge/On-device |
| Benchmarks | Excellent | Supérieur à Mistral 7B |

## 💡 Recommandations

1. **Pour production**: Testez d'abord avec Qwen 3B (support garanti)
2. **Pour expérimentation**: Essayez Ministral 3B si le support Unsloth est confirmé
3. **Monitoring**: Surveillez la qualité des sorties et comparez avec Qwen 3B

## 📝 Notes de Version

- **Version initiale**: Adaptation depuis Qwen 3B notebooks
- **Status**: Expérimental - Support Unsloth à confirmer
- **Alternative stable**: Notebooks Qwen (`ULTRA_2` et `DPO_REAL`)

## 🔗 Ressources

- [Ministral AI Announcement](https://mistral.ai/news/ministraux)
- [Unsloth GitHub](https://github.com/unslothai/unsloth)
- [Issue #1677 - Ministral Support](https://github.com/unslothai/unsloth/issues/1677)
- [HuggingFace Ministral](https://huggingface.co/models?search=ministral)

## ⚠️ Avertissement

Ces notebooks sont des adaptations des notebooks Qwen 3B. Le support de Ministral 3B dans Unsloth n'est pas garanti au moment de la création (janvier 2025).

**Utilisez les notebooks Qwen pour une expérience stable et garantie.**
