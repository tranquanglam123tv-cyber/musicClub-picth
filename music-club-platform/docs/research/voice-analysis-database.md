# Voice Analysis Results Database

## Mục lục
1. [Tổng quan](#1-tổng-quan)
2. [Database Schema](#2-database-schema)
3. [Voice Type Classification](#3-voice-type-classification)
4. [Quality Grading](#4-quality-grading)

---

## 1. Tổng quan

### 1.1 Voice Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│              VOICE ANALYSIS PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Audio Input ──▶ Preprocess ──▶ F0 Extract ──▶ Statistics │
│                                                             │
│      │           │            │            │                │
│      ▼           ▼            ▼            ▼                │
│   WAV file   Normalized   pYIN algo   min/max/avg F0      │
│   44100Hz    Mono         F0 contour  MIDI conversion      │
│   10-60s     Resampled                  Voice type         │
│                                                             │
│                           │                                │
│                           ▼                                │
│                    ┌──────────────┐                       │
│                    │   Database   │                       │
│                    │   Storage    │                       │
│                    └──────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Result Data Structure

```json
{
  "analysis_id": 1,
  "user_id": 123,
  "analysis_timestamp": "2026-09-19T15:30:00Z",
  
  "f0_statistics": {
    "min_f0_hz": 98.5,
    "max_f0_hz": 392.0,
    "avg_f0_hz": 220.0,
    "median_f0_hz": 215.0,
    "std_f0_hz": 45.0
  },
  
  "midi_statistics": {
    "min_midi": 43,
    "max_midi": 67,
    "median_midi": 60
  },
  
  "voice_classification": {
    "voice_type": "TENOR",
    "confidence": 0.85,
    "range_semitones": 24.0
  },
  
  "quality_metrics": {
    "voiced_ratio": 0.72,
    "stability_score": 0.78,
    "quality_grade": "B"
  },
  
  "f0_contour": [
    {"time_ms": 0, "f0_hz": 220.0, "midi": 60, "voiced": true},
    {"time_ms": 12, "f0_hz": 223.0, "midi": 60, "voiced": true}
  ]
}
```

---

## 2. Database Schema

### 2.1 voice_analyses Table

```sql
CREATE TABLE voice_analyses (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    session_id BIGINT,
    
    -- F0 Statistics (Hz)
    min_f0 DECIMAL(10,2),
    max_f0 DECIMAL(10,2),
    avg_f0 DECIMAL(10,2),
    median_f0 DECIMAL(10,2),
    std_f0 DECIMAL(10,4),
    
    -- MIDI Statistics
    min_midi INT,
    max_midi INT,
    median_midi INT,
    
    -- Voice Classification
    voice_type VARCHAR(50),
    confidence DECIMAL(4,3),
    range_semitones DECIMAL(6,2),
    
    -- Quality Metrics
    voiced_ratio DECIMAL(5,4),
    stability_score DECIMAL(4,3),
    quality_grade CHAR(1),
    
    -- F0 Contour (JSON - time series data)
    f0_contour JSON,
    
    -- Analysis Parameters
    analysis_params JSON,
    
    -- Timestamps
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_analyses (user_id, analyzed_at),
    INDEX idx_voice_type (voice_type)
);
```

### 2.2 voice_profiles Table

```sql
CREATE TABLE voice_profiles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL UNIQUE,
    
    -- Current Voice Type
    voice_type VARCHAR(50),
    confidence DECIMAL(4,3),
    
    -- Aggregated Statistics (from all analyses)
    min_f0 DECIMAL(10,2),
    max_f0 DECIMAL(10,2),
    avg_f0 DECIMAL(10,2),
    median_f0 DECIMAL(10,2),
    std_f0 DECIMAL(10,4),
    
    -- MIDI
    min_midi INT,
    max_midi INT,
    median_midi INT,
    range_semitones DECIMAL(6,2),
    
    -- Quality
    stability_score DECIMAL(4,3),
    quality_grade CHAR(1),
    
    -- Analysis Count
    total_analyses INT DEFAULT 0,
    last_analyzed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_voice_type (voice_type)
);
```

### 2.3 Analysis Sessions Table

```sql
CREATE TABLE analysis_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    
    session_type ENUM('SINGLE', 'SERIES', 'COMPARISON') DEFAULT 'SINGLE',
    sample_count INT DEFAULT 0,
    
    -- Summary from all samples in session
    overall_voice_type VARCHAR(50),
    overall_confidence DECIMAL(4,3),
    
    session_summary JSON,
    
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_sessions (user_id, created_at)
);
```

---

## 3. Voice Type Classification

### 3.1 Voice Type Ranges (Standard)

| Voice Type | Category | Typical Min | Typical Max | Range (semitones) |
|------------|----------|-------------|-------------|-------------------|
| **Soprano** | HIGH (Female) | G3 (55) | C6 (84) | 29 |
| **Mezzo-Soprano** | HIGH (Female) | A3 (57) | B5 (83) | 26 |
| **Alto** | MIDDLE (Female) | F3 (53) | D5 (77) | 24 |
| **Tenor** | MIDDLE (Male) | C3 (48) | C5 (72) | 24 |
| **Baritone** | MIDDLE (Male) | A2 (45) | A4 (69) | 24 |
| **Bass** | LOW (Male) | E2 (40) | E4 (64) | 24 |

### 3.2 Overlap Zones

```
┌─────────────────────────────────────────────────────────────┐
│              VOICE TYPE OVERLAP ZONES                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Soprano ──────────┬─────────────────────────────────────  │
│                    │ G3-A3 (55-69): Overlap with Tenor    │
│  Mezzo-Soprano ────┼─────────────────────────────────────  │
│                    │ F3-B3 (53-71): Overlap zone          │
│  Alto ─────────────┼─────────────────────────────────────  │
│                    │ C3-F3 (48-65): Overlap with Tenor    │
│  Tenor ────────────┼─────────────────────────────────────  │
│                    │ G3-B3 (55-71): Major overlap zone     │
│  Baritone ─────────┼─────────────────────────────────────  │
│                    │ C3-E3 (48-64): Overlap with Bass     │
│  Bass ─────────────┴─────────────────────────────────────  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Classification Algorithm

```python
def classify_voice_type(min_midi: int, max_midi: int) -> tuple[str, float]:
    """
    Classify voice type based on min and max MIDI values.
    
    Returns:
        Tuple of (voice_type, confidence)
    """
    
    # Voice type ranges with overlap zones
    voice_ranges = {
        'SOPRANO': {
            'typical_min': 55,   # G3
            'typical_max': 84,   # C6
            'overlap_min': 53,   # F3
            'overlap_max': 71,   # B4
        },
        'MEZZO_SOPRANO': {
            'typical_min': 57,   # A3
            'typical_max': 83,   # B5
            'overlap_min': 53,   # F3
            'overlap_max': 74,   # D5
        },
        'ALTO': {
            'typical_min': 53,   # F3
            'typical_max': 77,   # D5
            'overlap_min': 48,   # C3
            'overlap_max': 71,   # B4
        },
        'TENOR': {
            'typical_min': 48,   # C3
            'typical_max': 72,   # C5
            'overlap_min': 45,   # A2
            'overlap_max': 74,   # D5
        },
        'BARITONE': {
            'typical_min': 45,   # A2
            'typical_max': 69,   # A4
            'overlap_min': 40,   # E2
            'overlap_max': 72,   # C5
        },
        'BASS': {
            'typical_min': 40,   # E2
            'typical_max': 64,   # E4
            'overlap_min': 38,   # D2
            'overlap_max': 69,   # A4
        }
    }
    
    # Calculate range in semitones
    range_semitones = max_midi - min_midi
    
    # Score each voice type
    scores = {}
    
    for voice_type, ranges in voice_ranges.items():
        score = 0
        weight = 0
        
        # Check if min is in typical range
        if ranges['typical_min'] <= min_midi <= ranges['typical_max']:
            score += 2
            weight += 2
        elif ranges['overlap_min'] <= min_midi <= ranges['overlap_max']:
            score += 1
            weight += 2
        else:
            weight += 2
        
        # Check if max is in typical range
        if ranges['typical_min'] <= max_midi <= ranges['typical_max']:
            score += 2
            weight += 2
        elif ranges['overlap_min'] <= max_midi <= ranges['overlap_max']:
            score += 1
            weight += 2
        else:
            weight += 2
        
        # Bonus for range size
        expected_range = ranges['typical_max'] - ranges['typical_min']
        range_diff = abs(range_semitones - expected_range)
        if range_diff <= 3:
            score += 1
            weight += 1
        
        scores[voice_type] = score / weight if weight > 0 else 0
    
    # Get best match
    best_match = max(scores, key=scores.get)
    confidence = scores[best_match]
    
    return best_match, confidence
```

### 3.4 Gender-Aware Classification

```python
def classify_with_gender(min_midi: int, max_midi: int, gender: str = None) -> tuple[str, float]:
    """
    Classify voice type with gender awareness.
    
    Gender helps narrow down:
    - Male voices typically in 40-72 MIDI range
    - Female voices typically in 53-84 MIDI range
    """
    
    # Female voice types
    female_types = ['SOPRANO', 'MEZZO_SOPRANO', 'ALTO']
    
    # Male voice types
    male_types = ['TENOR', 'BARITONE', 'BASS']
    
    voice_type, confidence = classify_voice_type(min_midi, max_midi)
    
    if gender == 'MALE' and voice_type in female_types:
        # Try male classification with lower confidence
        male_type, male_conf = classify_male_voice(min_midi, max_midi)
        if male_conf > confidence * 0.7:
            return male_type, male_conf * 0.9  # Lower confidence due to mismatch
        else:
            return voice_type, confidence * 0.8  # Still return but with warning
    
    elif gender == 'FEMALE' and voice_type in male_types:
        female_type, female_conf = classify_female_voice(min_midi, max_midi)
        if female_conf > confidence * 0.7:
            return female_type, female_conf * 0.9
        else:
            return voice_type, confidence * 0.8
    
    return voice_type, confidence


def classify_male_voice(min_midi: int, max_midi: int) -> tuple[str, float]:
    """Classify specifically for male voices."""
    # TENOR: 48-72
    if min_midi >= 48 and max_midi <= 72:
        return 'TENOR', 0.9
    
    # BARITONE: 45-69
    if min_midi >= 45 and max_midi <= 69:
        return 'BARITONE', 0.9
    
    # BASS: 40-64
    if min_midi >= 40 and max_midi <= 64:
        return 'BASS', 0.9
    
    # Overlap zones
    if min_midi < 48:
        return 'TENOR', 0.7
    elif min_midi < 45:
        return 'BARITONE', 0.7
    else:
        return 'BASS', 0.7


def classify_female_voice(min_midi: int, max_midi: int) -> tuple[str, float]:
    """Classify specifically for female voices."""
    # SOPRANO: 60-84
    if min_midi >= 60 and max_midi <= 84:
        return 'SOPRANO', 0.9
    
    # MEZZO_SOPRANO: 57-83
    if min_midi >= 57 and max_midi <= 83:
        return 'MEZZO_SOPRANO', 0.9
    
    # ALTO: 53-77
    if min_midi >= 53 and max_midi <= 77:
        return 'ALTO', 0.9
    
    # Overlap zones
    if min_midi < 57:
        return 'MEZZO_SOPRANO', 0.7
    elif min_midi < 53:
        return 'ALTO', 0.7
    else:
        return 'SOPRANO', 0.7
```

---

## 4. Quality Grading

### 4.1 Quality Metrics

| Metric | Description | Good | Acceptable | Poor |
|--------|-------------|------|------------|------|
| **Voiced Ratio** | % of voiced frames | > 0.65 | 0.40-0.65 | < 0.40 |
| **Stability Score** | Pitch consistency | > 0.80 | 0.60-0.80 | < 0.60 |
| **Range Score** | Vocal range span | > 24 semitones | 18-24 | < 18 |
| **Confidence** | Algorithm confidence | > 0.80 | 0.60-0.80 | < 0.60 |

### 4.2 Quality Grade Calculation

```python
def calculate_quality_grade(
    voiced_ratio: float,
    stability_score: float,
    range_semitones: float,
    confidence: float
) -> str:
    """
    Calculate overall quality grade (A-F).
    
    Grading Scale:
    - A: Excellent (all metrics excellent)
    - B: Good (all metrics acceptable)
    - C: Fair (some metrics acceptable, some poor)
    - D: Poor (most metrics poor)
    - F: Fail (analysis not reliable)
    """
    
    # Score each metric (0-2 scale)
    scores = {
        'voiced': 0,
        'stability': 0,
        'range': 0,
        'confidence': 0
    }
    
    # Voiced ratio scoring
    if voiced_ratio >= 0.65:
        scores['voiced'] = 2
    elif voiced_ratio >= 0.40:
        scores['voiced'] = 1
    else:
        scores['voiced'] = 0
    
    # Stability scoring
    if stability_score >= 0.80:
        scores['stability'] = 2
    elif stability_score >= 0.60:
        scores['stability'] = 1
    else:
        scores['stability'] = 0
    
    # Range scoring
    if range_semitones >= 24:
        scores['range'] = 2
    elif range_semitones >= 18:
        scores['range'] = 1
    else:
        scores['range'] = 0
    
    # Confidence scoring
    if confidence >= 0.80:
        scores['confidence'] = 2
    elif confidence >= 0.60:
        scores['confidence'] = 1
    else:
        scores['confidence'] = 0
    
    # Calculate total score (max 8)
    total = sum(scores.values())
    
    # Assign grade
    if total >= 7:
        return 'A'
    elif total >= 5:
        return 'B'
    elif total >= 3:
        return 'C'
    elif total >= 2:
        return 'D'
    else:
        return 'F'


def get_quality_feedback(grade: str) -> dict:
    """Get detailed feedback based on quality grade."""
    
    feedback = {
        'A': {
            'level': 'Excellent',
            'message': 'Voice analysis is highly reliable',
            'recommendations': [
                'Analysis can be used for recommendations',
                'Voice type classification is confident'
            ]
        },
        'B': {
            'level': 'Good',
            'message': 'Voice analysis is reliable with minor issues',
            'recommendations': [
                'Results can be used for recommendations',
                'Consider re-recording for better quality'
            ]
        },
        'C': {
            'level': 'Fair',
            'message': 'Voice analysis has some reliability issues',
            'recommendations': [
                'Use with caution for recommendations',
                'Consider recording in quieter environment',
                'Ensure consistent volume throughout'
            ]
        },
        'D': {
            'level': 'Poor',
            'message': 'Voice analysis has significant reliability issues',
            'recommendations': [
                'Re-recording strongly recommended',
                'Check microphone placement',
                'Reduce background noise'
            ]
        },
        'F': {
            'level': 'Failed',
            'message': 'Voice analysis is not reliable',
            'recommendations': [
                'Please re-record',
                'Check audio device settings',
                'Ensure you are singing clearly'
            ]
        }
    }
    
    return feedback.get(grade, feedback['F'])
```

### 4.3 Stability Score Calculation

```python
def calculate_stability_score(f0_hz: np.ndarray, voiced_flag: np.ndarray) -> float:
    """
    Calculate pitch stability score.
    
    Measures how consistently the voice produces pitch.
    A stable voice has low variance in F0.
    """
    
    # Filter voiced frames
    voiced_f0 = f0_hz[voiced_flag]
    voiced_f0 = voiced_f0[~np.isnan(voiced_f0)]
    
    if len(voiced_f0) == 0:
        return 0.0
    
    # Calculate coefficient of variation (CV)
    # CV = std / mean (lower = more stable)
    mean_f0 = np.mean(voiced_f0)
    std_f0 = np.std(voiced_f0)
    
    if mean_f0 == 0:
        return 0.0
    
    cv = std_f0 / mean_f0
    
    # Convert CV to stability score (0-1)
    # CV of 0.05 (5%) = perfect stability = 1.0
    # CV of 0.50 (50%) = very unstable = 0.0
    stability = max(0, 1 - (cv / 0.50))
    
    return round(stability, 3)
```

### 4.4 Note Distribution

```python
def calculate_note_distribution(f0_hz: np.ndarray, voiced_flag: np.ndarray) -> dict:
    """
    Calculate note distribution from F0 contour.
    
    Returns count of each note sung.
    """
    
    # Filter voiced frames
    voiced_f0 = f0_hz[voiced_flag]
    voiced_f0 = voiced_f0[~np.isnan(voiced_f0)]
    
    if len(voiced_f0) == 0:
        return {}
    
    # Convert to MIDI and quantize to nearest note
    midi_values = 12 * np.log2(voiced_f0 / 440) + 69
    midi_rounded = np.round(midi_values).astype(int)
    
    # Count occurrences
    note_counts = {}
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    for midi in midi_rounded:
        note_name = NOTE_NAMES[midi % 12]
        octave = (midi // 12) - 1
        full_name = f"{note_name}{octave}"
        
        if full_name in note_counts:
            note_counts[full_name] += 1
        else:
            note_counts[full_name] = 1
    
    return note_counts
```

---

**Document Version:** 1.0  
**Created:** September 19, 2026  
**Status:** Complete
