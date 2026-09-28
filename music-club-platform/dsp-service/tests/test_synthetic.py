"""Test voice classifier with synthetic F0 distributions for each voice type."""
import sys
sys.path.insert(0, r'c:\Users\ADMIN\musicClub-picth\music-club-platform\dsp-service')
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
from app.audio.f0_extractor import F0Extractor
from app.config import DSPConfig

# Test cases: each is a typical F0 (Hz) median value for that voice type
# These are well-established from music pedagogy:
test_cases = [
    # (name, expected_voice, median_hz, p25_hz, p75_hz)
    ("Low Bass singer",       "BASS",         80,  70,  95),
    ("Bass (typical)",        "BASS",        100,  85, 130),
    ("Baritone (low)",        "BARITONE",    115, 100, 140),
    ("Baritone (typical)",    "BARITONE",    130, 110, 160),
    ("High Baritone",         "BARITONE",    140, 120, 175),
    ("Tenor (low)",           "TENOR",       145, 125, 180),
    ("Tenor (typical)",       "TENOR",       155, 135, 195),
    ("Tenor (high)",          "TENOR",       165, 145, 210),
    ("Countertenor",          "ALTO",        180, 150, 230),  # male alto
    ("Alto (F)",              "ALTO",        195, 165, 240),
    ("Mezzo-soprano",         "MEZZO_SOPRANO",230, 195, 290),
    ("Soprano",               "SOPRANO",     270, 230, 340),
    ("Coloratura Soprano",    "SOPRANO",     350, 290, 450),
]

config = DSPConfig()
extractor = F0Extractor(config)

print('=' * 90)
print(' TEST VOICE TYPE CLASSIFIER WITH KNOWN F0 DISTRIBUTIONS')
print('=' * 90)
print(f'{"Test case":<25} {"Expected":<14} {"Median":<8} {"P25":<8} {"P75":<8} {"Got":<14} {"Conf":<6} {"OK?"}')
print('-' * 90)

correct = 0
total = 0
for name, expected, med, p25, p75 in test_cases:
    # Compute tessitura boundaries for classification
    median_midi = 12 * np.log2(med / 440.0) + 69
    p25_midi = 12 * np.log2(p25 / 440.0) + 69
    p75_midi = 12 * np.log2(p75 / 440.0) + 69
    voiced_ratio = 0.6  # typical singing

    got, conf = extractor._classify_voice_type(
        median_midi=median_midi,
        tessitura_low_midi=p25_midi,
        tessitura_high_midi=p75_midi,
        voiced_ratio=voiced_ratio
    )

    ok = 'OK' if got == expected else 'X'
    if got == expected:
        correct += 1
    total += 1

    print(f'{name:<25} {expected:<14} {med:<8.1f} {p25:<8.1f} {p75:<8.1f} {got:<14} {conf:<6.2f} {ok}')

print('-' * 90)
print(f'ACCURACY: {correct}/{total} = {100*correct/total:.1f}%')
