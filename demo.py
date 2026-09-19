#!/usr/bin/env python3
"""
Music Club Platform - Demo Script
Usage: python demo.py
"""

import sys
import os

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_step(step, text):
    print(f"\n[Step {step}] {text}")

def demo_part1():
    """Demo Part 1: Module Tests"""
    print_header("PART 1: MODULE TESTS")
    
    sys.path.insert(0, 'music-club-platform/dsp-service')
    
    # Test 1: Imports
    print_step(1, "Testing imports...")
    from app.audio.f0_extractor import F0Extractor, F0Config
    from app.audio.preprocessor import AudioPreprocessor
    from app.audio.utils import hz_to_midi, midi_to_note_name
    print("  OK: All imports successful!")
    
    # Test 2: Utilities
    print_step(2, "Testing MIDI utilities...")
    print(f"  A4 (440 Hz) -> MIDI: {hz_to_midi(440):.0f}")
    print(f"  MIDI 60 (C4) -> Note: {midi_to_note_name(60)}")
    print(f"  MIDI 69 (A4) -> Note: {midi_to_note_name(69)}")
    print(f"  MIDI 72 (C5) -> Note: {midi_to_note_name(72)}")
    print("  OK: MIDI conversion working!")
    
    # Test 3: Audio Preprocessing
    print_step(3, "Testing audio preprocessing...")
    import numpy as np
    import soundfile as sf
    
    sr = 44100
    duration = 10.0
    t = np.linspace(0, duration, int(sr * duration))
    
    # Create test signal (TENOR voice simulation)
    f0_freq = 220  # A3
    audio = np.sin(2 * np.pi * f0_freq * t) * 0.8
    audio += np.sin(2 * np.pi * f0_freq * 2 * t) * 0.4
    audio += np.sin(2 * np.pi * f0_freq * 3 * t) * 0.2
    
    sf.write('test_voice.wav', audio, sr)
    print(f"  OK: Created test audio ({duration}s)")
    
    preprocessor = AudioPreprocessor()
    audio_data = preprocessor.preprocess('test_voice.wav')
    print(f"  OK: Audio preprocessed ({len(audio_data)/sr:.2f}s)")
    
    # Test 4: F0 Extraction
    print_step(4, "Testing F0 extraction (pYIN algorithm)...")
    config = F0Config(
        sample_rate=44100,
        frame_length=2048,
        hop_length=512,
        fmin=50.0,
        fmax=1000.0
    )
    extractor = F0Extractor(config)
    result = extractor.extract(audio_data)
    
    print(f"  Voice Type: {result.voice_type}")
    print(f"  Confidence: {result.confidence:.1%}")
    print(f"  Min F0: {result.min_f0:.1f} Hz")
    print(f"  Max F0: {result.max_f0:.1f} Hz")
    print(f"  Avg F0: {result.avg_f0:.1f} Hz")
    print(f"  Range: {result.range_semitones:.1f} semitones")
    print("  OK: F0 extraction complete!")
    
    # Cleanup
    os.remove('test_voice.wav')
    
    return result

def demo_part2():
    """Demo Part 2: Voice Types"""
    print_header("PART 2: VOICE TYPE DETECTION")
    
    sys.path.insert(0, 'music-club-platform/dsp-service')
    from app.audio.f0_extractor import F0Extractor, F0Config
    import numpy as np
    import soundfile as sf
    
    sr = 44100
    duration = 5.0
    
    # Test different voice types
    voice_tests = [
        ('BASS', 82, 'E2'),
        ('BARITONE', 110, 'A2'),
        ('TENOR', 196, 'G3'),
        ('ALTO', 262, 'C4'),
        ('MEZZO_SOPRANO', 330, 'E4'),
        ('SOPRANO', 523, 'C5'),
    ]
    
    print("\nTesting different voice types:")
    print("-" * 50)
    print(f"{'Voice Type':<20} {'Frequency':<15} {'Note'}")
    print("-" * 50)
    
    for voice_type, freq, note in voice_tests:
        # Create test signal
        t = np.linspace(0, duration, int(sr * duration))
        audio = np.sin(2 * np.pi * freq * t) * 0.8
        audio += np.sin(2 * np.pi * freq * 2 * t) * 0.4
        
        sf.write(f'test_{voice_type.lower()}.wav', audio, sr)
        
        preprocessor_path = f'test_{voice_type.lower()}.wav'
        
        # Extract F0
        import librosa
        audio_data, _ = librosa.load(preprocessor_path, sr=sr)
        config = F0Config()
        extractor = F0Extractor(config)
        result = extractor.extract(audio_data)
        
        print(f"{voice_type:<20} {freq:<15} {note}")
        
        os.remove(preprocessor_path)
    
    print("-" * 50)

def demo_part3():
    """Demo Part 3: Server Info"""
    print_header("PART 3: FASTAPI SERVER")
    
    print("\nTo start the FastAPI server:")
    print("  cd music-club-platform/dsp-service")
    print("  .venv\\Scripts\\activate  (Windows)")
    print("  source .venv/bin/activate  (Mac/Linux)")
    print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    print("\nEndpoints:")
    print("  GET  /              - Root info")
    print("  GET  /docs          - Swagger UI")
    print("  GET  /api/v1/health - Health check")
    print("  POST /api/v1/voice/analyze - Analyze voice")

def demo_part4():
    """Demo Part 4: Database Info"""
    print_header("PART 4: DATABASE SCHEMA")
    
    print("\nTables created:")
    tables = [
        "users", "voice_types", "voice_profiles", "voice_analyses",
        "genres", "songs", "song_genres", "user_genres",
        "events", "event_registrations", "posts", "post_comments",
        "recommendation_logs", "system_settings", "audit_logs"
    ]
    
    for i, table in enumerate(tables, 1):
        print(f"  {i:2}. {table}")

def main():
    print("\n" + "=" * 60)
    print("  MUSIC CLUB PLATFORM - DEMONSTRATION")
    print("  Voice Analysis with F0 Detection")
    print("=" * 60)
    
    try:
        demo_part1()
        demo_part2()
        demo_part3()
        demo_part4()
        
        print("\n" + "=" * 60)
        print("  DEMO COMPLETE!")
        print("=" * 60)
        print("\nFor API testing, start the server and visit:")
        print("  http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
