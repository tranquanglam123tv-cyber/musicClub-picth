import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Test save-recording (gửi fake audio data)
audio_data = b'fake audio bytes for testing'
files = {'file': ('test.wav', audio_data, 'audio/wav')}
data = {
    'user_id': 'guest',
    'voice_type': 'TENOR',
    'min_midi': '48',
    'max_midi': '72',
    'avg_f0': '220.5',
    'range_semitones': '24',
    'confidence': '0.85',
    'notes': 'Bài test đầu tiên'
}
r = requests.post('http://localhost:8000/api/v1/voice/save-recording',
                  files=files, data=data, timeout=30)
print('Save-recording status:', r.status_code)
print(r.text[:300])
print()

# Test list-recordings
r = requests.get('http://localhost:8000/api/v1/recordings/guest', timeout=10)
print('List recordings status:', r.status_code)
result = r.json()
print('Total recordings:', result.get('count', 0))
for rec in result.get('data', [])[:3]:
    print('  -', rec.get('filename'), '|', rec.get('voice_type'),
          '|', rec.get('saved_at'))
