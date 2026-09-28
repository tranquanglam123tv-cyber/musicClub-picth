"""
F0 Extractor
============

Voice type classification based on standard music pedagogy:
  - SOPRANO         (C4 - C6)    tessitura: C4-G5   female high
  - MEZZO_SOPRANO   (A3 - A5)    tessitura: E4-G5   female mid-high
  - ALTO            (F3 - F5)    tessitura: G3-E5   female low / male falsetto
  - TENOR           (C3 - A4)    tessitura: D3-A4   male high
  - BARITONE        (A2 - F4)    tessitura: C3-F4   male mid
  - BASS            (E2 - E4)    tessitura: G2-E4   male low

Classification is based on:
  1. Median F0 (most reliable indicator of voice type)
  2. Comfortable tessitura (P25 - P75 of F0 distribution, NOT min/max outliers)
  3. Vowel-stable range (IQR-based, robust to single-note outliers)
"""

import librosa
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class F0Config:
    """F0 extraction configuration."""
    SAMPLE_RATE: int = 44100
    FRAME_LENGTH: int = 2048
    HOP_LENGTH: int = 512
    F_MIN: float = 50.0
    F_MAX: float = 1000.0


@dataclass
class F0Result:
    """F0 extraction result."""
    # Time series
    f0_times: np.ndarray
    f0_hz: np.ndarray
    voiced_flag: np.ndarray
    voiced_probs: np.ndarray

    # Primary pitch estimate: mode-based (most frequent pitch, robust to
    # vibrato-induced harmonic tracking). Fallback to median if not enough
    # voiced frames for reliable mode.
    pitch_estimate: float

    # Statistics
    min_f0: float
    max_f0: float
    avg_f0: float
    median_f0: float
    std_f0: float
    p25_f0: float       # 25th percentile - lower edge of comfortable range
    p75_f0: float       # 75th percentile - upper edge of comfortable range
    iqr_f0: float       # interquartile range (robust range indicator)
    # MIDI
    min_midi: float
    max_midi: float
    range_semitones: float

    # Quality
    voiced_ratio: float
    confidence: float

    # Voice type
    voice_type: str
    voice_type_confidence: float


class F0Extractor:
    """F0 Extractor using pYIN algorithm with music-accurate voice classification."""

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
            fmin=self.config.F_MIN,
            fmax=self.config.F_MAX,
            sr=self.config.SAMPLE_RATE,
            frame_length=self.config.FRAME_LENGTH,
            hop_length=self.config.HOP_LENGTH,
        )

        # Generate time stamps
        f0_times = librosa.times_like(
            f0,
            sr=self.config.SAMPLE_RATE,
            hop_length=self.config.HOP_LENGTH
        )

        # Calculate statistics (now includes percentiles)
        stats = self._calculate_statistics(f0, voiced_flag, voiced_probs)

        # Compute tessitura-based MIDI for voice classification
        # Use pitch_estimate (mode) for voice type — robust to vibrato/harmonics.
        # Use p25/p75 from all voiced frames for tessitura — captures full range.
        pitch_estimate_midi = self._hz_to_midi(stats['pitch_estimate'])
        p25_midi = self._hz_to_midi(stats['p25_f0'])
        p75_midi = self._hz_to_midi(stats['p75_f0'])

        # Classify voice type - use mode-based pitch for classification
        voice_type, voice_conf = self._classify_voice_type(
            median_midi=pitch_estimate_midi,
            tessitura_low_midi=p25_midi,
            tessitura_high_midi=p75_midi,
            voiced_ratio=stats['voiced_ratio']
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

    def _pitch_mode(self, voiced_f0: np.ndarray, sr: int) -> float:
        """
        Estimate the fundamental frequency using histogram-mode binning.

        Bins F0 values into 1-Hz bins and returns the most frequent bin
        center.  This is robust to vibrato-induced harmonic/octave jumps
        that bias the arithmetic median.

        Returns the median as fallback when too few frames are available.
        """
        if len(voiced_f0) < 5:
            return float(np.median(voiced_f0)) if len(voiced_f0) > 0 else 0.0

        # Bin to nearest 1 Hz
        bins = np.round(voiced_f0).astype(int)

        # Require at least 3 votes to consider a bin "stable"
        # (avoids mode being a single spurious frame)
        min_votes = min(3, len(voiced_f0) // 5)

        vals, counts = np.unique(bins, return_counts=True)
        stable = vals[counts >= min_votes]
        stable_counts = counts[counts >= min_votes]

        if len(stable) == 0:
            return float(np.median(voiced_f0))

        mode_bin = stable[np.argmax(stable_counts)]
        return float(mode_bin)

    def _calculate_statistics(
        self,
        f0: np.ndarray,
        voiced_flag: np.ndarray,
        voiced_probs: np.ndarray
    ) -> dict:
        """Calculate F0 statistics with percentile-based tessitura."""

        # Filter voiced frames only
        voiced_f0 = f0[voiced_flag]
        voiced_f0 = voiced_f0[~np.isnan(voiced_f0)]

        if len(voiced_f0) == 0:
            return {
                'min_f0': 0, 'max_f0': 0, 'avg_f0': 0,
                'median_f0': 0, 'std_f0': 0,
                'p25_f0': 0, 'p75_f0': 0, 'iqr_f0': 0,
                'min_midi': 0, 'max_midi': 0,
                'range_semitones': 0,
                'voiced_ratio': 0, 'confidence': 0,
                'pitch_estimate': 0.0,
            }

        # === Basic Hz statistics ===
        min_f0 = float(np.min(voiced_f0))
        max_f0 = float(np.max(voiced_f0))
        avg_f0 = float(np.mean(voiced_f0))
        median_f0 = float(np.median(voiced_f0))
        std_f0 = float(np.std(voiced_f0))

        # === Percentile-based tessitura (robust to single-note outliers) ===
        # P25-P75 captures the "comfortable" range where the singer spends
        # most of their time - much more representative than min/max.
        p25_f0 = float(np.percentile(voiced_f0, 25))
        p75_f0 = float(np.percentile(voiced_f0, 75))
        iqr_f0 = p75_f0 - p25_f0

        # === MIDI conversions ===
        min_midi = self._hz_to_midi(min_f0)
        max_midi = self._hz_to_midi(max_f0)

        # === Range in semitones (based on absolute min/max) ===
        range_semitones = 12 * np.log2(max_f0 / min_f0) if min_f0 > 0 else 0

        # === Quality metrics ===
        voiced_ratio = np.sum(voiced_flag) / len(voiced_flag)
        confidence = float(np.mean(voiced_probs[voiced_flag])) if np.any(voiced_flag) else 0

        # === Mode-based pitch estimate (harmonic/vibrato robust) ===
        pitch_estimate = self._pitch_mode(voiced_f0, self.config.SAMPLE_RATE)

        return {
            'min_f0': min_f0,
            'max_f0': max_f0,
            'avg_f0': avg_f0,
            'median_f0': median_f0,
            'std_f0': std_f0,
            'p25_f0': p25_f0,
            'p75_f0': p75_f0,
            'iqr_f0': iqr_f0,
            'min_midi': min_midi,
            'max_midi': max_midi,
            'range_semitones': range_semitones,
            'voiced_ratio': voiced_ratio,
            'confidence': confidence,
            'pitch_estimate': pitch_estimate,
        }

    def _hz_to_midi(self, hz: float) -> float:
        """Convert Hz to MIDI note number (A4=440Hz=MIDI 69)."""
        if hz <= 0:
            return 0
        return 12 * np.log2(hz / 440.0) + 69

    def _classify_voice_type(
        self,
        median_midi: float,
        tessitura_low_midi: float,
        tessitura_high_midi: float,
        voiced_ratio: float
    ) -> tuple:
        """
        Classify voice type using a HYBRID multi-feature voting scheme.

        Six weighted features (sum to 1.0):
          F1 (40%) Median F0 Gaussian           — soft similarity
          F2 (20%) Tessitura centroid match     — midpoint distance
          F3 (20%) Range-center distance        — hard penalty if outside
          F4 (10%) P25 lower-bound sanity check — physical limits
          F5  (5%) Tessitura-width bonus        — wide→low voice, narrow→high
          F6  (5%) Voiced-ratio reliability     — quality gate

        Returns (voice_type, confidence in [0,1]).
        """
        if voiced_ratio < 0.1 or median_midi <= 0:
            return 'UNKNOWN', 0.0

        voice_types = [
            # (name, median_hz, tessitura_low_midi, tessitura_high_midi)
            ('SOPRANO',       261.0, 60, 79),   # ~C4
            ('MEZZO_SOPRANO', 220.0, 57, 79),   # ~A3
            ('ALTO',          196.0, 55, 76),   # ~G3
            ('TENOR',         147.0, 50, 69),   # ~D3
            ('BARITONE',      123.0, 47, 65),   # ~B2
            ('BASS',           88.0, 41, 64),   # ~F2
        ]

        def hz_to_midi(hz):
            return 12 * np.log2(hz / 440.0) + 69

        tessitura_center = (tessitura_low_midi + tessitura_high_midi) / 2.0
        tessitura_width = tessitura_high_midi - tessitura_low_midi
        sigma_median = 3.5   # widened from 2.0 → forgiving for register breaks
        sigma_center = 4.0

        scores = {}
        for name, med_hz, t_low, t_high in voice_types:
            type_center_midi = hz_to_midi(med_hz)
            type_centroid_midi = (t_low + t_high) / 2.0

            # ---- F1: Median F0 Gaussian (40%) ----
            d_median = median_midi - type_center_midi
            f1 = float(np.exp(-0.5 * (d_median / sigma_median) ** 2))

            # ---- F2: Tessitura centroid match (20%) ----
            d_centroid = tessitura_center - type_centroid_midi
            f2 = float(np.exp(-0.5 * (d_centroid / sigma_center) ** 2))

            # ---- F3: Range-center distance (20%) ----
            if tessitura_low_midi > t_high + 5 or tessitura_high_midi < t_low - 5:
                f3 = 0.05  # tessitura fully outside typical range
            else:
                cd = abs(tessitura_center - type_centroid_midi)
                f3 = float(np.exp(-0.5 * (cd / 6.0) ** 2))

            # ---- F4: P25 lower-bound sanity check (10%) ----
            # Physical floor for each voice type, but only as soft penalty
            # because some wide-range singers (e.g. contralto) dip below
            # their type's typical floor while median stays high.
            if name in ('SOPRANO', 'MEZZO_SOPRANO'):
                # Floor ~G3 (196Hz). Allow dip if median clearly soprano.
                if tessitura_low_midi >= 53:
                    f4 = 1.0
                elif tessitura_low_midi >= 48 and median_midi >= 58:
                    f4 = 0.6  # wide-range female
                else:
                    f4 = 0.3
            elif name == 'ALTO':
                if tessitura_low_midi >= 50:
                    f4 = 1.0
                elif tessitura_low_midi >= 45 and median_midi >= 55:
                    f4 = 0.5  # wide-range alto
                else:
                    f4 = 0.4
            elif name == 'TENOR':
                # Floor ~A2 (G#2). Allow higher.
                if 46 <= tessitura_low_midi <= 56:
                    f4 = 1.0
                elif tessitura_low_midi < 46 and median_midi >= 50:
                    f4 = 0.5  # baritone-range tenor — softer penalty
                else:
                    f4 = 0.4
            elif name == 'BARITONE':
                if 43 <= tessitura_low_midi <= 52:
                    f4 = 1.0
                elif tessitura_low_midi <= 55 and median_midi >= 47:
                    f4 = 0.6  # baritone with some bass extension
                else:
                    f4 = 0.5
            elif name == 'BASS':
                if tessitura_low_midi <= 50:
                    f4 = 1.0
                elif tessitura_low_midi <= 55 and median_midi < 47:
                    f4 = 0.7  # bass-baritone
                else:
                    f4 = 0.3
            else:
                f4 = 0.5

            # ---- F5: Tessitura-width bonus (5%) ----
            if name in ('BASS', 'BARITONE'):
                f5 = min(1.0, tessitura_width / 14.0)
            elif name in ('SOPRANO', 'MEZZO_SOPRANO'):
                f5 = min(1.0, (18 - tessitura_width) / 12.0) if tessitura_width < 18 else 0.4
            else:
                f5 = 0.7

            # ---- F6: Voiced-ratio reliability (5%) ----
            f6 = min(1.0, voiced_ratio / 0.4)

            total = 0.50*f1 + 0.15*f2 + 0.20*f3 + 0.05*f4 + 0.05*f5 + 0.05*f6
            scores[name] = total

        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_match, best_score = sorted_items[0]
        runner_up = sorted_items[1][1] if len(sorted_items) > 1 else 0.0

        if best_score > 0:
            margin = 1 - (runner_up / best_score)
            confidence = best_score * (0.5 + 0.5 * margin) * min(1.0, voiced_ratio / 0.3 + 0.3)
        else:
            confidence = 0.0

        return best_match, round(float(min(1.0, max(0.0, confidence))), 3)
