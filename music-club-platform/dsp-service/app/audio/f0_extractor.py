"""
F0 Extractor
============
"""

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
    fmin: float = 50.0
    fmax: float = 1000.0


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
