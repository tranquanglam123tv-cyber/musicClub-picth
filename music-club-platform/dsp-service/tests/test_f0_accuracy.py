"""
F0 Accuracy Evaluation Script
=============================
Measures pitch detection accuracy in cents (1 semitone = 100 cents).
Ground truth from synthetic test tones with known fundamental frequencies.

Usage:
    python tests/test_f0_accuracy.py
"""
import sys
sys.path.insert(0, '.')
import numpy as np
import soundfile as sf
import tempfile
from pathlib import Path

from app.audio.preprocessor import AudioPreprocessor
from app.audio.f0_extractor import F0Extractor

# temp dir works on Windows too
TMP = Path(tempfile.gettempdir())

# ── helpers ────────────────────────────────────────────────────────────────
SAMPLE_RATE = 44100
A4 = 440.0

def hz_to_midi(hz):
    if hz <= 0: return 0
    return 12 * np.log2(hz / A4) + 69

def midi_to_note(midi):
    names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    n = int(round(midi))
    return f"{names[n % 12]}{(n // 12) - 1}"

def error_cents(measured, truth):
    if measured <= 0 or truth <= 0:
        return None
    return abs(1200 * np.log2(measured / truth))

def grade_cents(err):
    if err is None: return "N/A"
    if err < 5:   return "A*"
    if err < 10:  return "A"
    if err < 20:  return "B"
    if err < 50:  return "C"
    return "FAIL"

def synthesize_tone(freq, duration=3.0, vibrato_hz=5.0, vibrato_depth=0.012):
    """Create a synthetic vocal-like tone with vibrato and harmonics."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n)
    lfo = 1.0 + vibrato_depth * np.sin(2 * np.pi * vibrato_hz * t)
    audio = np.sin(2 * np.pi * freq * lfo * t)
    for h in range(2, 5):
        audio += (0.4 / h) * np.sin(2 * np.pi * freq * h * lfo * t)
    audio += 0.08 * np.random.randn(n)
    peak = np.max(np.abs(audio))
    audio = audio / peak * 0.707
    return audio.astype(np.float32)

def tmp_wav(name):
    return str(TMP / name)

# ── voice-type test grid ───────────────────────────────────────────────────
VOICE_GRID = [
    ("BASS",        [82, 98, 110, 130]),
    ("BARITONE",    [110, 123, 147, 165]),
    ("TENOR",       [147, 165, 196, 220]),
    ("ALTO",        [220, 262, 294, 330]),
    ("MEZZO",       [294, 330, 392, 440]),
    ("SOPRANO",     [440, 523, 587, 698]),
]

extractor = F0Extractor()
preprocessor = AudioPreprocessor()

# ── 1. Synthetic accuracy per voice type ───────────────────────────────────
print("=" * 70)
print("F0 ACCURACY EVALUATION  (target: < 10 cents = grade A)")
print("=" * 70)

print("\n[1] SYNTHETIC TONES - per voice type")
print("  Voice         | Freq Hz | Note  | Median Hz  | Err(ct)  | Grade")
print("  " + "-" * 60)

results = {}
for voice, freqs in VOICE_GRID:
    voice_results = []
    for freq in freqs:
        audio = synthesize_tone(freq, duration=3.0)
        wav = tmp_wav("_eval_tone.wav")
        sf.write(wav, audio, SAMPLE_RATE)

        audio_clean = preprocessor.preprocess(wav)
        r = extractor.extract(audio_clean)

        err = error_cents(r.pitch_estimate, freq)
        grade = grade_cents(err)
        voice_results.append(err)

        note = midi_to_note(hz_to_midi(freq))
        median_str = f"{r.pitch_estimate:.1f}" if r.pitch_estimate else "N/A"
        err_str = f"{err:.2f}" if err is not None else "N/A"
        ok_flag = "  " if err and err < 10 else " !"
        print(f"{ok_flag} {voice:12} | {freq:7.1f} | {note:5} | {median_str:9} | {err_str:8} | {grade}")

    results[voice] = voice_results

# summary per voice type
print("\n  Voice Type Summary:")
print("  Voice         | Mean err(ct) | Max err(ct) | All <10ct?")
print("  " + "-" * 52)
for voice, errs in results.items():
    mean_e = np.mean([e for e in errs if e is not None])
    max_e  = np.max([e for e in errs if e is not None])
    ok = "YES" if max_e < 10 else "NO"
    print(f"  {voice:12} | {mean_e:12.2f} | {max_e:11.2f} | {ok}")

# ── 2. Effect of duration ─────────────────────────────────────────────────
print("\n[2] DURATION vs ACCURACY (220 Hz)")
print("  Duration  | Err(ct)  | Grade")
print("  " + "-" * 30)
ref_freq = 220.0
for dur in [1.0, 2.0, 3.0, 5.0, 10.0]:
    audio = synthesize_tone(ref_freq, duration=dur)
    wav = tmp_wav("_eval_dur.wav")
    sf.write(wav, audio, SAMPLE_RATE)
    r = extractor.extract(preprocessor.preprocess(wav))
    err = error_cents(r.pitch_estimate, ref_freq)
    g = grade_cents(err)
    e_str = f"{err:.2f}" if err else "N/A"
    print(f"  {dur:9.1f}s | {e_str:8} | {g}")

# ── 3. Effect of vibrato depth ────────────────────────────────────────────
print("\n[3] VIBRATO DEPTH vs ACCURACY (3s, 220 Hz)")
print("  Vibrato % | Err(ct)  | Grade")
print("  " + "-" * 30)
for pct in [0, 0.5, 1.0, 1.2, 2.0, 3.0]:
    audio = synthesize_tone(220.0, duration=3.0, vibrato_depth=pct/100)
    wav = tmp_wav("_eval_vib.wav")
    sf.write(wav, audio, SAMPLE_RATE)
    r = extractor.extract(preprocessor.preprocess(wav))
    err = error_cents(r.pitch_estimate, 220.0)
    g = grade_cents(err)
    e_str = f"{err:.2f}" if err else "N/A"
    print(f"  {pct:9.1f}% | {e_str:8} | {g}")

# ── 4. Real recordings ────────────────────────────────────────────────────
print("\n[4] REAL RECORDINGS")
real_dir = Path("recordings/guest")
if real_dir.exists():
    recordings = sorted(real_dir.glob("*.wav"))
    print("  Filename                      | Median Hz | Est Note | Quality")
    print("  " + "-" * 65)
    for wav in recordings:
        try:
            r = extractor.extract(preprocessor.preprocess(str(wav)))
            if r.voiced_ratio < 0.1:
                print(f"  {wav.name:28} | BAD QUALITY (voiced_ratio={r.voiced_ratio:.2f})")
                continue
            note = midi_to_note(hz_to_midi(r.median_f0))
            qual = "A" if r.voice_type_confidence > 0.4 else "B" if r.voice_type_confidence > 0.2 else "C"
            print(f"  {wav.name:28} | {r.median_f0:9.1f} | {note:8} | [{qual}] {r.voice_type} conf={r.voice_type_confidence:.2f}")
        except Exception as e:
            print(f"  {wav.name:28} | ERROR: {e}")
else:
    print("  recordings/guest/ not found - skipping real-data check")

# ── 5. Summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
all_errs = [e for errs in results.values() for e in errs if e is not None]
overall_mean = np.mean(all_errs)
overall_max  = np.max(all_errs)
print(f"SUMMARY: mean={overall_mean:.2f} cents, max={overall_max:.2f} cents")
print(f"  Overall grade: {grade_cents(overall_mean)}")
if overall_mean < 10:
    print("  PASS - F0 extraction meets < 10 cent target")
else:
    print("  MARGINAL - consider tuning frame/hop parameters")
print("=" * 70)
