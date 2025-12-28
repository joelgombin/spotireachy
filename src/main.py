#!/usr/bin/env python3
"""
Spotireachy - Voice-controlled music player for Reachy Mini
Main application entry point.
"""

import logging
import sys
import yaml
from pathlib import Path
from typing import Optional

from music_library import MusicLibrary
from semantic_search import SemanticSearchEngine, QueryProcessor
from voice_recognition import VoiceRecognizer
from tts_engine import ReachyTTS
from audio_player import AudioPlayer
from dance_controller import DanceController

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpotireachyApp:
    """Main application class."""

    def __init__(self, config: dict):
        """Initialize application with configuration."""
        self.config = config
        self.running = False

        # Initialize components
        logger.info("Initializing Spotireachy...")

        # Try to connect to Reachy Mini
        self.reachy = self._connect_reachy()

        # Initialize subsystems
        self.library = self._init_library()
        self.search_engine = self._init_search_engine()
        self.voice_recognizer = self._init_voice_recognizer()
        self.tts = self._init_tts()
        self.audio_player = self._init_audio_player()
        self.dance_controller = self._init_dance_controller()

        logger.info("✅ Spotireachy initialized successfully")

    def _connect_reachy(self):
        """Connect to Reachy Mini robot."""
        reachy_config = self.config.get('reachy', {})
        ip = reachy_config.get('ip', 'localhost')

        try:
            logger.info(f"Connecting to Reachy Mini at {ip}...")

            # Import Reachy SDK
            try:
                from reachy_mini import ReachyMini
                reachy = ReachyMini(ip)
                logger.info("✅ Connected to Reachy Mini")
                return reachy
            except ImportError:
                logger.warning("reachy-mini package not installed, running in simulation mode")
                return None
            except Exception as e:
                logger.warning(f"Could not connect to Reachy Mini: {e}")
                logger.info("Running in simulation mode")
                return None

        except Exception as e:
            logger.error(f"Error connecting to Reachy: {e}")
            return None

    def _init_library(self) -> MusicLibrary:
        """Initialize music library."""
        music_config = self.config['music']
        data_config = self.config['data']

        library = MusicLibrary(
            library_path=music_config['library_path'],
            supported_formats=music_config['supported_formats']
        )

        # Try to load from cache
        logger.info("Loading music library from cache...")
        if not library.load_from_cache(data_config['metadata_cache']):
            logger.error("Could not load library from cache!")
            logger.info("Please run: python src/index_library.py")
            sys.exit(1)

        logger.info(f"✅ Loaded {len(library.tracks)} tracks")
        return library

    def _init_search_engine(self) -> SemanticSearchEngine:
        """Initialize semantic search engine."""
        search_config = self.config['search']
        data_config = self.config['data']

        engine = SemanticSearchEngine(
            model_name=search_config['model'],
            device="cpu"
        )

        # Try to load from cache
        logger.info("Loading search index from cache...")
        if not engine.load_index(
            index_path=data_config['index_cache'],
            embeddings_path=data_config['embeddings_cache'],
            tracks=self.library.tracks
        ):
            logger.error("Could not load search index from cache!")
            logger.info("Please run: python src/index_library.py")
            sys.exit(1)

        logger.info("✅ Search index loaded")
        return engine

    def _init_voice_recognizer(self) -> VoiceRecognizer:
        """Initialize voice recognizer."""
        whisper_config = self.config['whisper']

        return VoiceRecognizer(
            model_size=whisper_config['model'],
            language=whisper_config['language'],
            device=whisper_config['device']
        )

    def _init_tts(self) -> ReachyTTS:
        """Initialize text-to-speech."""
        tts_config = self.config['tts']

        # Get Reachy speaker if available
        reachy_speaker = None
        if self.reachy and hasattr(self.reachy, 'speaker'):
            reachy_speaker = self.reachy.speaker

        return ReachyTTS(
            reachy_speaker=reachy_speaker,
            fallback_language=tts_config['language'],
            fallback_rate=tts_config['rate']
        )

    def _init_audio_player(self) -> AudioPlayer:
        """Initialize audio player."""
        audio_config = self.config['audio']
        return AudioPlayer(volume=audio_config['volume'])

    def _init_dance_controller(self) -> DanceController:
        """Initialize dance controller."""
        dance_config = self.config['dance']

        return DanceController(
            reachy_mini=self.reachy,
            choreography_path=dance_config.get('choreography_path'),
            bpm_tolerance=dance_config.get('bpm_tolerance', 10)
        )

    def process_voice_command(self, command: str) -> bool:
        """
        Process a voice command.

        Args:
            command: Voice command text

        Returns:
            True if command was processed successfully
        """
        # Clean query
        query = QueryProcessor.clean_query(command)

        if not query:
            logger.warning("Empty query after cleaning")
            return False

        logger.info(f"Processing query: '{query}'")

        # Search for matching tracks
        search_config = self.config['search']
        results = self.search_engine.search(
            query,
            top_k=search_config['top_k'],
            normalize=True
        )

        if not results:
            logger.warning("No results found")
            self.tts.say_not_found(query)
            return False

        # Get best match
        best_track, score = results[0]
        logger.info(f"Best match: {best_track.artist} - {best_track.title} (score: {score:.3f})")

        # Check confidence threshold
        if score < search_config['confidence_threshold']:
            logger.warning(f"Low confidence score: {score:.3f}")
            self.tts.say_not_found(query)
            return False

        # Ask for confirmation
        self.tts.ask_confirmation(best_track.artist, best_track.title)

        # Simple confirmation: listen for "oui" or "yes"
        logger.info("Listening for confirmation...")
        confirmation = self.voice_recognizer.listen_and_transcribe(duration=3)
        confirmation_lower = confirmation.lower()

        if any(word in confirmation_lower for word in ['oui', 'yes', 'ok', 'ouais', 'd\'accord']):
            logger.info("Confirmation received")
            self.play_track(best_track)
            return True
        else:
            logger.info("Confirmation denied")
            self.tts.say("D'accord, annulé")
            return False

    def play_track(self, track):
        """Play a track with dance synchronization."""
        try:
            # Announce track
            self.tts.confirm_track(track.artist, track.title)

            # Start dancing if enabled
            dance_config = self.config['dance']
            if dance_config.get('enable_dance', True) and track.bpm > 0:
                logger.info(f"Starting dance at {track.bpm} BPM")
                self.dance_controller.dance_to_track(track.bpm, track.duration)

            # Play audio
            logger.info("Starting playback")

            def on_finish():
                logger.info("Track finished")
                self.dance_controller.stop_dancing()

            self.audio_player.play(track, on_finish=on_finish)

        except Exception as e:
            logger.error(f"Error playing track: {e}")
            self.tts.say_error("playback")
            self.dance_controller.stop_dancing()

    def run(self):
        """Run main application loop."""
        self.running = True

        print("\n" + "=" * 60)
        print("🎵 Spotireachy - Voice Music Player for Reachy Mini")
        print("=" * 60)
        print(f"\n✅ Ready! Library: {len(self.library.tracks)} tracks")
        print("\n💡 Say a song name, artist, or album to play music")
        print("   Press Ctrl+C to quit\n")

        # Welcome message
        self.tts.say("Bonjour, je suis prêt à jouer de la musique !")

        try:
            while self.running:
                # Listen for command
                print("\n🎤 Listening... (speak now)")
                try:
                    command = self.voice_recognizer.listen_and_transcribe(duration=5)

                    if command:
                        print(f"   You said: '{command}'")
                        self.process_voice_command(command)
                    else:
                        print("   (no speech detected)")

                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Error processing command: {e}")
                    continue

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")
            self.shutdown()

    def shutdown(self):
        """Cleanup and shutdown."""
        self.running = False

        # Stop playback
        if self.audio_player.is_playing:
            self.audio_player.stop()

        # Stop dancing
        if self.dance_controller.is_dancing:
            self.dance_controller.stop_dancing()

        logger.info("Shutdown complete")


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
    """Main entry point."""
    # Load configuration
    config = load_config()

    # Create and run application
    app = SpotireachyApp(config)
    app.run()


if __name__ == "__main__":
    main()
