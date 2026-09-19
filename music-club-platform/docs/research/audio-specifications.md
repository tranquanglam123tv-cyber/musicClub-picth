# Audio Specifications Document

## Mục lục
1. [Tổng quan](#1-tổng-quan)
2. [Recording Specifications](#2-recording-specifications)
3. [Processing Specifications](#3-processing-specifications)
4. [Flutter Implementation Guide](#4-flutter-implementation-guide)
5. [FastAPI DSP Service Specifications](#5-fastapi-dsp-service-specifications)

---

## 1. Tổng quan

Tài liệu này định nghĩa các thông số kỹ thuật âm thanh bắt buộc cho toàn bộ hệ thống, đảm bảo tính nhất quán từ thu âm đến xử lý F0.

### 1.1 Mục tiêu

```
┌─────────────────────────────────────────────────────────────┐
│                 AUDIO PIPELINE                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐│
│  │   Mobile     │───▶│   FastAPI    │───▶│  Spring      ││
│  │   Recording  │    │   DSP        │    │  Backend      ││
│  │   (Flutter)  │    │   (Python)   │    │  (Java)       ││
│  └──────────────┘    └──────────────┘    └──────────────┘│
│        │                   │                    │            │
│        ▼                   ▼                    ▼            │
│   ┌─────────┐        ┌─────────┐        ┌─────────┐    │
│   │ WAV/PCM │        │ F0 Data │        │  JSON   │    │
│   │ 16-bit  │        │ Analysis │        │ Response│    │
│   │ 44100Hz │        │          │        │         │    │
│   │  Mono   │        │          │        │         │    │
│   └─────────┘        └─────────┘        └─────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Recording Specifications

### 2.1 Bắt buộc (Required)

| Tham số | Giá trị | Lý do |
|----------|---------|-------|
| **Sample Rate** | 44100 Hz | Chuẩn CD, Nyquist = 22050 Hz đủ cho giọng hát |
| **Bit Depth** | 16-bit | Đủ cho F0, tiết kiệm storage |
| **Channels** | **1 (Mono)** | F0 cần mono, tránh phase issues |
| **Format** | WAV (PCM) | Lossless, không compression artifacts |
| **Duration** | 10-60 giây | Tối thiểu 10s cho độ chính xác |

### 2.2 Khuyến nghị (Recommended)

| Tham số | Giá trị | Lý do |
|----------|---------|-------|
| **Bit Depth** | 24-bit | Tốt hơn cho F0 extraction |
| **Buffer Size** | 512-1024 samples | Balance latency vs quality |
| **Noise Reduction** | ON (nếu có) | Giảm noise floor |

### 2.3 Không được phép (Prohibited)

| Tham số | Lý do loại trừ |
|----------|-----------------|
| **MP3/AAC** | Compression artifacts ảnh hưởng F0 |
| **Stereo** | Phase differences gây sai lệch F0 |
| **< 44100 Hz** | Nyquist quá thấp, mất thông tin |
| **< 10 giây** | Không đủ data cho accurate F0 |

### 2.4 Chi tiết kỹ thuật

```
┌─────────────────────────────────────────────────────────────┐
│                 WAV FILE SPECIFICATIONS                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Container:     RIFF WAV                                    │
│  Sample Rate:   44100 Hz                                    │
│  Bit Depth:     16-bit PCM                                  │
│  Channels:      1 (Mono)                                    │
│  Byte Rate:     44100 × 1 × 2 = 88200 bytes/sec            │
│  Block Align:   2 bytes (1 channel × 2 bytes)              │
│                                                             │
│  File Size Calculation:                                     │
│  size = duration_seconds × sample_rate × channels × (bit_depth/8)│
│                                                             │
│  Ví dụ: 30 giây = 30 × 44100 × 1 × 2 = 2,646,000 bytes   │
│                    ≈ 2.5 MB                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Processing Specifications

### 3.1 DSP Parameters cho F0 Extraction

| Tham số | Giá trị | Tunable Range | Ghi chú |
|----------|---------|---------------|---------|
| **Frame Length** | 2048 samples | 1024-4096 | 46-93ms at 44.1kHz |
| **Hop Length** | 512 samples | 256-1024 | Độ phân giải thời gian |
| **Fmin** | 50 Hz | 30-100 Hz | Thấp hơn Bass |
| **Fmax** | 500 Hz | 300-1000 Hz | Cao hơn Soprano |
| **Voiced Threshold** | 0.5 | 0.3-0.8 | Sensitivity |
| **Algorithm** | pYIN | YIN/pYIN | pYIN mặc định |

### 3.2 Frame/Hop Calculation

```
┌─────────────────────────────────────────────────────────────┐
│                 FRAME TIMING                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Sample Rate: 44100 Hz                                      │
│  Frame Length: 2048 samples                                 │
│  Hop Length: 512 samples                                    │
│                                                             │
│  Frame Duration = 2048 / 44100 = 46.4 ms                   │
│  Hop Duration = 512 / 44100 = 11.6 ms                      │
│                                                             │
│  ┌────┬────┬────┬────┬────┬────┬────┬────┐              │
│  │ F1 │    │ F2 │    │ F3 │    │ F4 │    │ ...          │
│  └────┴────┴────┴────┴────┴────┴────┴────┘              │
│  ├────┤    ├────┤    ├────┤    ├────┤                     │
│  Hops ──────────────────────────────────▶                   │
│                                                             │
│  Frames overlap = 2048 - 512 = 1536 samples (75%)          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Quality Thresholds

| Metric | Minimum | Good | Excellent |
|--------|---------|------|-----------|
| **Voiced Ratio** | > 0.5 | > 0.65 | > 0.75 |
| **Confidence** | > 0.5 | > 0.7 | > 0.85 |
| **F0 Stability** | std < 100 Hz | std < 50 Hz | std < 25 Hz |

---

## 4. Flutter Implementation Guide

### 4.1 Required Package

```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  record: ^5.1.0          # Audio recording
  path_provider: ^2.1.2   # File paths
```

### 4.2 Audio Recorder Configuration

```dart
// lib/services/audio_recorder_service.dart

import 'package:record/record.dart';

class AudioRecorderService {
  final AudioRecorder _recorder = AudioRecorder();
  
  // ═══════════════════════════════════════════════════════════
  // REQUIRED CONFIGURATION - DO NOT CHANGE
  // ═══════════════════════════════════════════════════════════
  
  /// Sample rate: 44100 Hz (CD quality standard)
  static const int sampleRate = 44100;
  
  /// Bit depth: 16-bit PCM
  static const int bitDepth = 16;
  
  /// Channels: MONO (required for F0 analysis)
  static const int numChannels = 1;
  
  /// Minimum recording duration: 10 seconds
  static const int minDurationSeconds = 10;
  
  /// Maximum recording duration: 60 seconds
  static const int maxDurationSeconds = 60;
  
  /// Maximum file size: 10 MB
  static const int maxFileSizeMB = 10;
  
  // ═══════════════════════════════════════════════════════════

  /// Check if recorder has required capabilities
  Future<bool> checkCapabilities() async {
    // Verify device supports required sample rate
    final isSupported = await _recorder.hasPermission();
    return isSupported;
  }
  
  /// Start recording with required specifications
  Future<String> startRecording() async {
    // Configure encoder for WAV/PCM
    const encoder = AudioEncoder.wav;
    
    // Configure path for temporary storage
    final path = await _getRecordingPath();
    
    // Start recording with config
    await _recorder.start(
      const RecordConfig(
        encoder: encoder,
        sampleRate: sampleRate,
        bitRate: bitDepth * sampleRate,
        numChannels: numChannels,
      ),
      path: path,
    );
    
    return path;
  }
  
  /// Get recording path
  Future<String> _getRecordingPath() async {
    // Implementation...
  }
}
```

### 4.3 Validation Checklist

```dart
// lib/utils/audio_validator.dart

class AudioValidator {
  /// Validate recorded audio meets specifications
  static ValidationResult validate(String filePath) {
    final result = ValidationResult();
    
    // 1. Check file extension is WAV
    if (!filePath.endsWith('.wav')) {
      result.addError('File must be WAV format');
    }
    
    // 2. Check file size
    final file = File(filePath);
    final sizeMB = file.lengthSync() / (1024 * 1024);
    if (sizeMB > 10) {
      result.addError('File size exceeds 10 MB limit');
    }
    if (sizeMB < 0.1) {
      result.addError('File too short (minimum 10 seconds required)');
    }
    
    // 3. Additional validation can be done with ffprobe or similar
    
    return result;
  }
}
```

### 4.4 Recording UI

```dart
// lib/screens/recording_screen.dart

class RecordingScreen extends StatefulWidget {
  const RecordingScreen({super.key});

  @override
  State<RecordingScreen> createState() => _RecordingScreenState();
}

class _RecordingScreenState extends State<RecordingScreen> {
  // Recording state
  bool _isRecording = false;
  Duration _duration = Duration.zero;
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Thu âm')),
      body: Column(
        children: [
          // Duration display
          Text(
            _formatDuration(_duration),
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          
          // Recording indicator
          if (_isRecording)
            const Text('🔴 ĐANG GHI ÂM'),
          
          // Min duration warning
          if (_duration.inSeconds < 10 && _duration.inSeconds > 0)
            const Text(
              '⚠️ Cần ít nhất 10 giây để phân tích',
              style: TextStyle(color: Colors.orange),
            ),
          
          // Record button
          ElevatedButton(
            onPressed: _isRecording ? _stopRecording : _startRecording,
            child: Icon(_isRecording ? Icons.stop : Icons.mic),
          ),
          
          // Tips
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('💡 Tips thu âm:', style: TextStyle(fontWeight: FontWeight.bold)),
                  Text('• Hát 10-60 giây'),
                  Text('• Giọng rõ ràng, không ồn ào'),
                  Text('• Giữ microphone 15-20cm'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
```

---

## 5. FastAPI DSP Service Specifications

### 5.1 Audio Input Requirements

```python
# app/api/routes/audio.py

from fastapi import APIRouter, UploadFile, File, HTTPException
import numpy as np

router = APIRouter()

# ═══════════════════════════════════════════════════════════
# REQUIRED AUDIO SPECIFICATIONS
# ═══════════════════════════════════════════════════════════

REQUIRED_SAMPLE_RATE = 44100
REQUIRED_CHANNELS = 1
REQUIRED_FORMAT = ['wav', 'wave', 'rf64']
MAX_DURATION_SECONDS = 60
MAX_FILE_SIZE_MB = 10
MIN_DURATION_SECONDS = 10

# ═══════════════════════════════════════════════════════════

@router.post("/analyze")
async def analyze_audio(
    file: UploadFile = File(...)
):
    """Analyze audio file for F0 extraction"""
    
    # 1. Validate file format
    if not any(file.filename.endswith(ext) for ext in REQUIRED_FORMAT):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Required: {REQUIRED_FORMAT}"
        )
    
    # 2. Validate file size
    file_size_mb = len(await file.read()) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum: {MAX_FILE_SIZE_MB} MB"
        )
    
    # 3. Load and validate audio
    audio_data = await load_audio(file)
    
    # Check sample rate
    if audio_data.samplerate != REQUIRED_SAMPLE_RATE:
        # Resample if needed
        audio_data = librosa.resample(
            audio_data.y,
            orig_sr=audio_data.samplerate,
            target_sr=REQUIRED_SAMPLE_RATE
        )
    
    # Check channels (convert to mono if stereo)
    if audio_data.ndim > 1 and audio_data.shape[0] > 1:
        audio_data = librosa.to_mono(audio_data.T)
    
    # Check duration
    duration = len(audio_data) / REQUIRED_SAMPLE_RATE
    if duration < MIN_DURATION_SECONDS:
        raise HTTPException(
            status_code=400,
            detail=f"Recording too short. Minimum: {MIN_DURATION_SECONDS}s"
        )
    if duration > MAX_DURATION_SECONDS:
        raise HTTPException(
            status_code=400,
            detail=f"Recording too long. Maximum: {MAX_DURATION_SECONDS}s"
        )
    
    # 4. Proceed with analysis...
```

### 5.2 DSP Processing Parameters

```python
# app/config.py

class DSPConfig:
    """DSP Configuration - Tunable Parameters"""
    
    # Audio preprocessing
    TARGET_SAMPLE_RATE = 44100
    TARGET_CHANNELS = 1
    
    # F0 extraction (pYIN)
    FRAME_LENGTH = 2048      # samples
    HOP_LENGTH = 512         # samples
    F_MIN = 50               # Hz (below lowest voice)
    F_MAX = 500              # Hz (above highest voice)
    
    # pYIN specific
    THRESHOLD = 0.5          # voiced probability threshold
    WEIGHT = 0.5             # pYIN weight
    
    # Voice range calculation
    CONFIDENCE_THRESHOLD = 0.5   # minimum confidence to accept
    OUTLIER_PERCENTILE = 5       # trim outliers
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        assert cls.FRAME_LENGTH >= 1024, "Frame length too small"
        assert cls.FRAME_LENGTH <= 4096, "Frame length too large"
        assert cls.F_MIN < cls.F_MAX, "F_MIN must be less than F_MAX"
        assert cls.F_MAX > 1000, "F_MAX must be > 1000 Hz for soprano"
```

---

## 6. Quality Assurance Checklist

### 6.1 Pre-Recording Checklist (Flutter)

- [ ] Microphone permission granted
- [ ] Sample rate set to 44100 Hz
- [ ] Channel set to Mono
- [ ] Format set to WAV/PCM
- [ ] Duration limit set (10-60s)

### 6.2 Post-Recording Validation (Flutter)

- [ ] File exists and is readable
- [ ] File size < 10 MB
- [ ] Duration >= 10 seconds
- [ ] Format is WAV

### 6.3 DSP Validation (Python)

- [ ] Sample rate is 44100 Hz
- [ ] Audio is mono
- [ ] Duration is valid
- [ ] No NaN values in audio
- [ ] Audio level is not silent

---

## Tài liệu tham khảo

1. Librosa Documentation: https://librosa.org/doc/
2. Web Audio API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
3. Flutter Record Package: https://pub.dev/packages/record
4. ITU-R BS.775-1: Multichannel stereophonic sound system

---

**Document Version:** 1.0  
**Created:** September 19, 2026  
**Status:** Ready for Implementation
