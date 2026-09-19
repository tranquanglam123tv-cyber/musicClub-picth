"""
Pydantic Models
===============
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional


class VoiceAnalysisData(BaseModel):
    """Voice analysis result data."""
    min_f0: float
    max_f0: float
    avg_f0: float
    median_f0: float
    std_f0: float
    min_midi: float
    max_midi: float
    range_semitones: float
    voiced_ratio: float
    confidence: float
    voice_type: str
    voice_type_confidence: float


class VoiceAnalysisResponse(BaseModel):
    """API response for voice analysis."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    libraries: Dict[str, str]
