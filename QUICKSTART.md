# Démarrage Rapide - Spotireachy

Guide pour configurer et lancer rapidement votre lecteur musical vocal pour Reachy Mini.

## 📋 Prérequis

- Reachy Mini (Lite ou Wireless)
- Python 3.8 ou plus récent
- [uv](https://github.com/astral-sh/uv) (recommandé) ou pip
- Fichiers musicaux (MP3, WAV, FLAC, M4A)

## 🚀 Installation en 5 minutes

### 1. Installer uv et les dépendances

**Avec uv (recommandé ⚡ - beaucoup plus rapide) :**

```bash
# Installer uv si nécessaire
curl -LsSf https://astral.sh/uv/install.sh | sh

# Installer toutes les dépendances
uv sync
```

**Avec pip (alternative) :**

```bash
pip install -r requirements.txt
```

**Note** : L'installation peut prendre quelques minutes car elle télécharge les modèles Whisper et Sentence Transformers. Avec uv, c'est beaucoup plus rapide !

### 2. Ajouter votre musique

Copiez vos fichiers musicaux dans le dossier `music/` :

```bash
# Créer le dossier s'il n'existe pas
mkdir -p music

# Copier vos fichiers musicaux
cp ~/Music/*.mp3 music/
```

### 3. Indexer votre bibliothèque

Lancez le script d'indexation pour analyser vos chansons :

```bash
# Avec uv (recommandé)
uv run spotireachy-index

# Ou avec python directement
python src/index_library.py
```

Cela va :
- ✅ Scanner tous vos fichiers musicaux
- ✅ Extraire les métadonnées (titre, artiste, album)
- ✅ Analyser le BPM de chaque chanson
- ✅ Créer l'index de recherche sémantique

**Temps estimé** : ~10-30 secondes par chanson (selon la taille de votre bibliothèque)

### 4. Configurer la connexion Reachy (optionnel)

Si vous utilisez un Reachy Mini sur le réseau, éditez `config.yaml` :

```yaml
reachy:
  ip: "192.168.1.100"  # Remplacez par l'IP de votre Reachy
```

Pour un Reachy Mini local, laissez `localhost`.

### 5. Lancer l'application

```bash
# Avec uv (recommandé)
uv run spotireachy

# Ou avec python directement
python src/main.py
```

## 🎤 Utilisation

### Commandes vocales

Une fois l'application lancée, parlez simplement à Reachy :

**Exemples de commandes** :
- "Let it be"
- "Joue Bohemian Rhapsody"
- "Mets du Queen"
- "Lance Yesterday des Beatles"
- "Hotel California"

### Déroulement

1. **🎤 Vous parlez** : "Let it be"
2. **🔍 Reachy cherche** la chanson dans votre bibliothèque
3. **🗣️ Reachy demande** : "Voulez-vous écouter Let It Be de The Beatles ?"
4. **✅ Vous confirmez** : "Oui"
5. **🎵 Reachy lance** la musique et danse sur le BPM !

### Arrêter l'application

Appuyez sur `Ctrl+C` pour quitter proprement.

## ⚙️ Configuration avancée

### Changer le modèle Whisper

Pour une meilleure précision (mais plus lent), éditez `config.yaml` :

```yaml
whisper:
  model: "small"  # Changez de "base" à "small" ou "medium"
```

**Modèles disponibles** :
- `tiny` : Très rapide, précision moyenne
- `base` : ✅ **Recommandé** - Bon équilibre
- `small` : Plus précis, un peu plus lent
- `medium` : Très précis, lent
- `large` : Maximum précision, très lent

### Ajuster le volume

```yaml
audio:
  volume: 0.8  # De 0.0 (muet) à 1.0 (max)
```

### Désactiver la danse

```yaml
dance:
  enable_dance: false
```

## 🐛 Problèmes courants

### "Could not load library from cache"

➡️ **Solution** : Vous devez d'abord indexer votre bibliothèque :
```bash
uv run spotireachy-index
# ou : python src/index_library.py
```

### "No tracks found in library"

➡️ **Solution** : Vérifiez que vous avez bien copié des fichiers musicaux dans `music/`
```bash
ls music/  # Doit afficher vos fichiers MP3/WAV/FLAC
```

### "Error initializing audio player"

➡️ **Solution** : Vérifiez que pygame est bien installé :
```bash
uv sync  # Réinstalle toutes les dépendances
# ou : pip install pygame --upgrade
```

### La reconnaissance vocale ne fonctionne pas

➡️ **Solutions** :
1. Vérifiez que votre microphone fonctionne
2. Essayez un modèle Whisper plus petit (`tiny`) pour tester
3. Vérifiez les permissions d'accès au microphone

### Reachy ne danse pas

➡️ **Solutions** :
1. Vérifiez que `enable_dance: true` dans `config.yaml`
2. Vérifiez la connexion au Reachy Mini
3. L'application peut fonctionner en mode simulation sans Reachy connecté

## 📚 Ressources

- **README complet** : [README.md](README.md)
- **Documentation Reachy Mini** : https://github.com/pollen-robotics/reachy_mini
- **Problèmes** : Ouvrir une issue sur GitHub

## 🎉 C'est tout !

Vous êtes prêt à profiter de la musique avec Reachy Mini ! 🕺🎵
