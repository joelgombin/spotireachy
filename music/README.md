# Dossier Music

Placez vos fichiers musicaux dans ce dossier.

## Formats supportés

- MP3 (`.mp3`)
- WAV (`.wav`)
- FLAC (`.flac`)
- M4A/AAC (`.m4a`)

## Organisation

Vous pouvez organiser vos fichiers comme vous voulez :

```
music/
├── Beatles/
│   ├── Let It Be.mp3
│   └── Yesterday.mp3
├── Queen/
│   ├── Bohemian Rhapsody.mp3
│   └── We Will Rock You.mp3
└── various.mp3
```

Ou simplement tout mettre à plat :

```
music/
├── song1.mp3
├── song2.mp3
└── song3.mp3
```

L'application scannera récursivement tous les sous-dossiers.

## Après avoir ajouté des chansons

N'oubliez pas de réindexer votre bibliothèque :

```bash
python src/index_library.py
```

Cela mettra à jour l'index de recherche avec vos nouvelles chansons.
