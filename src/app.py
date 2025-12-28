"""
Spotireachy - Reachy Mini App wrapper
Adapts the main application to the Reachy Mini App framework.
"""

import logging
import threading
import yaml
from pathlib import Path
from typing import Optional

from reachy_mini import ReachyMini
from reachy_mini.app import ReachyMiniApp

from .music_library import MusicLibrary
from .semantic_search import SemanticSearchEngine, QueryProcessor
from .voice_recognition import VoiceRecognizer
from .tts_engine import ReachyTTS
from .audio_player import AudioPlayer
from .dance_controller import DanceController

logger = logging.getLogger(__name__)


class SpotireachyApp(ReachyMiniApp):
    """
    Spotireachy - Voice-controlled music player for Reachy Mini.

    This app allows Reachy Mini to:
    - Listen to voice commands
    - Search for music using semantic search
    - Confirm selection with TTS
    - Play music and dance synchronized to BPM
    """

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the Spotireachy app."""
        super().__init__()

        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Components (initialized in run())
        self.library: Optional[MusicLibrary] = None
        self.search_engine: Optional[SemanticSearchEngine] = None
        self.voice_recognizer: Optional[VoiceRecognizer] = None
        self.tts: Optional[ReachyTTS] = None
        self.audio_player: Optional[AudioPlayer] = None
        self.dance_controller: Optional[DanceController] = None

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            # Return default config
            return self._get_default_config()

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _get_default_config(self) -> dict:
        """Get default configuration."""
        return {
            'whisper': {
                'model': 'base',
                'language': 'fr',
                'device': 'cpu'
            },
            'music': {
                'library_path': './music',
                'supported_formats': ['.mp3', '.wav', '.flac', '.m4a']
            },
            'search': {
                'model': 'paraphrase-multilingual-MiniLM-L12-v2',
                'top_k': 3,
                'confidence_threshold': 0.6
            },
            'audio': {
                'volume': 0.8
            },
            'dance': {
                'enable_dance': True,
                'choreography_path': None,
                'bpm_tolerance': 10
            },
            'tts': {
                'language': 'fr',
                'rate': 150
            },
            'data': {
                'embeddings_cache': './data/embeddings.npy',
                'metadata_cache': './data/metadata.json',
                'index_cache': './data/faiss.index'
            }
        }

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
        """
        Main app loop - called by Reachy Mini daemon.

        Args:
            reachy_mini: Initialized ReachyMini instance
            stop_event: Event to signal when to stop the app
        """
        logger.info("🎵 Starting Spotireachy...")

        try:
            # Initialize components
            self._initialize_components(reachy_mini)

            # Welcome message
            self.tts.say("Bonjour, je suis prêt à jouer de la musique !")

            # Main loop
            while not stop_event.is_set():
                try:
                    # Listen for command
                    logger.info("Listening for voice command...")
                    command = self.voice_recognizer.listen_and_transcribe(duration=5)

                    if command and not stop_event.is_set():
                        logger.info(f"Received command: '{command}'")
                        self._process_command(command, stop_event)

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    if not stop_event.is_set():
                        self.tts.say_error()

        except Exception as e:
            logger.error(f"Fatal error in Spotireachy: {e}", exc_info=True)

        finally:
            # Cleanup
            self._cleanup()
            logger.info("Spotireachy stopped")

    def _initialize_components(self, reachy_mini: ReachyMini):
        """Initialize all app components."""
        logger.info("Initializing components...")

        # Music library
        music_config = self.config['music']
        data_config = self.config['data']

        self.library = MusicLibrary(
            library_path=music_config['library_path'],
            supported_formats=music_config['supported_formats']
        )

        # Load from cache
        if not self.library.load_from_cache(data_config['metadata_cache']):
            logger.error("Could not load music library from cache!")
            logger.info("Please run: uv run spotireachy-index")
            raise RuntimeError("Music library not indexed")

        logger.info(f"Loaded {len(self.library.tracks)} tracks")

        # Semantic search engine
        search_config = self.config['search']
        self.search_engine = SemanticSearchEngine(
            model_name=search_config['model'],
            device='cpu'
        )

        if not self.search_engine.load_index(
            index_path=data_config['index_cache'],
            embeddings_path=data_config['embeddings_cache'],
            tracks=self.library.tracks
        ):
            logger.error("Could not load search index!")
            raise RuntimeError("Search index not built")

        # Voice recognizer
        whisper_config = self.config['whisper']
        self.voice_recognizer = VoiceRecognizer(
            model_size=whisper_config['model'],
            language=whisper_config['language'],
            device=whisper_config['device']
        )

        # TTS with Reachy speaker
        tts_config = self.config['tts']
        reachy_speaker = reachy_mini.speaker if hasattr(reachy_mini, 'speaker') else None
        self.tts = ReachyTTS(
            reachy_speaker=reachy_speaker,
            fallback_language=tts_config['language'],
            fallback_rate=tts_config['rate']
        )

        # Audio player
        audio_config = self.config['audio']
        self.audio_player = AudioPlayer(volume=audio_config['volume'])

        # Dance controller
        dance_config = self.config['dance']
        self.dance_controller = DanceController(
            reachy_mini=reachy_mini,
            choreography_path=dance_config.get('choreography_path'),
            bpm_tolerance=dance_config.get('bpm_tolerance', 10)
        )

        logger.info("✅ All components initialized")

    def _process_command(self, command: str, stop_event: threading.Event):
        """Process a voice command."""
        # Clean query
        query = QueryProcessor.clean_query(command)

        if not query:
            return

        logger.info(f"Processing query: '{query}'")

        # Search for tracks
        search_config = self.config['search']
        results = self.search_engine.search(
            query,
            top_k=search_config['top_k'],
            normalize=True
        )

        if not results:
            logger.warning("No results found")
            self.tts.say_not_found(query)
            return

        # Get best match
        best_track, score = results[0]
        logger.info(f"Best match: {best_track.artist} - {best_track.title} (score: {score:.3f})")

        # Check confidence
        if score < search_config['confidence_threshold']:
            logger.warning(f"Low confidence: {score:.3f}")
            self.tts.say_not_found(query)
            return

        # Ask confirmation
        self.tts.ask_confirmation(best_track.artist, best_track.title)

        # Listen for confirmation (but check stop_event)
        if stop_event.is_set():
            return

        confirmation = self.voice_recognizer.listen_and_transcribe(duration=3)

        if stop_event.is_set():
            return

        # Check confirmation
        confirmation_words = ['oui', 'yes', 'ok', 'ouais', 'd\'accord', 'vas-y']
        if any(word in confirmation.lower() for word in confirmation_words):
            self._play_track(best_track, stop_event)
        else:
            self.tts.say("D'accord, annulé")

    def _play_track(self, track, stop_event: threading.Event):
        """Play a track with dance."""
        try:
            # Announce
            self.tts.confirm_track(track.artist, track.title)

            if stop_event.is_set():
                return

            # Start dance if enabled
            dance_config = self.config['dance']
            if dance_config.get('enable_dance', True) and track.bpm > 0:
                self.dance_controller.dance_to_track(track.bpm, track.duration)

            # Play audio
            def on_finish():
                self.dance_controller.stop_dancing()

            self.audio_player.play(track, on_finish=on_finish)

        except Exception as e:
            logger.error(f"Error playing track: {e}")
            self.tts.say_error("playback")
            self.dance_controller.stop_dancing()

    def _cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up...")

        if self.audio_player and self.audio_player.is_playing:
            self.audio_player.stop()

        if self.dance_controller and self.dance_controller.is_dancing:
            self.dance_controller.stop_dancing()


# For standalone execution
def main():
    """Run Spotireachy in standalone mode (not as Reachy app)."""
    from .main import main as standalone_main
    standalone_main()


if __name__ == "__main__":
    main()
