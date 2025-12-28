"""
Text-to-Speech engine for voice feedback.
"""

import logging
from typing import Optional
import pyttsx3

logger = logging.getLogger(__name__)


class TTSEngine:
    """Text-to-Speech engine using pyttsx3."""

    def __init__(self, language: str = "fr", rate: int = 150):
        """
        Initialize TTS engine.

        Args:
            language: Language code (fr, en, etc.)
            rate: Speech rate (words per minute)
        """
        self.language = language
        logger.info("Initializing TTS engine...")

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)

            # Try to set French voice if available
            if language == "fr":
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if 'french' in voice.name.lower() or 'fr' in voice.languages:
                        self.engine.setProperty('voice', voice.id)
                        logger.info(f"Using French voice: {voice.name}")
                        break

            logger.info("TTS engine initialized")

        except Exception as e:
            logger.error(f"Error initializing TTS engine: {e}")
            self.engine = None

    def say(self, text: str, wait: bool = True):
        """
        Speak text.

        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete
        """
        if self.engine is None:
            logger.warning("TTS engine not available")
            return

        try:
            logger.info(f"Speaking: '{text}'")
            self.engine.say(text)

            if wait:
                self.engine.runAndWait()

        except Exception as e:
            logger.error(f"Error speaking text: {e}")

    def stop(self):
        """Stop current speech."""
        if self.engine:
            try:
                self.engine.stop()
            except Exception as e:
                logger.error(f"Error stopping TTS: {e}")


class ReachyTTS:
    """TTS wrapper that can use either pyttsx3 or Reachy's built-in speaker."""

    def __init__(
        self,
        reachy_speaker=None,
        fallback_language: str = "fr",
        fallback_rate: int = 150
    ):
        """
        Initialize Reachy TTS.

        Args:
            reachy_speaker: Reachy's speaker object (if available)
            fallback_language: Language for fallback TTS
            fallback_rate: Rate for fallback TTS
        """
        self.reachy_speaker = reachy_speaker
        self.fallback_tts = TTSEngine(fallback_language, fallback_rate)

    def say(self, text: str, wait: bool = True):
        """
        Speak text using Reachy's speaker or fallback TTS.

        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete
        """
        if self.reachy_speaker:
            try:
                logger.info(f"Speaking via Reachy: '{text}'")
                self.reachy_speaker.say(text)
                return
            except Exception as e:
                logger.warning(f"Error using Reachy speaker, falling back to pyttsx3: {e}")

        # Fallback to pyttsx3
        self.fallback_tts.say(text, wait)

    def confirm_track(self, artist: str, title: str) -> str:
        """
        Generate and speak confirmation message for a track.

        Args:
            artist: Artist name
            title: Track title

        Returns:
            Confirmation message
        """
        message = f"Je lance {title} de {artist}"
        self.say(message)
        return message

    def ask_confirmation(self, artist: str, title: str) -> str:
        """
        Generate and speak confirmation question for a track.

        Args:
            artist: Artist name
            title: Track title

        Returns:
            Confirmation question
        """
        message = f"Voulez-vous écouter {title} de {artist} ?"
        self.say(message)
        return message

    def say_not_found(self, query: str) -> str:
        """
        Say that no track was found.

        Args:
            query: Original query

        Returns:
            Error message
        """
        message = f"Désolé, je n'ai pas trouvé de chanson correspondant à {query}"
        self.say(message)
        return message

    def say_error(self, error_type: str = "unknown") -> str:
        """
        Say that an error occurred.

        Args:
            error_type: Type of error

        Returns:
            Error message
        """
        messages = {
            "playback": "Désolé, je ne peux pas lire cette chanson",
            "connection": "Désolé, je ne peux pas me connecter",
            "unknown": "Désolé, une erreur s'est produite"
        }
        message = messages.get(error_type, messages["unknown"])
        self.say(message)
        return message


if __name__ == "__main__":
    # Test TTS engine
    logging.basicConfig(level=logging.INFO)

    tts = ReachyTTS()

    print("\n🔊 Test TTS")
    tts.say("Bonjour, je suis Reachy Mini")
    tts.confirm_track("The Beatles", "Let It Be")
    tts.ask_confirmation("Queen", "Bohemian Rhapsody")
