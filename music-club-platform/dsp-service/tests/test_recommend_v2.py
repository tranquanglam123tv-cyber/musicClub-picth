"""Test recommend-songs v2."""
import sys
sys.path.insert(0, '.')
import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

# Test với BARITONE
r = requests.post('http://localhost:8000/api/v1/voice/recommend-songs', json={
    'voice_type': 'BARITONE',
    'min_midi': 48,
    'max_midi': 67,
    'range_semitones': 19,
    'preferred_genres': ['POP', 'BALLAD'],
    'max_results': 5
}, timeout=15)
data = r.json()
print(f'Algorithm: {data["data"]["algorithm"]}')
print(f'User range: {data["data"]["user_range"]["min_note"]} - {data["data"]["user_range"]["max_note"]}')
print(f'Total candidates: {data["data"]["total_candidates"]}')
print()
recs = data['data']['recommendations']
for s in recs:
    b = s['scoring_breakdown']
    print(f'  [{s["match_pct"]}%]: {s["title"]} ({s["artist"]})')
    print(f'    range={b["range_score"]} genre={b["genre_score"]} key={b["key_score"]} diff={b["difficulty_score"]}')
    for r2 in s['reasons']:
        print(f'      - {r2}')
    print()

# Test với SOPRANO
r2 = requests.post('http://localhost:8000/api/v1/voice/recommend-songs', json={
    'voice_type': 'SOPRANO',
    'min_midi': 60,
    'max_midi': 79,
    'range_semitones': 19,
    'preferred_genres': ['BALLAD', 'CLASSICAL'],
    'max_results': 3
}, timeout=15)
d2 = r2.json()
print('--- SOPRANO ---')
recs2 = d2['data']['recommendations']
for s in recs2:
    b = s['scoring_breakdown']
    print(f'  [{s["match_pct"]}%]: {s["title"]}')
    print(f'    range={b["range_score"]} genre={b["genre_score"]} key={b["key_score"]} diff={b["difficulty_score"]}')
