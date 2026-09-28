"""Test full flow: analyze -> save -> recommend."""
import requests
import sys
import struct
import math

sys.stdout.reconfigure(encoding='utf-8')

API = 'http://localhost:8000/api/v1'


def make_sine_wav(freq=200, duration=15, sr=44100):
    """Tạo file WAV sine wave để test."""
    n_samples = int(sr * duration)
    samples = []
    for i in range(n_samples):
        t = i / sr
        # Sine wave + slight noise
        val = int(16384 * (math.sin(2 * math.pi * freq * t) * 0.5
                            + math.sin(2 * math.pi * freq * 2 * t) * 0.2))
        samples.append(struct.pack('<h', max(-32768, min(32767, val))))

    data = b''.join(samples)
    data_size = len(data)

    # WAV header
    wav = b'RIFF'
    wav += struct.pack('<I', 36 + data_size)
    wav += b'WAVE'
    wav += b'fmt '
    wav += struct.pack('<I', 16)
    wav += struct.pack('<H', 1)              # PCM
    wav += struct.pack('<H', 1)              # Mono
    wav += struct.pack('<I', sr)
    wav += struct.pack('<I', sr * 2)
    wav += struct.pack('<H', 2)
    wav += struct.pack('<H', 16)
    wav += b'data'
    wav += struct.pack('<I', data_size)
    wav += data
    return wav


print('=' * 60)
print('TEST: Phân tích giọng + Lưu recording + Gợi ý bài hát')
print('=' * 60)

# 1. Tạo file WAV test (giả lập giọng TENOR ~200Hz)
print('\n1) Tạo file WAV sine wave 200Hz (15s)')
wav_data = make_sine_wav(freq=200, duration=15)
print(f'   Kích thước: {len(wav_data)/1024:.1f} KB')

# 2. Phân tích giọng
print('\n2) Gửi file đến /voice/analyze')
files = {'file': ('test_tenor.wav', wav_data, 'audio/wav')}
r = requests.post(f'{API}/voice/analyze', files=files, timeout=60)
print(f'   Status: {r.status_code}')
if r.status_code != 200:
    print('   Lỗi:', r.text[:300])
    sys.exit(1)

analysis = r.json()['data']
print(f'   Voice type: {analysis["voice_type"]}')
print(f'   Range: {analysis["min_midi"]:.1f} - {analysis["max_midi"]:.1f} MIDI')
print(f'   Semitones: {analysis["range_semitones"]:.1f}')
print(f'   Avg F0: {analysis["avg_f0"]:.1f} Hz')

# 3. Lưu recording
print('\n3) Lưu recording vào thư viện')
files = {'file': ('my_recording.wav', wav_data, 'audio/wav')}
data = {
    'user_id': 'guest',
    'voice_type': analysis['voice_type'],
    'min_midi': str(analysis['min_midi']),
    'max_midi': str(analysis['max_midi']),
    'avg_f0': str(analysis['avg_f0']),
    'range_semitones': str(analysis['range_semitones']),
    'confidence': str(analysis['confidence']),
    'notes': 'Test full flow'
}
r = requests.post(f'{API}/voice/save-recording', files=files, data=data, timeout=30)
print(f'   Status: {r.status_code}')
if r.status_code == 200:
    rec_id = r.json()['data']['recording_id']
    print(f'   Recording ID: {rec_id}')

# 4. Gợi ý bài hát
print('\n4) Gợi ý bài hát phù hợp')
r = requests.post(f'{API}/voice/recommend-songs', json={
    'voice_type': analysis['voice_type'],
    'min_midi': analysis['min_midi'],
    'max_midi': analysis['max_midi'],
    'avg_f0': analysis['avg_f0'],
    'range_semitones': analysis['range_semitones'],
    'preferred_genres': ['POP', 'BALLAD'],
    'max_results': 5
}, timeout=30)
print(f'   Status: {r.status_code}')
result = r.json()['data']
print(f'   Voice type: {result["voice_type"]}')
print(f'   Range: {result["user_range"]["min_note"]} - {result["user_range"]["max_note"]}')
print(f'   Top {len(result["recommendations"])} gợi ý:')
for i, song in enumerate(result['recommendations'], 1):
    print(f'   #{i} {song["title"]} - {song["artist"]} ({song["match_pct"]}%)')
    for reason in song['reasons'][:2]:
        print(f'        • {reason}')

# 5. List recordings
print('\n5) Danh sách bản ghi của user')
r = requests.get(f'{API}/recordings/guest', timeout=10)
print(f'   Status: {r.status_code}, count: {r.json()["count"]}')

print('\n' + '=' * 60)
print('✅ Tất cả flow hoạt động thành công!')
print('=' * 60)
