# Music Club Platform

**Hệ thống Quản lý Câu lạc bộ Âm nhạc với Phân tích Tần số Âm thanh F₀ và Gợi ý Bài hát**

## 🎯 Mục tiêu

- Phân tích giọng hát (F0 extraction, voice type classification)
- Gợi ý bài hát phù hợp với quãng giọng
- Quản lý sự kiện, thành viên, bài viết cộng đồng

## 🏗️ Kiến trúc

| Thành phần | Công nghệ | Vai trò |
|------------|-----------|---------|
| **Backend** | Java 17 + Spring Boot 3.x | REST API, Authentication, Business Logic |
| **DSP Service** | Python 3.10+ + FastAPI | F0 Analysis, Voice Type Classification |
| **Mobile** | Flutter 3.x | App cho thành viên |
| **Admin Web** | React 18 + TypeScript | Dashboard cho Ban Chủ Nhiệm |
| **Database** | MySQL 8.0 (Server) + SQLite (Local) | Hybrid storage |

## 📁 Cấu trúc Project

```
music-club-platform/
├── backend-java/        # P3 - Backend Lead
├── dsp-service/         # P2 - Research Lead (F0 Analysis)
├── mobile-flutter/      # P4 - Mobile Lead
├── admin-web/           # P5 - Admin Lead
├── database/            # Schema & Seeds
└── docs/                # Documentation
```

## ⏱️ Timeline: 100 Ngày

| Phase | Thời gian | Mục tiêu |
|-------|-----------|-----------|
| Phase 1 | Day 01-20 | Nền tảng & Nghiên cứu |
| Phase 2 | Day 21-40 | Backend & Database |
| Phase 3 | Day 41-55 | DSP & Recommendation |
| Phase 4 | Day 56-75 | Mobile & Admin |
| Phase 5 | Day 76-90 | Tích hợp & Testing |
| Phase 6 | Day 91-100 | Báo cáo & Bảo vệ |

## 👥 Đội ngũ

| Vai trò | Thành viên |
|---------|------------|
| P1 - Project Manager & Architect | - |
| P2 - Research Lead (DSP/F0) | - |
| P3 - Backend Lead | - |
| P4 - Mobile Lead | - |
| P5 - Admin Lead | - |

## 🚀 Bắt đầu

```bash
# Clone repo
git clone <repo-url>
cd musicClub-picth

# Setup database
mysql -u root -p < database/schema.sql

# Start backend
cd backend-java && mvn spring-boot:run

# Start DSP service
cd dsp-service && python -m uvicorn app.main:app --reload
```

## 📚 Tài liệu

- [Roadmap](roadmap.md) - Lịch trình chi tiết 100 ngày
- [Database Schema](music-club-platform/database/schema.sql) - ERD và SQL
- [API Documentation](roadmap.md#phần-v-api-documentation) - API endpoints
