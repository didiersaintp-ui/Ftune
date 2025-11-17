# 📊 Dataset Creation Progress

## Objectif Total : 550 Exemples Manuels

### ✅ Complété

#### Batch 1 : Core SFT Simple (20/20) ✅
- **Fichier** : `dataset/core_sft_batch1.json`
- **Status** : ✅ COMPLET
- **Exemples** : 20
- **Complexité** : LOW to MEDIUM
- **CAR couvertes** : 7, 14, 22, 9, 4, 21
- **Produits types** :
  - Tickets unitaires (métro, bus, tramway)
  - Abonnements mensuels (plein tarif, jeune, senior, étudiant, solidaire)
  - Carnets (5, 10, 20 voyages)
  - Pass temporels (24h, 48h, 72h, hebdo)
  - Carnet multi-usager

#### Batch 2 : Core SFT Medium (9/30) 🔄
- **Fichier** : `dataset/core_sft_batch2.json`
- **Status** : 🔄 EN COURS (30%)
- **Exemples** : 9/30
- **Complexité** : MEDIUM (3-4 CAR)
- **CAR couvertes** : 3, 10, 102, 107, 97, 2
- **Produits types** :
  - Abonnements avec restrictions (lignes, horaires, zones)
  - Forfaits avec limitations (trajets/jour)
  - Tacite reconduction
  - Promotions durée
  - Remboursement
  - Pass groupe

**À terminer** : 21 exemples restants

### 🔄 En Cours / À Faire

#### Batch 2 - Suite (21 exemples restants)
**Subtilités à couvrir** :
1. Forfait 20 déplacements/semaine (CAR_10)
2. Abonnement tous modes SAUF train (CAR_14 interdit)
3. Ticket avec fidélité 2 points/validation (CAR_23)
4. Pass 5 jours consécutifs
5. Abonnement zones 2-3 sans zone 1 (CAR_4)
6. Carnet 15 voyages
7. Pass matinée 6h-12h (CAR_9)
8. Abonnement mensuel bus uniquement
9. Pass 10 jours utilisables sur 1 mois
10. Abonnement semestriel 6 mois
11. Ticket famille 4 personnes (CAR_2)
12. Pass nuit 20h-6h (CAR_9)
13. Abonnement lignes T1-T2-T3 tramway (CAR_3)
14. Forfait 30 déplacements/mois (CAR_10)
15. Pass jour groupe 3 personnes (CAR_2)
16. Abonnement 2 mois
17. Ticket correspondance 2h
18. Pass événement spécial dates fixes (nature 0)
19. Abonnement jeune annuel
20. Carnet 30 voyages 6 mois
21. Pass multi-jours non consécutifs

#### Batch 3 : Core SFT All CAR (50 exemples)
**Objectif** : Couvrir TOUTES les 29 CAR
**CAR manquantes** : 6, 8, 11, 23, 38, 48, 58, 73, 74, 86, 87, 90, 91, 98, 103, 105, 121
**Complexité** : MEDIUM to HIGH

#### DPO Pairs : Incompatibilités (50 paires)
**Incompatibilités à couvrir** :
- CAR_14 ⊗ CAR_74 (10 variations)
- CAR_22 ⊗ CAR_21 (10 variations)
- CAR_2 ⊗ CAR_38 (5 variations)
- CAR_3 ⊗ CAR_87 (5 variations)
- CAR_4 ⊗ CAR_121 (5 variations)
- CAR_6 ⊗ CAR_21 (3 variations)
- BSC + CAR_10 (3 variations)
- BSC + CAR_102 (3 variations)
- BSC + rechargement (3 variations)
- Autres combinaisons (3 variations)

#### DPO Pairs : Qualité Conversationnelle (30 paires)
**Scénarios** :
- Requête incomplète → Questions (10 paires)
- Format JSON vs Texte brut (5 paires)
- Raisonnement vs Réponse directe (5 paires)
- Multi-turn vs One-shot (5 paires)
- Validation utilisateur vs Silence (5 paires)

#### Advanced SFT : Produits Complexes (100 exemples)
**Types** :
- 5+ CAR combinées (40 exemples)
- Produits réels TCL/RATP/autres (30 exemples)
- Cas edge durées inhabituelles (15 exemples)
- Cas edge prix (10 exemples)
- Produits multi-réseaux (5 exemples)

#### Edge Cases (100 exemples)
**Catégories** :
- Durées : 30min, 90min, 5j, 15j, 18 mois, 24 mois (20)
- Prix : 0.50€, 0.80€, 150€, 250€ (10)
- Modes combinés inhabituels (15)
- Zones non standard (10)
- Horaires complexes multi-tranches (15)
- Limitations complexes (10)
- Promotions variées (10)
- Produits saisonniers (10)

#### Multi-Turn Dialogues (50 exemples)
**Scénarios** :
- Création progressive (15 dialogues)
- Clarification besoin (10 dialogues)
- Correction erreur (10 dialogues)
- Recommandation + ajustement (10 dialogues)
- Comparaison produits (5 dialogues)

#### CAR Explanations (60 exemples)
**Format** : 2 exemples par CAR (29×2 + 2 bonus)
- Question : "Comment fonctionne CAR_X ?"
- Réponse : Explication détaillée + 2 exemples

## 📈 Progression Totale

| Catégorie | Complété | Objectif | % |
|-----------|----------|----------|---|
| Batch 1 | 20 | 20 | 100% |
| Batch 2 | 9 | 30 | 30% |
| Batch 3 | 0 | 50 | 0% |
| DPO Incomp. | 0 | 50 | 0% |
| DPO Conv. | 0 | 30 | 0% |
| Advanced SFT | 0 | 100 | 0% |
| Edge Cases | 0 | 100 | 0% |
| Multi-Turn | 0 | 50 | 0% |
| CAR Expl. | 0 | 60 | 0% |
| **TOTAL** | **29** | **490** | **5.9%** |

Note : Objectif ajusté à 490 (vs 550 initial) pour focus qualité

## 🎯 Prochaines Étapes Immédiates

1. **Compléter Batch 2** : +21 exemples (target: 30 total)
2. **Créer DPO Incompatibilités** : 50 paires
3. **Créer Batch 3** : 50 exemples couvrant CAR manquantes
4. **DPO Conversationnel** : 30 paires
5. **Advanced + Edge + Multi-turn** : 250 exemples
6. **CAR Explanations** : 60 exemples

## 💾 Fichiers à Créer

- ✅ `core_sft_batch1.json` (20)
- 🔄 `core_sft_batch2.json` (9/30)
- ⏳ `core_sft_batch3.json` (0/50)
- ⏳ `dpo_incompatibilities.json` (0/50)
- ⏳ `dpo_conversational.json` (0/30)
- ⏳ `advanced_sft.json` (0/100)
- ⏳ `edge_cases.json` (0/100)
- ⏳ `multi_turn_dialogues.json` (0/50)
- ⏳ `car_explanations.json` (0/60)

**Total fichiers** : 9 fichiers JSON

---

**Dernière mise à jour** : 2025-01-16
**Progression globale** : 29/490 (5.9%)
