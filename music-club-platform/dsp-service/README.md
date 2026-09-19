# DSP Service - FastAPI Application

## Mục lục
1. [Architecture](#1-architecture)
2. [API Endpoints](#2-api-endpoints)
3. [Project Structure](#3-project-structure)
4. [Usage](#4-usage)

---

## 1. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 DSP SERVICE ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                   FastAPI Server                     │  │
│  │                                                      │  │
│  │  POST /api/v1/voice/analyze                        │  │
│  │  GET  /api/v1/health                               │  │
│  │                                                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                 Audio Processing                     │  │
│  │                                                      │  │
│  │  Preprocessor → F0 Extractor → Analyzer            │  │
│  │                                                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                 DSP Libraries                       │  │
│  │                                                      │  │
│  │  librosa (pYIN) | scipy | numpy | soundfile        │  │
│  │                                                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. API Endpoints

### 2.1 Analyze Voice

```
POST /api/v1/voice/analyze
```

**Request:**
- Content-Type: multipart/form-data
- Body: audio file (WAV)

**Response:**
```json
{
  "success": true,
  "data": {
    "min_f0": 98.5,
    "max_f0": 392.0,
    "avg_f0": 220.0,
    "median_f0": 215.0,
    "std_f0": 45.0,
    "min_midi": 43.2,
    "max_midi": 71.0,
    "range_semitones": 27.8,
    "voiced_ratio": 0.72,
    "confidence": 0.85,
    "voice_type": "TENOR",
    "voice_type_confidence": 0.85
  }
}
```

### 2.2 Health Check

```
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "libraries": {
    "librosa": "0.10.0",
    "numpy": "2.5.3",
    "scipy": "1.18.1"
  }
}
```

---

## 3. Project Structure

```
music-club-platform/
├── dsp-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py           # Configuration
│   │   ├── models.py           # Pydantic models
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py       # API routes
│   │   ├── audio/
│   │   │   ├── __init__.py
│   │   │   ├── preprocessor.py # Audio preprocessing
│   │   │   ├── f0_extractor.py # F0 extraction
│   │   │   └── utils.py        # Utilities
│   │   └── core/
│   │       ├── __init__.py
│   │       └── exceptions.py   # Error handling
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_f0_extractor.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
```

---

## 4. Usage

### 4.1 Install

```bash
cd dsp-service
pip install -r requirements.txt
```

### 4.2 Run

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4.3 Test

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

**Document Version:** 1.0  
**Created:** September 19, 2026  
**Status:** Complete
