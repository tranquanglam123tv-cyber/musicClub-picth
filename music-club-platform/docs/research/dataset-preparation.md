# Dataset Preparation Document

## Mục lục
1. [Tổng quan Dataset](#1-tổng-quan-dataset)
2. [Dataset Requirements](#2-dataset-requirements)
3. [Data Schema](#3-data-schema)
4. [Collection Protocol](#4-collection-protocol)
5. [Validation Checklist](#5-validation-checklist)
6. [Storage Strategy](#6-storage-strategy)

---

## 1. Tổng quan Dataset

### 1.1 Dataset cho Voice Analysis

```
┌─────────────────────────────────────────────────────────────┐
│                    DATASET OVERVIEW                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Voice Profile Dataset:                                     │
│  ├── Audio recordings (WAV)                                │
│  ├── F0 analysis results                                   │
│  ├── Metadata (voice type, range)                          │
│  └── Quality metrics                                      │
│                                                             │
│  Training Data:                                             │
│  ├── Clean recordings (studio quality)                     │
│  ├── Real-world recordings (mobile)                        │
│  └── Edge cases (noisy, breathy)                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Dataset Sizes

| Dataset Type | Size | Purpose |
|-------------|------|---------|
| **Development** | ~50 recordings | Testing |
| **Validation** | ~20 recordings | Accuracy verification |
| **Production** | ~200+ recordings | Full deployment |

---

## 2. Dataset Requirements

### 2.1 Audio Recording Requirements

| Tham số | Giá trị bắt buộc |
|----------|-------------------|
| Sample Rate | 44100 Hz |
| Bit Depth | 16-bit PCM |
| Channels | 1 (Mono) |
| Format | WAV |
| Duration | 10-60 seconds |
| SNR | > 20 dB preferred |

### 2.2 Recording Protocol

```
┌─────────────────────────────────────────────────────────────┐
│              RECORDING PROTOCOL                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. PRE-RECORDING CHECKLIST                                │
│     [ ] Quiet environment (< 40 dB background)            │
│     [ ] Microphone distance: 15-20 cm                       │
│     [ ] Microphone level: -12 dB to -6 dB                  │
│     [ ] Recording device calibrated                         │
│                                                             │
│  2. VOCAL WARMUP                                           │
│     [ ] 5 minutes warmup                                   │
│     [ ] Range exercises                                     │
│     [ ] Breathing exercises                                 │
│                                                             │
│  3. RECORDING SESSION                                      │
│     [ ] Speak/Count for 10 seconds (baseline)              │
│     [ ] Sing scales (C3-C5)                               │
│     [ ] Sing a familiar song (30-60 seconds)               │
│     [ ] Take breaks between attempts                       │
│                                                             │
│  4. POST-RECORDING                                        │
│     [ ] Listen back for quality                            │
│     [ ] Note any issues                                    │
│     [ ] Label and save properly                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | String | Yes | Anonymous user ID |
| `audio_path` | String | Yes | Path to WAV file |
| `duration_seconds` | Float | Yes | Recording duration |
| `sample_rate` | Integer | Yes | Must be 44100 |
| `channels` | Integer | Yes | Must be 1 |
| `format` | String | Yes | Must be WAV |
| `voice_type` | String | Yes | Self-reported voice type |
| `age_range` | String | No | Age range for demographics |
| `recording_date` | DateTime | Yes | Recording timestamp |
| `is_processed` | Boolean | Yes | F0 extraction done |

---

## 3. Data Schema

### 3.1 SQLite Local Database

```sql
-- Voice profiles (one per user)
CREATE TABLE voice_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    voice_type TEXT,
    min_f0 REAL,
    max_f0 REAL,
    avg_f0 REAL,
    range_semitones REAL,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

-- Practice sessions (F0 data points)
CREATE TABLE practice_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_type TEXT DEFAULT 'FULL_SONG',
    duration_seconds INTEGER,
    min_f0 REAL,
    max_f0 REAL,
    avg_f0 REAL,
    range_semitones REAL,
    pitch_accuracy_score REAL,
    voiced_ratio REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES voice_profiles(user_id)
);

-- F0 data points (detailed time series)
CREATE TABLE f0_data_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    timestamp_ms REAL NOT NULL,
    f0_hz REAL NOT NULL,
    voiced INTEGER NOT NULL,
    confidence REAL,
    FOREIGN KEY (session_id) REFERENCES practice_sessions(id)
);

-- Recording metadata
CREATE TABLE recordings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER,
    duration_seconds REAL,
    sample_rate INTEGER,
    channels INTEGER,
    format TEXT,
    quality_score REAL,
    status TEXT DEFAULT 'PENDING',
    f0_result_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES voice_profiles(user_id)
);

-- Song recommendations cache
CREATE TABLE song_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    song_id TEXT NOT NULL,
    match_score REAL,
    recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES voice_profiles(user_id)
);
```

### 3.2 JSON Export Format

```json
{
  "user_id": "user_abc123",
  "voice_type": "TENOR",
  "voice_analysis": {
    "min_f0_hz": 131.0,
    "max_f0_hz": 392.0,
    "avg_f0_hz": 220.0,
    "median_f0_hz": 215.0,
    "std_f0_hz": 45.0,
    "range_semitones": 24.0,
    "min_midi": 48,
    "max_midi": 72,
    "confidence": 0.85,
    "voiced_ratio": 0.72
  },
  "f0_timeseries": [
    {"timestamp_ms": 0, "f0_hz": 220.0, "voiced": true, "confidence": 0.9},
    {"timestamp_ms": 12, "f0_hz": 223.0, "voiced": true, "confidence": 0.85},
    ...
  ],
  "metadata": {
    "recording_date": "2026-09-19T15:00:00Z",
    "duration_seconds": 30.5,
    "sample_rate": 44100,
    "analysis_version": "1.0.0"
  }
}
```

---

## 4. Collection Protocol

### 4.1 Sample Distribution

| Voice Type | Target % | Min Samples |
|------------|----------|-------------|
| Bass | 10% | 5 |
| Baritone | 20% | 10 |
| Tenor | 20% | 10 |
| Alto | 15% | 8 |
| Mezzo-Soprano | 15% | 8 |
| Soprano | 20% | 10 |

### 4.2 Recording Checklist

```python
# Example: Recording validation
def validate_recording(file_path):
    """Validate recording meets requirements."""
    results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check file exists
    if not os.path.exists(file_path):
        results['valid'] = False
        results['errors'].append('File not found')
        return results
    
    # Check file extension
    if not file_path.endswith('.wav'):
        results['valid'] = False
        results['errors'].append('Must be WAV format')
    
    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > 10:
        results['valid'] = False
        results['errors'].append('File too large (>10MB)')
    
    # Load and check audio properties
    try:
        info = sf.info(file_path)
        
        if info.samplerate != 44100:
            results['valid'] = False
            results['errors'].append(f'Wrong sample rate: {info.samplerate}')
        
        if info.channels != 1:
            results['valid'] = False
            results['errors'].append(f'Wrong channels: {info.channels} (must be 1)')
        
        duration = info.duration
        if duration < 10:
            results['valid'] = False
            results['errors'].append(f'Too short: {duration:.1f}s (min 10s)')
        elif duration > 60:
            results['warnings'].append(f'Long recording: {duration:.1f}s')
        
    except Exception as e:
        results['valid'] = False
        results['errors'].append(f'Cannot read file: {str(e)}')
    
    return results
```

---

## 5. Validation Checklist

### 5.1 Pre-Analysis Checklist

- [ ] File is WAV format
- [ ] Sample rate is 44100 Hz
- [ ] Channel count is 1 (mono)
- [ ] Duration is 10-60 seconds
- [ ] File size < 10 MB
- [ ] No clipping (audio not too loud)
- [ ] SNR > 20 dB

### 5.2 Post-Analysis Checklist

- [ ] F0 extraction completed
- [ ] min_f0 within valid range (40-1100 Hz)
- [ ] max_f0 within valid range (40-1100 Hz)
- [ ] voiced_ratio > 0.3
- [ ] confidence > 0.5
- [ ] No NaN values in F0 array

### 5.3 Quality Metrics

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| **Voiced Ratio** | > 0.65 | 0.40-0.65 | < 0.40 |
| **Confidence** | > 0.80 | 0.50-0.80 | < 0.50 |
| **Range (semitones)** | 20-40 | 10-20 or 40-50 | < 10 or > 50 |
| **F0 Stability (std)** | < 30 Hz | 30-60 Hz | > 60 Hz |

---

## 6. Storage Strategy

### 6.1 Local vs Cloud

```
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE STRATEGY                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LOCAL (SQLite - Mobile):                                  │
│  ├── Voice profile summary                                 │
│  ├── F0 statistics (not raw audio)                        │
│  ├── Practice session history                              │
│  └── Song recommendations cache                            │
│  └── Max storage: ~50MB per user                          │
│                                                             │
│  CLOUD (MySQL - Server):                                   │
│  ├── Full F0 time series data                             │
│  ├── Aggregated statistics                                │
│  ├── Song library                                         │
│  └── User management                                      │
│  └── Unlimited storage                                    │
│                                                             │
│  OFFLINE AUDIO (Local - Only if needed):                   │
│  ├── Raw recordings (encrypted)                           │
│  └── Only for pending sync                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Sync Strategy

```python
# Sync strategy
SYNC_RULES = {
    # Always sync (small data)
    'voice_profile': {
        'sync_on_change': True,
        'priority': 'HIGH',
        'max_size': '1KB'
    },
    
    # Sync on WiFi only (large data)
    'practice_session': {
        'sync_on_change': False,
        'sync_on_wifi': True,
        'priority': 'MEDIUM',
        'max_size': '100KB'
    },
    
    # Manual sync (very large)
    'raw_recording': {
        'sync_on_change': False,
        'sync_on_wifi': True,
        'sync_manual': True,
        'priority': 'LOW',
        'max_size': '10MB'
    }
}
```

---

## 7. Dataset Files Structure

```
music-club-platform/
├── datasets/
│   ├── development/
│   │   ├── audio/
│   │   │   ├── bass_001.wav
│   │   │   ├── tenor_001.wav
│   │   │   └── ...
│   │   └── metadata/
│   │       └── recordings.csv
│   │
│   ├── validation/
│   │   ├── audio/
│   │   └── metadata/
│   │
│   └── production/
│       └── README.md
│
├── docs/
│   └── research/
│       └── dataset-preparation.md
│
└── dsp-service/
    └── tests/
        └── dataset_validator.py
```

---

**Document Version:** 1.0  
**Created:** September 19, 2026  
**Status:** Complete
