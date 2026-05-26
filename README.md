# Projet SMA — Système Multi‑Agents pour l'apprentissage des langues

Ce dépôt contient une plateforme expérimentale qui simule des conversations réalistes en langue étrangère,
corrige la grammaire via un pipeline RAG, vérifie la pertinence culturelle et formate la réponse finale.
Le système est orchestré par un graphe d'agents (LangGraph) et propose une interface Web et un mode CLI.

---

## Points forts

- Multi‑agents : pipeline séquentiel et agents spécialisés (génération, correction, contrôle culturel, formatage, sauvegarde).
- RAG pour la correction grammaticale : récupération BM25 sur la base documentaire fournie (`files/Grammer.pdf`).
- Interface Web en Streamlit et mode CLI pour usage léger.
- Framework d'évaluation de prompts (A/B/C) inclus.

---

## Installation rapide

Pré-requis : Python 3.10+ et `pip`.

1. Installer les dépendances :

```bash
pip install -r requirements.txt
```

2. Créer un fichier `.env` (variables d'environnement) avec au minimum :

- `MODELNAME` — nom du modèle Ollama à utiliser
- `TAVILYAPIKEY` — clé Tavily pour la recherche web
- `OLLAMA_API_KEY` — token Bearer pour Ollama

Les clés optionnelles (ex. `LANGSMITH_API_KEY`) permettent d'activer le traçage.

---

## Structure du projet

Voir l'organisation principale des fichiers :

- `agents.py` — définitions et prompts des agents
- `workflows.py` — graphe LangGraph (déroulement des agents)
- `Ui.py` — interface Streamlit
- `withoutUi.py` — interface CLI
- `prompt_evaluation.py` — framework d'évaluation des prompts
- `files/Grammer.pdf` — base de connaissances pour RAG
- `picture/` — captures d'écran et schémas (listées ci‑dessous)

---

## Utilisation

Web (recommandé) :

```bash
streamlit run Ui.py
```

CLI :

```bash
python withoutUi.py
```

Évaluation des prompts :

```bash
python prompt_evaluation.py
```

---

## Architecture et agents (résumé)

Le flux principal : génération de scénario → réponse `character` → correction `teacher` (RAG) → contrôle `mentality` → `styler` → demande de sauvegarde (`save_check`) → `save_agent`.

Agents clés : `situational`, `character`, `teacher`, `mentality`, `styler`, `save_agent`.

---

## Captures d'écran et schémas

Ci‑dessous les captures disponibles dans le répertoire `picture/` avec une brève description.

- Interface principale — vue générale annotée
  ![Interface principale](<picture/Interface principale — vue générale annotée .png>)

- Barre latérale — détail des contrôles
  ![Barre latérale — détail des contrôles](<picture/Barre latérale — détail des contrôles.png>)

- Page de connexion — onglets Sign In et Create Account
  ![Page de connexion](<picture/Page de connexion — onglets Sign In et Create Account.png>)

- Écran d'inscription — formulaire Create Account
  ![Écran d'inscription](<picture/Écran d'inscription — formulaire Create Account.png>)

- Page profil — statistiques et historique des erreurs grammaticales
  ![Page profil](<picture/Page de profil — statistiques et historique des erreurs grammaticales .png>)

- Scénario généré — Exemple: Informatique Intermédiaire Français
  ![Scénario généré](<picture/Scénario généré — Informatique Intermédiaire Français .png>)

- Échange de conversation avec corrections — domaine Informatique
  ![Échange de conversation](<picture/Échange de conversation avec corrections — domaine Informatique.png>)

- Composition du SMA — 5 agents spécialisés et leurs interactions
  ![Composition du SMA](<picture/Composition du SMA — 5 agents spécialisés et leurs interactions.png>)

- Pipeline de l'Agent Enseignant — RAG avec BM25 sur PDF de grammaire
  ![Pipeline de l'Agent Enseignant](<picture/Pipeline de l'Agent Enseignant — RAG avec BM25 sur PDF de grammaire .png>)

- Diagramme de flux des agents — traitement d'un message
  ![Diagramme de flux des agents](<picture/— Diagramme de flux des agents — traitement d'un message .png>)

- Architecture globale du système SMA
  ![Architecture globale du système SMA](<picture/Architecture globale du système SMA .png>)

---

## Collaborateurs

- ILYAS MOUSSNAOUI
- MUSTAPHA EL MIFDALI
- HICHAM OUAOUCHE

---

## Remarques et prochaines étapes

- Pour exécuter localement, vérifier que `files/Grammer.pdf` est présent pour activer la RAG.
- Si vous voulez, j'ajoute une miniature (README) plus compacte pour le README GitHub ou j'ouvre une branche et commit les changements.

Pour toute modification (ordre des captures, changement de textes ou ajout d'auteurs), dites-moi et j'adapte.
 
---

## README — Version détaillée

Cette section fournit des instructions approfondies pour les développeurs et contributeurs : configuration d'environnement, exécution pas à pas, structure des données, et guide pour étendre le système (ajout d'agents et sources RAG).

### 1) Configuration de l'environnement (recommandé pour développement)

1. Créer un environnement virtuel Python :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# ou : .venv\Scripts\activate    # cmd
```

2. Mettre à jour pip et installer les dépendances :

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Exemple de fichier `.env` (créer à la racine) :

```
MODELNAME=llama3
TAVILYAPIKEY=cle_tavily_xxx
OLLAMA_API_KEY=token_ollama_xxx
LANGSMITH_API_KEY=cle_langsmith_xxx   # optionnel
```

4. Vérifier la présence des ressources :

- `files/Grammer.pdf` — base documentaire utilisée par l'agent `teacher` pour la recherche BM25.
- `picture/` — captures d'écran et schémas pour documentation.

---

### 2) Commandes d'exécution

- Lancer l'interface Web Streamlit :

```bash
streamlit run Ui.py
```

- Lancer le mode CLI :

```bash
python withoutUi.py
```

- Exécuter l'évaluation des prompts (A/B/C) :

```bash
python prompt_evaluation.py
```

- Démarrer LangGraph Studio (si installé) :

```bash
langgraph dev
```

---

### 3) Structure des fichiers et rôle des modules

- `agents.py` : définitions des agents (prompts, outils, accès RAG). Contient les wrappers d'API et adaptateurs d'entrée/sortie.
- `workflows.py` : configuration du graphe LangGraph, orchestration des agents dans l'ordre désiré.
- `Ui.py` : application Streamlit (frontend léger, affichage conversation et boutons de sauvegarde).
- `withoutUi.py` : interface en ligne de commande, mode minimaliste pour tests et usage hors Web.
- `prompt_evaluation.py` : script qui exécute des séries de prompts pour comparer variantes et produire `prompt_evaluation_results.json`.
- `files/Grammer.pdf` : base de connaissances pour la recherche BM25.
- `picture/` : captures d'écran et diagrammes utilisés dans la documentation.

---

### 4) Détails techniques — Agents et pipeline

Flux principal :

1. `situational` : construit un contexte / scénario réaliste (thème, niveau, rôle des participants).
2. `character` : génère la réponse dans le rôle (registre, émotion, longueur souhaitée).
3. `teacher` : corrige grammaticalement la réponse via un pipeline RAG :
   - chunking du PDF (`files/Grammer.pdf`) en segments indexables
   - index BM25 (via `rank-bm25`) pour récupérer passages pertinents
   - reformulation/correction par le modèle en s'appuyant sur les passages récupérés
4. `mentality` : vérifications culturelles et de ton (détection d'expressions potentiellement inappropriées).
5. `styler` : formatage final (markdown, annotations des corrections, suggestions pédagogiques).
6. `save_check` / `save_agent` : interaction humaine (sauf en mode sans UI) puis persistance des corrections dans `files/`.

Chaque agent attend des entrées (prompt, contexte, historique) et renvoie un objet structuré :

```
{
  "text": "...",
  "metadata": { "agent": "teacher", "confidence": 0.87, ... },
  "sources": ["files/Grammer.pdf#chunk-12", ...]
}
```

---

### 5) RAG (Retrieval-Augmented Generation) — points clés

- Le pipeline RAG utilise `rank-bm25` pour une recherche rapide sur le PDF transformé en chunks.
- Les chunks sont stockés temporairement en mémoire (ou dans un cache local selon implémentation).
- Pour améliorer la qualité : augmenter la granularité des chunks ou ajouter des métadonnées (titre, section) dans `files/Grammer.pdf`.

---

### 6) Formats de données et fichiers produits

- `prompt_evaluation_results.json` : format JSON avec les métriques A/B/C et exemples annotés.
- `saved_corrections_YYYYMMDD_HHMMSS.txt` : sessions sauvegardées (format texte simple) ; chaque sauvegarde contient :
  - en‑tête avec métadonnées (utilisateur, date, scenario)
  - dialogue original
  - version corrigée
  - sources utilisées

Exemple court :

```
---
User: Bonjour je veux apprendre.
Corrected: Bonjour, je veux apprendre.
Sources: files/Grammer.pdf#section-2
---
```

---

### 7) Développement et extension — ajouter un agent

1. Créer une nouvelle fonction/Classe d'agent dans `agents.py` avec interface d'entrée/sortie cohérente.
2. Ajouter le nœud correspondant dans `workflows.py` et relier l'ordre d'exécution.
3. Écrire des tests unitaires simples (si vous avez un framework de test) et exécuter une session CLI pour validation.

Conseil : conservez la compatibilité des messages échangés (format JSON ci‑dessus) pour faciliter l'orchestration.

---

### 8) Débogage et dépannage

- Si l'agent `teacher` ne retrouve pas de sources : vérifier que `files/Grammer.pdf` est lisible et que le parser de PDF ne renvoie pas d'erreurs.
- Erreurs d'API Ollama/Tavily : contrôlez les variables d'environnement et testez les requêtes séparément.
- Streamlit ne démarre pas : vérifier le port et conflits (par défaut 8501) et lancer `streamlit run Ui.py --server.port 8502` si nécessaire.

---

### 9) Captures d'écran (légendes détaillées)

- `Interface principale — vue générale annotée .png` — Vue complète de l'application web avec panneaux de conversation, zone de saisie et historique des corrections.
- `Barre latérale — détail des contrôles.png` — Description des boutons, filtres de niveau et options de sauvegarde.
- `Page de connexion — onglets Sign In et Create Account.png` — Écrans d'authentification et création de compte.
- `Écran d'inscription — formulaire Create Account.png` — Champs requis et validation côté client.
- `Page de profil — statistiques et historique des erreurs grammaticales .png` — Visualisation des progrès et erreurs fréquentes.
- `Scénario généré — Informatique Intermédiaire Français .png` — Exemple concret de scénario thématique généré par `situational`.
- `Échange de conversation avec corrections — domaine Informatique.png` — Exemple de dialogue avant/après correction.
- `Composition du SMA — 5 agents spécialisés et leurs interactions.png` — Schéma conceptuel des agents et flux de données.
- `Pipeline de l'Agent Enseignant — RAG avec BM25 sur PDF de grammaire .png` — Schéma expliquant l'indexation et la recherche BM25.
- `— Diagramme de flux des agents — traitement d'un message .png` — Diagramme séquentiel du traitement d'un message utilisateur.
- `Architecture globale du système SMA .png` — Vue d'ensemble des composants et intégrations externes.

---

### 10) Crédits et collaborateurs

- ILYAS MOUSSNAOUI — Conception des agents et prompts
- MUSTAPHA EL MIFDALI — Orchestration LangGraph, intégration RAG
- HICHAM OUAOUCHE — Interface Web, UX et documentation

---

### 11) Licence

Ajoutez ici la licence souhaitée (MIT, Apache‑2.0, etc.). Si aucune licence n'est fournie, le dépôt reste "All rights reserved".

---

Si vous souhaitez que j'ajoute :

- un fichier `.env.example` dans le dépôt, ou
- un script d'initialisation `scripts/setup.sh` (ou `setup.ps1`), ou
- que je crée et pousse ces changements sur une branche Git,

indiquez la ou les options et je m'en occupe.
