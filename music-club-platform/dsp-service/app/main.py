"""
FastAPI DSP Service
===================

Voice analysis service using pYIN algorithm.
"""

import os
import sys
import logging
import traceback
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dsp_service.log', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Base directory for static files
BASE_DIR = Path(__file__).parent.parent

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import numpy as np

from app.config import DSPConfig
from app.models import VoiceAnalysisResponse, HealthResponse
from app.audio.preprocessor import AudioPreprocessor
from app.audio.f0_extractor import F0Extractor
from app.core.exceptions import DSPError, AudioValidationError, F0ExtractionError
from app.library import LibraryManager

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
    try:
        import psutil  # type: ignore
        process = psutil.Process()
        uptime_seconds = time.time() - process.create_time()
        memory_mb = process.memory_info().rss / (1024 * 1024)
    except Exception:
        uptime_seconds = None
        memory_mb = None

    return HealthResponse(
        status="healthy",
        version="1.1.0",
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
    
    Accepts audio files with:
    - Formats: .wav, .webm, .mp3, .ogg, .m4a, .flac
    - Sample rate: 44100 Hz (auto-converted)
    - Duration: 10-60 seconds
    
    Returns voice analysis results including F0 statistics and voice type.
    """
    try:
        return await _analyze_voice_internal(file)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Unexpected error: {traceback.format_exc()}')
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


async def _analyze_voice_internal(file: UploadFile) -> VoiceAnalysisResponse:
    """Internal analyze voice logic."""
    # Check file format - accept multiple audio formats
    allowed_formats = ['.wav', '.webm', '.mp3', '.ogg', '.m4a', '.flac', '.aac']
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Supported formats: {', '.join(allowed_formats)}"
        )
    
    # Save uploaded file temporarily
    temp_path = BASE_DIR / f"temp_audio{file_ext}"
    wav_path = BASE_DIR / "temp_audio_converted.wav"
    
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
        logger.info(f'Saving uploaded file to {temp_path}')
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Convert to WAV if needed (frontend always sends WAV for recordings)
        if file_ext != '.wav':
            try:
                from pydub import AudioSegment
                audio_seg = AudioSegment.from_file(str(temp_path))
                audio_seg = audio_seg.set_frame_rate(44100).set_channels(1)
                audio_seg.export(str(wav_path), format='wav')
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Audio conversion failed. Please upload a .wav file. ({str(e)})"
                )
        else:
            import shutil
            shutil.copy(str(temp_path), str(wav_path))
        
        # Validate audio
        logger.info(f'Validating {wav_path}')
        validation = preprocessor.validate(str(wav_path))
        logger.info(f'Validation: {validation}')
        if not validation['valid']:
            raise HTTPException(
                status_code=400,
                detail=f"Validation failed: {'; '.join(validation['errors'])}"
            )
        
        # Preprocess audio
        try:
            logger.info(f'Preprocessing {wav_path}')
            audio_data = preprocessor.preprocess(str(wav_path))
            logger.info(f'Preprocessing OK: shape={audio_data.shape}')
        except Exception as e:
            logger.error(f'Preprocessing failed: {traceback.format_exc()}')
            raise HTTPException(
                status_code=500,
                detail=f"Preprocessing failed: {str(e)}"
            )
        
        # Check duration after preprocessing
        duration = len(audio_data) / config.SAMPLE_RATE
        if duration < 10:
            raise HTTPException(
                status_code=400,
                detail="Recording too short. Minimum 10 seconds required."
            )
        
        # Extract F0
        try:
            logger.info(f'Extracting F0 from audio of length {len(audio_data)}')
            result = f0_extractor.extract(audio_data)
            logger.info(f'F0 extraction OK: avg={result.avg_f0}')
        except Exception as e:
            logger.error(f'F0 extraction failed: {traceback.format_exc()}')
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
                "p25_f0": round(result.p25_f0, 2),
                "p75_f0": round(result.p75_f0, 2),
                "iqr_f0": round(result.iqr_f0, 2),
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
        # Clean up temp files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)


@app.get("/api/v1/pitch/analyze/{analysis_id}")
async def get_pitch_data(analysis_id: str):
    """
    Get detailed pitch contour data for visualization.
    Returns downsampled F0 data suitable for plotting.
    """
    # For demo: read latest recorded buffers if available
    try:
        import pickle, tempfile
        cache_path = Path(tempfile.gettempdir()) / f"pitch_{analysis_id}.pkl"
        if not cache_path.exists():
            raise HTTPException(status_code=404, detail="Analysis not found")
        with open(cache_path, 'rb') as f:
            data = pickle.load(f)
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Pitch data error: {e}')
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/voice/recommend-genres")
async def recommend_genres(request: dict):
    """
    Recommend music genres based on voice profile.
    Body: { voice_type: 'TENOR', min_midi: 48, max_midi: 72, range_semitones: 19 }
    """
    voice_type = request.get('voice_type', 'UNKNOWN')
    min_midi = int(request.get('min_midi', 0))
    max_midi = int(request.get('max_midi', 0))
    range_semitones = float(request.get('range_semitones', 0))

    # Recommendation logic
    recommendations = []

    # Soprano/Mezzosoprano -> Ballad, Pop, Jazz
    if voice_type in ('SOPRANO', 'MEZZO_SOPRANO'):
        recommendations = [
            {'genre': 'BALLAD', 'score': 0.95, 'reason': 'Quãng giọng cao, phù hợp ballad sâu lắng'},
            {'genre': 'POP',   'score': 0.85, 'reason': 'Catchy và dễ nghe'},
            {'genre': 'JAZZ',  'score': 0.75, 'reason': 'Phù hợp các bản jazz cổ điển'}
        ]
    elif voice_type == 'ALTO':
        recommendations = [
            {'genre': 'BALLAD',  'score': 0.90, 'reason': 'Giọng ấm, hợp ballad'},
            {'genre': 'RNB',     'score': 0.85, 'reason': 'Groove mượt mà'},
            {'genre': 'ACOUSTIC','score': 0.80, 'reason': 'Nhẹ nhàng, mộc mạc'}
        ]
    elif voice_type == 'TENOR':
        recommendations = [
            {'genre': 'POP',      'score': 0.92, 'reason': 'Quãng nam cao, sáng và mạnh'},
            {'genre': 'ROCK',     'score': 0.80, 'reason': 'Nhiều năng lượng'},
            {'genre': 'INDIE',    'score': 0.75, 'reason': 'Phong cách độc đáo'}
        ]
    elif voice_type == 'BARITONE':
        recommendations = [
            {'genre': 'ACOUSTIC', 'score': 0.90, 'reason': 'Giọng dày, hợp acoustic'},
            {'genre': 'FOLK',     'score': 0.85, 'reason': 'Truyền thống, mộc mạc'},
            {'genre': 'POP',      'score': 0.78, 'reason': 'Đa dạng bài hát'}
        ]
    elif voice_type == 'BASS':
        recommendations = [
            {'genre': 'CLASSICAL','score': 0.92, 'reason': 'Phù hợp nhạc cổ điển, opera'},
            {'genre': 'JAZZ',     'score': 0.85, 'reason': 'Smooth jazz bass'},
            {'genre': 'FOLK',     'score': 0.80, 'reason': 'Dân ca, trữ tình'}
        ]
    else:
        recommendations = [
            {'genre': 'POP', 'score': 0.70, 'reason': 'An toàn, dễ nghe'}
        ]

    # Adjust by range
    if range_semitones >= 24:    # 2 octaves
        for r in recommendations:
            r['score'] = min(1.0, r['score'] + 0.05)

    recommendations.sort(key=lambda x: x['score'], reverse=True)

    return {
        'success': True,
        'data': {
            'voice_type': voice_type,
            'recommendations': recommendations,
            'note': f'Gợi ý dựa trên {voice_type}, quãng {range_semitones:.1f} semitones'
        }
    }


@app.post("/api/v1/voice/quality-report")
async def quality_report(request: dict):
    """
    Detailed voice quality report with improvement suggestions.
    Body: { voiced_ratio, confidence, range_semitones, stability_score }
    """
    voiced_ratio = float(request.get('voiced_ratio', 0))
    confidence = float(request.get('confidence', 0))
    range_semitones = float(request.get('range_semitones', 0))
    stability = float(request.get('stability_score', 0))

    # Calculate quality grade
    score = (voiced_ratio * 0.3 + confidence * 0.3 +
             min(range_semitones/24, 1.0) * 0.2 + stability * 0.2)

    if score >= 0.85:
        grade = 'A'; emoji = '🌟'
    elif score >= 0.70:
        grade = 'B'; emoji = '👍'
    elif score >= 0.55:
        grade = 'C'; emoji = '👌'
    elif score >= 0.40:
        grade = 'D'; emoji = '💪'
    else:
        grade = 'F'; emoji = '🎯'

    suggestions = []
    if voiced_ratio < 0.5:
        suggestions.append('Hát rõ ràng hơn, tránh im lặng quá nhiều')
    if confidence < 0.5:
        suggestions.append('Tập luyện trước khi ghi âm để cải thiện độ tin cậy')
    if range_semitones < 12:
        suggestions.append('Tập mở rộng quãng giọng với các bài warm-up')
    if stability < 0.5:
        suggestions.append('Luyện hơi thở để giữ pitch ổn định')

    return {
        'success': True,
        'data': {
            'grade': grade,
            'emoji': emoji,
            'score': round(score, 3),
            'voiced_ratio': voiced_ratio,
            'confidence': confidence,
            'range_semitones': range_semitones,
            'stability_score': stability,
            'suggestions': suggestions,
            'metrics': {
                'clarity': round(voiced_ratio, 3),
                'accuracy': round(confidence, 3),
                'versatility': round(min(range_semitones/24, 1.0), 3),
                'stability': round(stability, 3)
            }
        }
    }


# =====================================================================
# RECORDINGS LIBRARY - Lưu trữ bản ghi & gợi ý bài hát phù hợp
# =====================================================================

import uuid
import json as _json
from datetime import datetime as _dt
from typing import Optional

RECORDINGS_DIR = BASE_DIR / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)
RECORDINGS_INDEX = RECORDINGS_DIR / "index.json"

# Library manager - thread-safe CRUD for recordings
library = LibraryManager(RECORDINGS_DIR)

# Song database (mini) - trong production sẽ query từ MySQL
SONGS_DB = [
    {"id": 1, "title": "Nơi này có anh", "artist": "Sơn Tùng M-TP", "min_midi": 55, "max_midi": 72,
     "difficulty": "INTERMEDIATE", "genres": ["POP", "BALLAD"]},
    {"id": 2, "title": "Hơn cả yêu", "artist": "Đức Phúc", "min_midi": 53, "max_midi": 69,
     "difficulty": "BEGINNER", "genres": ["BALLAD", "POP"]},
    {"id": 3, "title": "Chạm đáy nỗi đau", "artist": "Erik", "min_midi": 55, "max_midi": 72,
     "difficulty": "ADVANCED", "genres": ["BALLAD"]},
    {"id": 4, "title": "Đừng làm trái tim anh đau", "artist": "Sơn Tùng M-TP", "min_midi": 57, "max_midi": 74,
     "difficulty": "INTERMEDIATE", "genres": ["POP", "BALLAD"]},
    {"id": 5, "title": "Lạc", "artist": "Trúc Nhân", "min_midi": 53, "max_midi": 69,
     "difficulty": "BEGINNER", "genres": ["POP", "INDIE"]},
    {"id": 6, "title": "Yêu đơn phương", "artist": "OnlyC", "min_midi": 55, "max_midi": 70,
     "difficulty": "BEGINNER", "genres": ["POP", "BALLAD"]},
    {"id": 7, "title": "Sóng gió", "artist": "K-ICM, Jack", "min_midi": 57, "max_midi": 74,
     "difficulty": "INTERMEDIATE", "genres": ["POP", "ELECTRONIC"]},
    {"id": 8, "title": "Thằng điên", "artist": "Justatee, Phương Ly", "min_midi": 55, "max_midi": 72,
     "difficulty": "INTERMEDIATE", "genres": ["POP", "RNB"]},
    {"id": 9, "title": "Đi để trở về", "artist": "Soobin Hoàng Sơn", "min_midi": 53, "max_midi": 69,
     "difficulty": "BEGINNER", "genres": ["ACOUSTIC", "BALLAD"]},
    {"id": 10, "title": "Chúng ta không thuộc về nhau", "artist": "Sơn Tùng M-TP", "min_midi": 57, "max_midi": 74,
     "difficulty": "ADVANCED", "genres": ["POP", "BALLAD"]},
    {"id": 11, "title": "Em gái mưa", "artist": "Hương Tràm", "min_midi": 55, "max_midi": 72,
     "difficulty": "INTERMEDIATE", "genres": ["BALLAD"]},
    {"id": 12, "title": "Có chàng trai viết lên cây", "artist": "Phùng Khánh Linh", "min_midi": 53, "max_midi": 70,
     "difficulty": "BEGINNER", "genres": ["ACOUSTIC", "INDIE"]},
    {"id": 13, "title": "Túy âm", "artist": "Xesi, Masew, Nhật Nguyệt", "min_midi": 55, "max_midi": 72,
     "difficulty": "INTERMEDIATE", "genres": ["ELECTRONIC", "POP"]},
    {"id": 14, "title": "Nắm tay em đi", "artist": "Vũ Thảo My", "min_midi": 53, "max_midi": 69,
     "difficulty": "BEGINNER", "genres": ["ACOUSTIC", "BALLAD"]},
    {"id": 15, "title": "Hồng nhan", "artist": "Gia Ân", "min_midi": 55, "max_midi": 72,
     "difficulty": "INTERMEDIATE", "genres": ["ACOUSTIC", "BALLAD"]},
    {"id": 16, "title": "Đến bên em", "artist": "Lynk Lee", "min_midi": 57, "max_midi": 74,
     "difficulty": "ADVANCED", "genres": ["BALLAD", "RNB"]},
    {"id": 17, "title": "Lời chưa nói", "artist": "Phan Mạnh Quỳnh", "min_midi": 48, "max_midi": 67,
     "difficulty": "INTERMEDIATE", "genres": ["ACOUSTIC", "BALLAD"]},
    {"id": 18, "title": "Cao ốc 20", "artist": "B-Ray, Masew", "min_midi": 48, "max_midi": 67,
     "difficulty": "BEGINNER", "genres": ["POP", "ELECTRONIC"]},
    {"id": 19, "title": "Anh muốn em sống sao", "artist": "B Ray", "min_midi": 48, "max_midi": 69,
     "difficulty": "INTERMEDIATE", "genres": ["POP"]},
    {"id": 20, "title": "Đã lỡ yêu em nhiều", "artist": "Justatee", "min_midi": 55, "max_midi": 70,
     "difficulty": "INTERMEDIATE", "genres": ["BALLAD", "POP"]},
]


@app.post("/api/v1/voice/save-recording")
async def save_recording(
    file: UploadFile = File(...),
    user_id: str = "guest",
    voice_type: str = "UNKNOWN",
    voice_type_confidence: Optional[float] = None,
    min_midi: Optional[float] = None,
    max_midi: Optional[float] = None,
    median_midi: Optional[float] = None,
    avg_f0: Optional[float] = None,
    min_f0: Optional[float] = None,
    max_f0: Optional[float] = None,
    std_f0: Optional[float] = None,
    p25_f0: Optional[float] = None,
    p75_f0: Optional[float] = None,
    iqr_f0: Optional[float] = None,
    range_semitones: Optional[float] = None,
    confidence: Optional[float] = None,
    voiced_ratio: Optional[float] = None,
    notes: Optional[str] = None,
):
    """
    Lưu bản ghi âm + metadata phân tích đầy đủ vào thư viện.

    Frontend gọi endpoint này sau khi analyze thành công để lưu giữ
    bản ghi và metadata đi kèm (voice type, F0 stats, MIDI range...).
    """
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")

        # Estimate duration nếu có thể
        duration = None
        try:
            import io, soundfile as _sf
            info = _sf.info(io.BytesIO(content))
            duration = float(info.duration)
        except Exception:
            pass

        entry = library.save(
            file_bytes=content,
            filename=file.filename or "recording.wav",
            user_id=user_id,
            voice_type=voice_type,
            voice_type_confidence=voice_type_confidence,
            min_midi=min_midi, max_midi=max_midi, median_midi=median_midi,
            min_f0=min_f0, max_f0=max_f0, avg_f0=avg_f0, std_f0=std_f0,
            p25_f0=p25_f0, p75_f0=p75_f0, iqr_f0=iqr_f0,
            range_semitones=range_semitones,
            confidence=confidence,
            voiced_ratio=voiced_ratio,
            notes=notes,
            duration_seconds=duration,
        )

        return {
            "success": True,
            "data": {
                "recording_id": entry["id"],
                "voice_type": entry["voice_type"],
                "saved_path": entry["file_path"],
                "file_size": entry["file_size"],
                "saved_at": entry["saved_at"],
                "message": "Bản ghi đã được lưu vào thư viện.",
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Save recording error: {traceback.format_exc()}')
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/recordings/{user_id}")
async def list_recordings(user_id: str):
    """Lấy danh sách bản ghi của một user (mới nhất trước)."""
    items = library.list_user(user_id)
    return {"success": True, "data": items, "count": len(items)}


@app.get("/api/v1/recordings/{user_id}/{recording_id}")
async def get_recording(user_id: str, recording_id: str):
    """Lấy metadata chi tiết của một bản ghi."""
    rec = library.get(user_id, recording_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found")
    return {"success": True, "data": rec}


@app.get("/api/v1/recordings/{user_id}/{recording_id}/audio")
async def get_recording_audio(user_id: str, recording_id: str):
    """Phát lại file audio đã lưu."""
    rec = library.get(user_id, recording_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found")
    file_path = Path(rec.get("file_path"))
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file missing")
    media_type = "audio/wav" if rec.get("file_ext") == ".wav" else "audio/mpeg"
    return FileResponse(str(file_path), media_type=media_type)


@app.delete("/api/v1/recordings/{user_id}/{recording_id}")
async def delete_recording(user_id: str, recording_id: str):
    """Xóa bản ghi (cả file audio + metadata)."""
    ok = library.delete(user_id, recording_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Recording not found")
    return {"success": True, "data": {"deleted": recording_id}}


@app.get("/api/v1/stats/{user_id}")
async def recordings_stats(user_id: str):
    """Thống kê tổng hợp về các bản ghi của user."""
    return {"success": True, "data": library.stats(user_id)}


@app.post("/api/v1/recordings/compare")
async def compare_recordings(request: dict):
    """
    So sánh 2 bản ghi cùng user.

    Input: { user_id, recording_id_a, recording_id_b }

    Output:
        - metrics cho từng bản ghi
        - deltas (B - A)
        - similarity_score (0-100)
        - insights (nhận xét)
    """
    user_id = request.get("user_id", "")
    id_a = request.get("recording_id_a", "")
    id_b = request.get("recording_id_b", "")

    if not (user_id and id_a and id_b):
        raise HTTPException(status_code=400, detail="Missing user_id / recording_id_a / recording_id_b")
    if id_a == id_b:
        raise HTTPException(status_code=400, detail="Cannot compare a recording with itself")

    rec_a = library.get(user_id, id_a)
    rec_b = library.get(user_id, id_b)
    if not rec_a or not rec_b:
        raise HTTPException(status_code=404, detail="Recording(s) not found")

    def _delta(a, b):
        if a is None or b is None:
            return None
        try:
            return round(float(b) - float(a), 3)
        except (TypeError, ValueError):
            return None

    def _pct_change(a, b):
        if a is None or b is None or float(a) == 0:
            return None
        try:
            return round((float(b) - float(a)) / abs(float(a)) * 100, 1)
        except (TypeError, ValueError, ZeroDivisionError):
            return None

    # === Similarity score ===
    # Weighted average of normalized differences
    weights = {
        "avg_f0":      0.30,  # 30% pitch center
        "range_semitones": 0.25,  # 25% range
        "voiced_ratio":0.15,  # 15% voice activity
        "confidence":  0.15,  # 15% confidence
        "std_f0":      0.15,  # 15% variability
    }
    similarity = 100.0
    breakdown = {}
    for field, w in weights.items():
        a, b = rec_a.get(field), rec_b.get(field)
        if a is None or b is None or float(a) == 0:
            continue
        diff_pct = abs(float(b) - float(a)) / (abs(float(a)) + 1e-6) * 100
        # Cap diff to avoid extreme outlier ruining score
        diff_pct = min(diff_pct, 100)
        contribution = w * diff_pct
        similarity -= contribution
        breakdown[field] = {
            "a": float(a),
            "b": float(b),
            "diff_pct": round(diff_pct, 1),
            "weight": w,
        }
    similarity = round(max(0.0, similarity), 1)

    # === Insights ===
    insights = []
    voice_changed = rec_a.get("voice_type") != rec_b.get("voice_type")
    if voice_changed:
        insights.append(
            f"🔄 Voice type thay đổi: {rec_a.get('voice_type', '?')} → {rec_b.get('voice_type', '?')}"
        )

    range_delta = _delta(rec_a.get("range_semitones"), rec_b.get("range_semitones"))
    if range_delta is not None:
        if range_delta > 2:
            insights.append(f"📈 Quãng giọng mở rộng thêm {range_delta:.1f} semitones")
        elif range_delta < -2:
            insights.append(f"📉 Quãng giọng thu hẹp {abs(range_delta):.1f} semitones")

    conf_delta = _delta(rec_a.get("confidence"), rec_b.get("confidence"))
    if conf_delta is not None and abs(conf_delta) > 0.05:
        direction = "tăng" if conf_delta > 0 else "giảm"
        insights.append(f"🎯 Độ tin cậy {direction} {abs(conf_delta)*100:.0f}%")

    voiced_delta = _delta(rec_a.get("voiced_ratio"), rec_b.get("voiced_ratio"))
    if voiced_delta is not None and abs(voiced_delta) > 0.05:
        direction = "tốt hơn" if voiced_delta > 0 else "kém hơn"
        insights.append(f"🎤 Tỷ lệ giọng hát {direction} {abs(voiced_delta)*100:.0f}%")

    if similarity >= 85:
        insights.append("✨ Hai bản ghi rất giống nhau — phong cách hát ổn định!")
    elif similarity >= 60:
        insights.append("👍 Có sự khác biệt vừa phải.")
    else:
        insights.append("⚡ Có sự khác biệt lớn — kiểm tra lại thiết bị thu hoặc phong cách hát.")

    return {
        "success": True,
        "data": {
            "recording_a": {
                "id": rec_a["id"],
                "filename": rec_a["filename"],
                "saved_at": rec_a["saved_at"],
                "voice_type": rec_a.get("voice_type"),
                "avg_f0": rec_a.get("avg_f0"),
                "min_f0": rec_a.get("min_f0"),
                "max_f0": rec_a.get("max_f0"),
                "range_semitones": rec_a.get("range_semitones"),
                "voiced_ratio": rec_a.get("voiced_ratio"),
                "confidence": rec_a.get("confidence"),
                "std_f0": rec_a.get("std_f0"),
            },
            "recording_b": {
                "id": rec_b["id"],
                "filename": rec_b["filename"],
                "saved_at": rec_b["saved_at"],
                "voice_type": rec_b.get("voice_type"),
                "avg_f0": rec_b.get("avg_f0"),
                "min_f0": rec_b.get("min_f0"),
                "max_f0": rec_b.get("max_f0"),
                "range_semitones": rec_b.get("range_semitones"),
                "voiced_ratio": rec_b.get("voiced_ratio"),
                "confidence": rec_b.get("confidence"),
                "std_f0": rec_b.get("std_f0"),
            },
            "deltas": {
                "avg_f0": _delta(rec_a.get("avg_f0"), rec_b.get("avg_f0")),
                "min_f0": _delta(rec_a.get("min_f0"), rec_b.get("min_f0")),
                "max_f0": _delta(rec_a.get("max_f0"), rec_b.get("max_f0")),
                "range_semitones": _delta(rec_a.get("range_semitones"), rec_b.get("range_semitones")),
                "voiced_ratio": _delta(rec_a.get("voiced_ratio"), rec_b.get("voiced_ratio")),
                "confidence": _delta(rec_a.get("confidence"), rec_b.get("confidence")),
                "std_f0": _delta(rec_a.get("std_f0"), rec_b.get("std_f0")),
                "pct_changes": {
                    "avg_f0": _pct_change(rec_a.get("avg_f0"), rec_b.get("avg_f0")),
                    "range_semitones": _pct_change(rec_a.get("range_semitones"), rec_b.get("range_semitones")),
                    "voiced_ratio": _pct_change(rec_a.get("voiced_ratio"), rec_b.get("voiced_ratio")),
                }
            },
            "similarity_score": similarity,
            "similarity_breakdown": breakdown,
            "insights": insights,
        }
    }


@app.post("/api/v1/recordings/export")
async def export_recordings_csv(user_id: str):
    """Xuất toàn bộ metadata recordings của user ra CSV."""
    import csv
    import io

    items = library.list_user(user_id)
    if not items:
        raise HTTPException(status_code=404, detail="No recordings to export")

    # Build CSV in memory
    buf = io.StringIO()
    fieldnames = [
        "id", "filename", "saved_at", "duration_seconds",
        "voice_type", "voice_type_confidence",
        "min_f0", "max_f0", "avg_f0", "median_f0", "std_f0",
        "p25_f0", "p75_f0", "iqr_f0",
        "min_midi", "max_midi", "median_midi",
        "range_semitones", "voiced_ratio", "confidence",
        "file_size", "file_ext", "notes"
    ]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for it in items:
        # Compute median_midi from median_f0 if not present
        if not it.get("median_midi") and it.get("median_f0"):
            it["median_midi"] = round(12 * __import__('math').log2(it["median_f0"] / 440) + 69, 2)
        writer.writerow(it)

    from fastapi.responses import Response
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=recordings_{user_id}.csv"}
    )


@app.post("/api/v1/recordings/{user_id}/{recording_id}/reanalyze")
async def reanalyze_recording(user_id: str, recording_id: str):
    """Phân tích lại một bản ghi đã lưu (dùng khi bản ghi cũ bị thiếu metadata).

    Đọc lại file audio từ ổ cứng, chạy pipeline F0 extraction đầy đủ,
    cập nhật metadata trong index.
    """
    rec = library.get(user_id, recording_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found")
    file_path = Path(rec.get("file_path", ""))
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file missing")

    try:
        # Validate
        validation = preprocessor.validate(str(file_path))
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid audio: {'; '.join(validation['errors'])}",
            )

        # Preprocess + extract
        audio_data = preprocessor.preprocess(str(file_path))
        result = f0_extractor.extract(audio_data)
        if result.voiced_ratio < 0.1:
            raise HTTPException(status_code=400, detail="No voiced speech detected")

        duration = len(audio_data) / config.SAMPLE_RATE

        # Update metadata
        items = library._load_index()
        for r in items:
            if r.get("user_id") == rec["user_id"] and r.get("id") == recording_id:
                r.update({
                    "voice_type": result.voice_type,
                    "voice_type_confidence": round(result.voice_type_confidence, 3),
                    "min_f0": round(result.min_f0, 2),
                    "max_f0": round(result.max_f0, 2),
                    "avg_f0": round(result.avg_f0, 2),
                    "median_f0": round(result.median_f0, 2),
                    "std_f0": round(result.std_f0, 2),
                    "p25_f0": round(result.p25_f0, 2),
                    "p75_f0": round(result.p75_f0, 2),
                    "iqr_f0": round(result.iqr_f0, 2),
                    "min_midi": round(result.min_midi, 2),
                    "max_midi": round(result.max_midi, 2),
                    "range_semitones": round(result.range_semitones, 2),
                    "confidence": round(result.confidence, 3),
                    "voiced_ratio": round(result.voiced_ratio, 3),
                    "duration_seconds": round(duration, 2),
                    "reanalyzed_at": _dt.now().isoformat(timespec="seconds"),
                })
                break
        library._save_index(items)

        return {
            "success": True,
            "data": {
                "recording_id": recording_id,
                "voice_type": result.voice_type,
                "min_f0": round(result.min_f0, 2),
                "max_f0": round(result.max_f0, 2),
                "avg_f0": round(result.avg_f0, 2),
                "range_semitones": round(result.range_semitones, 2),
                "message": "Đã phân tích lại và cập nhật metadata.",
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reanalyze error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# === Migrate legacy index.json on startup (one-time) ===
def _migrate_legacy_index():
    if not RECORDINGS_INDEX.exists():
        return
    try:
        current = library._load_index()
        if current:
            return
        with RECORDINGS_INDEX.open("r", encoding="utf-8") as f:
            legacy = _json.load(f)
        if legacy:
            library._save_index(legacy)
            logger.info(f"Migrated {len(legacy)} legacy recordings into library")
    except Exception as e:
        logger.warning(f"Legacy migration skipped: {e}")

_migrate_legacy_index()


def _midi_to_note(midi: float) -> str:
    """Convert MIDI number sang note name (vd: 60 -> C4)."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    midi_int = int(round(midi))
    note = notes[midi_int % 12]
    octave = (midi_int // 12) - 1
    return f"{note}{octave}"


# ── Recommendation scoring helpers ───────────────────────────────────────────
_WEIGHTS = {'range': 0.60, 'genre': 0.25, 'key': 0.10, 'difficulty': 0.05}

# Key compatibility wheel (roadmap section 8.5.4)
_KEY_COMPAT = {
    'C':  ['G', 'F', 'Am', 'Dm', 'Em'],
    'C#': ['G#', 'F#', 'A#m', 'D#m', 'Fm'],
    'D':  ['A', 'G', 'Bm', 'Em', 'F#m'],
    'Eb': ['Bb', 'F', 'Cm', 'Gm', 'Am'],
    'E':  ['B', 'A', 'C#m', 'G#m', 'F#m'],
    'F':  ['C', 'Bb', 'Dm', 'Am', 'Bm'],
    'F#': ['C#', 'B', 'D#m', 'A#m', 'Bbm'],
    'G':  ['D', 'C', 'Em', 'Bm', 'Am'],
    'Ab': ['Eb', 'Db', 'Cbm', 'Fm', 'Gm'],
    'A':  ['E', 'D', 'C#m', 'F#m', 'Bm'],
    'Bb': ['F', 'Eb', 'Gm', 'Cm', 'Dm'],
    'B':  ['F#', 'E', 'G#m', 'D#m', 'C#m'],
}

# Voice-type comfortable keys (roadmap 8.5.4)
_VT_KEYS = {
    'BASS':          ['C', 'D', 'E', 'F'],
    'BARITONE':      ['D', 'E', 'F', 'G'],
    'TENOR':         ['F', 'G', 'A', 'Bb'],
    'ALTO':          ['G', 'A', 'Bb', 'C'],
    'MEZZO_SOPRANO': ['A', 'Bb', 'C', 'D'],
    'SOPRANO':       ['C', 'D', 'E', 'F#'],
}


def _score_range(user_min_m: int, user_max_m: int,
                 song_min_m: int, song_max_m: int) -> float:
    """
    Range Score (60% weight) — roadmap section 8.5.2.

    Perfect match: entire song fits in user's comfortable range.
    Sweet-spot bonus: song stays within 3 st of user's center.
    """
    overlap_min = max(user_min_m, song_min_m)
    overlap_max = min(user_max_m, song_max_m)

    if overlap_min > overlap_max:
        return 0.0

    overlap_st = overlap_max - overlap_min
    song_st = song_max_m - song_min_m
    if song_st <= 0:
        return 0.0

    # % of song user can sing comfortably
    score = overlap_st / song_st

    # Sweet-spot bonus: 3 st from center
    user_center = (user_min_m + user_max_m) / 2
    sweet_lo = user_min_m + 3
    sweet_hi = user_max_m - 3
    if song_min_m >= sweet_lo and song_max_m <= sweet_hi:
        score = min(1.0, score * 1.1)

    return round(score, 3)


def _score_genre(preferred: list, song_genres: list) -> float:
    """
    Genre Score (25% weight) — roadmap section 8.5.3.

    Primary genre = weight 1.0, secondary = 0.5.
    Preference normalised from 1-5 to 0-1.
    """
    if not song_genres:
        return 0.0
    matched = 0.0
    total = 0.0
    for g in song_genres:
        pref = 0  # default: unknown preference = neutral
        if g in preferred:
            pref = 3  # map unknown to middle preference
        norm = (pref - 1) / 4  # 0-1 scale
        matched += norm * 1.0
        total += 1.0
    return round(matched / total, 3) if total > 0 else 0.0


def _score_key(voice_type: str, song_key: str) -> float:
    """
    Key Score (10% weight) — roadmap section 8.5.4.

    Perfect key for voice type = 1.0.
    Compatible key (in wheel) = 0.8.
    Requires transposition = 0.5.
    """
    if not song_key:
        return 0.5
    root = song_key[0] if len(song_key) > 0 else None
    if not root:
        return 0.5
    comfortable = _VT_KEYS.get(voice_type, ['C', 'D', 'E', 'F', 'G'])
    if root in comfortable:
        return 1.0
    # Check key wheel for compatible keys
    compat = _KEY_COMPAT.get(root, [])
    for k in compat:
        if k in comfortable:
            return 0.8
    return 0.5


def _score_difficulty(user_range_st: float, song_diff: str) -> float:
    """
    Difficulty Score (5% weight) — roadmap section 8.5.5.

    Ideal: user's median difficulty ≈ song difficulty.
    Defaults to INTERMEDIATE for new users (range ~12-22 st).
    """
    diff_map = {'BEGINNER': 1, 'INTERMEDIATE': 2, 'ADVANCED': 3, 'EXPERT': 4}

    # Estimate user level from range
    if user_range_st < 10:
        user_level = 1
    elif user_range_st < 16:
        user_level = 2
    elif user_range_st < 22:
        user_level = 3
    else:
        user_level = 4

    song_level = diff_map.get(song_diff, 2)
    diff = abs(user_level - song_level)

    table = {0: 1.0, 1: 0.7, 2: 0.4, 3: 0.1}
    return table.get(diff, 0.1)


@app.post("/api/v1/voice/recommend-songs")
async def recommend_songs(request: dict):
    """
    Gợi ý bài hát phù hợp với giọng hát.

    Input:
        voice_type        : 'TENOR', 'BARITONE', ...
        min_midi          : comfortable min MIDI (P25)
        max_midi          : comfortable max MIDI (P75)
        range_semitones   : tessitura width in semitones
        preferred_genres   : list of preferred genre codes (optional)
        max_results       : number of results (default 10)

    Algorithm (roadmap section 8.5.1):
        FinalScore = (RangeScore x 0.60)
                   + (GenreScore x 0.25)
                   + (KeyScore x 0.10)
                   + (DifficultyScore x 0.05)

    Returns per-song:
        - final score (0-1)
        - breakdown by component
        - match reasons in Vietnamese
        - overlap percentage
    """
    voice_type = request.get('voice_type', 'UNKNOWN')
    min_midi = int(request.get('min_midi', 0))
    max_midi = int(request.get('max_midi', 0))
    range_semitones = float(request.get('range_semitones', 12))
    preferred = request.get('preferred_genres') or []
    max_results = int(request.get('max_results', 10))

    if min_midi >= max_midi or min_midi <= 0:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Invalid MIDI range"}
        )

    scored = []
    for song in SONGS_DB:
        s_min = song.get('min_midi', 0)
        s_max = song.get('max_midi', 100)
        s_genres = song.get('genres', [])
        s_key = song.get('original_key', '')
        s_diff = song.get('difficulty', 'INTERMEDIATE')

        # ── Component scores ────────────────────────────────────────
        range_score      = _score_range(min_midi, max_midi, s_min, s_max)
        genre_score      = _score_genre(preferred, s_genres)
        key_score        = _score_key(voice_type, s_key)
        diff_score       = _score_difficulty(range_semitones, s_diff)

        final_score = (
            _WEIGHTS['range']      * range_score
            + _WEIGHTS['genre']    * genre_score
            + _WEIGHTS['key']      * key_score
            + _WEIGHTS['difficulty']* diff_score
        )

        # ── Match reasons (Vietnamese) ───────────────────────────────
        reasons = []

        # Range
        overlap_min = max(min_midi, s_min)
        overlap_max = min(max_midi, s_max)
        if overlap_min <= overlap_max:
            pct = min(100, int(
                (overlap_max - overlap_min) / max(s_max - s_min, 1) * 100
            ))
            if pct >= 90:
                reasons.append(f'Trong vung thoai mai ({pct}% overlap)')
            elif pct >= 60:
                reasons.append(f'Phu hop ({pct}% overlap)')
            else:
                reasons.append(f'Mot phan trong vung ({pct}% overlap)')
        else:
            reasons.append(f'Nam ngoai vung thoai mai')

        # Genre
        if preferred and any(g in preferred for g in s_genres):
            matched = [g for g in preferred if g in s_genres]
            reasons.append(f'The loai yeu thich: {", ".join(matched)}')

        # Key
        root = s_key[0] if s_key else None
        comfortable = _VT_KEYS.get(voice_type, [])
        if root in comfortable:
            reasons.append(f'Khoa {root} phu hop voi giong {voice_type}')

        # Difficulty
        diff_labels = {
            'BEGINNER': 'de', 'INTERMEDIATE': 'trung binh',
            'ADVANCED': 'cao', 'EXPERT': 'chuyen sau'
        }
        reasons.append(f'Do kho {diff_labels.get(s_diff, "trung binh")}')

        scored.append({
            **song,
            "match_score": round(final_score, 3),
            "match_pct": int(min(final_score * 100, 100)),
            "scoring_breakdown": {
                "range_score":      round(range_score, 3),
                "genre_score":      round(genre_score, 3),
                "key_score":        round(key_score, 3),
                "difficulty_score": round(diff_score, 3),
                "weights": _WEIGHTS,
            },
            "overlap_pct": int(min(
                max(overlap_max - overlap_min, 0) / max(s_max - s_min, 1) * 100, 100
            )),
            "reasons": reasons,
        })

    scored.sort(key=lambda x: x['match_score'], reverse=True)
    top = scored[:max_results]

    return {
        "success": True,
        "data": {
            "voice_type": voice_type,
            "user_range": {
                "min_note": _midi_to_note(min_midi) if min_midi else None,
                "max_note": _midi_to_note(max_midi) if max_midi else None,
                "min_midi": min_midi,
                "max_midi": max_midi,
                "range_semitones": round(range_semitones, 1),
            },
            "weights": _WEIGHTS,
            "total_candidates": len(SONGS_DB),
            "recommendations": top,
            "algorithm": "roadmap-v3.3 (range 60% + genre 25% + key 10% + difficulty 5%)"
        }
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Music Club DSP Service",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/index.html")
async def serve_index():
    """Serve the main UI page."""
    index_path = BASE_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    raise HTTPException(status_code=404, detail="Index file not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
