import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

r = requests.get('http://localhost:8000/openapi.json', timeout=10)
paths = list(r.json()['paths'].keys())
print('Server OK -', len(paths), 'endpoints:')
for p in paths:
    print(' ', p)
print()

r = requests.get('http://localhost:8000/api/v1/recordings/guest', timeout=10)
result = r.json()
print('Library:', result['count'], 'recordings saved')

# Get recommendations
r = requests.post('http://localhost:8000/api/v1/voice/recommend-songs', json={
    'voice_type': 'TENOR', 'min_midi': 48, 'max_midi': 72,
    'avg_f0': 220, 'range_semitones': 24, 'preferred_genres': ['POP','BALLAD']
}, timeout=10)
result = r.json()
print('Recommender: returns', len(result['data']['recommendations']), 'songs for TENOR')
