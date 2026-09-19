"""
F0 Extraction Experiment Scripts
===============================

Các script thu nghiem de test F0 extraction voi librosa.
Chay trong moi truong: .venv/Scripts/python.exe
"""

import numpy as np
import librosa
import soundfile as sf
import os
from pathlib import Path

# Constants - Audio Specifications
SAMPLE_RATE = 44100
DURATION_SECONDS = 30
F_MIN = 50   # Hz - below lowest voice (Bass E2 = 82 Hz)
F_MAX = 500  # Hz - above highest voice (Soprano C6 = 1046 Hz)

# pYIN parameters
FRAME_LENGTH = 2048
HOP_LENGTH = 512

# MIDI reference
A4_HZ = 440.0
A4_MIDI = 69

def hz_to_midi(hz: float) -> float:
    if hz <= 0:
        return 0
    return 12 * np.log2(hz / A4_HZ) + A4_MIDI

def midi_to_hz(midi: float) -> float:
    return A4_HZ * np.power(2, (midi - A4_MIDI) / 12)

def midi_to_note_name(midi: float) -> str:
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    midi = int(round(midi))
    octave = (midi // 12) - 1
    note = note_names[midi % 12]
    return f"{note}{octave}"

def calculate_semitones(f1: float, f2: float) -> float:
    if f1 <= 0 or f2 <= 0:
        return 0
    return 12 * np.log2(f2 / f1)

def create_test_tone(frequency: float, duration: float = 3.0) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    audio = np.sin(2 * np.pi * frequency * t)
    return audio.astype(np.float32)

def create_vocal_test_audio() -> np.ndarray:
    print("[*] Creating synthetic vocal test audio...")
    
    # Notes from C4 to C5 (soprano range)
    notes = [
        (261.63, 0.5),   # C4
        (293.66, 0.5),   # D4
        (329.63, 0.5),   # E4
        (349.23, 0.5),   # F4
        (392.00, 0.5),   # G4
        (440.00, 0.5),   # A4
        (493.88, 0.5),   # B4
        (523.25, 1.0),   # C5
    ]
    
    audio_segments = []
    
    for freq, dur in notes:
        segment = create_test_tone(freq, dur)
        audio_segments.append(segment)
    
    audio = np.concatenate(audio_segments)
    
    # Add vibrato
    t = np.linspace(0, len(audio)/SAMPLE_RATE, len(audio))
    vibrato = 1 + 0.02 * np.sin(2 * np.pi * 5 * t)
    audio = audio * vibrato
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    print(f"[+] Created test audio: {len(audio)/SAMPLE_RATE:.2f}s")
    
    return audio

def extract_f0_with_librosa(audio) -> dict:
    print(f"[*] Loading audio: {len(audio)/SAMPLE_RATE:.2f}s at {SAMPLE_RATE}Hz")
    print(f"[*] Extracting F0 with pYIN...")
    print(f"    - Frame length: {FRAME_LENGTH}")
    print(f"    - Hop length: {HOP_LENGTH}")
    print(f"    - Fmin: {F_MIN} Hz")
    print(f"    - Fmax: {F_MAX} Hz")
    
    f0, voiced_flag, voiced_probs = librosa.pyin(
        audio,
        fmin=F_MIN,
        fmax=F_MAX,
        sr=SAMPLE_RATE,
        frame_length=FRAME_LENGTH,
        hop_length=HOP_LENGTH,
    )
    
    f0_times = librosa.times_like(f0, sr=SAMPLE_RATE, hop_length=HOP_LENGTH)
    
    print(f"[+] F0 extracted: {len(f0)} frames")
    print(f"    - Voiced frames: {np.sum(voiced_flag)}/{len(f0)}")
    
    return {
        'f0_times': f0_times,
        'f0_hz': f0,
        'voiced_flag': voiced_flag,
        'voiced_probs': voiced_probs
    }

def analyze_results(f0_data: dict) -> dict:
    f0_hz = f0_data['f0_hz']
    voiced_flag = f0_data['voiced_flag']
    
    voiced_f0 = f0_hz[voiced_flag]
    voiced_f0 = voiced_f0[~np.isnan(voiced_f0)]
    
    if len(voiced_f0) == 0:
        print("[!] No voiced frames detected!")
        return {'error': 'No voiced frames'}
    
    min_f0 = np.min(voiced_f0)
    max_f0 = np.max(voiced_f0)
    avg_f0 = np.mean(voiced_f0)
    median_f0 = np.median(voiced_f0)
    std_f0 = np.std(voiced_f0)
    
    min_midi = hz_to_midi(min_f0)
    max_midi = hz_to_midi(max_f0)
    
    range_semitones = calculate_semitones(min_f0, max_f0)
    voiced_ratio = np.sum(voiced_flag) / len(voiced_flag)
    
    # Voice type classification
    voice_type = classify_voice_type(min_midi, max_midi)
    
    results = {
        'min_f0': round(min_f0, 2),
        'max_f0': round(max_f0, 2),
        'avg_f0': round(avg_f0, 2),
        'median_f0': round(median_f0, 2),
        'std_f0': round(std_f0, 2),
        'min_midi': round(min_midi, 2),
        'max_midi': round(max_midi, 2),
        'min_note': midi_to_note_name(min_midi),
        'max_note': midi_to_note_name(max_midi),
        'range_semitones': round(range_semitones, 2),
        'voiced_ratio': round(voiced_ratio, 3),
        'voice_type': voice_type['primary_type'],
        'voice_type_confidence': voice_type['confidence']
    }
    
    return results

def classify_voice_type(min_midi: float, max_midi: float) -> dict:
    voice_ranges = {
        'SOPRANO': (55, 84),
        'MEZZO_SOPRANO': (57, 81),
        'ALTO': (53, 77),
        'TENOR': (48, 72),
        'BARITONE': (45, 69),
        'BASS': (40, 64)
    }
    
    matches = []
    
    for voice_type, (type_min, type_max) in voice_ranges.items():
        overlap_min = max(min_midi, type_min)
        overlap_max = min(max_midi, type_max)
        
        if overlap_min <= overlap_max:
            overlap = overlap_max - overlap_min + 1
            type_range = type_max - type_min + 1
            overlap_percent = (overlap / type_range) * 100
            matches.append({
                'voice_type': voice_type,
                'overlap_percent': round(overlap_percent, 1)
            })
    
    matches.sort(key=lambda x: x['overlap_percent'], reverse=True)
    
    if matches:
        return {
            'primary_type': matches[0]['voice_type'],
            'confidence': matches[0]['overlap_percent'] / 100
        }
    
    return {'primary_type': 'UNKNOWN', 'confidence': 0}

def run_test():
    print("\n" + "=" * 60)
    print("VOICE ANALYSIS PIPELINE TEST")
    print("=" * 60)
    
    # Create test audio
    audio = create_vocal_test_audio()
    
    # Extract F0
    f0_data = extract_f0_with_librosa(audio)
    
    # Analyze
    print("\n[*] Analyzing results...")
    results = analyze_results(f0_data)
    
    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    
    print(f"\nF0 Statistics:")
    print(f"   Min F0: {results['min_f0']} Hz ({results['min_note']})")
    print(f"   Max F0: {results['max_f0']} Hz ({results['max_note']})")
    print(f"   Avg F0: {results['avg_f0']} Hz")
    print(f"   Std F0: {results['std_f0']} Hz")
    
    print(f"\nVocal Range:")
    print(f"   Min MIDI: {results['min_midi']:.1f}")
    print(f"   Max MIDI: {results['max_midi']:.1f}")
    print(f"   Range: {results['range_semitones']:.1f} semitones")
    
    print(f"\nVoice Type: {results['voice_type']}")
    print(f"   Confidence: {results['voice_type_confidence']:.1%}")
    
    print(f"\nQuality:")
    print(f"   Voiced Ratio: {results['voiced_ratio']:.1%}")
    
    print("\n" + "=" * 60)
    
    return results

if __name__ == "__main__":
    results = run_test()
    print("\n[OK] Test complete!")
