"""
Semantic search using sentence embeddings and FAISS for fast similarity search.
"""

import logging
from pathlib import Path
from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from .music_library import Track

logger = logging.getLogger(__name__)


class SemanticSearchEngine:
    """Semantic search engine for music tracks."""

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        device: str = "cpu"
    ):
        """
        Initialize semantic search engine.

        Args:
            model_name: Name of the sentence-transformers model
            device: Device to use (cpu, cuda)
        """
        logger.info(f"Loading embedding model '{model_name}'...")
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded (dimension: {self.dimension})")

        self.index = None
        self.tracks = []

    def build_index(self, tracks: List[Track], normalize: bool = True):
        """
        Build FAISS index from tracks.

        Args:
            tracks: List of Track objects
            normalize: Whether to normalize embeddings (recommended for cosine similarity)
        """
        logger.info(f"Building index for {len(tracks)} tracks...")

        self.tracks = tracks

        # Extract text for each track
        texts = [track.get_search_text() for track in tracks]

        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )

        # Build FAISS index
        logger.info("Building FAISS index...")
        if normalize:
            # Use inner product for normalized vectors (equivalent to cosine similarity)
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            # Use L2 distance
            self.index = faiss.IndexFlatL2(self.dimension)

        self.index.add(embeddings.astype(np.float32))
        logger.info("Index built successfully")

    def search(
        self,
        query: str,
        top_k: int = 3,
        normalize: bool = True
    ) -> List[Tuple[Track, float]]:
        """
        Search for tracks matching the query.

        Args:
            query: Search query text
            top_k: Number of results to return
            normalize: Whether to normalize query embedding

        Returns:
            List of (Track, score) tuples, sorted by relevance
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")

        # Generate query embedding
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )

        # Search
        scores, indices = self.index.search(query_embedding.astype(np.float32), top_k)

        # Return results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.tracks):
                results.append((self.tracks[idx], float(score)))

        logger.info(f"Search for '{query}' returned {len(results)} results")
        return results

    def save_index(self, index_path: str, embeddings_path: str):
        """
        Save FAISS index and embeddings to disk.

        Args:
            index_path: Path to save FAISS index
            embeddings_path: Path to save track embeddings
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")

        index_path = Path(index_path)
        embeddings_path = Path(embeddings_path)

        # Create directories
        index_path.parent.mkdir(parents=True, exist_ok=True)
        embeddings_path.parent.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, str(index_path))

        # Save track references (we need this to map indices back to tracks)
        track_refs = [
            {
                'file_path': track.file_path,
                'title': track.title,
                'artist': track.artist
            }
            for track in self.tracks
        ]
        np.save(embeddings_path, track_refs)

        logger.info(f"Index saved to {index_path}")

    def load_index(self, index_path: str, embeddings_path: str, tracks: List[Track]) -> bool:
        """
        Load FAISS index from disk.

        Args:
            index_path: Path to FAISS index file
            embeddings_path: Path to embeddings file
            tracks: List of Track objects (must match saved index)

        Returns:
            True if loaded successfully, False otherwise
        """
        index_path = Path(index_path)
        embeddings_path = Path(embeddings_path)

        if not index_path.exists() or not embeddings_path.exists():
            logger.warning("Index files not found")
            return False

        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_path))

            # Load track references
            track_refs = np.load(embeddings_path, allow_pickle=True)

            # Match tracks (assuming same order)
            if len(track_refs) != len(tracks):
                logger.warning("Track count mismatch between index and library")
                return False

            self.tracks = tracks
            logger.info(f"Index loaded successfully ({len(self.tracks)} tracks)")
            return True

        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False


class QueryProcessor:
    """Process and normalize user queries."""

    @staticmethod
    def clean_query(query: str) -> str:
        """
        Clean and normalize query text.

        Args:
            query: Raw query text

        Returns:
            Cleaned query text
        """
        # Remove common command words
        command_words = ['joue', 'lance', 'mets', 'play', 'put', 'start']

        words = query.lower().split()
        cleaned_words = [w for w in words if w not in command_words]

        return ' '.join(cleaned_words).strip()

    @staticmethod
    def extract_artist_title(query: str) -> Tuple[str, str]:
        """
        Try to extract artist and title from query.

        Args:
            query: Query text

        Returns:
            (artist, title) tuple
        """
        # Look for patterns like "title by artist" or "artist - title"
        query = query.lower()

        # Pattern: "title by/par artist"
        for separator in [' by ', ' par ', ' de ']:
            if separator in query:
                parts = query.split(separator, 1)
                return parts[1].strip(), parts[0].strip()  # (artist, title)

        # Pattern: "artist - title"
        if ' - ' in query:
            parts = query.split(' - ', 1)
            return parts[0].strip(), parts[1].strip()  # (artist, title)

        # Default: treat whole query as title
        return "", query.strip()


if __name__ == "__main__":
    # Test semantic search
    logging.basicConfig(level=logging.INFO)

    from music_library import Track

    # Create dummy tracks
    tracks = [
        Track("song1.mp3", "Let It Be", "The Beatles", "Let It Be", 243, 76),
        Track("song2.mp3", "Yesterday", "The Beatles", "Help!", 125, 94),
        Track("song3.mp3", "Bohemian Rhapsody", "Queen", "A Night at the Opera", 354, 72),
        Track("song4.mp3", "We Will Rock You", "Queen", "News of the World", 122, 81),
    ]

    # Build search engine
    engine = SemanticSearchEngine()
    engine.build_index(tracks)

    # Test searches
    queries = [
        "let it be",
        "Beatles",
        "Queen rock song",
        "yesterday beatles",
    ]

    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        results = engine.search(query, top_k=2)
        for i, (track, score) in enumerate(results, 1):
            print(f"  {i}. {track.artist} - {track.title} (score: {score:.3f})")
