# F0 Theory Document

## Mục lục
1. [Giới thiệu F0](#1-giới-thiệu-f0)
2. [Pitch, Frequency, Harmonics](#2-pitch-frequency-harmonics)
3. [Đặc tính giọng hát](#3-đặc-tính-giọng-hát)
4. [Chuẩn âm A4 = 440Hz](#4-chuẩn-âm-a4--440hz)
5. [MIDI Note Numbers](#5-midi-note-numbers)
6. [Voice Type Ranges](#6-voice-type-ranges)

---

## 1. Giới thiệu F0

### F0 là gì?

**F0 (Fundamental Frequency)** là tần số cơ bản của một sóng âm tuần hoàn - tần số thấp nhất và quan trọng nhất quyết định cao độ (pitch) mà tai người cảm nhận được.

```
┌─────────────────────────────────────────────────────────────┐
│                    SÓNG ÂM THANH                            │
│                                                             │
│    ┌───┐         ┌───┐         ┌───┐                       │
│   │   │         │   │         │   │                       │
│───┘   └─────────┘   └─────────┘   └─────────▶ Thời gian    │
│                                                             │
│   ▲        ▲        ▲        ▲        ▲                    │
│   │        │        │        │        │                    │
│   │ F0     │ 2×F0   │ 3×F0   │ 4×F0   │ 5×F0              │
│   │        │        │        │        │                    │
│   └────────┴────────┴────────┴────────┴─────                │
│                                                             │
│   F0 = Fundamental Frequency (Tần số cơ bản)               │
│   2×F0, 3×F0... = Harmonics (Thượng thanh)                │
└─────────────────────────────────────────────────────────────┘
```

### Tại sao F0 quan trọng?

| Ứng dụng | Giải thích |
|-----------|------------|
| **Nhận diện giọng nói** | Mỗi người có F0 trung bình khác nhau |
| **Phân tích giọng hát** | Xác định cao độ bài hát |
| **Phân loại voice type** | Soprano cao hơn Bass |
| **Gợi ý bài hát** | So khớp quãng giọng với bài hát |

---

## 2. Pitch, Frequency, Harmonics

### 2.1 Frequency (Tần số) vs Pitch (Cao độ)

| Khái niệm | Định nghĩa | Đơn vị |
|-----------|------------|---------|
| **Frequency** | Số chu kỳ/giây của sóng âm | Hz (Hertz) |
| **Pitch** | Cảm nhận chủ quan về "cao" hoặc "thấp" của âm | perceptual |

```
Relationship: Frequency → Pitch (mối quan hệ tuyến tính theo log)

Công thức: Pitch (semitones) = 12 × log₂(frequency / reference)
```

### 2.2 Harmonics (Thượng thanh)

Khi thanh môn rung động, chúng tạo ra:
- **F0** - Tần số cơ bản (fundamental)
- **Thượng thanh** - Bội số của F0 (2×, 3×, 4×, ...)

```
Ví dụ: F0 = 220 Hz (A3)

Harmonics:
- H1 = 220 Hz (F0)
- H2 = 440 Hz (A4)  
- H3 = 660 Hz (E5)
- H4 = 880 Hz (A5)
- ...
```

### 2.3 Tại sao dùng F0 thay vì Harmonics?

| Yếu tố | F0 | Harmonics |
|--------|-----|-----------|
| Ổn định | ✅ Cao | ❌ Biến đổi theo vowel |
| Đo lường | ✅ Dễ dàng | ❌ Phức tạp |
| Phản ánh pitch | ✅ Trực tiếp | ❌ Gián tiếp |

---

## 3. Đặc tính giọng hát

### 3.1 Các thành phần của giọng hát

```
┌─────────────────────────────────────────────────────────────┐
│                    GIỌNG HÁT                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │   Phổi     │───▶│  Thanh môn │───▶│   Miệng    │    │
│   │  (Lungs)   │    │  (Vocal    │    │  (Mouth)   │    │
│   │            │    │   Folds)   │    │            │    │
│   └─────────────┘    └─────────────┘    └─────────────┘    │
│        │                  │                  │              │
│        ▼                  ▼                  ▼              │
│   Air Pressure      Vibration         Resonance             │
│   (Áp lực khí)     (Rung động)      (Cộng hưởng)          │
│                                                             │
│   Kết quả: F0 = Tần số rung của thanh môn                  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Voiced vs Unvoiced

| Loại | Mô tả | Ví dụ |
|------|-------|-------|
| **Voiced** | Thanh môn rung, có F0 xác định | Nguyên âm (a, e, i, o, u), các nốt nhạc |
| **Unvoiced** | Thanh môn không rung, không có F0 | Phụ âm (s, sh, f, t), tiếng thở |

```
Voiced frame:    ▓▓▓▓▓▓▓▓▓▓▓  (có pitch)
Unvoiced frame:  ░░░░░░░░░░░  (không có pitch / noise)
```

### 3.3 Các tham số F0 quan trọng

| Tham số | Mô tả | Ý nghĩa |
|---------|--------|----------|
| **min_f0** | Tần số thấp nhất | Giọng hát có thể hát được nốt thấp đến đâu |
| **max_f0** | Tần số cao nhất | Giọng hát có thể hát được nốt cao đến đâu |
| **avg_f0** | Tần số trung bình | "Trung tâm" của giọng hát |
| **median_f0** | Tần số trung vị | Giá trị giữa, ít bị outlier ảnh hưởng |
| **std_f0** | Độ lệch chuẩn | Độ ổn định của giọng hát |
| **range_semitones** | Quãng giọng (semitones) | Khoảng cách từ nốt thấp đến nốt cao |

---

## 4. Chuẩn âm A4 = 440Hz

### 4.1 Định nghĩa

**A4 (La4)** là nốt tham chiếu có tần số **440 Hz** - đây là chuẩn quốc tế được thiết lập năm 1939.

### 4.2 Công thức chuyển đổi

```python
# Hz → MIDI (A4 = 69)
midi_note = 12 * log2(frequency / 440) + 69

# MIDI → Hz
frequency = 440 * 2^((midi_note - 69) / 12)

# MIDI → Note Name
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
note_name = note_names[midi_note % 12] + str(midi_note // 12 - 1)
```

### 4.3 Bảng tham chiếu MIDI - Hz

| MIDI | Note | Hz | Voice Type Range |
|------|------|-----|-----------------|
| 48 | C3 | 130.81 | Bass max |
| 55 | G3 | 196.00 | Tenor max |
| 60 | C4 | 261.63 | Middle C |
| 65 | F4 | 349.23 | Baritone max |
| 69 | A4 | 440.00 | Reference |
| 72 | C5 | 523.25 | Tenor high |
| 76 | E5 | 659.25 | Alto high |
| 81 | F#5 | 739.99 | Soprano high |
| 84 | C6 | 1046.50 | Soprano max |

### 4.4 Semitone (Nửa cung)

- **1 Semitone** = Khoảng cách giữa 2 nốt liền kề (vd: C → C#)
- **1 Octave** = 12 semitones
- **Công thức tính semitones giữa 2 tần số:**

```python
semitones = 12 * log2(f2 / f1)
```

---

## 5. MIDI Note Numbers

### 5.1 Quy ước MIDI

```
MIDI Note Number = Số thứ tự của nốt nhạc, bắt đầu từ C-1 = 0

C-1 = 0
C0 = 12
C1 = 24
C2 = 36
C3 = 48
C4 = 60 (Middle C)
C5 = 72
C6 = 84
C7 = 96
C8 = 108
```

### 5.2 Bảng MIDI đầy đủ (Middle octave)

| Note | Octave | MIDI | Hz |
|------|--------|------|-----|
| C | 4 | 60 | 261.63 |
| C# | 4 | 61 | 277.18 |
| D | 4 | 62 | 293.66 |
| D# | 4 | 63 | 311.13 |
| E | 4 | 64 | 329.63 |
| F | 4 | 65 | 349.23 |
| F# | 4 | 66 | 369.99 |
| G | 4 | 67 | 392.00 |
| G# | 4 | 68 | 415.30 |
| A | 4 | 69 | 440.00 |
| A# | 4 | 70 | 466.16 |
| B | 4 | 71 | 493.88 |

### 5.3 Ứng dụng trong phân tích giọng hát

```python
# Ví dụ: Giọng Baritone
# min_f0 = 98 Hz (G2), max_f0 = 330 Hz (E4)

min_midi = 12 * log2(98 / 440) + 69  # ≈ 43
max_midi = 12 * log2(330 / 440) + 69  # ≈ 60

range_semitones = 12 * log2(330 / 98)  # ≈ 24 semitones
```

---

## 6. Voice Type Ranges

### 6.1 Phân loại giọng hát

| Voice Type | Giới tính | Quãng thường gặp | MIDI Range |
|------------|-----------|------------------|------------|
| **Soprano** | Nữ | C4-C6 | 60-84 |
| **Mezzo-Soprano** | Nữ | A3-A5 | 57-81 |
| **Alto** | Nữ | F3-F5 | 53-77 |
| **Tenor** | Nam | C3-C5 | 48-72 |
| **Baritone** | Nam | A2-A4 | 45-69 |
| **Bass** | Nam | E2-E4 | 40-64 |

### 6.2 Chi tiết Voice Type Ranges

```
┌─────────────────────────────────────────────────────────────────┐
│                     VOICE TYPE RANGES (MIDI)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BASS:      E2 ──────────────────────────────── E4              │
│             (40)                                              (64)│
│                                                                 │
│  BARITONE:       A2 ─────────────────────────── A4               │
│                  (45)                                       (69) │
│                                                                 │
│  TENOR:           C3 ─────────────────────────── C5              │
│                   (48)                                      (72) │
│                                                                 │
│  ─────────────── OVERLAP ZONE (G3-B3) ───────────────          │
│                                                                 │
│  ALTO:                   F3 ──────────────────── F5              │
│                          (53)                              (77)│
│                                                                 │
│  MEZZO-SOPRANO:           A3 ─────────────────── A5              │
│                           (57)                              (81)│
│                                                                 │
│  SOPRANO:                   C4 ─────────────────── C6          │
│                             (60)                              (84)│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Overlap Zones (Vùng chồng lấn)

| Vùng chồng lấn | MIDI | Giọng có thể hát |
|----------------|------|-------------------|
| G3-B3 | 55-71 | Tenor ↔ Alto |
| C3-E3 | 48-52 | Baritone ↔ Tenor |
| C3-F3 | 48-53 | Baritone ↔ Alto |

**Ý nghĩa:** Vùng overlap là nơi 2 voice type có thể hát cùng nốt - dùng để phân biệt trong trường hợp khó xác định.

### 6.4 Đặc tính âm sắc (Timbre)

| Voice Type | Đặc điểm âm sắc |
|------------|------------------|
| **Soprano** | Sáng, trong, dễ bay lên cao |
| **Mezzo-Soprano** | Trung gian, linh hoạt |
| **Alto** | ấm, đầy đặn, ổn định |
| **Tenor** | Sáng, mạnh mẽ, dễ projection |
| **Baritone** | ấm, trung tâm, đa dụng |
| **Bass** | Trầm, mạnh, nền tảng |

---

## 7. Audio Specifications cho F0 Analysis

### 7.1 Thông số kỹ thuật

| Tham số | Giá trị khuyến nghị | Ghi chú |
|---------|---------------------|---------|
| Sample Rate | 44100 Hz | CD quality standard |
| Bit Depth | 16-bit hoặc 24-bit | 24-bit cho F0 tốt hơn |
| Channels | **Mono** (1) | Required cho F0 extraction |
| Format | WAV (uncompressed) | Lossless, không artifacts |
| Duration | 10-60 giây | Đủ để có kết quả chính xác |

### 7.2 Tại sao cần Mono?

```
Stereo:    [Left Channel] + [Right Channel]
           ┌─────────────────────────────┐
           │ F0 extracted from L = 220 Hz │
           │ F0 extracted from R = 222 Hz │ ← Khác nhau!
           └─────────────────────────────┘

Mono:      [Left + Right / 2]
           ┌─────────────────────────────┐
           │ F0 = 221 Hz (consistent)      │
           └─────────────────────────────┘
```

### 7.3 Nyquist Frequency

```
Nyquist Frequency = Sample Rate / 2

Ví dụ: 44100 Hz / 2 = 22050 Hz

→ Có thể capture tần số tối đa = 22050 Hz
→ Giọng hát max ≈ 2000 Hz (C7 = 2093 Hz) ✓
→ Đủ cho F0 extraction
```

---

## 8. Summary

### Key Takeaways

```
┌─────────────────────────────────────────────────────────────┐
│                    F0 ESSENTIALS                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. F0 = Fundamental Frequency (Tần số cơ bản)          │
│     → Xác định cao độ (pitch) của giọng hát               │
│                                                             │
│  2. F0 → MIDI: midi = 12 × log₂(f/440) + 69              │
│     → MIDI → F0: f = 440 × 2^((midi-69)/12)               │
│                                                             │
│  3. Voice Types được xác định bởi min/max F0             │
│     → Soprano: C4-C6 (260-1046 Hz)                         │
│     → Bass: E2-E4 (82-330 Hz)                              │
│                                                             │
│  4. Audio specs: Mono, 44100 Hz, 16-bit, 10-60s           │
│                                                             │
│  5. Voiced vs Unvoiced                                     │
│     → Voiced: có F0 (nguyên âm)                            │
│     → Unvoiced: không có F0 (phụ âm)                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Tài liệu tham khảo

1. Mauch, M., & Dixon, S. (2014). pYIN: A fundamental frequency estimator using probabilistic threshold-free pitch tracking.
2. De Cheveigné, A., & Kawahara, H. (2002). YIN, a fundamental frequency estimator for speech and music.
3. Librosa Documentation: https://librosa.org/doc/
4. MIDI Association: https://www.midi.org/

---

**Document Version:** 1.0  
**Created:** September 19, 2026  
**Status:** Ready for Implementation
