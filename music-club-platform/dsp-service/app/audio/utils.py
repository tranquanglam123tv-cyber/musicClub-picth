"""
Audio Utilities
===============
"""

import numpy as np

# Note names for display
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def hz_to_midi(hz: float) -> float:
    """
    Convert Hz to MIDI note number.
    
    Formula: MIDI = 12 × log₂(f/440) + 69
    """
    if hz <= 0:
        return 0
    return 12 * np.log2(hz / 440.0) + 69


def midi_to_hz(midi: float) -> float:
    """
    Convert MIDI note number to Hz.
    
    Formula: f = 440 × 2^((midi-69)/12)
    """
    return 440.0 * np.power(2, (midi - 69) / 12)


def midi_to_note_name(midi: float) -> str:
    """
    Convert MIDI number to note name.
    
    Example: 60 → "C4", 69 → "A4"
    """
    midi = int(round(midi))
    octave = (midi // 12) - 1
    note = NOTE_NAMES[midi % 12]
    return f"{note}{octave}"


def hz_to_note_name(hz: float) -> str:
    """Convert Hz directly to note name."""
    midi = hz_to_midi(hz)
    return midi_to_note_name(midi)


def calculate_semitones(f1: float, f2: float) -> float:
    """
    Calculate distance in semitones between two frequencies.
    
    Formula: semitones = 12 × log₂(f2/f1)
    """
    if f1 <= 0 or f2 <= 0:
        return 0
    return 12 * np.log2(f2 / f1)


def frequency_to_cents(f: float, ref: float = 440.0) -> float:
    """
    Convert frequency to cents relative to reference.
    
    100 cents = 1 semitone
    1200 cents = 1 octave
    """
    if f <= 0 or ref <= 0:
        return 0
    return 1200 * np.log2(f / ref)
