# Migration vers uv

Ce document explique la migration du projet vers uv, le gestionnaire de paquets Python ultra-rapide.

## Pourquoi uv ?

**uv** est développé par Astral (créateurs de Ruff) et apporte plusieurs avantages :

- ⚡ **10-100x plus rapide** que pip
- 🔒 **Lock file** pour des installations reproductibles
- 🎯 **Résolution de dépendances** plus intelligente
- 📦 **Tout-en-un** : remplace pip, pip-tools, virtualenv, etc.
- 🚀 **Installation sans douleur** : un seul binaire

## Changements apportés

### Fichiers ajoutés

1. **pyproject.toml** - Configuration moderne du projet (PEP 621)
   - Définit toutes les dépendances
   - Métadonnées du projet
   - Scripts d'entrée (`spotireachy`, `spotireachy-index`)
   - Dépendances optionnelles (dev, gpu)

2. **Makefile** - Commandes utiles pour le développement
   - `make install` : Installation complète
   - `make index` : Indexer la bibliothèque
   - `make run` : Lancer l'application
   - `make help` : Voir toutes les commandes

3. **justfile** - Alternative moderne au Makefile
   - Même fonctionnalités que Makefile
   - Syntaxe plus simple
   - Nécessite [just](https://github.com/casey/just)

4. **.python-version** - Version Python recommandée (3.11)

### Fichiers modifiés

1. **README.md** - Instructions mises à jour pour uv
2. **QUICKSTART.md** - Guide de démarrage avec uv
3. **.gitignore** - Ajout de `.venv/` et `uv.lock`

### Fichiers conservés

- **requirements.txt** - Conservé pour compatibilité pip

## Utilisation

### Installation rapide

```bash
# Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Tout installer
uv sync
```

### Avec Make

```bash
# Voir toutes les commandes
make help

# Installation complète
make setup

# Indexer et lancer
make index
make run
```

### Avec Just

```bash
# Installer just
cargo install just
# ou : brew install just

# Voir toutes les commandes
just

# Installation complète
just setup

# Indexer et lancer
just index
just run
```

### Scripts d'entrée

Avec `pyproject.toml`, vous pouvez maintenant utiliser :

```bash
# Au lieu de : python src/index_library.py
uv run spotireachy-index

# Au lieu de : python src/main.py
uv run spotireachy
```

## Commandes uv essentielles

```bash
# Installer les dépendances
uv sync

# Ajouter une dépendance
uv add package-name

# Ajouter une dépendance de dev
uv add --dev package-name

# Mettre à jour les dépendances
uv sync --upgrade

# Exécuter un script
uv run python script.py

# Exécuter un script d'entrée
uv run spotireachy
```

## Migration depuis pip

Si vous avez déjà installé avec pip :

```bash
# Supprimer l'ancien venv
rm -rf venv/

# Installer avec uv
uv sync

# Vérifier que tout fonctionne
uv run spotireachy-index
```

## Dépendances optionnelles

### Développement

```bash
# Installer avec outils de dev (black, ruff, pytest)
uv sync --extra dev

# Formater le code
make format
# ou : just format

# Vérifier le code
make lint
# ou : just lint
```

### Support GPU

```bash
# Installer avec support GPU (FAISS GPU)
uv sync --extra gpu
```

## Avantages pour Spotireachy

1. **Installation ultra-rapide** : ~10s au lieu de plusieurs minutes
2. **Lock file** : Garantit que tout le monde a les mêmes versions
3. **Scripts d'entrée** : Commandes plus propres (`spotireachy` vs `python src/main.py`)
4. **Dépendances optionnelles** : GPU support sans forcer tout le monde à l'installer
5. **Meilleure gestion des conflits** : uv résout mieux les dépendances

## Compatibilité

- ✅ **pip** fonctionne toujours (requirements.txt conservé)
- ✅ **Python 3.8+** supporté
- ✅ **Linux, macOS, Windows** tous supportés
- ✅ **Installation existante** : pas besoin de désinstaller pip

## Ressources

- [uv documentation](https://github.com/astral-sh/uv)
- [pyproject.toml guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Make tutorial](https://makefiletutorial.com/)
- [Just documentation](https://just.systems/)

## FAQ

### Dois-je supprimer pip ?

Non ! uv et pip peuvent coexister. uv est juste plus rapide.

### Que faire de requirements.txt ?

Conservez-le pour la compatibilité, mais utilisez `pyproject.toml` comme source de vérité.

### Comment mettre à jour une dépendance ?

```bash
# Avec uv
uv add package-name@latest

# Ou éditer pyproject.toml puis
uv sync
```

### uv.lock doit-il être versionné ?

Oui ! Il garantit des installations reproductibles. Mais il est dans .gitignore pour l'instant car il peut causer des conflits de merge. Vous pouvez le retirer du .gitignore si votre équipe le souhaite.

### Puis-je toujours utiliser pip ?

Oui, `requirements.txt` est toujours là. Mais uv est beaucoup plus rapide !
