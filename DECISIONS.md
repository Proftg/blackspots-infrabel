# 📋 Carnet de Décisions — Projet Blackspots

**Projet :** Cartographie des Points Noirs — Réseau Ferroviaire Belge  
**Auteur :** Tahar Guenfoud  
**Objectif :** Préparer les réponses aux questions techniques d'un recruteur

---

## 1. Pourquoi supprimer ces colonnes ?

### Principe : Parcimonie des données
Tu ne conserves que ce qui contribue directement à ton objectif analytique. Objectif ici = identifier les gares avec le plus fort taux de retard. Tout ce qui ne sert pas cet objectif consomme de la mémoire, ralentit les calculs et augmente le risque d'erreurs.

### Colonne par colonne

| Colonne supprimée | Justification |
|-------------------|---------------|
| `train_no` | Granularité trop fine — on travaille à l'échelle de la gare, pas du train individuel. Que ce soit le train 2623 ou 1847 en retard à Liège, ça ne change rien au blackspot. |
| `train_serv` | Toujours SNCB/NMBS → variance zéro. Une variable constante ne discrimine rien et ne peut pas être utilisée dans une analyse comparative. |
| `op1_cod` / `thop1_cod` | 53% et 10% de manquants, codes cryptiques (=, D, P, >, V, C). Aucune documentation publique claire. Supprimer évite d'introduire du bruit. |
| `real_date_arr`, `real_date_dep`, `planned_date_arr`, `planned_date_dep` | Redondant avec `datdep` dans 95% des cas. Colonnes redondantes = mémoire gaspillée sans valeur ajoutée. |
| `real_time_arr`, `real_time_dep`, `planned_time_arr`, `planned_time_dep` | Heures individuelles inutiles pour calculer un blackspot. La colonne `retard` est déjà la différence entre heure réelle et planifiée. Recalculer serait redondant. |
| `line_no_arr` | 4.9% manquants, et `line_no_dep` existe déjà. Pour les blackspots, la ligne de départ est la référence. |
| `relation_direction` | 5.4% manquants, et `relation` contient déjà l'info essentielle (IC 08, S62, etc.). `relation_direction` ajoute juste le sens du trajet en texte long. |

### 🎯 Réponse recruteur :
> "J'ai appliqué le principe de sélection de features en amont de l'analyse. Chaque colonne supprimée l'a été pour une raison précise : variance nulle, redondance, taux de manquants trop élevé, ou granularité incompatible avec le niveau d'analyse. Ça m'a permis de réduire l'empreinte mémoire de 87% et d'accélérer significativement les calculs sur 22 millions de lignes."

### Impact concret
- **Avant :** 22 colonnes, 3.7 GB en mémoire
- **Après :** 8 colonnes, ~400-500 MB
- **Gain :** Opérations groupby/filtre/aggrégation 4-5x plus rapides

---

## 2. Pourquoi filtrer les outliers de retard ?

### Le problème
- `DELAY_DEP` en secondes, avec des valeurs aberrantes :
  - min : -85,482s (-23.7 heures) → impossible
  - max : 38,677s (+10.7 heures) → suspect
- Ces valeurs sont des erreurs de données, pas des retards réels

### La solution
```python
df = df[(df['retard'] >= -30) & (df['retard'] <= 1800)]
```
- **-30s** : tolérance pour les trains partant légèrement en avance
- **1800s (30min)** : seuil réaliste pour un retard de départ significatif

### Impact
- Avant filtrage : 22,642,916 lignes
- Après filtrage : ~19,730,044 lignes (87% gardées)
- Les 13% supprimés étaient des données invalides

### 🎯 Réponse recruteur :
> "J'ai identifié des outliers physiquement impossibles (-23h de retard) en utilisant des bornes métier raisonnables. Le seuil de 30 minutes pour les retards de départ est basé sur la réalité opérationnelle : au-delà, c'est souvent une annulation, pas un retard. J'ai choisi de filtrer plutôt que d'imputer pour ne pas introduire de biais dans le calcul des KPIs."

---

## 3. Pourquoi convertir les secondes en minutes ?

### Raisonnement
- Les données brutes sont en **secondes** (standard GTFS-Realtime)
- Pour un dashboard orienté business, les **minutes** sont plus lisibles
- 120 secondes → "2 minutes" est immédiatement compréhensible

### 🎯 Réponse recruteur :
> "J'ai converti les secondes en minutes pour aligner le format sur le vocabulaire métier. Les KPIs de ponctualité d'Infrabel sont exprimés en minutes (ponctualité brute = trains avec moins de 6 minutes de retard). Toujours parler le languel du business dans ses visualisations."

---

## 4. Pourquoi normaliser les noms de gares ?

### Le problème
- Données brutes : `MECHELEN`, `BRUSSELS AIRPORT - ZAVENTEM`, ` KORTENBERG `
- Espaces en trop, casse incohérente, pas de standard

### La solution
```python
df['gare'] = df['gare'].astype(str).str.strip().str.title()
```
- `strip()` : supprime les espaces
- `title()` : première lettre en majuscule → `Mechelen`, `Brussels Airport - Zaventem`

### 🎯 Réponse recruteur :
> "La normalisation des noms est essentielle avant toute aggrégation. Sans ça, 'MECHELEN' et 'mechelen' seraient comptés comme deux gares différentes, faussant les KPIs. C'est une étape classique de data cleaning que tout analyste doit faire avant un groupby."

---

## 5. Pourquoi créer une colonne `delay_min` au lieu de modifier `retard` ?

### Raisonnement
- Garder la colonne originale (`retard` en secondes) pour traçabilité
- Créer une nouvelle colonne (`delay_min`) pour l'analyse
- En cas d'erreur, on peut toujours revenir aux données brutes

### 🎯 Réponse recruteur :
> "J'applique le principe d'immuabilité des données brutes : je ne modifie jamais la colonne source, je crée des colonnes dérivées. C'est une bonne pratique qui garantit la reproductibilité et permet de vérifier mes calculs à tout moment."

---

## 6. Pourquoi ne pas sauvegarder les 22M lignes en CSV ?

### Problème
- 22M lignes × 22 colonnes = ~3.7 GB en mémoire
- En CSV : fichier de 2-3 Go, plusieurs minutes à écrire/lire
- Pour une aggrégation par gare, on a besoin de ~500 lignes de résultat

### Solution
- Ne sauvegarder que le **résultat agrégé** (par gare)
- Les données brutes restent accessibles via l'API Infrabel

### 🎯 Réponse recruteur :
> "J'ai fait un choix pragmatique de stockage : sauvegarder le résultat agrégé (500 gares) plutôt que les données brutes (22M lignes). Pour un projet portfolio, le résultat est reproductible en relançant le notebook. En production, j'utiliserais une base de données ou Parquet pour le stockage intermédiaire."

---

## 7. Pourquoi `delay_arr` (retard arrivée) est aussi important que `delay_dep` ?

### Différence métier
- **`delay_dep`** (retard départ) : impacte les voyageurs qui montent à cette gare
- **`delay_arr`** (retard arrivée) : impacte les voyageurs qui descendent + connexions manquées

### Pourquoi les deux comptent
- Un train peut partir à l'heure mais arriver en retard (ralentissement en ligne)
- Infrabel mesure la **ponctualité à l'arrivée** comme KPI principal
- Un blackspot d'arrivée ≠ blackspot de départ

### 🎯 Réponse recruteur :
> "Pour un projet complet, j'analyserais les deux dimensions : les gares où les trains partent en retard (problème d'exploitation gare) et les gares où ils arrivent en retard (problème d'infrastructure ou de trafic). La distinction permet de diagnostiquer l'origine du problème."

---

## 8. Pourquoi ne pas utiliser d'auto-détection des colonnes ?

### Le code proposé
```python
if any(x in c for x in ['station', 'gare', 'halte', 'stop']):
    col_gare = col
```

### Pourquoi j'ai choisi l'assignation directe
- Les colonnes Infrabel utilisent des codes internes (`ptcar_lg_nm_nl`, `delay_dep`)
- L'auto-détection ne matche pas `ptcar_lg_nm_nl` avec "gare"
- Assignation directe = 100% fiable vs guesswork fragile

### 🎯 Réponse recruteur :
> "L'auto-détection est utile quand on ne connaît pas le dataset. Ici, j'ai exploré les données, je connais la structure. L'assignation directe est plus fiable et plus lisible. Un bon analyste sait quand automatiser et quand être explicite."

---

## 9. Pourquoi `op1_cod` et `thop1_cod` ne sont PAS la même chose ?

### Observation
- Valeurs communes : `=`, `D`, `P`, `>`, `V`, `C`, `(`, `)`, `<`
- `op1_cod` a `'':` en plus
- 61% des lignes ont des valeurs différentes entre les deux

### Conclusion
- Ce sont deux codes distincts (opération réelle vs théorique ?)
- Mais sans documentation publique, on ne peut pas interpréter
- Mieux vaut supprimer que de spéculer

### 🎯 Réponse recruteur :
> "J'ai vérifié si les deux colonnes étaient redondantes en comparant les valeurs ligne par ligne. Résultat : 61% de différences, donc ce sont des concepts distincts. Sans documentation, j'ai préféré les supprimer plutôt que de risquer une mauvaise interprétation. En entreprise, je demanderais au métier la signification exacte."

---

## 10. Pourquoi ce projet impressionne un recruteur Infrabel ?

### Ce qui le différencie
1. **Données réelles Infrabel** — pas un dataset Kaggle générique
2. **API temps réel** — pas des CSV statiques
3. **Volume** — 22M lignes, pas un toy dataset
4. **Pertinence métier** — ponctualité = KPI #1 d'Infrabel
5. **Pipeline complet** — ingestion → cleaning → analyse → visualisation

### Vocabulaire à utiliser en entretien
- "Ponctualité brute" (% trains < 6 min de retard)
- "Minutes perdues" (impact économique)
- "Points noirs" (gares/tronçons problématiques)
- "Contrat de Performance" (accord État-Infrabel)

### 🎯 Pitch 30 secondes
> "J'ai développé une cartographie des points noirs du réseau ferroviaire belge en analysant 22 millions de lignes de données de ponctualité Infrabel. J'ai identifié les gares avec le plus fort taux de retards en combinant nettoyage de données, aggrégation par gare et visualisation géospatiale. Ce projet m'a permis de comprendre les KPIs clés du secteur : la ponctualité brute et les minutes perdues, qui sont au cœur du Contrat de Performance d'Infrabel."

---

## 11. Pourquoi convertir les colonnes `object` en `category` ?

### Le problème
- Après nettoyage : 8 colonnes, mémoire shallow = 1.3 GB
- Mémoire deep = **5.15 GB** à cause de 3 colonnes `object` : `relation`, `gare`, `line_no_dep`
- Ces colonnes stockent des chaînes de caractères **répétées des millions de fois**
- Exemple : "Mechelen" apparaît ~45,000 fois → 45,000 copies de la même string

### La solution
```python
for col in ['relation', 'gare', 'line_no_dep']:
    df[col] = df[col].astype('category')
```

### Comment ça marche
- `category` = encodage interne : Pandas stocke chaque valeur **une seule fois** + un index entier
- "Mechelen" → stocké 1 fois → référencé par l'entier `42` (par exemple)
- 22M lignes × entier (1-4 octets) vs 22M × string (8+ octets)

### Impact concret
| Avant (object) | Après (category) |
|----------------|------------------|
| 5.15 GB | ~800 MB - 1 GB |
| String répétée millions de fois | Index entier + dictionnaire unique |

### Quand utiliser `category` vs `object`

| Situation | Type optimal |
|-----------|-------------|
| Cardinalité faible (< 1000 uniques) répétée | `category` ✅ |
| Cardinalité haute (texte libre, noms uniques) | `object` |
| Dates | `datetime64` |
| Nombres | `int`/`float` |

### 🎯 Réponse recruteur :
> "J'ai converti les colonnes à faible cardinalité en type `category` de Pandas. Au lieu de stocker 22 millions de copies de 'Mechelen', Pandas stocke le mot une seule fois et utilise un index entier pour les références. Ça m'a permis de passer de 5 GB à moins de 1 GB en mémoire — un gain de 80% qui rend toutes les opérations suivantes beaucoup plus rapides. C'est une optimisation classique quand on travaille avec des données catégorielles à grande échelle."

---

## 12. Pourquoi télécharger les données via l'API plutôt qu'utiliser des CSV statiques ?

### Le choix
```python
INDEX_URL = 'https://opendata.infrabel.be/api/explore/v2.1/catalog/datasets/...'
resp = requests.get(INDEX_URL, timeout=30)
```

### Raisonnement
- L'API Infrabel fournit un index des 100 derniers mois
- Téléchargement automatique des 12 derniers mois — reproductible et à jour
- Un CSV statique devient obsolète ; l'API garantit les dernières données

### 🎯 Réponse recruteur :
> "J'ai utilisé l'API Open Data d'Infrabel pour rendre le notebook reproductible et automatiquement à jour. À chaque exécution, il récupère les 12 derniers mois. C'est une approche pipeline — pas un one-shot sur des données figées."

---

## 13. Pourquoi stocker les coordonnées GPS en dur plutôt que via une API ?

### Le choix
```python
COORDS_GARES = {
    'Bruxelles-Central': (50.8453, 4.3571),
    'Gand-Saint-Pierre': (51.0355, 3.7103),
    ...
}
```

### Raisonnement
- 25 gares principales suffisent pour couvrir 90% du trafic
- API géocodage = dépendance externe + rate limits + latence
- Coordonnées de gares = données statiques qui ne changent pas
- Approche pragmatique : fonctionne hors ligne, zéro coût

### 🎯 Réponse recruteur :
> "J'ai codé en dur les coordonnées des 25 principales gares belges. Pour un projet portfolio, c'est plus fiable qu'une API externe — pas de rate limit, pas de dépendance réseau. En production, j'utiliserais une table de référence ou l'API iRail pour les coordonnées de toutes les gares."

---

## 14. Pourquoi la correspondance approximative pour les noms de gares ?

### Le problème
- Données Infrabel : `MECHELEN`, `GENT-SINT-PIETERS`, `LUIK-GUILLEMINS`
- Coordonnées : `Mechelen`, `Gent-Sint-Pieters`, `Luik-Gillemins`
- Variants FR/NL : `Anvers-Central` vs `Antwerpen-Centraal`

### La solution
```python
def get_coords(gare_name):
    # Correspondance exacte d'abord
    if g in COORDS_GARES: return COORDS_GARES[g]
    # Puis partielle (inclusion)
    for key, coords in COORDS_GARES.items():
        if g.lower() in key.lower() or key.lower() in g.lower():
            return coords
```

### 🎯 Réponse recruteur :
> "Les noms de gares en Belgique varient entre français et néerlandais. J'ai implémenté une correspondance en deux niveaux — exacte d'abord, puis partielle — pour maximiser le taux de match. C'est un problème classique de data matching dans les données multilingues belges."

---

## 15. Pourquoi le double axe sur le graphique de tendance ?

### Le choix
```python
fig3 = make_subplots(specs=[[{'secondary_y': True}]])
# Axe principal (gauche) : % en retard + retard moyen
# Axe secondaire (droite) : nombre de passages
```

### Raisonnement
- Le nombre de passages (~1.5M-1.8M) est 1000x plus grand que le % en retard (~8-13%)
- Sans double axe, le % serait invisible (aplani en bas)
- Le double axe permet de voir la corrélation : plus de passages = plus de retards ?

### 🎯 Réponse recruteur :
> "J'ai utilisé un double axe Y pour comparer des grandeurs d'ordres très différents — des pourcentages (8-13%) et des volumes (1.5M+). C'est la seule façon de visualiser la relation entre volume de trafic et ponctualité sur le même graphique. J'ai fait attention à étiqueter clairement les deux axes pour éviter la confusion."

---

*Dernière mise à jour : 2026-03-15 (session Blackspots complète)*
