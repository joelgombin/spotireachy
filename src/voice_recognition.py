"""
Voice recognition module using Whisper for local speech-to-text.
"""

import logging
from typing import Optional
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class VoiceRecognizer:
    """Voice recognition using Whisper model."""

    def __init__(
        self,
        model_size: str = "base",
        language: str = "fr",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Initialize Whisper voice recognizer.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code (fr, en, etc.)
            device: Device to use (cpu, cuda)
            compute_type: Compute type for inference (int8, float16, float32)
        """
        self.language = language
        self.sample_rate = 16000  # Whisper expects 16kHz
        self.duration = 5  # Recording duration in seconds

        logger.info(f"Loading Whisper model '{model_size}' on {device}...")
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        logger.info("Whisper model loaded successfully")

    def listen(self, duration: Optional[float] = None) -> np.ndarray:
        """
        Record audio from microphone.

        Args:
            duration: Recording duration in seconds (default: self.duration)

        Returns:
            Audio data as numpy array
        """
        duration = duration or self.duration
        logger.info(f"Recording for {duration} seconds...")

        try:
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            logger.info("Recording complete")
            return audio.flatten()
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            raise

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Transcribe audio to text using Whisper.

        Args:
            audio: Audio data as numpy array

        Returns:
            Transcribed text
        """
        logger.info("Transcribing audio...")

        try:
            segments, info = self.model.transcribe(
                audio,
                language=self.language,
                beam_size=5
            )

            # Concatenate all segments
            text = " ".join([segment.text for segment in segments])
            text = text.strip()

            logger.info(f"Transcription: '{text}' (confidence: {info.language_probability:.2f})")
            return text

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    def listen_and_transcribe(self, duration: Optional[float] = None) -> str:
        """
        Record audio and transcribe it in one go.

        Args:
            duration: Recording duration in seconds

        Returns:
            Transcribed text
        """
        audio = self.listen(duration)
        return self.transcribe(audio)

    def wait_for_wake_word(self, wake_word: str = "reachy", timeout: int = 30) -> bool:
        """
        Wait for a wake word to activate listening.

        Args:
            wake_word: Word to listen for
            timeout: Maximum time to wait in seconds

        Returns:
            True if wake word detected, False otherwise
        """
        logger.info(f"Waiting for wake word '{wake_word}'...")

        # Simple implementation: record chunks and check for wake word
        chunk_duration = 3
        attempts = timeout // chunk_duration

        for _ in range(attempts):
            try:
                text = self.listen_and_transcribe(duration=chunk_duration)
                if wake_word.lower() in text.lower():
                    logger.info("Wake word detected!")
                    return True
            except Exception as e:
                logger.warning(f"Error during wake word detection: {e}")
                continue

        logger.info("Wake word timeout")
        return False


if __name__ == "__main__":
    # Test the voice recognition
    logging.basicConfig(level=logging.INFO)

    recognizer = VoiceRecognizer(model_size="tiny", language="fr")

    print("\n🎤 Test de reconnaissance vocale")
    print("Parlez maintenant (5 secondes)...")

    text = recognizer.listen_and_transcribe()
    print(f"\n✅ Transcription: {text}")
