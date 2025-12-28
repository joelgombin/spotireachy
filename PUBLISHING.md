# Guide de Publication sur Hugging Face Space

Ce guide explique comment publier Spotireachy comme app officielle Reachy Mini sur Hugging Face.

## Prérequis

1. Compte Hugging Face
2. `reachy-mini-app-assistant` installé (vient avec `reachy-mini`)
3. Projet Spotireachy testé localement

## Méthode 1 : Publication automatique avec app-assistant

### Vérification

Avant de publier, vérifiez que tout est en ordre :

```bash
# Vérifier la structure du projet
reachy-mini-app-assistant check

# Vérifier que l'app fonctionne
python -m pytest  # Si vous avez des tests
uv run spotireachy-index  # Tester l'indexation
uv run spotireachy  # Tester l'app
```

### Publication

```bash
# Publier sur votre compte HF (privé ou public)
reachy-mini-app-assistant publish \
    --path . \
    --privacy public

# Vous serez invité à vous connecter à HF si nécessaire
```

Cela va :
- Créer un Space sur `https://huggingface.co/spaces/YOUR_USERNAME/spotireachy`
- Uploader tous les fichiers nécessaires
- Configurer les métadonnées du Space

### Publication officielle (optionnel)

Pour soumettre à l'App Store officiel Reachy :

```bash
reachy-mini-app-assistant publish --official
```

Cela créera une Pull Request vers le dataset officiel. Vous devrez fournir :
- Une description de votre app
- Pourquoi elle devrait être officielle
- Preuves de tests et stabilité

## Méthode 2 : Publication manuelle

Si vous préférez publier manuellement :

### 1. Créer un nouveau Space HF

1. Allez sur https://huggingface.co/new-space
2. Nom : `spotireachy`
3. SDK : Sélectionnez "Static" (car on a index.html)
4. License : MIT
5. Cliquez "Create Space"

### 2. Cloner le Space

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/spotireachy
cd spotireachy
```

### 3. Copier les fichiers

Copiez tous les fichiers du projet Spotireachy :

```bash
# À partir du repo Spotireachy
cp -r src/ ../spotireachy/
cp pyproject.toml ../spotireachy/
cp index.html ../spotireachy/
cp style.css ../spotireachy/
cp README.md ../spotireachy/SPACE_README.md
cp .gitattributes ../spotireachy/
cp config.example.yaml ../spotireachy/
```

### 4. Créer le README avec métadonnées

Le fichier `README.md` dans le Space doit avoir les métadonnées HF en en-tête :

```markdown
---
title: Spotireachy - Voice Music Player
emoji: 🎵
colorFrom: blue
colorTo: purple
sdk: static
pinned: false
license: mit
tags:
  - reachy-mini
  - voice-control
  - music
---

[Votre contenu README...]
```

### 5. Commit et push

```bash
cd ../spotireachy  # Le dossier du Space HF
git add .
git commit -m "Initial commit of Spotireachy app"
git push
```

### 6. Vérifier le Space

Allez sur `https://huggingface.co/spaces/YOUR_USERNAME/spotireachy`

Vous devriez voir votre page avec `index.html` rendu.

## Structure finale du Space

```
spotireachy/
├── .gitattributes          # Normalisation line endings
├── README.md               # Avec métadonnées HF (utiliser SPACE_README.md)
├── index.html              # Page de présentation
├── style.css               # Styles de la page
├── pyproject.toml          # Configuration du projet
├── config.example.yaml     # Config exemple
├── src/                    # Code source
│   ├── __init__.py
│   ├── app.py              # SpotireachyApp (ReachyMiniApp)
│   ├── main.py
│   ├── voice_recognition.py
│   ├── music_library.py
│   ├── semantic_search.py
│   ├── audio_player.py
│   ├── tts_engine.py
│   ├── dance_controller.py
│   └── index_library.py
├── music/                  # Pour les fichiers musicaux (vide dans le repo)
│   └── README.md
└── scripts/                # Scripts utiles
    ├── test_microphone.py
    └── test_whisper.py
```

## Configuration du Space

### Paramètres à configurer sur HF

Dans les settings du Space :

1. **Hardware** : CPU Basic (gratuit) suffit pour la page statique
2. **Visibility** : Public
3. **License** : MIT
4. **Tags** : `reachy-mini`, `voice-control`, `music`, `robotics`

### Secrets (optionnels)

Si vous avez besoin de secrets (API keys, etc.), ajoutez-les dans :
Settings → Variables and Secrets

## Après la publication

### 1. Tester l'installation

Sur un Reachy Mini :

```bash
# Installer depuis le Space HF
pip install git+https://huggingface.co/spaces/YOUR_USERNAME/spotireachy

# Ou avec uv
uv pip install git+https://huggingface.co/spaces/YOUR_USERNAME/spotireachy
```

### 2. Apparition dans le Dashboard

L'app devrait maintenant apparaître dans le dashboard Reachy Mini dans la section "Community Apps".

### 3. Promotion

- Partagez sur Twitter/X avec #ReachyMini
- Postez dans le Discord Hugging Face
- Ajoutez à la liste des apps communautaires

## Soumission à l'App Store officiel

Pour devenir une app officielle :

1. Testez l'app sur plusieurs Reachy Mini
2. Assurez-vous de la stabilité
3. Documentez bien l'utilisation
4. Soumettez via `reachy-mini-app-assistant publish --official`
5. Ou créez une PR manuelle vers le dataset officiel

Le reviewers Pollen Robotics / Hugging Face vérifieront :
- ✅ Code quality
- ✅ Documentation
- ✅ Tests
- ✅ Stabilité
- ✅ Utilité pour la communauté

## Mise à jour de l'app

Pour mettre à jour votre app déjà publiée :

```bash
# Dans votre repo Spotireachy local
git pull  # Récupérer les derniers changements

# Faire vos modifications
# ...

# Republier
reachy-mini-app-assistant publish --update
```

## Dépannage

### L'app n'apparaît pas dans le dashboard

- Vérifiez que `pyproject.toml` a bien l'entry point `reachy_mini.apps`
- Vérifiez que la classe hérite de `ReachyMiniApp`
- Réinstallez : `pip install --force-reinstall git+https://...`

### Erreur lors de l'indexation

- Assurez-vous que le dossier `data/` existe
- Vérifiez les permissions d'écriture
- Lancez `mkdir -p data` avant l'indexation

### L'app ne démarre pas

- Vérifiez les logs : `reachy-mini-daemon` en mode verbose
- Testez en standalone : `uv run spotireachy`
- Vérifiez que toutes les dépendances sont installées

## Ressources

- [Guide officiel Pollen Robotics](https://huggingface.co/blog/pollen-robotics/make-and-publish-your-reachy-mini-apps)
- [Documentation Reachy Mini SDK](https://github.com/pollen-robotics/reachy_mini)
- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Exemple d'app officielle](https://huggingface.co/spaces/pollen-robotics/reachy_mini_conversation_app)

---

Bonne publication ! 🚀
