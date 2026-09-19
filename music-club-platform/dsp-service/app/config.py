"""
DSP Configuration
=================
"""

class DSPConfig:
    """DSP Configuration settings."""
    
    # Audio preprocessing
    REQUIRED_SAMPLE_RATE = 44100
    REQUIRED_CHANNELS = 1
    MIN_DURATION = 10  # seconds
    MAX_DURATION = 60  # seconds
    MAX_FILE_SIZE_MB = 10
    
    # F0 extraction (pYIN)
    SAMPLE_RATE = 44100
    FRAME_LENGTH = 2048
    HOP_LENGTH = 512
    F_MIN = 50.0   # Hz - below Bass E2 (82 Hz)
    F_MAX = 1000.0  # Hz - above Soprano C6 (1047 Hz)
    
    # Quality thresholds
    MIN_VOICED_RATIO = 0.30
    MIN_CONFIDENCE = 0.40
    MIN_RANGE_SEMITONES = 6
    
    # Voice type ranges (MIDI)
    VOICE_RANGES = {
        'SOPRANO': (55, 84),
        'MEZZO_SOPRANO': (57, 81),
        'ALTO': (53, 77),
        'TENOR': (48, 72),
        'BARITONE': (45, 69),
        'BASS': (40, 64)
    }
