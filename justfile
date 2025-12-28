# Justfile for Spotireachy
# Alternative to Makefile with simpler syntax

# List all available commands
default:
    @just --list

# Install uv and dependencies
install:
    @echo "📦 Installation de uv et des dépendances..."
    @command -v uv >/dev/null 2>&1 || (echo "Installation de uv..." && curl -LsSf https://astral.sh/uv/install.sh | sh)
    uv sync

# Synchronize dependencies
sync:
    @echo "🔄 Synchronisation des dépendances..."
    uv sync

# Index music library
index:
    @echo "🎵 Indexation de la bibliothèque musicale..."
    uv run spotireachy-index

# Run the application
run:
    @echo "🚀 Lancement de Spotireachy..."
    uv run spotireachy

# Test microphone
test-mic:
    @echo "🎤 Test du microphone..."
    uv run python scripts/test_microphone.py

# Test Whisper
test-whisper:
    @echo "🗣️  Test de Whisper..."
    uv run python scripts/test_whisper.py

# Create config file
config:
    #!/usr/bin/env bash
    if [ ! -f config.yaml ]; then
        echo "⚙️  Création de config.yaml..."
        cp config.example.yaml config.yaml
        echo "✅ config.yaml créé. Éditez-le pour personnaliser."
    else
        echo "⚠️  config.yaml existe déjà."
    fi

# Complete setup
setup: install config
    @echo "✅ Setup complet terminé!"
    @echo ""
    @echo "Prochaines étapes:"
    @echo "  1. Ajoutez vos fichiers musicaux dans music/"
    @echo "  2. Lancez: just index"
    @echo "  3. Lancez: just run"

# Clean generated files
clean:
    @echo "🧹 Nettoyage..."
    rm -rf data/*.json data/*.npy data/*.index
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    @echo "✅ Nettoyage terminé"

# Install with dev dependencies
dev:
    uv sync --extra dev

# Format code
format:
    uv run black src/ scripts/

# Lint code
lint:
    uv run ruff check src/ scripts/
