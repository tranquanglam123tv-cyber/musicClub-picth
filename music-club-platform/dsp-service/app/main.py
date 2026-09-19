"""
FastAPI DSP Service
===================

Voice analysis service using pYIN algorithm.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np

from app.config import DSPConfig
from app.models import VoiceAnalysisResponse, HealthResponse
from app.audio.preprocessor import AudioPreprocessor
from app.audio.f0_extractor import F0Extractor
from app.core.exceptions import DSPError, AudioValidationError, F0ExtractionError

# Create FastAPI app
app = FastAPI(
    title="Music Club DSP Service",
    description="Voice analysis service for music club platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
config = DSPConfig()
preprocessor = AudioPreprocessor()
f0_extractor = F0Extractor(config)


@app.get("/api/v1/health")
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    import librosa
    import scipy
    import numpy
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        libraries={
            "librosa": librosa.__version__,
            "scipy": scipy.__version__,
            "numpy": numpy.__version__
        }
    )


@app.post("/api/v1/voice/analyze")
async def analyze_voice(file: UploadFile = File(...)) -> VoiceAnalysisResponse:
    """
    Analyze voice from audio file.
    
    Accepts WAV file with:
    - Sample rate: 44100 Hz
    - Channels: 1 (mono)
    - Duration: 10-60 seconds
    
    Returns voice analysis results including F0 statistics and voice type.
    """
    # Check file format
    if not file.filename.endswith('.wav'):
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Only WAV files are supported."
        )
    
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    try:
        # Read file content
        content = await file.read()
        
        # Check file size
        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > 10:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10 MB."
            )
        
        # Save to temp file
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Validate audio
        validation = preprocessor.validate(temp_path)
        if not validation['valid']:
            raise HTTPException(
                status_code=400,
                detail=f"Validation failed: {'; '.join(validation['errors'])}"
            )
        
        # Preprocess audio
        try:
            audio = preprocessor.preprocess(temp_path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Preprocessing failed: {str(e)}"
            )
        
        # Check duration after preprocessing
        duration = len(audio) / config.sample_rate
        if duration < 10:
            raise HTTPException(
                status_code=400,
                detail="Recording too short. Minimum 10 seconds required."
            )
        
        # Extract F0
        try:
            result = f0_extractor.extract(audio)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"F0 extraction failed: {str(e)}"
            )
        
        # Check for no voiced data
        if result.voiced_ratio < 0.1:
            raise HTTPException(
                status_code=400,
                detail="No voiced speech detected in recording."
            )
        
        # Return response
        return VoiceAnalysisResponse(
            success=True,
            data={
                "min_f0": round(result.min_f0, 2),
                "max_f0": round(result.max_f0, 2),
                "avg_f0": round(result.avg_f0, 2),
                "median_f0": round(result.median_f0, 2),
                "std_f0": round(result.std_f0, 2),
                "min_midi": round(result.min_midi, 2),
                "max_midi": round(result.max_midi, 2),
                "range_semitones": round(result.range_semitones, 2),
                "voiced_ratio": round(result.voiced_ratio, 3),
                "confidence": round(result.confidence, 3),
                "voice_type": result.voice_type,
                "voice_type_confidence": round(result.voice_type_confidence, 3)
            }
        )
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Music Club DSP Service",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
