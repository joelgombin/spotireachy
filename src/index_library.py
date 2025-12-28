#!/usr/bin/env python3
"""
Script to index music library and build search index.
Run this before using the main application.
"""

import logging
import sys
import yaml
from pathlib import Path

from music_library import MusicLibrary
from semantic_search import SemanticSearchEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    config_file = Path(config_path)

    if not config_file.exists():
        logger.error(f"Configuration file not found: {config_path}")
        logger.info("Please copy config.example.yaml to config.yaml and edit it")
        sys.exit(1)

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config


def main():
    """Main indexing function."""
    print("=" * 60)
    print("🎵 Spotireachy - Music Library Indexer")
    print("=" * 60)

    # Load configuration
    logger.info("Loading configuration...")
    config = load_config()

    # Initialize music library
    music_config = config['music']
    library = MusicLibrary(
        library_path=music_config['library_path'],
        supported_formats=music_config['supported_formats']
    )

    # Scan library
    print("\n📁 Scanning music library...")
    print(f"   Location: {music_config['library_path']}")
    print(f"   Formats: {', '.join(music_config['supported_formats'])}")
    print()

    tracks = library.scan_library(extract_bpm=True)

    if not tracks:
        logger.error("No tracks found in library!")
        logger.info(f"Please add music files to: {music_config['library_path']}")
        sys.exit(1)

    print(f"\n✅ Found {len(tracks)} tracks")
    print("\n📊 Sample tracks:")
    for i, track in enumerate(tracks[:5], 1):
        print(f"   {i}. {track.artist} - {track.title}")
        print(f"      BPM: {track.bpm:.0f} | Duration: {track.duration:.0f}s")

    # Save metadata cache
    data_config = config['data']
    print(f"\n💾 Saving metadata cache...")
    library.save_to_cache(data_config['metadata_cache'])

    # Build semantic search index
    print(f"\n🔍 Building semantic search index...")
    search_config = config['search']

    engine = SemanticSearchEngine(
        model_name=search_config['model'],
        device="cpu"
    )

    engine.build_index(tracks, normalize=True)

    # Save search index
    print(f"\n💾 Saving search index...")
    engine.save_index(
        index_path=data_config['index_cache'],
        embeddings_path=data_config['embeddings_cache']
    )

    print("\n" + "=" * 60)
    print("✅ Indexing complete!")
    print("=" * 60)
    print("\nYou can now run the main application:")
    print("  python src/main.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Indexing cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during indexing: {e}", exc_info=True)
        sys.exit(1)
