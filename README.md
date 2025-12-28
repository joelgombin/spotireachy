# Spotireachy - Voice-Controlled Music Player for Reachy Mini

Application de contrôle vocal pour lancer de la musique et faire danser votre Reachy Mini !

## Fonctionnalités

- 🎤 **Reconnaissance vocale** : Commande vocale avec Whisper (local)
- 🎵 **Bibliothèque musicale locale** : Support MP3/WAV/FLAC avec extraction automatique des métadonnées
- 🔍 **Recherche sémantique** : Trouve la bonne chanson même avec des commandes approximatives
- 🗣️ **Confirmation TTS** : Le robot confirme vocalement la chanson trouvée
- 💃 **Synchronisation danse** : Utilise la bibliothèque de danses Reachy Mini synchronisée au BPM
- 📊 **Extraction BPM** : Analyse automatique du tempo pour synchroniser les mouvements

## Prérequis

- Reachy Mini (version Lite ou Wireless)
- Python 3.8+
- Connexion au Reachy Mini via réseau

## Installation

1. Cloner le dépôt :
```bash
git clone <repo-url>
cd spotireachy
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Copier vos fichiers musicaux dans le dossier `music/` :
```bash
mkdir -p music
# Copier vos MP3/WAV/FLAC dans ce dossier
```

4. Configurer l'application :
```bash
cp config.example.yaml config.yaml
# Éditer config.yaml avec vos paramètres
```

## Configuration

Éditer `config.yaml` pour personnaliser :
- IP du Reachy Mini
- Modèle Whisper (tiny, base, small, medium, large)
- Dossier de musique
- Langue de reconnaissance vocale

## Utilisation

### Première utilisation - Indexation

Indexer votre bibliothèque musicale :
```bash
python src/index_library.py
```

Cela va :
- Scanner tous les fichiers musicaux
- Extraire les métadonnées (titre, artiste, album)
- Analyser le BPM de chaque chanson
- Créer les embeddings sémantiques

### Lancer l'application

```bash
python src/main.py
```

L'application va :
1. Se connecter au Reachy Mini
2. Charger la bibliothèque musicale
3. Attendre vos commandes vocales

### Commandes vocales

Exemples de commandes :
- "Let it be"
- "Joue Bohemian Rhapsody"
- "Mets du Queen"
- "Lance Yesterday des Beatles"

Le robot va :
1. Écouter votre commande
2. Chercher la meilleure correspondance
3. Vous demander confirmation
4. Lancer la musique et danser !

## Architecture

```
spotireachy/
├── src/
│   ├── voice_recognition.py   # Module Whisper pour reconnaissance vocale
│   ├── music_library.py       # Gestion bibliothèque et extraction BPM
│   ├── semantic_search.py     # Recherche sémantique avec embeddings
│   ├── audio_player.py        # Lecture audio
│   ├── dance_controller.py    # Contrôle des danses Reachy
│   ├── index_library.py       # Script d'indexation
│   └── main.py                # Application principale
├── music/                     # Dossier pour vos fichiers musicaux
├── data/                      # Cache des embeddings et métadonnées
└── config.yaml                # Configuration
```

## Dépannage

### Le robot ne répond pas
- Vérifier la connexion réseau au Reachy Mini
- Vérifier l'IP dans config.yaml

### La reconnaissance vocale ne fonctionne pas
- Vérifier que le microphone est bien détecté
- Essayer un modèle Whisper plus petit (tiny, base)

### Pas de musique trouvée
- Relancer l'indexation : `python src/index_library.py`
- Vérifier que les fichiers sont bien dans le dossier `music/`

## Technologies utilisées

- **Reachy Mini SDK** : Contrôle du robot
- **Whisper** : Reconnaissance vocale locale
- **librosa** : Analyse audio et extraction BPM
- **sentence-transformers** : Embeddings sémantiques
- **FAISS** : Recherche de similarité rapide
- **pygame** : Lecture audio

## Licence

MIT

## Contributions

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
