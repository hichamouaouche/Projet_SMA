# Projet SMA — Systeme Multi‑Agents pour l'apprentissage des langues

Ce projet propose une plateforme d'apprentissage des langues basee sur une architecture multi‑agents. L'objectif est de placer l'apprenant dans des situations de conversation realistes, d'ameliorer sa production ecrite et de fournir des corrections argumentees par des sources grammaticales. L'ensemble du flux est orchestre par LangGraph et propose une interface Web Streamlit ainsi qu'un mode CLI.

---

## Resume executif

Le systeme genere un scenario, produit une reponse humaine, corrige la grammaire via un pipeline RAG, verifie la pertinence culturelle et formate une reponse pedagogique. Il s'appuie sur une base documentaire (PDF de grammaire) et sur des outils externes (LLM, recherche web) pour fournir une experience d'apprentissage guidee.

---

## Contexte et problematique

L'apprentissage des langues souffre souvent d'un manque de feedback immediat, coherent et explique. Les apprenants ont besoin de corrections claires, de reformulations naturelles et d'un contexte de dialogue pour progresser. Ce projet vise a automatiser ces taches tout en conservant un cadre pedagogique.

---

## Objectifs

- Simuler des conversations realistes adaptees au niveau de l'apprenant
- Corriger et expliquer les erreurs grammaticales via RAG
- Controler la pertinence culturelle et le ton
- Produire une sortie claire, structuree et pedagogique
- Permettre une evaluation des prompts pour stabiliser la qualite

---

## Fonctionnalites principales

- Orchestration multi‑agents (LangGraph)
- Correction grammaticale via RAG (BM25 sur `files/Grammer.pdf`)
- Verification culturelle et reformulation stylistique
- Sauvegarde des corrections (mode CLI)
- Interface Web Streamlit + interface CLI
- Evaluation de prompts (A/B/C)

---

## Architecture du systeme

Flux principal : scenario -> `character` -> `teacher` (RAG) -> `mentality` -> `styler` -> `save_check` -> `save_agent`.

Roles :

- `situational` : genere un contexte de conversation (theme, niveau, roles)
- `character` : produit la reponse dans le role cible
- `teacher` : corrige la grammaire avec RAG
- `mentality` : verifie le registre et les risques culturels
- `styler` : met en forme la reponse finale et la rend pedagogique
- `save_agent` : sauvegarde les corrections si validees

---

## RAG (Retrieval‑Augmented Generation)

- Source : `files/Grammer.pdf`
- Indexation : BM25
- Objectif : recuperer des regles pertinentes pour justifier les corrections

Le pipeline RAG isole des passages utiles a la correction afin de renforcer la justesse et la transparence des reponses. Pour ameliorer la qualite, il est conseille d'enrichir le PDF avec des sections explicites et bien structurees.

---

## Flux utilisateur

1. L'utilisateur lance un scenario (web ou CLI)
2. Le systeme genere une reponse dans le role
3. La reponse est corrigee et justifiee
4. La sortie finale est formatee et proposee a l'utilisateur
5. En CLI, l'utilisateur decide de sauvegarder ou non la correction

---

## Installation

Pre‑requis : Python 3.10+ et `pip`.

```bash
pip install -r requirements.txt
```

Creer un fichier `.env` a la racine :

```
MODELNAME=your-ollama-model
TAVILYAPIKEY=your-tavily-key
OLLAMA_API_KEY=your-ollama-token
LANGSMITH_API_KEY=optional
```

---

## Lancer l'application

Web (recommande) :

```bash
streamlit run Ui.py
```

CLI :

```bash
python withoutUi.py
```

Evaluation de prompts :

```bash
python prompt_evaluation.py
```

---

## Structure du projet

- `agents.py` — Agents, prompts, outils, RAG
- `workflows.py` — Graphe LangGraph
- `Ui.py` — UI Streamlit
- `withoutUi.py` — CLI
- `prompt_evaluation.py` — Evaluation A/B/C
- `prompt_evaluation_results.json` — Resultats des evaluations
- `files/Grammer.pdf` — Base RAG

---

## Donnees generees

- `prompt_evaluation_results.json` : rapports de comparaison de prompts
- `saved_corrections_*.txt` : sauvegardes de sessions (mode CLI)

---

## Evaluation et qualite

Le module `prompt_evaluation.py` compare plusieurs variantes de prompts sur un jeu de phrases. Les resultats sont exportes en JSON afin d'identifier la variante la plus stable. Cette etape aide a reduire les regressions de qualite lors des evolutions.

---

## Limites connues

- Depend de la qualite du PDF grammatical
- Variabilite des sorties LLM selon le modele et le contexte
- Couverture culturelle limitee si la recherche web est indisponible

---

## Pistes d'amelioration

- Ajouter des tests automatiques sur un corpus fixe
- Enrichir la base RAG avec plusieurs sources et metadonnees
- Ajouter des statistiques par utilisateur et un suivi de progression
- Internationaliser l'interface et les scenarios

---

## Depannage rapide

- Si `teacher` ne corrige pas : verifier `files/Grammer.pdf`
- Si l'UI ne demarre pas : verifier le port (8501 par defaut)
- Si l'API ne repond pas : verifier `.env`

---

## Collaborateurs

- ILYAS MOUSSNAOUI
- MUSTAPHA EL MIFDALI
- HICHAM OUAOUCHE
