# Music Club Platform

> Đồ án NCKH: **Nghiên cứu ứng dụng kỹ thuật phân tích tần số âm thanh F₀ tự động nhận diện Tông giọng và gợi ý bài hát theo thể loại cho hệ thống quản lý Câu lạc bộ Âm nhạc đa nền tảng.**

Xem chi tiết kế hoạch 100 ngày: [`roadmap.md`](./roadmap.md)
Xem project charter (scope, RQ, phân công, milestones): [`PROJECT_CHARTER.md`](./PROJECT_CHARTER.md)

## Tổng quan

Hệ thống gồm 4 thành phần:

| Thành phần | Stack | Vai trò |
|---|---|---|
| **Mobile** | Flutter / Dart | App thành viên: thu âm, xem voice range, nhận recommendation, đăng ký sự kiện |
| **Backend** | Java + Spring Boot | REST API nghiệp vụ, auth JWT, CRUD core, gateway tới Python |
| **DSP Service** | Python + FastAPI | Audio preprocessing, pYIN pitch detection, vocal range, voice type |
| **Admin Web** | React + TypeScript | Quản trị: thành viên, sự kiện, bài hát, bài viết, voice profile |
| **Database** | MySQL | Lưu user, song, event, post, voice profile, voice analysis |

## Câu hỏi nghiên cứu (Research Questions)

1. **RQ1:** pYIN trích xuất F₀ từ giọng hát chính xác đến đâu?
2. **RQ2:** Preprocessing + filtering cải thiện F₀ như thế nào?
3. **RQ3:** F₀ contour có thể ước lượng vocal range và phân nhóm giọng ở mức ứng dụng không?
4. **RQ4:** Kết hợp range + key + genre có recommendation tốt hơn chỉ dùng genre không?

## Trạng thái hiện tại

- **Day 01 — Kickoff** ✅
- Chưa khởi tạo source code cho 4 stack. Sẽ bắt đầu ở Day 02+.

## Cấu trúc thư mục (sẽ tạo ở giai đoạn sau)

```text
music-club-picth/
├── backend/          # Spring Boot REST API
├── dsp-service/      # Python FastAPI audio analysis
├── mobile/           # Flutter app
├── admin-web/        # React + TypeScript admin
├── database/         # MySQL schema, seed, migrations
├── docs/             # Architecture, API, research notes
├── experiments/      # Notebooks, datasets, results
├── postman/          # API testing collection
└── docker-compose.yml
```

## Cài đặt nhanh (khi đã có code)

> Sẽ cập nhật sau khi các service được scaffold (khoảng Day 16+).

## Đóng góp

- Branch strategy: `main` ← `develop` ← `feature/<scope>-<task>`
- Commit convention: `feat(scope): ...`, `fix(scope): ...`, `docs(scope): ...`, `test(scope): ...`
- Xem `PROJECT_CHARTER.md` mục 11 để biết nguyên tắc làm việc.

## Thành viên

- **A** — Backend & DSP/Algorithm Lead
- **B** — Mobile & UI/UX Lead

## License

NCKH sinh viên — chỉ sử dụng cho mục đích học thuật.