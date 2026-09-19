# PROJECT CHARTER
## Đề tài
**Nghiên cứu ứng dụng kỹ thuật phân tích tần số âm thanh F₀ tự động nhận diện Tông giọng và gợi ý bài hát theo thể loại cho hệ thống quản lý Câu lạc bộ Âm nhạc đa nền tảng**

> Tài liệu này là **Day 01** — Kickoff. Nó chốt **mục tiêu, phạm vi, phân công, milestones 100 ngày** để hai thành viên làm việc đồng bộ.
> Chi tiết kỹ thuật từng ngày xem `roadmap.md` (master plan).

---

## 1. Thông tin dự án

| Mục | Nội dung |
|---|---|
| Tên | Music Club Platform |
| Loại | Đồ án nghiên cứu ứng dụng — NCKH sinh viên |
| Thời gian | 100 ngày |
| Quy mô | 2 thành viên |
| Ngôn ngữ chính | Python (DSP), Java/Spring Boot (backend), Dart/Flutter (mobile), TypeScript/React (admin) |
| Repo | https://github.com/tranquanglam123tv-cyber/musicClub-picth |
| Ngày bắt đầu | 19/09/2026 |

---

## 2. Mục tiêu dự án

### 2.1. Mục tiêu nghiên cứu (Research Goal)
Chứng minh rằng quy trình **F₀ extraction → voice classification → song recommendation** có thể được triển khai thành một hệ thống thực tế với **phương pháp rõ ràng, số liệu đo được và giới hạn được ghi nhận** — không chỉ là "app chạy được".

### 2.2. Mục tiêu sản phẩm (Product Goal)
Xây dựng hệ thống quản lý Câu lạc bộ Âm nhạc đa nền tảng:
- **Mobile** (Flutter) cho thành viên: thu âm, xem voice range, nhận đề xuất bài hát, đăng ký sự kiện.
- **Admin Web** (React) cho quản trị: quản lý thành viên, sự kiện, bài hát, bài viết, xem voice profile.
- **Backend** (Spring Boot) xử lý nghiệp vụ.
- **DSP Service** (Python FastAPI) xử lý phân tích âm thanh.

### 2.3. Mục tiêu cá nhân
- Thành viên A: làm chủ Spring Boot + Python DSP + Recommendation + Admin Web.
- Thành viên B: làm chủ Flutter + Audio UI + UX flow + Mobile testing.

---

## 3. Câu hỏi nghiên cứu (Research Questions)

Đồ án phải trả lời được **4 câu hỏi** này trong chương Thực nghiệm của báo cáo.

### RQ1 — F₀ Accuracy
> Phương pháp pYIN có thể trích xuất F₀ từ giọng hát trong điều kiện thử nghiệm với độ chính xác như thế nào?

**Metric gợi ý:** Cents error (RPA), Gross Pitch Error (GPE), Voicing Recall.

### RQ2 — Robustness
> Preprocessing và filtering cải thiện kết quả F₀ như thế nào?

**Metric gợi ý:** So sánh F₀ error trước/sau preprocessing (resample, normalize, VAD, smoothing) trên cùng dataset.

### RQ3 — Voice Range & Classification
> F₀ contour có thể được sử dụng để ước lượng vocal range và phân nhóm giọng (Soprano/Alto/Tenor/Bass) ở mức ứng dụng như thế nào?

**Metric gợi ý:** Confusion matrix trên dataset có nhãn giọng (nếu có), hoặc manual evaluation.

### RQ4 — Recommendation
> Việc kết hợp vocal range + key + genre có tạo recommendation phù hợp hơn so với chỉ dùng genre hay không?

**Metric gợi ý:** Ablation study — so sánh `genre only`, `range only`, `range + genre`, `range + genre + key`; Precision@K nếu có ground truth.

> Các RQ này là **trọng tâm bảo vệ**. Tính năng phụ (realtime, push notification, ML nâng cao) sẽ bị cắt trước nếu trễ tiến độ — RQ thì không.

---

## 4. Phạm vi MVP

### 4.1. MUST HAVE (không cắt)

**Research / Audio**
- Upload/thu âm giọng hát
- Chuẩn hóa audio (mono, resample, normalize)
- Pitch/F₀ detection bằng pYIN (librosa)
- Loại bỏ frame không có pitch, smoothing, outlier removal
- Hz → MIDI → Note name
- Vocal range (percentile-based, robust)
- Phân nhóm giọng rule-based (Soprano/Alto/Tenor/Bass)
- Confidence/quality indicator
- Đánh giá thuật toán trên dataset thử nghiệm

**Recommendation**
- Metadata bài hát (title, artist, key, range, genre, difficulty)
- Rule-based scoring (range + genre + key + difficulty)
- Top-N recommendation
- Explanation cho mỗi gợi ý

**Backend (Spring Boot)**
- Auth (JWT) + Role MEMBER/ADMIN
- CRUD Users, Songs, Events, Posts, VoiceProfiles, VoiceAnalyses
- Event registration
- Recommendation API
- Voice analysis API gateway → gọi Python service

**Mobile (Flutter)**
- Login/Register
- Home, Event list/detail, Event registration
- Thu âm + upload
- Hiển thị F₀/voice range/voice type
- Hiển thị recommendation + giải thích

**Admin Web (React + TypeScript)**
- Login + Dashboard cơ bản
- Quản lý thành viên, sự kiện, bài hát, bài viết
- Xem voice profile

### 4.2. OPTIONAL (chỉ làm nếu MVP ổn định)

- F₀ realtime trên mobile
- Biểu đồ F₀ realtime, spectrogram
- Speaker-independent deep learning pitch detection
- Collaborative filtering recommendation
- Push notification, cloud storage
- Docker production deployment
- Multi-language
- Phân tích bài hát tự động thay vì nhập metadata thủ công

> **Quy tắc:** không triển khai realtime hoặc ML nâng cao nếu upload-file pipeline chưa ổn định.

---

## 5. Kiến trúc tổng thể

```text
                +----------------------+
                |   Flutter Mobile     |
                | Member Application   |
                +----------+-----------+
                           |
                           | HTTPS / REST
                           v
                +----------------------+
                | Spring Boot Backend  |
                | Auth / Club / Song / |
                | Event / Recommendation
                +----+------------+----+
                     |            |
             REST    |            | JDBC/JPA
                     |            v
                     |       +---------+
                     |       | MySQL   |
                     |       +---------+
                     |
                     | Internal REST
                     v
             +----------------------+
             | Python FastAPI       |
             | Audio Analysis       |
             | - preprocessing      |
             | - F0 / pitch         |
             | - range              |
             | - voice type         |
             +----------------------+
```

**Nguyên tắc:**
- Python chỉ xử lý DSP, không quản lý business DB.
- Spring Boot là trung tâm nghiệp vụ, gọi Python qua REST internal.
- Mobile và Admin Web chỉ giao tiếp với Spring Boot.

---

## 6. Phân công

### Thành viên A — Backend & DSP/Algorithm Lead

- Java/Spring Boot (REST API, Security, JPA)
- MySQL (schema, migration, seed)
- Python DSP (preprocessing, pYIN, range, voice type)
- Recommendation engine
- React Admin Web
- API integration architecture
- Experiment & evaluation (RQ1–RQ4)
- Backend/algorithm documentation

### Thành viên B — Mobile & UI/UX Lead  ← **bạn**

- Flutter (mobile architecture, navigation, theme)
- Recording + audio UI
- REST integration với Spring Boot
- Member experience flow
- UI/UX design
- Mobile testing
- Mobile documentation

### Chung

- Thiết kế kiến trúc, review API
- Git/GitHub workflow (branch + PR)
- Dataset/ground truth (chia sẻ)
- Demo, báo cáo, slide bảo vệ

---

## 7. Timeline 100 ngày — Milestones

| Phase | Ngày | Tên | Mục tiêu chính |
|---|---|---|---|
| 1 | 1–15 | **Nền tảng nghiên cứu & Kiến trúc** | Chốt scope, có F₀ pipeline v0, ERD, kiến trúc, dataset test |
| 2 | 16–35 | **Backend & Database** | Spring Boot + MySQL + JWT + Python service online, end-to-end audio request |
| 3 | 36–55 | **F₀, Voice Range & Recommendation** | Có evaluation RQ1–RQ4, recommendation v1 chạy đúng |
| 4 | 56–75 | **Flutter Mobile & Admin Web** | Mobile + Admin chạy được MVP features |
| 5 | 76–90 | **Integration, Testing & Optimization** | End-to-end regression, performance, security |
| 6 | 91–100 | **Báo cáo, Đóng gói & Bảo vệ** | Report + slide + demo reproducible |

### Milestone gates (PASS criteria)

- **M1 (Day 15):** F₀ pipeline v0 chạy được, có ERD, kiến trúc, dataset test.
- **M2 (Day 35):** Spring Boot + MySQL ổn, JWT chạy, Python service nhận audio, end-to-end hoạt động.
- **M3 (Day 55):** Có F₀ accuracy, voice classification, recommendation có scoring rõ ràng và bảng ablation.
- **M4 (Day 75):** User login → record → upload → analysis → recommendation chạy trên mobile + admin CRUD core data.
- **M5 (Day 90):** Không còn blocker, có benchmark, có F₀ + recommendation evaluation, có limitation list.
- **FINAL (Day 100):** MVP end-to-end, báo cáo hoàn chỉnh, demo reproducible, tag `v1.0-final`.

Chi tiết task từng ngày xem `roadmap.md`.

---

## 8. Definition of Done

### Task chung
- [ ] Code chạy được, không có blocker
- [ ] Có test (unit/integration) hoặc test thủ công rõ ràng
- [ ] API/doc được cập nhật nếu liên quan
- [ ] Code đã commit + push
- [ ] Branch merge vào `develop`
- [ ] Người còn lại review nếu ảnh hưởng integration

### F₀ module
- [ ] Input audio hợp lệ
- [ ] Có preprocessing
- [ ] Có pitch detection (pYIN)
- [ ] Có filtering (voiced probability, outlier, smoothing)
- [ ] Có Hz → note
- [ ] Có range (percentile)
- [ ] Có voice classification
- [ ] Có confidence/warning
- [ ] Có evaluation (RQ1–RQ3)
- [ ] Có limitation

### Recommendation module
- [ ] Có song metadata + user voice profile + genre preference
- [ ] Có scoring formula với weights được đánh giá (RQ4)
- [ ] Có Top-N
- [ ] Có explanation
- [ ] Có test cases

---

## 9. Risks (Top 5)

| Risk | Mức độ | Cách xử lý |
|---|---|---|
| F₀ octave error | Cao | pYIN + filtering + smoothing + evaluation |
| Voice type khó phân loại | Cao | Rule-based + ghi limitation trong báo cáo |
| Python/Java integration lỗi | Cao | Chốt API contract từ Day 14 |
| Dataset ít cho evaluation | Cao | Kết hợp public dataset (ví dụ: MIR-1K, Vocalset) + controlled samples |
| Scope creep | Rất cao | Tách MUST/OPTIONAL rõ ràng, ưu tiên RQ |

Chi tiết đầy đủ 15 risks xem `roadmap.md` mục 13.

---

## 10. Deliverables cuối cùng

### Software
- [ ] Flutter Mobile App
- [ ] Spring Boot REST API
- [ ] Python FastAPI DSP Service
- [ ] React + TypeScript Admin Web
- [ ] MySQL database (schema + seed)
- [ ] Postman collection

### Research
- [ ] F₀ methodology (preprocessing + pYIN)
- [ ] Voice range method
- [ ] Voice classification rule
- [ ] Recommendation algorithm với ablation
- [ ] Evaluation metrics + benchmark results
- [ ] Limitations list

### Documentation
- [ ] README, Installation guide
- [ ] Architecture diagram, ERD
- [ ] API documentation
- [ ] Final report (LaTeX hoặc Markdown)
- [ ] Slide bảo vệ
- [ ] Demo script

---

## 11. Nguyên tắc làm việc

1. **Hai người đọc lại tài liệu này và `roadmap.md`** trước khi code.
2. **Không code trực tiếp trên `main`.** Mọi task tạo branch riêng từ `develop`.
3. **Commit nhỏ, có ý nghĩa**, message theo convention `feat(scope): ...`.
4. **Mỗi 3–5 ngày sync 1 lần** để cập nhật tiến độ + blockers.
5. **Nếu phải lựa chọn** giữa "thêm tính năng" và "nâng chất lượng nghiên cứu" → chọn nghiên cứu.
6. **Trễ 3 ngày** → cắt community nâng cao, dashboard nâng cao.
7. **Trễ 7 ngày** → cắt realtime, voice history, push notification.
8. **Trễ 14 ngày** → chỉ giữ: Login → Record → Analyze → Recommend → Event.

---

## 12. Tài liệu tham chiếu

- `roadmap.md` — Kế hoạch chi tiết 100 ngày (master plan)
- `README.md` — Hướng dẫn cài đặt & chạy dự án
- `docs/` — Architecture, API, Research notes (sẽ tạo ở Day 14+)

---

**Ngày khởi tạo:** 19/09/2026
**Trạng thái:** Day 01 — Kickoff ✅
**Cập nhật lần cuối:** 19/09/2026