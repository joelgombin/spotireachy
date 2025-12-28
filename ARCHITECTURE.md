# Architecture de Spotireachy

Documentation technique de l'architecture du système.

## Vue d'ensemble

Spotireachy est une application modulaire composée de plusieurs systèmes interconnectés :

```
┌─────────────────────────────────────────────────────────┐
│                    Main Application                      │
│                     (main.py)                            │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┼───────┬─────────┬──────────┬─────────┐
       │       │       │         │          │         │
   ┌───▼──┐ ┌─▼────┐ ┌▼─────┐ ┌─▼───────┐ ┌▼──────┐ ┌▼──────┐
   │Voice │ │Search│ │Music │ │  Audio  │ │ TTS   │ │ Dance │
   │ Rec  │ │Engine│ │ Lib  │ │ Player  │ │Engine │ │ Ctrl  │
   └──────┘ └──────┘ └──────┘ └─────────┘ └───────┘ └───────┘
```

## Modules

### 1. Voice Recognition (`voice_recognition.py`)

**Responsabilité** : Capture et transcription de la parole

**Technologies** :
- `faster-whisper` : Modèle de reconnaissance vocale locale
- `sounddevice` : Capture audio depuis le microphone

**API principale** :
```python
recognizer = VoiceRecognizer(model_size="base", language="fr")
text = recognizer.listen_and_transcribe(duration=5)
```

**Performances** :
- Modèle "tiny" : ~1s de latence
- Modèle "base" : ~2-3s de latence
- Modèle "small" : ~4-5s de latence

### 2. Music Library (`music_library.py`)

**Responsabilité** : Gestion et indexation de la bibliothèque musicale

**Technologies** :
- `mutagen` : Extraction des métadonnées (ID3, etc.)
- `librosa` : Analyse audio et extraction BPM

**API principale** :
```python
library = MusicLibrary("./music")
tracks = library.scan_library(extract_bpm=True)
library.save_to_cache("data/metadata.json")
```

**Format Track** :
```python
@dataclass
class Track:
    file_path: str
    title: str
    artist: str
    album: str
    duration: float
    bpm: float
    genre: Optional[str]
    year: Optional[int]
```

### 3. Semantic Search (`semantic_search.py`)

**Responsabilité** : Recherche sémantique de chansons

**Technologies** :
- `sentence-transformers` : Génération d'embeddings multilingues
- `FAISS` : Index de recherche par similarité vectorielle

**Pipeline** :
1. Texte → Embeddings (384 dimensions)
2. Recherche FAISS (similarité cosinus)
3. Ranking par score

**API principale** :
```python
engine = SemanticSearchEngine()
engine.build_index(tracks)
results = engine.search("let it be", top_k=3)
# Returns: [(Track, score), ...]
```

**Avantages** :
- Recherche floue : "let it be" trouve "Let It Be"
- Multilingue : fonctionne en français et anglais
- Sémantique : "chanson triste beatles" trouve "Yesterday"

### 4. Audio Player (`audio_player.py`)

**Responsabilité** : Lecture de fichiers audio

**Technologies** :
- `pygame.mixer` : Playback audio

**Features** :
- Playback asynchrone dans un thread
- Callback `on_finish`
- Contrôle volume
- Pause/Resume

**API principale** :
```python
player = AudioPlayer(volume=0.8)
player.play(track, on_finish=callback)
player.stop()
```

### 5. TTS Engine (`tts_engine.py`)

**Responsabilité** : Synthèse vocale pour feedback

**Technologies** :
- `pyttsx3` : TTS local (fallback)
- Reachy speaker : TTS natif si disponible

**API principale** :
```python
tts = ReachyTTS(reachy_speaker=reachy.speaker)
tts.confirm_track(artist, title)
tts.ask_confirmation(artist, title)
```

### 6. Dance Controller (`dance_controller.py`)

**Responsabilité** : Synchronisation danse/musique

**Technologies** :
- `reachy-mini` SDK : Contrôle moteurs
- BPM matching : Sélection chorégraphie

**Features** :
- Dance simple : Mouvements de tête synchronisés au BPM
- Support chorégraphies JSON (reachy_mini_dances_library)
- Thread asynchrone pour non-blocage

**API principale** :
```python
controller = DanceController(reachy_mini=reachy)
controller.dance_to_track(bpm=120, duration=180)
controller.stop_dancing()
```

## Flux de données

### Indexation (offline)

```
Fichiers MP3/WAV
    │
    ├─→ mutagen ──→ Métadonnées (titre, artiste)
    │
    ├─→ librosa ──→ BPM
    │
    └─→ sentence-transformers ──→ Embeddings
                                      │
                                      ├─→ metadata.json
                                      ├─→ embeddings.npy
                                      └─→ faiss.index
```

### Runtime (online)

```
Microphone
    │
    ├─→ Whisper ──→ "let it be"
            │
            ├─→ QueryProcessor ──→ "let it be" (cleaned)
                    │
                    ├─→ SemanticSearch ──→ [(Track, score), ...]
                            │
                            ├─→ Best Track
                                    │
                                    ├─→ TTS ──→ "Voulez-vous écouter..."
                                    │
                                    ├─→ Microphone ──→ Confirmation
                                            │
                                            ├─→ AudioPlayer ──→ 🎵
                                            │
                                            └─→ DanceController ──→ 💃
```

## Configuration

Le fichier `config.yaml` contrôle tous les paramètres :

```yaml
whisper:
  model: "base"        # Précision vs vitesse
  language: "fr"       # Langue

search:
  top_k: 3             # Nombre de candidats
  confidence_threshold: 0.6  # Seuil minimum

dance:
  enable_dance: true
  bpm_tolerance: 10    # ±10 BPM pour matching
```

## Caching et Performance

### Stratégie de cache

1. **Métadonnées** : `data/metadata.json`
   - Contenu : Tous les Track objects
   - Invalidation : Manuelle (réindexation)

2. **Embeddings** : `data/embeddings.npy`
   - Contenu : Vecteurs numpy (N × 384)
   - Invalidation : Manuelle

3. **Index FAISS** : `data/faiss.index`
   - Contenu : Structure de recherche optimisée
   - Invalidation : Manuelle

### Performance

Pour une bibliothèque de 1000 chansons :

- **Indexation** : ~10-15 minutes (one-time)
- **Recherche** : <50ms
- **Reconnaissance vocale** : 2-3s (modèle base)
- **Latence totale** : ~3-4s du voice input au playback

## Extensibilité

### Ajouter un nouveau fournisseur de musique

1. Implémenter interface `MusicProvider`
2. Retourner des objets `Track`
3. Intégrer dans `main.py`

### Ajouter de nouvelles chorégraphies

1. Créer JSON selon format `reachy_mini_dances_library`
2. Placer dans `choreography_path`
3. Ajuster `bpm_tolerance` si nécessaire

### Changer le moteur TTS

Modifier `ReachyTTS.__init__()` pour utiliser un autre backend (gTTS, Azure, etc.)

## Tests

Chaque module peut être testé indépendamment :

```bash
# Test reconnaissance vocale
python scripts/test_whisper.py

# Test microphone
python scripts/test_microphone.py

# Test module individuel
python src/music_library.py
python src/semantic_search.py
```

## Limites connues

1. **BPM extraction** : Peut être imprécis pour musique complexe
2. **Whisper latence** : 2-5s selon modèle
3. **Mémoire** : ~1GB pour modèle "base" + embeddings
4. **Reachy connection** : Fonctionne en simulation si non connecté

## Roadmap

- [ ] Support Spotify API (streaming)
- [ ] Amélioration matching chorégraphie/BPM
- [ ] Playlist support
- [ ] Web UI pour configuration
- [ ] Multi-room sync
