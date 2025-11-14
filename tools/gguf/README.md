# 📦 Cache des Binaires GGUF

Ce dossier contient les binaires compilés de `llama.cpp` pour éviter de les recompiler à chaque fine-tuning.

## 🎯 Objectif

Économiser **3-5 minutes** par fine-tuning en réutilisant les binaires déjà compilés.

## 📁 Structure

```
tools/gguf/
├── README.md                    # Ce fichier
├── bin/                         # Binaires compilés
│   ├── llama-quantize          # Binaire de quantification
│   └── quantize                # (ou ce nom selon la version)
└── convert_hf_to_gguf.py       # Script de conversion HF→GGUF
```

## 🔧 Utilisation Automatique

Les notebooks optimisés vérifient automatiquement ce dossier :

1. **Si les binaires existent** : Utilisation directe (rapide ⚡)
2. **Si les binaires n'existent pas** :
   - Compilation de llama.cpp
   - Sauvegarde dans ce dossier pour la prochaine fois

## 📦 Mise à Jour des Binaires

Pour mettre à jour vers une version plus récente de llama.cpp :

```bash
# 1. Supprimer les anciens binaires
rm -rf /content/Ftune/tools/gguf/bin/*
rm -f /content/Ftune/tools/gguf/convert_hf_to_gguf.py

# 2. Relancer le notebook
# Les nouveaux binaires seront compilés et sauvegardés automatiquement
```

## 🚀 Intégration dans les Notebooks

Les notebooks utilisent ce code pour le cache :

```python
tools_gguf_dir = "/content/Ftune/tools/gguf"

# Vérifier si les binaires existent
if os.path.exists(os.path.join(tools_gguf_dir, "bin/llama-quantize")):
    print("✅ Binaires trouvés dans le cache")
    quantize_bin = os.path.join(tools_gguf_dir, "bin/llama-quantize")
else:
    print("⚠️  Compilation nécessaire (première fois)")
    # Compiler et sauvegarder dans tools/gguf
```

## 📊 Bénéfices

| Étape | Sans Cache | Avec Cache | Gain |
|-------|------------|------------|------|
| Clone llama.cpp | 30s | 0s | ⚡ |
| Compilation | 3-5min | 0s | ⚡⚡⚡ |
| Quantification | 2-3min | 2-3min | - |
| **TOTAL** | **5-8min** | **2-3min** | **~60% plus rapide** |

## 🔄 Synchronisation Git

Les binaires **ne sont pas** commités dans le repo (trop volumineux).

Chaque environnement (Colab, local, etc.) compilera et cachera ses propres binaires.

## 🐛 Dépannage

### Binaires non trouvés
```bash
# Vérifier la présence
ls -lh /content/Ftune/tools/gguf/bin/

# Si vide, le notebook recompilera automatiquement
```

### Erreur de permission
```bash
# Rendre exécutable
chmod +x /content/Ftune/tools/gguf/bin/*
```

### Binaires corrompus
```bash
# Supprimer et recompiler
rm -rf /content/Ftune/tools/gguf/bin/*
# Relancer le notebook
```

## 📝 Notes

- Les binaires sont spécifiques à l'architecture (CPU vs CUDA)
- Le cache fonctionne mieux sur des environnements stables (pas Colab)
- Sur Colab, le cache est perdu entre sessions (mais reste utile dans une session)
- Pour une utilisation locale, les binaires persistent entre fine-tunings

## 🎯 Future Enhancement

Une amélioration future pourrait être de :
- Héberger les binaires pré-compilés sur GitHub Releases
- Télécharger au lieu de compiler (encore plus rapide)
- Supporter plusieurs architectures (x86_64, ARM, etc.)
