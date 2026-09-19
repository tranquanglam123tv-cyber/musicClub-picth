"""
F0 Extraction Experiment Scripts
===============================

Các script thử nghiệm để test F0 extraction với librosa.
Chạy trong môi trường: .venv/Scripts/python.exe

Usage:
    .venv\Scripts\python.exe test_f0_extraction.py
"""

import numpy as np
import librosa
import soundfile as sf
import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS - Audio Specifications
# ═══════════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def hz_to_midi(hz: float) -> float:
    """Convert Hz to MIDI note number
    
    Formula: MIDI = 12 × log₂(f/440) + 69
    """
    if hz <= 0:
        return 0
    return 12 * np.log2(hz / A4_HZ) + A4_MIDI


def midi_to_hz(midi: float) -> float:
    """Convert MIDI note number to Hz
    
    Formula: f = 440 × 2^((midi-69)/12)
    """
    return A4_HZ * np.power(2, (midi - A4_MIDI) / 12)


def midi_to_note_name(midi: float) -> str:
    """Convert MIDI number to note name
    
    Example: 60 -> "C4", 69 -> "A4"
    """
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    midi = int(round(midi))
    octave = (midi // 12) - 1
    note = note_names[midi % 12]
    return f"{note}{octave}"


def calculate_semitones(f1: float, f2: float) -> float:
    """Calculate distance in semitones between two frequencies
    
    Formula: semitones = 12 × log₂(f2/f1)
    """
    if f1 <= 0 or f2 <= 0:
        return 0
    return 12 * np.log2(f2 / f1)


# ═══════════════════════════════════════════════════════════════════
# F0 EXTRACTION
# ═══════════════════════════════════════════════════════════════════

def extract_f0_librosa(audio_path: str) -> dict:
    """
    Extract F0 from audio file using librosa.
    
    Returns dict with:
    - f0_times: Time stamps for each frame
    - f0_hz: Array of F0 values in Hz
    - voiced_flag: Boolean array for voiced/unvoiced
    - voiced_probs: Probability of being voiced
    """
    print(f"\n📂 Loading audio: {audio_path}")
    
    # Load audio
    y, sr = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)
    
    print(f"✅ Audio loaded:")
    print(f"   - Sample rate: {sr} Hz")
    print(f"   - Duration: {len(y)/sr:.2f} seconds")
    print(f"   - Samples: {len(y)}")
    
    # Check if mono, convert if needed
    if y.ndim > 1:
        y = librosa.to_mono(y)
        print(f"   - Converted to mono")
    
    # Extract F0 using pYIN (Probabilistic YIN)
    print(f"\n🔍 Extracting F0 with pYIN...")
    print(f"   - Frame length: {FRAME_LENGTH}")
    print(f"   - Hop length: {HOP_LENGTH}")
    print(f"   - Fmin: {F_MIN} Hz")
    print(f"   - Fmax: {F_MAX} Hz")
    
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=F_MIN,
        fmax=F_MAX,
        sr=sr,
        frame_length=FRAME_LENGTH,
        hop_length=HOP_LENGTH,
    )
    
    # Generate time stamps
    f0_times = librosa.times_like(f0, sr=sr, hop_length=HOP_LENGTH)
    
    print(f"✅ F0 extracted:")
    print(f"   - Frames: {len(f0)}")
    print(f"   - Voiced frames: {np.sum(voiced_flag)}/{len(f0)}")
    
    return {
        'f0_times': f0_times,
        'f0_hz': f0,
        'voiced_flag': voiced_flag,
        'voiced_probs': voiced_probs,
        'sample_rate': sr,
        'audio': y
    }


def analyze_f0_results(f0_data: dict) -> dict:
    """
    Analyze F0 extraction results and calculate statistics.
    """
    f0_hz = f0_data['f0_hz']
    voiced_flag = f0_data['voiced_flag']
    
    # Filter voiced frames only
    voiced_f0 = f0_hz[voiced_flag]
    voiced_f0 = voiced_f0[~np.isnan(voiced_f0)]
    
    if len(voiced_f0) == 0:
        print("⚠️ No voiced frames detected!")
        return {
            'error': 'No voiced frames detected',
            'min_f0': 0,
            'max_f0': 0,
            'avg_f0': 0,
            'median_f0': 0
        }
    
    # Calculate statistics
    min_f0 = np.min(voiced_f0)
    max_f0 = np.max(voiced_f0)
    avg_f0 = np.mean(voiced_f0)
    median_f0 = np.median(voiced_f0)
    std_f0 = np.std(voiced_f0)
    
    # Convert to MIDI
    min_midi = hz_to_midi(min_f0)
    max_midi = hz_to_midi(max_f0)
    avg_midi = hz_to_midi(avg_f0)
    median_midi = hz_to_midi(median_f0)
    
    # Calculate vocal range in semitones
    range_semitones = calculate_semitones(min_f0, max_f0)
    
    # Voiced ratio
    voiced_ratio = np.sum(voiced_flag) / len(voiced_flag)
    
    # Calculate note distribution
    note_distribution = calculate_note_distribution(voiced_f0)
    
    results = {
        # F0 in Hz
        'min_f0': round(min_f0, 2),
        'max_f0': round(max_f0, 2),
        'avg_f0': round(avg_f0, 2),
        'median_f0': round(median_f0, 2),
        'std_f0': round(std_f0, 2),
        
        # MIDI
        'min_midi': round(min_midi, 2),
        'max_midi': round(max_midi, 2),
        'avg_midi': round(avg_midi, 2),
        'median_midi': round(median_midi, 2),
        
        # Display
        'min_note': midi_to_note_name(min_midi),
        'max_note': midi_to_note_name(max_midi),
        'avg_note': midi_to_note_name(avg_midi),
        
        # Range
        'range_semitones': round(range_semitones, 2),
        
        # Quality
        'voiced_ratio': round(voiced_ratio, 3),
        'voiced_frame_count': len(voiced_f0),
        'total_frames': len(f0_hz),
        
        # Note distribution
        'note_distribution': note_distribution
    }
    
    return results


def calculate_note_distribution(f0_hz: np.ndarray) -> dict:
    """
    Calculate distribution of notes sung.
    Returns count of each note.
    """
    note_counts = {}
    
    for f0 in f0_hz:
        if not np.isnan(f0) and f0 > 0:
            midi = hz_to_midi(f0)
            note_name = midi_to_note_name(midi)
            
            if note_name in note_counts:
                note_counts[note_name] += 1
            else:
                note_counts[note_name] = 1
    
    # Sort by count (descending)
    sorted_notes = dict(sorted(
        note_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ))
    
    return sorted_notes


def classify_voice_type(min_midi: float, max_midi: float) -> dict:
    """
    Classify voice type based on range.
    
    Voice type ranges (from roadmap):
    - Soprano: G3-C6 (55-84 MIDI)
    - Mezzo-Soprano: A3-A5 (57-81 MIDI)
    - Alto: F3-D5 (53-77 MIDI)
    - Tenor: C3-C5 (48-72 MIDI)
    - Baritone: A2-A4 (45-69 MIDI)
    - Bass: E2-E4 (40-64 MIDI)
    """
    voice_ranges = {
        'SOPRANO': (55, 84),
        'MEZZO_SOPRANO': (57, 81),
        'ALTO': (53, 77),
        'TENOR': (48, 72),
        'BARITONE': (45, 69),
        'BASS': (40, 64)
    }
    
    # Calculate overlap with each voice type
    matches = []
    
    for voice_type, (type_min, type_max) in voice_ranges.items():
        # Calculate overlap
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
    
    # Sort by overlap
    matches.sort(key=lambda x: x['overlap_percent'], reverse=True)
    
    if matches:
        return {
            'primary_type': matches[0]['voice_type'],
            'confidence': matches[0]['overlap_percent'] / 100,
            'alternatives': matches[1:3] if len(matches) > 1 else []
        }
    
    return {
        'primary_type': 'UNKNOWN',
        'confidence': 0,
        'alternatives': []
    }


# ═══════════════════════════════════════════════════════════════════
# MAIN ANALYSIS FUNCTION
# ═══════════════════════════════════════════════════════════════════

def analyze_voice(audio_path: str) -> dict:
    """
    Complete voice analysis pipeline.
    """
    print("=" * 60)
    print("🎤 VOICE ANALYSIS PIPELINE")
    print("=" * 60)
    
    # Step 1: Extract F0
    f0_data = extract_f0_librosa(audio_path)
    
    # Step 2: Analyze results
    print("\n📊 Analyzing F0 results...")
    results = analyze_f0_results(f0_data)
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return results
    
    # Step 3: Classify voice type
    print("\n🎭 Classifying voice type...")
    voice_type = classify_voice_type(
        results['min_midi'],
        results['max_midi']
    )
    results['voice_type'] = voice_type['primary_type']
    results['voice_type_confidence'] = voice_type['confidence']
    
    # Step 4: Print summary
    print_summary(results)
    
    return results


def print_summary(results: dict):
    """Print analysis summary"""
    print("\n" + "=" * 60)
    print("📋 ANALYSIS SUMMARY")
    print("=" * 60)
    
    print(f"\n🎵 F0 Statistics:")
    print(f"   Min F0: {results['min_f0']} Hz ({results['min_note']})")
    print(f"   Max F0: {results['max_f0']} Hz ({results['max_note']})")
    print(f"   Avg F0: {results['avg_f0']} Hz ({results['avg_note']})")
    print(f"   Median F0: {results['median_f0']} Hz")
    print(f"   Std F0: {results['std_f0']} Hz")
    
    print(f"\n🎹 MIDI Values:")
    print(f"   Min MIDI: {results['min_midi']:.1f}")
    print(f"   Max MIDI: {results['max_midi']:.1f}")
    print(f"   Range: {results['range_semitones']:.1f} semitones")
    
    print(f"\n🎭 Voice Type: {results['voice_type']}")
    print(f"   Confidence: {results['voice_type_confidence']:.1%}")
    
    print(f"\n📊 Quality Metrics:")
    print(f"   Voiced Ratio: {results['voiced_ratio']:.1%}")
    print(f"   Voiced Frames: {results['voiced_frame_count']}/{results['total_frames']}")
    
    print(f"\n🎼 Note Distribution (Top 10):")
    notes = list(results['note_distribution'].items())[:10]
    for note, count in notes:
        bar = '█' * min(count, 50)
        print(f"   {note:4s}: {bar} ({count})")
    
    print("\n" + "=" * 60)


# ═══════════════════════════════════════════════════════════════════
# TEST WITH SYNTHETIC AUDIO
# ═══════════════════════════════════════════════════════════════════

def create_test_tone(frequency: float, duration: float = 3.0) -> np.ndarray:
    """Create a pure sine wave test tone"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    audio = np.sin(2 * np.pi * frequency * t)
    return audio.astype(np.float32)


def create_vocal_test_audio() -> np.ndarray:
    """
    Create synthetic vocal-like audio for testing.
    Simulates a voice singing a scale from C3 to C5.
    """
    print("🎼 Creating synthetic vocal test audio...")
    
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
    
    # Concatenate all segments
    audio = np.concatenate(audio_segments)
    
    # Add some vibrato (slight pitch variation)
    t = np.linspace(0, len(audio)/SAMPLE_RATE, len(audio))
    vibrato = 1 + 0.02 * np.sin(2 * np.pi * 5 * t)  # 5 Hz vibrato
    audio = audio * vibrato
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    print(f"✅ Created test audio: {len(audio)/SAMPLE_RATE:.2f}s")
    
    return audio


def run_synthetic_test():
    """Run F0 extraction on synthetic audio"""
    print("\n" + "=" * 60)
    print("🧪 SYNTHETIC AUDIO TEST")
    print("=" * 60)
    
    # Create test audio (singing C4-C5)
    audio = create_vocal_test_audio()
    
    # Save to temp file
    test_file = "test_vocal.wav"
    sf.write(test_file, audio, SAMPLE_RATE)
    print(f"💾 Saved to: {test_file}")
    
    # Analyze
    results = analyze_voice(test_file)
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    return results


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    print("\n🎤 F0 Extraction Test Suite")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Analyze provided file
        audio_path = sys.argv[1]
        if os.path.exists(audio_path):
            results = analyze_voice(audio_path)
        else:
            print(f"❌ File not found: {audio_path}")
            sys.exit(1)
    else:
        # Run synthetic test
        print("\nNo audio file provided. Running synthetic test...")
        print("Usage: python test_f0_extraction.py <audio_file.wav>")
        print()
        
        results = run_synthetic_test()
        
        print("\n✅ Synthetic test complete!")
        print("\nNext steps:")
        print("1. Record your voice singing for 10-60 seconds")
        print("2. Save as WAV file")
        print("3. Run: python test_f0_extraction.py your_voice.wav")
