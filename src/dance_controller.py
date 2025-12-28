"""
Dance controller for Reachy Mini with BPM synchronization.
"""

import logging
import json
import random
import threading
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Choreography:
    """Represents a dance choreography."""
    name: str
    bpm: float
    duration: float
    moves: List[Dict]

    @classmethod
    def from_json(cls, json_path: str) -> 'Choreography':
        """Load choreography from JSON file."""
        with open(json_path, 'r') as f:
            data = json.load(f)

        return cls(
            name=data.get('name', 'unknown'),
            bpm=data.get('bpm', 120),
            duration=data.get('duration', 0),
            moves=data.get('moves', [])
        )


class DanceController:
    """Controller for Reachy Mini dance movements."""

    def __init__(
        self,
        reachy_mini=None,
        choreography_path: Optional[str] = None,
        bpm_tolerance: float = 10
    ):
        """
        Initialize dance controller.

        Args:
            reachy_mini: Reachy Mini robot instance
            choreography_path: Path to custom choreography files
            bpm_tolerance: BPM tolerance for matching choreographies (±)
        """
        self.reachy = reachy_mini
        self.bpm_tolerance = bpm_tolerance
        self.choreographies: List[Choreography] = []
        self.is_dancing = False
        self._dance_thread: Optional[threading.Thread] = None

        # Load choreographies if path provided
        if choreography_path:
            self.load_choreographies(choreography_path)

        logger.info(f"Dance controller initialized with {len(self.choreographies)} choreographies")

    def load_choreographies(self, path: str):
        """
        Load choreographies from directory.

        Args:
            path: Path to directory containing choreography JSON files
        """
        path = Path(path)
        if not path.exists():
            logger.warning(f"Choreography path not found: {path}")
            return

        json_files = list(path.glob("*.json"))
        logger.info(f"Loading {len(json_files)} choreographies from {path}")

        for json_file in json_files:
            try:
                choreo = Choreography.from_json(str(json_file))
                self.choreographies.append(choreo)
                logger.debug(f"Loaded choreography: {choreo.name} ({choreo.bpm} BPM)")
            except Exception as e:
                logger.warning(f"Error loading choreography {json_file.name}: {e}")

    def select_choreography(self, target_bpm: float) -> Optional[Choreography]:
        """
        Select best matching choreography for given BPM.

        Args:
            target_bpm: Target BPM to match

        Returns:
            Best matching Choreography or None
        """
        if not self.choreographies:
            logger.warning("No choreographies available")
            return None

        # Find choreographies within tolerance
        matching = [
            choreo for choreo in self.choreographies
            if abs(choreo.bpm - target_bpm) <= self.bpm_tolerance
        ]

        if matching:
            # Pick the closest match
            best = min(matching, key=lambda c: abs(c.bpm - target_bpm))
            logger.info(f"Selected choreography '{best.name}' ({best.bpm} BPM) for {target_bpm} BPM")
            return best

        # If no exact match, try doubling/halving BPM
        for multiplier in [2, 0.5]:
            adjusted_bpm = target_bpm * multiplier
            matching = [
                choreo for choreo in self.choreographies
                if abs(choreo.bpm - adjusted_bpm) <= self.bpm_tolerance
            ]
            if matching:
                best = min(matching, key=lambda c: abs(c.bpm - adjusted_bpm))
                logger.info(f"Selected choreography '{best.name}' ({best.bpm} BPM) "
                          f"with {multiplier}x speed for {target_bpm} BPM")
                return best

        # Fallback: pick random
        fallback = random.choice(self.choreographies)
        logger.info(f"No BPM match, using random choreography '{fallback.name}'")
        return fallback

    def dance_simple(self, bpm: float, duration: float):
        """
        Perform simple dance moves synchronized to BPM.

        Args:
            bpm: Beats per minute
            duration: Duration in seconds
        """
        if not self.reachy:
            logger.warning("Reachy Mini not connected, simulating dance")
            self._simulate_dance(bpm, duration)
            return

        try:
            logger.info(f"Dancing at {bpm} BPM for {duration}s")
            self.is_dancing = True

            # Calculate beat interval
            beat_interval = 60.0 / bpm  # seconds per beat

            # Simple head bobbing and antenna movements
            import time
            start_time = time.time()

            while time.time() - start_time < duration and self.is_dancing:
                # Head nod
                try:
                    # These are example movements - adjust based on actual Reachy API
                    if hasattr(self.reachy, 'head'):
                        # Nod down
                        self.reachy.head.look_at(x=0.5, y=0, z=-0.3, duration=beat_interval/2)
                        time.sleep(beat_interval/2)

                        # Nod up
                        self.reachy.head.look_at(x=0.5, y=0, z=0, duration=beat_interval/2)
                        time.sleep(beat_interval/2)

                    # Antenna wiggle
                    if hasattr(self.reachy, 'antennas'):
                        self.reachy.antennas.wiggle(duration=beat_interval)

                except Exception as e:
                    logger.warning(f"Error during dance movement: {e}")
                    break

            self.is_dancing = False
            logger.info("Dance complete")

        except Exception as e:
            logger.error(f"Error during dance: {e}")
            self.is_dancing = False

    def _simulate_dance(self, bpm: float, duration: float):
        """Simulate dance for testing without Reachy."""
        import time
        beat_interval = 60.0 / bpm
        num_beats = int(duration / beat_interval)

        logger.info(f"🕺 Simulating dance: {num_beats} beats at {bpm} BPM")

        for i in range(num_beats):
            if not self.is_dancing:
                break
            print(f"💃 Beat {i+1}/{num_beats}")
            time.sleep(beat_interval)

        self.is_dancing = False

    def dance_to_track(self, bpm: float, duration: float):
        """
        Start dancing in a separate thread.

        Args:
            bpm: Track BPM
            duration: Track duration in seconds
        """
        if self.is_dancing:
            logger.warning("Already dancing")
            return

        self.is_dancing = True
        self._dance_thread = threading.Thread(
            target=self.dance_simple,
            args=(bpm, duration)
        )
        self._dance_thread.daemon = True
        self._dance_thread.start()

    def stop_dancing(self):
        """Stop current dance."""
        if self.is_dancing:
            logger.info("Stopping dance")
            self.is_dancing = False

            if self._dance_thread:
                self._dance_thread.join(timeout=1.0)

    def celebrate(self):
        """Perform a celebratory gesture."""
        if not self.reachy:
            logger.info("🎉 *Celebrating!*")
            return

        try:
            # Example celebration - adjust based on actual Reachy API
            if hasattr(self.reachy, 'antennas'):
                self.reachy.antennas.wiggle(duration=2.0)

            if hasattr(self.reachy, 'head'):
                # Happy head shake
                self.reachy.head.look_at(x=0.5, y=0.2, z=0, duration=0.3)
                self.reachy.head.look_at(x=0.5, y=-0.2, z=0, duration=0.3)
                self.reachy.head.look_at(x=0.5, y=0, z=0, duration=0.3)

        except Exception as e:
            logger.error(f"Error during celebration: {e}")


if __name__ == "__main__":
    # Test dance controller
    logging.basicConfig(level=logging.INFO)

    controller = DanceController()

    print("\n🕺 Testing dance controller")
    controller.is_dancing = True
    controller.dance_simple(bpm=120, duration=5)
    print("✅ Dance test complete")
