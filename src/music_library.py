"""
Music library management with metadata extraction and BPM analysis.
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import librosa
import numpy as np
from mutagen import File as MutagenFile
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class Track:
    """Represents a music track with metadata."""
    file_path: str
    title: str
    artist: str
    album: str
    duration: float
    bpm: float
    genre: Optional[str] = None
    year: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Track':
        """Create Track from dictionary."""
        return cls(**data)

    def get_search_text(self) -> str:
        """Get combined text for semantic search."""
        parts = [self.title, self.artist, self.album]
        if self.genre:
            parts.append(self.genre)
        return " ".join(filter(None, parts))


class MusicLibrary:
    """Manages music library with metadata and BPM extraction."""

    def __init__(self, library_path: str, supported_formats: List[str] = None):
        """
        Initialize music library.

        Args:
            library_path: Path to music files directory
            supported_formats: List of supported file extensions
        """
        self.library_path = Path(library_path)
        self.supported_formats = supported_formats or ['.mp3', '.wav', '.flac', '.m4a']
        self.tracks: List[Track] = []

    def scan_library(self, extract_bpm: bool = True) -> List[Track]:
        """
        Scan library directory and extract metadata.

        Args:
            extract_bpm: Whether to extract BPM (slower but useful for dance)

        Returns:
            List of Track objects
        """
        logger.info(f"Scanning library at {self.library_path}...")

        if not self.library_path.exists():
            logger.error(f"Library path does not exist: {self.library_path}")
            raise ValueError(f"Library path not found: {self.library_path}")

        # Find all music files
        music_files = []
        for ext in self.supported_formats:
            music_files.extend(self.library_path.rglob(f"*{ext}"))

        logger.info(f"Found {len(music_files)} music files")

        # Process each file
        tracks = []
        for file_path in tqdm(music_files, desc="Processing tracks"):
            try:
                track = self._process_file(file_path, extract_bpm)
                if track:
                    tracks.append(track)
            except Exception as e:
                logger.warning(f"Error processing {file_path.name}: {e}")
                continue

        self.tracks = tracks
        logger.info(f"Successfully processed {len(tracks)} tracks")
        return tracks

    def _process_file(self, file_path: Path, extract_bpm: bool) -> Optional[Track]:
        """
        Process a single music file to extract metadata.

        Args:
            file_path: Path to music file
            extract_bpm: Whether to extract BPM

        Returns:
            Track object or None if processing failed
        """
        # Extract metadata using mutagen
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                logger.warning(f"Could not read metadata from {file_path.name}")
                return None

            # Get basic metadata
            title = self._get_tag(audio_file, ['title', 'TIT2', '\xa9nam']) or file_path.stem
            artist = self._get_tag(audio_file, ['artist', 'TPE1', '\xa9ART']) or "Unknown Artist"
            album = self._get_tag(audio_file, ['album', 'TALB', '\xa9alb']) or "Unknown Album"
            genre = self._get_tag(audio_file, ['genre', 'TCON', '\xa9gen'])
            year = self._get_year(audio_file)

            # Get duration
            duration = audio_file.info.length if hasattr(audio_file, 'info') else 0.0

        except Exception as e:
            logger.warning(f"Error reading metadata from {file_path.name}: {e}")
            title = file_path.stem
            artist = "Unknown Artist"
            album = "Unknown Album"
            genre = None
            year = None
            duration = 0.0

        # Extract BPM if requested
        bpm = 0.0
        if extract_bpm:
            bpm = self._extract_bpm(file_path)

        track = Track(
            file_path=str(file_path),
            title=title,
            artist=artist,
            album=album,
            duration=duration,
            bpm=bpm,
            genre=genre,
            year=year
        )

        return track

    def _get_tag(self, audio_file, tag_names: List[str]) -> Optional[str]:
        """Get tag value from multiple possible tag names."""
        for tag_name in tag_names:
            if tag_name in audio_file:
                value = audio_file[tag_name]
                if isinstance(value, list):
                    return str(value[0])
                return str(value)
        return None

    def _get_year(self, audio_file) -> Optional[int]:
        """Extract year from audio file."""
        year_tags = ['date', 'TDRC', '\xa9day', 'year']
        year_str = self._get_tag(audio_file, year_tags)
        if year_str:
            try:
                # Extract first 4 digits
                year_str = ''.join(filter(str.isdigit, str(year_str)))[:4]
                return int(year_str)
            except ValueError:
                return None
        return None

    def _extract_bpm(self, file_path: Path) -> float:
        """
        Extract BPM using librosa.

        Args:
            file_path: Path to audio file

        Returns:
            BPM value
        """
        try:
            # Load audio file
            y, sr = librosa.load(str(file_path), duration=60)  # Only analyze first 60 seconds

            # Extract tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            # Handle array vs scalar
            if isinstance(tempo, np.ndarray):
                tempo = float(tempo[0])
            else:
                tempo = float(tempo)

            logger.debug(f"Extracted BPM {tempo:.1f} from {file_path.name}")
            return round(tempo, 1)

        except Exception as e:
            logger.warning(f"Could not extract BPM from {file_path.name}: {e}")
            return 0.0

    def save_to_cache(self, cache_path: str):
        """Save library metadata to cache file."""
        cache_path = Path(cache_path)
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'tracks': [track.to_dict() for track in self.tracks]
        }

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.tracks)} tracks to cache: {cache_path}")

    def load_from_cache(self, cache_path: str) -> bool:
        """
        Load library metadata from cache file.

        Returns:
            True if loaded successfully, False otherwise
        """
        cache_path = Path(cache_path)

        if not cache_path.exists():
            logger.warning(f"Cache file not found: {cache_path}")
            return False

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.tracks = [Track.from_dict(track_data) for track_data in data['tracks']]
            logger.info(f"Loaded {len(self.tracks)} tracks from cache")
            return True

        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return False

    def get_track_by_index(self, index: int) -> Optional[Track]:
        """Get track by index."""
        if 0 <= index < len(self.tracks):
            return self.tracks[index]
        return None

    def search_by_title(self, title: str) -> List[Track]:
        """Simple search by title (case-insensitive)."""
        title_lower = title.lower()
        return [
            track for track in self.tracks
            if title_lower in track.title.lower()
        ]


if __name__ == "__main__":
    # Test the music library
    logging.basicConfig(level=logging.INFO)

    library = MusicLibrary("./music")

    print("\n🎵 Scanning music library...")
    tracks = library.scan_library(extract_bpm=True)

    print(f"\n✅ Found {len(tracks)} tracks")
    if tracks:
        print("\nFirst 5 tracks:")
        for i, track in enumerate(tracks[:5], 1):
            print(f"{i}. {track.artist} - {track.title} ({track.bpm:.0f} BPM)")

    # Save to cache
    library.save_to_cache("./data/metadata.json")
