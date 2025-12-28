#!/usr/bin/env python3
"""
Test script to verify Whisper voice recognition is working.
"""

import sys
sys.path.insert(0, 'src')

from voice_recognition import VoiceRecognizer
import logging

logging.basicConfig(level=logging.INFO)

print("🎤 Whisper Voice Recognition Test")
print("=" * 50)

# Initialize with tiny model for quick testing
print("\n📥 Loading Whisper model (this may take a moment)...")
recognizer = VoiceRecognizer(model_size="tiny", language="fr")

print("\n✅ Whisper model loaded!")
print("\n🔴 Speak now (5 seconds)...")
print("   Try saying: 'Bonjour Reachy'")

try:
    text = recognizer.listen_and_transcribe()
    print(f"\n✅ Transcription: '{text}'")

    if text:
        print("\n🎉 Success! Voice recognition is working!")
    else:
        print("\n⚠️  Warning: No speech detected")
        print("   Make sure your microphone is working")

except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
