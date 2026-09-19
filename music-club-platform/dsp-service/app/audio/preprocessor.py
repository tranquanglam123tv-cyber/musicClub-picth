"""
Audio Preprocessor
==================
"""

import os
import soundfile as sf
import librosa
import numpy as np
from typing import Dict, List


class AudioPreprocessor:
    """Audio preprocessing pipeline."""
    
    REQUIRED_SAMPLE_RATE = 44100
    REQUIRED_CHANNELS = 1
    MIN_DURATION = 10  # seconds
    MAX_DURATION = 60  # seconds
    MAX_FILE_SIZE_MB = 10
    
    def __init__(self):
        pass
    
    def validate(self, audio_path: str) -> Dict:
        """
        Validate audio file meets requirements.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dict with 'valid', 'errors', 'warnings' keys
        """
        errors = []
        warnings = []
        
        # Check file exists
        if not os.path.exists(audio_path):
            return {'valid': False, 'errors': ['File not found']}
        
        # Check file size
        try:
            file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            if file_size_mb > self.MAX_FILE_SIZE_MB:
                errors.append(f'File too large: {file_size_mb:.1f}MB (max {self.MAX_FILE_SIZE_MB}MB)')
        except Exception:
            pass
        
        # Load and check properties
        try:
            info = sf.info(audio_path)
            
            # Check sample rate
            if info.samplerate != self.REQUIRED_SAMPLE_RATE:
                warnings.append(f'Sample rate: {info.samplerate}Hz (will be resampled to {self.REQUIRED_SAMPLE_RATE}Hz)')
            
            # Check channels
            if info.channels != self.REQUIRED_CHANNELS:
                errors.append(f'Channels: {info.channels} (must be {self.REQUIRED_CHANNELS})')
            
            # Check duration
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
    
    def preprocess(self, audio_path: str) -> np.ndarray:
        """
        Preprocess audio file.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Preprocessed audio as numpy array
        """
        # Load audio using librosa
        audio, sr = librosa.load(audio_path, sr=None, mono=False)
        
        # Resample if needed
        if sr != self.REQUIRED_SAMPLE_RATE:
            if audio.ndim > 1:
                audio = librosa.resample(audio.T, orig_sr=sr, target_sr=self.REQUIRED_SAMPLE_RATE).T
            else:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.REQUIRED_SAMPLE_RATE)
            sr = self.REQUIRED_SAMPLE_RATE
        
        # Convert to mono
        if audio.ndim > 1:
            audio = librosa.to_mono(audio)
        
        # Normalize to [-1, 1]
        peak = np.max(np.abs(audio))
        if peak > 0:
            audio = audio / peak
        
        return audio.astype(np.float32)
    
    def trim_silence(
        self,
        audio: np.ndarray,
        top_db: int = 20
    ) -> np.ndarray:
        """
        Trim silence from beginning and end.
        
        Args:
            audio: Input audio
            top_db: Threshold in dB
        
        Returns:
            Trimmed audio
        """
        trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
        return trimmed
