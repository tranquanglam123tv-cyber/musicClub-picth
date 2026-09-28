"""Test new voice classifier on real recordings - standalone."""
import sys
sys.path.insert(0, r'c:\Users\ADMIN\musicClub-picth\music-club-platform\dsp-service')
sys.stdout.reconfigure(encoding='utf-8')

import os
os.chdir(r'c:\Users\ADMIN\musicClub-picth\music-club-platform\dsp-service')

import soundfile as sf
import numpy as np
from app.audio.f0_extractor import F0Extractor
from app.config import DSPConfig

# Load all real recordings
recordings_dir = r'recordings\guest'
files = [f for f in os.listdir(recordings_dir) if f.endswith('.wav')]

print('=' * 75)
print('  TEST PHAN LOAI GIONG HAT MOI - Real recordings')
print('=' * 75)
print()

config = DSPConfig()
extractor = F0Extractor(config)

for fname in sorted(files):
    fpath = os.path.join(recordings_dir, fname)
    fsize = os.path.getsize(fpath)
    if fsize < 1000:  # skip placeholder files
        print(f'  [SKIP] {fname} - file too small ({fsize} bytes, likely placeholder)')
        continue

    audio, sr = sf.read(fpath)
    audio = audio.astype(np.float32)
    duration = len(audio) / sr

    print(f'--- {fname} ---')
    print(f'  duration:  {duration:.2f}s, sr: {sr}')

    result = extractor.extract(audio)

    print(f'  min_f0:    {result.min_f0:.2f} Hz (MIDI {12*np.log2(max(result.min_f0,1)/440)+69:.1f})')
    print(f'  max_f0:    {result.max_f0:.2f} Hz (MIDI {12*np.log2(result.max_f0/440)+69:.1f})')
    print(f'  median_f0: {result.median_f0:.2f} Hz (MIDI {12*np.log2(result.median_f0/440)+69:.1f})')
    print(f'  avg_f0:    {result.avg_f0:.2f} Hz')
    print(f'  P25:       {result.p25_f0:.2f} Hz')
    print(f'  P75:       {result.p75_f0:.2f} Hz')
    print(f'  range:     {result.range_semitones:.1f} semitones')
    print(f'  voiced:    {result.voiced_ratio*100:.1f}%')
    print()
    print(f'  >>> VOICE TYPE: {result.voice_type} (confidence: {result.voice_type_confidence:.1%}) <<<')
    print()
