"""
Library Manager
==============

Thread-safe CRUD cho thư viện bản ghi âm.
- Atomic writes (write to .tmp, then replace)
- File locking để tránh race conditions
- Validation đầu vào
- Backup tự động khi file bị corrupt
"""

import json
import shutil
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LibraryManager:
    """Quản lý thư viện bản ghi với file lock để tránh race condition."""

    def __init__(self, recordings_dir: Path, index_filename: str = "index.json"):
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.recordings_dir / index_filename
        self._lock = threading.RLock()  # reentrant lock

    # === CRUD ===

    def save(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        voice_type: str = "UNKNOWN",
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
        voice_type_confidence: Optional[float] = None,
        notes: str = "",
        duration_seconds: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Lưu file audio + metadata vào thư viện. Trả về metadata đã lưu."""
        with self._lock:
            recording_id = uuid.uuid4().hex[:12]
            file_ext = self._safe_extension(filename)
            safe_user = self._sanitize(user_id)
            save_dir = self.recordings_dir / safe_user
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / f"{recording_id}{file_ext}"

            # Write audio file
            save_path.write_bytes(file_bytes)

            # Validate
            if save_path.stat().st_size != len(file_bytes):
                raise IOError("File write verification failed")

            entry = {
                "id": recording_id,
                "user_id": safe_user,
                "filename": self._sanitize_filename(filename),
                "saved_filename": save_path.name,
                "file_path": str(save_path),
                "file_size": len(file_bytes),
                "file_ext": file_ext,
                # Voice analysis metadata (đầy đủ)
                "voice_type": voice_type or "UNKNOWN",
                "voice_type_confidence": _float(voice_type_confidence),
                "min_f0": _float(min_f0),
                "max_f0": _float(max_f0),
                "avg_f0": _float(avg_f0),
                "median_f0": None,  # backward-compat alias cho median_midi
                "std_f0": _float(std_f0),
                "p25_f0": _float(p25_f0),
                "p75_f0": _float(p75_f0),
                "iqr_f0": _float(iqr_f0),
                "min_midi": _float(min_midi),
                "max_midi": _float(max_midi),
                "median_midi": _float(median_midi),
                "range_semitones": _float(range_semitones),
                "confidence": _float(confidence),
                "voiced_ratio": _float(voiced_ratio),
                "duration_seconds": _float(duration_seconds),
                "notes": notes or "",
                "saved_at": datetime.now().isoformat(timespec="seconds"),
            }

            items = self._load_index()
            items.append(entry)
            self._save_index(items)

            logger.info(
                f"Saved recording {recording_id} for user {safe_user} "
                f"({entry['file_size']} bytes, voice_type={entry['voice_type']})"
            )
            return entry

    def list_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Lấy danh sách bản ghi của user, sắp xếp mới nhất trước."""
        with self._lock:
            safe_user = self._sanitize(user_id)
            items = self._load_index()
            user_items = [r for r in items if r.get("user_id") == safe_user]
            user_items.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
            return user_items

    def get(self, user_id: str, recording_id: str) -> Optional[Dict[str, Any]]:
        """Lấy metadata của 1 recording."""
        with self._lock:
            safe_user = self._sanitize(user_id)
            items = self._load_index()
            return next(
                (r for r in items
                 if r.get("user_id") == safe_user and r.get("id") == recording_id),
                None,
            )

    def delete(self, user_id: str, recording_id: str) -> bool:
        """Xóa recording (cả file + metadata). Trả về True nếu xóa được."""
        with self._lock:
            safe_user = self._sanitize(user_id)
            items = self._load_index()
            new_items = []
            removed = None
            for r in items:
                if r.get("user_id") == safe_user and r.get("id") == recording_id:
                    removed = r
                else:
                    new_items.append(r)

            if not removed:
                return False

            file_path = Path(removed.get("file_path", ""))
            try:
                if file_path.exists():
                    file_path.unlink()
            except OSError as e:
                logger.warning(f"Could not delete file {file_path}: {e}")

            self._save_index(new_items)
            logger.info(f"Deleted recording {recording_id} for user {safe_user}")
            return True

    def stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Thống kê tổng hợp: tổng recordings, phân bố voice type, etc."""
        with self._lock:
            items = self._load_index()
            if user_id:
                safe_user = self._sanitize(user_id)
                items = [r for r in items if r.get("user_id") == safe_user]

            if not items:
                return {
                    "total_recordings": 0,
                    "voice_type_distribution": {},
                    "avg_f0_mean": None,
                    "avg_range_semitones": None,
                    "total_size_bytes": 0,
                }

            from collections import Counter
            dist = Counter(r.get("voice_type", "UNKNOWN") for r in items)

            f0s = [r["avg_f0"] for r in items if r.get("avg_f0")]
            ranges = [r["range_semitones"] for r in items if r.get("range_semitones")]

            return {
                "total_recordings": len(items),
                "voice_type_distribution": dict(dist),
                "avg_f0_mean": round(sum(f0s) / len(f0s), 2) if f0s else None,
                "avg_range_semitones": round(sum(ranges) / len(ranges), 2) if ranges else None,
                "total_size_bytes": sum(r.get("file_size", 0) for r in items),
                "earliest": min((r["saved_at"] for r in items), default=None),
                "latest": max((r["saved_at"] for r in items), default=None),
            }

    # === Helpers ===

    def _load_index(self) -> list:
        """Đọc index.json. Nếu file corrupt → restore từ backup hoặc trả về []."""
        if not self.index_path.exists():
            return []
        try:
            with self.index_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Corrupt index.json: {e}. Trying backup.")
            backup = self.index_path.with_suffix(".bak")
            if backup.exists():
                try:
                    with backup.open("r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
            # Save corrupt file for debugging, start fresh
            corrupt = self.index_path.with_suffix(".corrupt")
            try:
                shutil.copy(self.index_path, corrupt)
            except Exception:
                pass
            return []

    def _save_index(self, items: list) -> None:
        """Atomic write: ghi vào .tmp rồi replace. Backup file cũ."""
        # Backup file hiện tại trước khi ghi đè
        if self.index_path.exists():
            backup = self.index_path.with_suffix(".bak")
            try:
                shutil.copy(self.index_path, backup)
            except Exception as e:
                logger.warning(f"Could not backup index: {e}")

        tmp_path = self.index_path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        tmp_path.replace(self.index_path)

    @staticmethod
    def _sanitize(user_id: str) -> str:
        """Sanitize user_id an toàn cho filesystem."""
        if not user_id:
            return "guest"
        safe = "".join(c for c in str(user_id) if c.isalnum() or c in "-_")
        return safe[:32] or "guest"

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Tránh path traversal trong filename."""
        if not name:
            return "recording.wav"
        # Chỉ giữ phần basename
        return Path(name).name[:128] or "recording.wav"

    @staticmethod
    def _safe_extension(filename: str) -> str:
        """Extract extension an toàn, default .wav."""
        if not filename or "." not in filename:
            return ".wav"
        ext = "." + filename.rsplit(".", 1)[-1].lower()
        allowed = {".wav", ".mp3", ".webm", ".ogg", ".m4a", ".flac", ".aac"}
        return ext if ext in allowed else ".wav"


def _float(v) -> Optional[float]:
    """Convert sang float an toàn, None nếu không hợp lệ."""
    if v is None or v == "":
        return None
    try:
        f = float(v)
        if f != f:  # NaN check
            return None
        return f
    except (TypeError, ValueError):
        return None
