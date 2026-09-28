import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Test routes
r = requests.get('http://localhost:8000/openapi.json', timeout=10)
data = r.json()
paths = list(data.get('paths', {}).keys())
print('Total routes:', len(paths))
for p in paths:
    print(' ', p)
print()

# Test recommend-songs
r = requests.post('http://localhost:8000/api/v1/voice/recommend-songs', json={
    'voice_type': 'TENOR',
    'min_midi': 48,
    'max_midi': 72,
    'avg_f0': 220,
    'range_semitones': 24,
    'preferred_genres': ['POP', 'BALLAD']
}, timeout=30)
print('Recommend-songs status:', r.status_code)
result = r.json()
recs = result['data']['recommendations']
print('Top 3 recommendations:')
for s in recs[:3]:
    title = s['title']
    pct = s['match_pct']
    reasons = s['reasons']
    print('  -', title, '(', pct, '%)')
    for r2 in reasons:
        print('      *', r2)
