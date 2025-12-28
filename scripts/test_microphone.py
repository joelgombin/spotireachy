#!/usr/bin/env python3
"""
Test script to verify microphone is working.
"""

import sys
import sounddevice as sd
import numpy as np

print("🎤 Microphone Test")
print("=" * 50)

# List available devices
print("\n📋 Available audio devices:")
print(sd.query_devices())

# Test recording
print("\n🔴 Recording 3 seconds...")
duration = 3
sample_rate = 16000

try:
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.float32
    )
    sd.wait()

    # Check if we got audio
    max_amplitude = np.max(np.abs(audio))
    print(f"\n✅ Recording complete!")
    print(f"   Max amplitude: {max_amplitude:.4f}")

    if max_amplitude < 0.001:
        print("\n⚠️  Warning: Very low amplitude detected")
        print("   Make sure your microphone is not muted")
    else:
        print("\n✅ Microphone is working!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
