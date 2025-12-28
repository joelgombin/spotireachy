.PHONY: help install sync index run test clean

help:  ## Afficher cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Installer uv et les dépendances
	@echo "📦 Installation de uv et des dépendances..."
	@command -v uv >/dev/null 2>&1 || (echo "Installation de uv..." && curl -LsSf https://astral.sh/uv/install.sh | sh)
	uv sync

sync:  ## Synchroniser les dépendances avec uv
	@echo "🔄 Synchronisation des dépendances..."
	uv sync

index:  ## Indexer la bibliothèque musicale
	@echo "🎵 Indexation de la bibliothèque musicale..."
	uv run spotireachy-index

run:  ## Lancer l'application
	@echo "🚀 Lancement de Spotireachy..."
	uv run spotireachy

test-mic:  ## Tester le microphone
	@echo "🎤 Test du microphone..."
	uv run python scripts/test_microphone.py

test-whisper:  ## Tester Whisper
	@echo "🗣️  Test de Whisper..."
	uv run python scripts/test_whisper.py

config:  ## Créer le fichier de configuration
	@if [ ! -f config.yaml ]; then \
		echo "⚙️  Création de config.yaml..."; \
		cp config.example.yaml config.yaml; \
		echo "✅ config.yaml créé. Éditez-le pour personnaliser."; \
	else \
		echo "⚠️  config.yaml existe déjà."; \
	fi

setup: install config  ## Installation complète (uv + config)
	@echo "✅ Setup complet terminé!"
	@echo ""
	@echo "Prochaines étapes:"
	@echo "  1. Ajoutez vos fichiers musicaux dans music/"
	@echo "  2. Lancez: make index"
	@echo "  3. Lancez: make run"

clean:  ## Nettoyer les fichiers générés
	@echo "🧹 Nettoyage..."
	rm -rf data/*.json data/*.npy data/*.index
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Nettoyage terminé"

dev:  ## Installer avec dépendances de développement
	uv sync --extra dev

format:  ## Formater le code avec black
	uv run black src/ scripts/

lint:  ## Vérifier le code avec ruff
	uv run ruff check src/ scripts/

.DEFAULT_GOAL := help
