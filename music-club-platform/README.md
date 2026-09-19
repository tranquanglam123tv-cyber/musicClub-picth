# MUSIC CLUB PLATFORM - COMPLETE DOCUMENTATION

## Đề tài: Hệ thống Quản lý Câu lạc bộ Âm nhạc với Phân tích Tần số Âm thanh F₀ và Gợi ý Bài hát

**Số thành viên:** 5 sinh viên  
**Thời gian:** 100 ngày  
**Phiên bản:** 1.0.0  
**Ngày cập nhật:** September 19, 2026

---

## Mục lục

1. [Tổng quan](#1-tổng-quan)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Công nghệ sử dụng](#3-công-nghệ-sử-dụng)
4. [Database](#4-database)
5. [API Documentation](#5-api-documentation)
6. [DSP Service](#6-dsp-service)
7. [Mobile App](#7-mobile-app)
8. [Admin Web](#8-admin-web)
9. [Deployment](#9-deployment)
10. [Testing](#10-testing)

---

## 1. Tổng quan

### 1.1 Mục tiêu dự án

Xây dựng hệ thống quản lý câu lạc bộ âm nhạc với các tính năng:
- **Phân tích giọng hát**: Sử dụng F0 (tần số cơ bản) để phân tích và phân loại giọng hát
- **Gợi ý bài hát**: Đề xuất bài hát phù hợp với quãng giọng của thành viên
- **Quản lý sự kiện**: Tổ chức và quản lý sinh hoạt câu lạc bộ
- **Cộng đồng**: Chia sẻ kiến thức và kinh nghiệm

### 1.2 Phân công thành viên

| Thành viên | Vai trò | Trách nhiệm |
|------------|---------|--------------|
| P1 | PM & Architect | Quản lý dự án, thiết kế kiến trúc |
| P2 | Research Lead | DSP, F0 research, Python service |
| P3 | Backend Lead | Spring Boot API, MySQL |
| P4 | Mobile Lead | Flutter app |
| P5 | Admin Lead | React Admin Dashboard |

### 1.3 Timeline

```
Phase 1: Nền tảng & Nghiên cứu (Day 01 - Day 20)
Phase 2: Backend & Database (Day 21 - Day 40)
Phase 3: DSP & Recommendation (Day 41 - Day 55)
Phase 4: Mobile & Admin (Day 56 - Day 75)
Phase 5: Tích hợp & Testing (Day 76 - Day 90)
Phase 6: Báo cáo & Bảo vệ (Day 91 - Day 100)
```

---

## 2. Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Mobile     │  │   Admin      │  │   Web        │             │
│  │  (Flutter)   │  │   (React)    │  │   (Future)   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      NGINX (Reverse Proxy)                               │
│                      Port: 80, 443                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│     BACKEND         │ │    DSP SERVICE      │ │    ADMIN WEB       │
│  (Spring Boot)     │ │   (FastAPI/Python) │ │    (React)         │
│  Port: 8080        │ │   Port: 8000       │ │    Port: 3000      │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘
           │                       │
           │                       │
           ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      MYSQL DATABASE                                     │
│                      Port: 3306                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Công nghệ sử dụng

### 3.1 Backend

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|-----------|
| Java | 17+ | Ngôn ngữ lập trình |
| Spring Boot | 3.2.0 | Web framework |
| Spring Security | 6.x | Authentication & Authorization |
| Spring Data JPA | 3.x | Database access |
| MySQL | 8.0 | Database |
| Maven | 3.9 | Build tool |
| JWT | 0.12.x | Token-based auth |

### 3.2 DSP Service

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|-----------|
| Python | 3.10+ | Ngôn ngữ lập trình |
| FastAPI | 0.100+ | Web framework |
| librosa | 0.10+ | Audio processing |
| pYIN | - | Pitch detection |
| numpy | 1.24+ | Numerical computing |
| scipy | 1.11+ | Signal processing |

### 3.3 Mobile

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|-----------|
| Flutter | 3.x | UI framework |
| Dart | 3.x | Ngôn ngữ lập trình |
| Provider | 6.1+ | State management |
| Dio | 5.4+ | HTTP client |
| record | 5.0+ | Audio recording |
| sqflite | 2.3+ | Local database |

### 3.4 Admin Web

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|-----------|
| React | 18+ | UI framework |
| TypeScript | 5.x | Ngôn ngữ lập trình |
| Material UI | 5.x | Component library |
| Axios | 1.x | HTTP client |
| React Router | 6.x | Navigation |

---

## 4. Database

### 4.1 ERD Overview

```
USERS ──────┬────── VOICE_PROFILES
            │              │
            ├────── VOICE_ANALYSES
            │
            ├────── EVENT_REGISTRATIONS ── EVENT
            │
            ├────── USER_SONGS ─── SONGS ─── SONG_GENRES ─── GENRES
            │
            └────── POSTS ─── POST_COMMENTS
```

### 4.2 Key Tables

| Table | Description |
|-------|-------------|
| `users` | Thông tin tài khoản |
| `voice_profiles` | Hồ sơ giọng hát tổng hợp |
| `voice_analyses` | Chi tiết từng lần phân tích |
| `songs` | Kho bài hát |
| `events` | Sự kiện câu lạc bộ |
| `posts` | Bài viết cộng đồng |

---

## 5. API Documentation

### 5.1 Authentication

```
POST /api/auth/register - Đăng ký
POST /api/auth/login   - Đăng nhập
POST /api/auth/logout  - Đăng xuất
```

### 5.2 Voice Analysis

```
POST /api/voice/analyze  - Phân tích giọng hát
GET  /api/voice/profile  - Lấy hồ sơ giọng hát
GET  /api/voice/history  - Lịch sử phân tích
```

### 5.3 Songs & Recommendations

```
GET /api/songs              - Danh sách bài hát
GET /api/recommendations    - Gợi ý bài hát
```

### 5.4 Events

```
GET  /api/events           - Danh sách sự kiện
POST /api/events/{id}/register - Đăng ký sự kiện
```

---

## 6. DSP Service

### 6.1 F0 Extraction Pipeline

```
Audio Input → Preprocess → pYIN → Statistics → Voice Type → Database
```

### 6.2 Optimal Parameters

| Parameter | Value |
|-----------|-------|
| Sample Rate | 44100 Hz |
| Frame Length | 2048 samples |
| Hop Length | 512 samples |
| Fmin | 50 Hz |
| Fmax | 1000 Hz |

### 6.3 Voice Type Ranges

| Voice Type | MIDI Range | Hz Range |
|------------|-----------|----------|
| Soprano | 55-84 | 196-1046 |
| Mezzo-Soprano | 57-81 | 208-772 |
| Alto | 53-77 | 165-622 |
| Tenor | 48-72 | 131-523 |
| Baritone | 45-69 | 98-440 |
| Bass | 40-64 | 82-330 |

---

## 7. Mobile App

### 7.1 Features

- Đăng nhập/đăng ký
- Phân tích giọng hát
- Xem hồ sơ giọng hát
- Gợi ý bài hát
- Đăng ký sự kiện
- Cộng đồng

### 7.2 Audio Recording Requirements

| Parameter | Value |
|-----------|-------|
| Format | WAV |
| Sample Rate | 44100 Hz |
| Channels | 1 (Mono) |
| Duration | 10-60 seconds |
| Max Size | 10 MB |

---

## 8. Admin Web

### 8.1 Features

- Quản lý thành viên
- Quản lý bài hát
- Quản lý sự kiện
- Quản lý bài viết
- Xem thống kê giọng hát
- Dashboard tổng quan

---

## 9. Deployment

### 9.1 Docker Services

| Service | Image | Port |
|---------|-------|------|
| Nginx | nginx:alpine | 80, 443 |
| Backend | music_club_backend | 8080 |
| DSP Service | music_club_dsp | 8000 |
| Admin Web | music_club_admin | 80 |
| MySQL | mysql:8.0 | 3306 |

### 9.2 Quick Start

```bash
# Clone repository
git clone <repo-url>
cd music-club-platform

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## 10. Testing

### 10.1 Unit Tests

| Component | Coverage Target |
|-----------|----------------|
| Backend (Java) | > 80% |
| DSP Service (Python) | > 90% |
| Mobile (Flutter) | > 70% |

### 10.2 Integration Tests

- API integration tests
- Database integration tests
- End-to-end scenarios

---

## Tài liệu liên quan

| Document | Location |
|----------|----------|
| F0 Theory | `docs/research/f0-theory.md` |
| Pitch Detection | `docs/research/pitch-detection-algorithms.md` |
| DSP Signal Processing | `docs/research/dsp-signal-processing.md` |
| Library Testing | `docs/research/library-testing.md` |
| Dataset Preparation | `docs/research/dataset-preparation.md` |
| Voice Analysis Database | `docs/research/voice-analysis-database.md` |
| Recommendation Algorithm | `docs/research/recommendation-algorithm.md` |
| Backend API | `backend/README.md` |
| DSP Service | `dsp-service/README.md` |
| Mobile App | `mobile/README.md` |
| Docker | `docker/README.md` |
| Full Roadmap | `roadmap.md` |

---

## License

Copyright © 2026 Music Club Platform Team

---

**Document Version:** 1.0.0  
**Status:** Complete  
**Last Updated:** September 19, 2026
