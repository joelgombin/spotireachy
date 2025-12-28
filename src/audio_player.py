"""
Audio player with playback control.
"""

import logging
import threading
from pathlib import Path
from typing import Optional, Callable
import pygame
from .music_library import Track

logger = logging.getLogger(__name__)


class AudioPlayer:
    """Audio player using pygame mixer."""

    def __init__(self, volume: float = 0.8):
        """
        Initialize audio player.

        Args:
            volume: Initial volume (0.0 to 1.0)
        """
        logger.info("Initializing audio player...")

        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(volume)
            self.volume = volume
            logger.info("Audio player initialized")
        except Exception as e:
            logger.error(f"Error initializing audio player: {e}")
            raise

        self.current_track: Optional[Track] = None
        self.is_playing = False
        self._playback_thread: Optional[threading.Thread] = None
        self._on_finish_callback: Optional[Callable] = None

    def play(self, track: Track, on_finish: Optional[Callable] = None):
        """
        Play a track.

        Args:
            track: Track to play
            on_finish: Callback to call when playback finishes
        """
        try:
            # Stop current playback if any
            if self.is_playing:
                self.stop()

            logger.info(f"Playing: {track.artist} - {track.title}")

            # Load and play
            pygame.mixer.music.load(track.file_path)
            pygame.mixer.music.play()

            self.current_track = track
            self.is_playing = True
            self._on_finish_callback = on_finish

            # Start monitoring thread
            self._playback_thread = threading.Thread(target=self._monitor_playback)
            self._playback_thread.daemon = True
            self._playback_thread.start()

        except Exception as e:
            logger.error(f"Error playing track: {e}")
            raise

    def _monitor_playback(self):
        """Monitor playback and call callback when finished."""
        while self.is_playing:
            if not pygame.mixer.music.get_busy():
                self.is_playing = False
                logger.info("Playback finished")

                if self._on_finish_callback:
                    try:
                        self._on_finish_callback()
                    except Exception as e:
                        logger.error(f"Error in finish callback: {e}")
                break

            threading.Event().wait(0.1)  # Check every 100ms

    def stop(self):
        """Stop playback."""
        if self.is_playing:
            logger.info("Stopping playback")
            pygame.mixer.music.stop()
            self.is_playing = False
            self.current_track = None

    def pause(self):
        """Pause playback."""
        if self.is_playing:
            logger.info("Pausing playback")
            pygame.mixer.music.pause()

    def resume(self):
        """Resume playback."""
        if self.is_playing:
            logger.info("Resuming playback")
            pygame.mixer.music.unpause()

    def set_volume(self, volume: float):
        """
        Set volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(volume)
        self.volume = volume
        logger.debug(f"Volume set to {volume:.1%}")

    def get_position(self) -> float:
        """
        Get current playback position in seconds.

        Returns:
            Position in seconds
        """
        if self.is_playing:
            # pygame returns position in milliseconds
            return pygame.mixer.music.get_pos() / 1000.0
        return 0.0


if __name__ == "__main__":
    # Test audio player
    logging.basicConfig(level=logging.INFO)

    from music_library import Track

    # Create a dummy track (you'll need a real audio file to test)
    track = Track(
        file_path="test.mp3",  # Replace with actual file
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        duration=180,
        bpm=120
    )

    player = AudioPlayer()

    def on_finish():
        print("✅ Playback finished!")

    print("\n🎵 Playing test track...")
    # player.play(track, on_finish)

    # Keep running to let the track play
    # import time
    # time.sleep(10)
    # player.stop()
