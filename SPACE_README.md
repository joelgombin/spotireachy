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
  - robotics
  - ai
---

# 🎵 Spotireachy - Voice-Controlled Music Player for Reachy Mini

Transformez votre Reachy Mini en DJ intelligent ! Parlez-lui et il trouvera et jouera vos chansons préférées tout en dansant synchronisé au BPM.

## ✨ Fonctionnalités

- 🎤 **Reconnaissance vocale** locale avec Whisper (offline)
- 🔍 **Recherche sémantique** intelligente pour trouver vos chansons
- 🗣️ **Confirmation TTS** - Reachy confirme avant de jouer
- 💃 **Danse synchronisée** au BPM de la musique
- 📊 **Extraction BPM** automatique avec librosa
- 🎵 **Multi-formats** : MP3, WAV, FLAC, M4A

## 🚀 Installation

### Via Dashboard Reachy Mini (Recommandé)

1. Ouvrez le dashboard Reachy Mini
2. Allez dans "App Store"
3. Cherchez "Spotireachy"
4. Cliquez sur "Installer"
5. Ajoutez vos fichiers musicaux dans le dossier `music/`
6. Lancez l'indexation depuis le dashboard
7. Démarrez l'app !

### Installation manuelle

```bash
# Cloner le projet
git clone https://huggingface.co/spaces/YOUR_USERNAME/spotireachy
cd spotireachy

# Installer avec uv (rapide ⚡)
uv sync

# Ajouter votre musique
cp ~/Music/*.mp3 music/

# Indexer la bibliothèque
uv run spotireachy-index

# Lancer l'application
uv run spotireachy
```

### Avec Make (encore plus simple)

```bash
make setup  # Installation complète
make index  # Indexer la bibliothèque
make run    # Lancer l'app
```

## 🎬 Comment ça marche

1. **Vous** : "Let it be"
2. **Reachy** : Recherche dans votre bibliothèque musicale
3. **Reachy** : "Voulez-vous écouter Let It Be des Beatles ?"
4. **Vous** : "Oui !"
5. **Reachy** : Lance la musique et danse ! 🎉

## 📋 Prérequis

- Reachy Mini (Lite ou Wireless)
- Python 3.8+
- Fichiers musicaux locaux
- Microphone fonctionnel

## 🛠️ Technologies

- **Reachy Mini SDK** - Contrôle du robot
- **Whisper** - Reconnaissance vocale
- **librosa** - Extraction BPM
- **Sentence Transformers** - Recherche sémantique
- **FAISS** - Indexation vectorielle
- **pygame** - Lecture audio
- **uv** - Gestionnaire de paquets ultra-rapide

## 📖 Documentation

- [README complet](https://github.com/joelgombin/spotireachy/blob/main/README.md)
- [Quick Start Guide](https://github.com/joelgombin/spotireachy/blob/main/QUICKSTART.md)
- [Architecture technique](https://github.com/joelgombin/spotireachy/blob/main/ARCHITECTURE.md)

## 🐛 Problèmes ?

Ouvrez une issue sur [GitHub](https://github.com/joelgombin/spotireachy/issues)

## 📜 Licence

MIT License - Voir [LICENSE](https://github.com/joelgombin/spotireachy/blob/main/LICENSE)

---

Made with ❤️ for the Reachy Mini community
