# DSP Signal Processing Document

## Mục lục
1. [Tổng quan DSP](#1-tổng-quan-dsp)
2. [Audio Preprocessing](#2-audio-preprocessing)
3. [F0 Extraction Pipeline](#3-f0-extraction-pipeline)
4. [Post-Processing](#4-post-processing)
5. [Error Handling](#5-error-handling)
6. [Performance Optimization](#6-performance-optimization)

---

## 1. Tổng quan DSP

### 1.1 DSP Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DSP PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│  │    Audio     │ ──▶ │  Preprocess  │ ──▶ │  F0 Extract  │       │
│  │    Input     │     │              │     │   (pYIN)     │       │
│  │   (WAV)      │     │ • Normalize  │     │              │       │
│  │              │     │ • Resample   │     │ • Frame      │       │
│  │  44100 Hz    │     │ • To Mono    │     │ • Hop        │       │
│  │  16-bit      │     │ • Trim       │     │ • Extract    │       │
│  │  Mono        │     │              │     │              │       │
│  └──────────────┘     └──────────────┘     └──────────────┘       │
│                                                  │                  │
│                                                  ▼                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│  │   Results    │ ◀── │   Analyze   │ ◀── │  Post-Proc  │       │
│  │   (JSON)     │     │             │     │             │       │
│  │              │     │ • Stats     │     │ • Smooth    │       │
│  │ • min_f0     │     │ • Voice     │     │ • Filter    │       │
│  │ • max_f0     │     │   Type      │     │ • Validate  │       │
│  │ • voice_type │     │ • Quality   │     │             │       │
│  └──────────────┘     └──────────────┘     └──────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 DSP Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              FASTAPI DSP SERVICE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  POST /api/v1/voice/analyze                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                                                     │  │
│  │  Request:                                          │  │
│  │  {                                                  │  │
│  │    "audio": binary (WAV file)                     │  │
│  │  }                                                  │  │
│  │                                                     │  │
│  │  Response:                                          │  │
│  │  {                                                  │  │
│  │    "success": true,                               │  │
│  │    "data": {                                      │  │
│  │      "min_f0": 98.5,                             │  │
│  │      "max_f0": 392.0,                            │  │
│  │      "voice_type": "TENOR",                      │  │
│  │      "confidence": 0.85                          │  │
│  │    }                                              │  │
│  │  }                                                  │  │
│  │                                                     │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Audio Preprocessing

### 2.1 Preprocessing Steps

```python
# app/audio/preprocessor.py

import librosa
import numpy as np
import soundfile as sf

class AudioPreprocessor:
    """Audio preprocessing pipeline."""
    
    REQUIRED_SAMPLE_RATE = 44100
    REQUIRED_CHANNELS = 1
    MIN_DURATION = 10  # seconds
    MAX_DURATION = 60  # seconds
    MAX_FILE_SIZE_MB = 10
    
    def preprocess(self, audio_path: str) -> np.ndarray:
        """
        Preprocess audio file.
        
        Steps:
        1. Load audio
        2. Validate format
        3. Resample if needed
        4. Convert to mono
        5. Normalize
        6. Trim silence
        """
        # Load audio
        audio, sr = librosa.load(audio_path, sr=None, mono=False)
        
        # Validate sample rate
        if sr != self.REQUIRED_SAMPLE_RATE:
            audio = librosa.resample(
                audio,
                orig_sr=sr,
                target_sr=self.REQUIRED_SAMPLE_RATE
            )
            sr = self.REQUIRED_SAMPLE_RATE
        
        # Convert to mono
        if audio.ndim > 1:
            audio = librosa.to_mono(audio)
        
        # Normalize to [-1, 1]
        audio = audio / (np.max(np.abs(audio)) + 1e-10)
        
        # Trim silence from beginning and end
        audio, _ = librosa.effects.trim(audio, top_db=20)
        
        return audio
    
    def validate(self, audio_path: str) -> dict:
        """Validate audio file meets requirements."""
        errors = []
        warnings = []
        
        # Check file exists
        if not os.path.exists(audio_path):
            return {'valid': False, 'errors': ['File not found']}
        
        # Check file size
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            errors.append(f'File too large: {file_size_mb:.1f}MB (max {self.MAX_FILE_SIZE_MB}MB)')
        
        # Load and check properties
        try:
            info = sf.info(audio_path)
            
            if info.samplerate != self.REQUIRED_SAMPLE_RATE:
                warnings.append(f'Sample rate: {info.samplerate}Hz (will be resampled)')
            
            if info.channels != self.REQUIRED_CHANNELS:
                errors.append(f'Channels: {info.channels} (must be {self.REQUIRED_CHANNELS})')
            
            duration = info.duration
            if duration < self.MIN_DURATION:
                errors.append(f'Duration: {duration:.1f}s (min {self.MIN_DURATION}s)')
            elif duration > self.MAX_DURATION:
                warnings.append(f'Duration: {duration:.1f}s (max {self.MAX_DURATION}s)')
            
        except Exception as e:
            errors.append(f'Cannot read file: {str(e)}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
```

### 2.2 Normalization

```python
def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """
    Normalize audio to [-1, 1] range.
    
    Methods:
    - Peak normalization: divide by max absolute value
    - RMS normalization: normalize based on energy
    - LUFS normalization: broadcast standard (for streaming)
    """
    # Peak normalization (default)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak
    
    return audio


def check_clipping(audio: np.ndarray, threshold: float = 0.99) -> bool:
    """Check if audio is clipping."""
    return np.max(np.abs(audio)) >= threshold
```

### 2.3 Silence Trimming

```python
def trim_silence(
    audio: np.ndarray,
    top_db: int = 20,
    frame_length: int = 2048,
    hop_length: int = 512
) -> np.ndarray:
    """
    Trim silence from beginning and end of audio.
    
    Args:
        audio: Input audio signal
        top_db: Threshold in dB below reference
        frame_length: Frame length for analysis
        hop_length: Hop length for analysis
    
    Returns:
        Trimmed audio
    """
    trimmed, _ = librosa.effects.trim(
        audio,
        top_db=top_db,
        frame_length=frame_length,
        hop_length=hop_length
    )
    
    return trimmed
```

---

## 3. F0 Extraction Pipeline

### 3.1 F0 Extractor Class

```python
# app/audio/f0_extractor.py

import librosa
import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class F0Config:
    """F0 extraction configuration."""
    sample_rate: int = 44100
    frame_length: int = 2048
    hop_length: int = 512
    fmin: float = 50.0    # Hz - below Bass E2
    fmax: float = 1000.0  # Hz - above Soprano C6


@dataclass
class F0Result:
    """F0 extraction result."""
    # Time series
    f0_times: np.ndarray
    f0_hz: np.ndarray
    voiced_flag: np.ndarray
    voiced_probs: np.ndarray
    
    # Statistics
    min_f0: float
    max_f0: float
    avg_f0: float
    median_f0: float
    std_f0: float
    
    # MIDI
    min_midi: float
    max_midi: float
    
    # Range
    range_semitones: float
    
    # Quality
    voiced_ratio: float
    confidence: float
    
    # Voice type
    voice_type: str
    voice_type_confidence: float


class F0Extractor:
    """F0 Extractor using pYIN algorithm."""
    
    def __init__(self, config: Optional[F0Config] = None):
        self.config = config or F0Config()
    
    def extract(self, audio: np.ndarray) -> F0Result:
        """
        Extract F0 from audio signal.
        
        Args:
            audio: Audio signal (numpy array)
        
        Returns:
            F0Result with all analysis data
        """
        # Run pYIN
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=self.config.fmin,
            fmax=self.config.fmax,
            sr=self.config.sample_rate,
            frame_length=self.config.frame_length,
            hop_length=self.config.hop_length,
        )
        
        # Generate time stamps
        f0_times = librosa.times_like(
            f0,
            sr=self.config.sample_rate,
            hop_length=self.config.hop_length
        )
        
        # Calculate statistics
        stats = self._calculate_statistics(f0, voiced_flag, voiced_probs)
        
        # Classify voice type
        voice_type, voice_conf = self._classify_voice_type(
            stats['min_midi'],
            stats['max_midi']
        )
        
        return F0Result(
            f0_times=f0_times,
            f0_hz=f0,
            voiced_flag=voiced_flag,
            voiced_probs=voiced_probs,
            **stats,
            voice_type=voice_type,
            voice_type_confidence=voice_conf
        )
    
    def _calculate_statistics(
        self,
        f0: np.ndarray,
        voiced_flag: np.ndarray,
        voiced_probs: np.ndarray
    ) -> dict:
        """Calculate F0 statistics."""
        
        # Filter voiced frames only
        voiced_f0 = f0[voiced_flag]
        voiced_f0 = voiced_f0[~np.isnan(voiced_f0)]
        
        if len(voiced_f0) == 0:
            return {
                'min_f0': 0, 'max_f0': 0, 'avg_f0': 0,
                'median_f0': 0, 'std_f0': 0,
                'min_midi': 0, 'max_midi': 0,
                'range_semitones': 0,
                'voiced_ratio': 0, 'confidence': 0
            }
        
        # Calculate Hz statistics
        min_f0 = float(np.min(voiced_f0))
        max_f0 = float(np.max(voiced_f0))
        avg_f0 = float(np.mean(voiced_f0))
        median_f0 = float(np.median(voiced_f0))
        std_f0 = float(np.std(voiced_f0))
        
        # Calculate MIDI
        min_midi = self._hz_to_midi(min_f0)
        max_midi = self._hz_to_midi(max_f0)
        
        # Calculate range in semitones
        range_semitones = 12 * np.log2(max_f0 / min_f0)
        
        # Calculate quality metrics
        voiced_ratio = np.sum(voiced_flag) / len(voiced_flag)
        confidence = float(np.mean(voiced_probs[voiced_flag]))
        
        return {
            'min_f0': min_f0,
            'max_f0': max_f0,
            'avg_f0': avg_f0,
            'median_f0': median_f0,
            'std_f0': std_f0,
            'min_midi': min_midi,
            'max_midi': max_midi,
            'range_semitones': range_semitones,
            'voiced_ratio': voiced_ratio,
            'confidence': confidence
        }
    
    def _hz_to_midi(self, hz: float) -> float:
        """Convert Hz to MIDI note number."""
        if hz <= 0:
            return 0
        return 12 * np.log2(hz / 440.0) + 69
    
    def _classify_voice_type(self, min_midi: float, max_midi: float) -> tuple:
        """Classify voice type based on range."""
        
        voice_ranges = {
            'SOPRANO': (55, 84),
            'MEZZO_SOPRANO': (57, 81),
            'ALTO': (53, 77),
            'TENOR': (48, 72),
            'BARITONE': (45, 69),
            'BASS': (40, 64)
        }
        
        best_match = 'UNKNOWN'
        best_overlap = 0
        
        for voice_type, (type_min, type_max) in voice_ranges.items():
            overlap_min = max(min_midi, type_min)
            overlap_max = min(max_midi, type_max)
            
            if overlap_min <= overlap_max:
                overlap = overlap_max - overlap_min + 1
                type_range = type_max - type_min + 1
                overlap_percent = (overlap / type_range) * 100
                
                if overlap_percent > best_overlap:
                    best_overlap = overlap_percent
                    best_match = voice_type
        
        return best_match, best_overlap / 100
```

### 3.2 MIDI Conversion Utilities

```python
# app/audio/utils.py

import numpy as np

# Note names for display
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def hz_to_midi(hz: float) -> float:
    """
    Convert Hz to MIDI note number.
    
    Formula: MIDI = 12 × log₂(f/440) + 69
    
    Example:
        440 Hz → 69 (A4)
        261.63 Hz → 60 (C4)
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
    
    Example:
        60 → "C4"
        69 → "A4"
        72 → "C5"
    """
    midi = int(round(midi))
    octave = (midi // 12) - 1
    note = NOTE_NAMES[midi % 12]
    return f"{note}{octave}"


def midi_to_note_name_flat(midi: float) -> str:
    """Convert MIDI to note name with flats instead of sharps."""
    flat_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    midi = int(round(midi))
    octave = (midi // 12) - 1
    note = flat_names[midi % 12]
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
```

---

## 4. Post-Processing

### 4.1 Smoothing

```python
def smooth_f0(f0: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Smooth F0 values using moving average.
    
    Args:
        f0: F0 array (may contain NaN)
        window_size: Size of smoothing window
    
    Returns:
        Smoothed F0 array
    """
    # Replace NaN with interpolation
    f0_smooth = f0.copy()
    nan_mask = np.isnan(f0_smooth)
    
    if nan_mask.all():
        return f0_smooth
    
    # Interpolate NaN values
    valid_indices = np.arange(len(f0_smooth))
    invalid_indices = valid_indices[nan_mask]
    valid_values = f0_smooth[~nan_mask]
    
    if len(valid_values) > 0:
        f0_smooth[nan_mask] = np.interp(
            invalid_indices,
            valid_indices[~nan_mask],
            valid_values
        )
    
    # Apply moving average
    kernel = np.ones(window_size) / window_size
    f0_smooth = np.convolve(f0_smooth, kernel, mode='same')
    
    return f0_smooth


def median_filter_f0(f0: np.ndarray, window_size: int = 3) -> np.ndarray:
    """
    Apply median filter to remove outliers.
    
    Good for removing octave errors.
    """
    from scipy.ndimage import median_filter
    
    f0_filtered = f0.copy()
    nan_mask = np.isnan(f0_filtered)
    
    if not nan_mask.all():
        # Replace NaN with median for filtering
        valid_median = np.nanmedian(f0_filtered)
        f0_filtered[nan_mask] = valid_median
        
        # Apply median filter
        f0_filtered = median_filter(f0_filtered, size=window_size)
        
        # Restore NaN
        f0_filtered[nan_mask] = np.nan
    
    return f0_filtered
```

### 4.2 Outlier Removal

```python
def remove_f0_outliers(
    f0: np.ndarray,
    percentile_low: float = 5,
    percentile_high: float = 95
) -> np.ndarray:
    """
    Remove F0 outliers using percentile thresholds.
    
    Args:
        f0: F0 array
        percentile_low: Lower percentile threshold
        percentile_high: Upper percentile threshold
    
    Returns:
        F0 with outliers set to NaN
    """
    f0_clean = f0.copy()
    nan_mask = np.isnan(f0_clean)
    
    # Calculate thresholds
    valid_f0 = f0_clean[~nan_mask]
    if len(valid_f0) == 0:
        return f0_clean
    
    low_threshold = np.percentile(valid_f0, percentile_low)
    high_threshold = np.percentile(valid_f0, percentile_high)
    
    # Mark outliers
    outlier_mask = (f0_clean < low_threshold) | (f0_clean > high_threshold)
    f0_clean[outlier_mask] = np.nan
    
    return f0_clean
```

### 4.3 Viterbi Smoothing

```python
def viterbi_smooth_f0(f0: np.ndarray, voiced_probs: np.ndarray) -> np.ndarray:
    """
    Apply Viterbi smoothing to F0.
    
    This is what pYIN does internally, but we can apply it again
    for additional smoothing.
    """
    # For now, use simple median filter
    # Full Viterbi implementation would be more complex
    return median_filter_f0(f0, window_size=3)
```

---

## 5. Error Handling

### 5.1 Error Types

```python
class DSPError(Exception):
    """Base DSP error."""
    pass


class AudioValidationError(DSPError):
    """Audio file validation failed."""
    pass


class F0ExtractionError(DSPError):
    """F0 extraction failed."""
    pass


class InsufficientDataError(DSPError):
    """Not enough voiced data for analysis."""
    pass


# Error responses
ERROR_RESPONSES = {
    'FILE_NOT_FOUND': {
        'error': 'Audio file not found',
        'code': 'FILE_NOT_FOUND'
    },
    'INVALID_FORMAT': {
        'error': 'Invalid audio format. Must be WAV.',
        'code': 'INVALID_FORMAT'
    },
    'WRONG_SAMPLE_RATE': {
        'error': 'Sample rate must be 44100 Hz',
        'code': 'WRONG_SAMPLE_RATE'
    },
    'WRONG_CHANNELS': {
        'error': 'Audio must be mono (1 channel)',
        'code': 'WRONG_CHANNELS'
    },
    'FILE_TOO_LARGE': {
        'error': 'File size exceeds 10 MB limit',
        'code': 'FILE_TOO_LARGE'
    },
    'DURATION_TOO_SHORT': {
        'error': 'Recording too short. Minimum 10 seconds.',
        'code': 'DURATION_TOO_SHORT'
    },
    'DURATION_TOO_LONG': {
        'error': 'Recording too long. Maximum 60 seconds.',
        'code': 'DURATION_TOO_LONG'
    },
    'NO_VOICED_DATA': {
        'error': 'No voiced speech detected in recording',
        'code': 'NO_VOICED_DATA'
    },
    'LOW_QUALITY': {
        'error': 'Audio quality too low for analysis',
        'code': 'LOW_QUALITY'
    }
}
```

### 5.2 Quality Thresholds

```python
# Quality thresholds for accepting results
QUALITY_THRESHOLDS = {
    'voiced_ratio': {
        'min': 0.30,      # Minimum 30% voiced
        'good': 0.50,     # Good 50% voiced
        'excellent': 0.65  # Excellent 65% voiced
    },
    'confidence': {
        'min': 0.40,       # Minimum 40% confidence
        'good': 0.60,      # Good 60% confidence
        'excellent': 0.80  # Excellent 80% confidence
    },
    'range_semitones': {
        'min': 6,          # Minimum 6 semitones (minor 3rd)
        'good': 12,        # Good 12 semitones (octave)
        'excellent': 18    # Excellent 18+ semitones
    }
}


def assess_quality(result: F0Result) -> dict:
    """Assess analysis quality."""
    
    quality_score = 0
    issues = []
    
    # Check voiced ratio
    if result.voiced_ratio < QUALITY_THRESHOLDS['voiced_ratio']['min']:
        issues.append('voiced_ratio_too_low')
    else:
        quality_score += 1
    
    # Check confidence
    if result.confidence < QUALITY_THRESHOLDS['confidence']['min']:
        issues.append('confidence_too_low')
    else:
        quality_score += 1
    
    # Check range
    if result.range_semitones < QUALITY_THRESHOLDS['range_semitones']['min']:
        issues.append('range_too_narrow')
    else:
        quality_score += 1
    
    # Determine quality level
    if quality_score >= 3:
        level = 'excellent'
    elif quality_score >= 2:
        level = 'good'
    elif quality_score >= 1:
        level = 'fair'
    else:
        level = 'poor'
    
    return {
        'quality_level': level,
        'quality_score': quality_score,
        'issues': issues
    }
```

---

## 6. Performance Optimization

### 6.1 Caching

```python
# app/cache.py

import hashlib
import json
import os
from functools import lru_cache

class AnalysisCache:
    """Cache for F0 analysis results."""
    
    def __init__(self, cache_dir: str = '.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, audio_path: str) -> str:
        """Generate cache key from file path and modification time."""
        mtime = os.path.getmtime(audio_path)
        key_str = f"{audio_path}:{mtime}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, audio_path: str) -> Optional[dict]:
        """Get cached result if available."""
        cache_key = self._get_cache_key(audio_path)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def set(self, audio_path: str, result: dict):
        """Cache result."""
        cache_key = self._get_cache_key(audio_path)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        with open(cache_file, 'w') as f:
            json.dump(result, f)
    
    def clear(self):
        """Clear all cached results."""
        for file in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, file))
```

### 6.2 Batch Processing

```python
async def analyze_batch(
    audio_paths: list[str],
    max_concurrent: int = 3
) -> list[dict]:
    """
    Analyze multiple audio files concurrently.
    
    Args:
        audio_paths: List of audio file paths
        max_concurrent: Maximum concurrent analyses
    
    Returns:
        List of analysis results
    """
    import asyncio
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def analyze_with_limit(path: str) -> dict:
        async with semaphore:
            return await analyze_audio(path)
    
    tasks = [analyze_with_limit(p) for p in audio_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

---

**Document Version:** 1.0  
**Created:** September 19, 2026  
**Status:** Complete
