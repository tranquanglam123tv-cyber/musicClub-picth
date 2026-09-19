-- Music Club Platform - Seed Data
-- MySQL 8.0+

-- =============================================
-- VOICE TYPES
-- =============================================
INSERT INTO voice_types (code, name, description, category, sort_order, is_active) VALUES
('SOPRANO', 'Soprano', 'Giọng nữ cao, vùng âm cao nhất của nữ', 'HIGH', 1, TRUE),
('MEZZO_SOPRANO', 'Mezzo-Soprano', 'Giọng nữ trung-cao', 'HIGH', 2, TRUE),
('ALTO', 'Alto', 'Giọng nữ trung-thấp', 'MIDDLE', 3, TRUE),
('TENOR', 'Tenor', 'Giọng nam cao', 'MIDDLE', 4, TRUE),
('BARITONE', 'Baritone', 'Giọng nam trung', 'MIDDLE', 5, TRUE),
('BASS', 'Bass', 'Giọng nam thấp', 'LOW', 6, TRUE);

-- =============================================
-- GENRES
-- =============================================
INSERT INTO genres (name, code, description, icon, color, sort_order, is_active) VALUES
('Pop', 'POP', 'Nhạc Pop hiện đại', 'music_note', '#FF6B6B', 1, TRUE),
('Ballad', 'BALLAD', 'Nhạc tình ca, ballad', 'favorite', '#FF9F43', 2, TRUE),
('Rock', 'ROCK', 'Nhạc Rock', 'guitar', '#EE5A24', 3, TRUE),
('R&B/Soul', 'RB_SOUL', 'Rhythm and Blues, Soul', 'headphones', '#9B59B6', 4, TRUE),
('Jazz', 'JAZZ', 'Nhạc Jazz', 'piano', '#2C3E50', 5, TRUE),
('Classical', 'CLASSICAL', 'Nhạc Cổ điển', 'library_music', '#8E44AD', 6, TRUE),
('Folk', 'FOLK', 'Nhạc Dân gian', 'nature_people', '#27AE60', 7, TRUE),
('Country', 'COUNTRY', 'Nhạc Country', 'terrain', '#D35400', 8, TRUE),
('Hip-Hop/Rap', 'HIPHOP', 'Hip-Hop và Rap', 'mic', '#34495E', 9, TRUE),
('EDM', 'EDM', 'Electronic Dance Music', 'party_mode', '#00CEC9', 10, TRUE),
('Musical Theater', 'MUSICAL', 'Nhạc kịch', 'theater_comedy', '#FDCB6E', 11, TRUE),
('Traditional Vietnamese', 'VIETNAMESE', 'Nhạc Việt Truyền thống', 'flag', '#E74C3C', 12, TRUE);

-- =============================================
-- SYSTEM SETTINGS
-- =============================================
INSERT INTO system_settings (setting_key, setting_value, setting_type, description, category, is_public, is_system) VALUES
('audio_max_size_mb', '10', 'INTEGER', 'Maximum audio file size in MB', 'AUDIO', FALSE, TRUE),
('audio_allowed_formats', '["wav", "mp3", "m4a", "ogg"]', 'JSON', 'Allowed audio formats', 'AUDIO', TRUE, TRUE),
('audio_default_sample_rate', '44100', 'INTEGER', 'Default sample rate for processing', 'AUDIO', FALSE, TRUE),
('f0_analysis_timeout', '60', 'INTEGER', 'F0 analysis timeout in seconds', 'AUDIO', FALSE, TRUE),
('recommendation_max_songs', '20', 'INTEGER', 'Maximum songs in recommendation', 'RECOMMENDATION', TRUE, TRUE),
('recommendation_default_weights', '{"range": 0.6, "genre": 0.25, "key": 0.10, "difficulty": 0.05}', 'JSON', 'Default recommendation weights', 'RECOMMENDATION', FALSE, TRUE),
('event_default_capacity', '50', 'INTEGER', 'Default event capacity', 'GENERAL', TRUE, TRUE),
('registration_open_days', '14', 'INTEGER', 'Days before event to open registration', 'GENERAL', TRUE, TRUE),
('app_name', 'Music Club Platform', 'STRING', 'Application name', 'GENERAL', TRUE, TRUE),
('app_version', '1.0.0', 'STRING', 'Current application version', 'GENERAL', TRUE, TRUE);

-- =============================================
-- SAMPLE SONGS
-- =============================================
INSERT INTO songs (added_by, title, artist, original_key, difficulty, duration_seconds, min_midi, max_midi, comfortable_min_midi, comfortable_max_midi, range_semitones) VALUES
(NULL, 'Nơi Này Có Anh', 'Sơn Tùng M-TP', 'C', 'INTERMEDIATE', 245, 52, 64, 55, 62, 12),
(NULL, 'Buông Đôi Tay Nhau Ra', 'Sơn Tùng M-TP', 'G', 'INTERMEDIATE', 267, 50, 66, 54, 62, 16),
(NULL, 'Cơn Mưa Ngang Qua', 'Sơn Tùng M-TP', 'D', 'BEGINNER', 234, 48, 62, 52, 60, 14),
(NULL, 'Âm Thầm Bên Em', 'Sơn Tùng M-TP', 'A', 'INTERMEDIATE', 258, 45, 64, 50, 60, 19),
(NULL, 'Hơn Cả Yêu', 'Đông Nhi', 'F', 'BEGINNER', 214, 43, 60, 48, 57, 17),
(NULL, 'Ngắn', 'Mỹ Tâm', 'Db', 'ADVANCED', 298, 58, 74, 62, 72, 16),
(NULL, 'Đúng Người Đúng Thời Điểm', 'Mỹ Tâm', 'Eb', 'INTERMEDIATE', 276, 51, 68, 56, 65, 17),
(NULL, 'Yêu', 'Mỹ Tâm', 'F', 'BEGINNER', 245, 43, 62, 48, 58, 19),
(NULL, 'Giấc Mơ Hoa', 'Mỹ Tâm', 'G', 'INTERMEDIATE', 267, 48, 66, 54, 62, 18),
(NULL, 'Mây Lang Thang', 'Ngọc Sơn', 'D', 'BEGINNER', 298, 42, 58, 46, 55, 16),
(NULL, 'Bến Đợi', 'Tuấn Ngọc', 'G', 'BEGINNER', 312, 40, 55, 44, 52, 15),
(NULL, 'Tình Ca', 'Tùng Duyên', 'A', 'INTERMEDIATE', 287, 48, 65, 54, 62, 17),
(NULL, 'Nơi Tình Yêu Bắt Đầu', 'Cẩm Ly', 'F', 'BEGINNER', 267, 43, 60, 48, 57, 17),
(NULL, 'Mùa Xuân Ơi', 'Hương Lan', 'C', 'INTERMEDIATE', 198, 48, 65, 54, 62, 17),
(NULL, 'Hát Với Chim Sáo', 'Lê Minh Sơn', 'D', 'BEGINNER', 245, 42, 58, 46, 55, 16),
(NULL, 'Đường Về Quê', 'Quang Lê', 'G', 'BEGINNER', 287, 38, 54, 42, 51, 16),
(NULL, 'Về Đây Cùng Nhau', 'Quang Lê', 'A', 'INTERMEDIATE', 312, 40, 56, 45, 53, 16),
(NULL, 'Thiệp Hồng', 'Quang Lê', 'F', 'BEGINNER', 267, 43, 58, 48, 55, 15),
(NULL, 'Cô Đơn', 'Khởi My', 'B', 'INTERMEDIATE', 234, 50, 66, 56, 63, 16),
(NULL, 'Từ Ngày Gặp Anh', 'Bảo Thy', 'G', 'BEGINNER', 221, 45, 60, 50, 57, 15);

-- =============================================
-- SONG GENRES
-- =============================================
INSERT INTO song_genres (song_id, genre_id, is_primary, weight) VALUES
-- Nơi Này Có Anh
(1, 1, TRUE, 1.00),  -- POP
-- Buông Đôi Tay Nhau Ra
(2, 1, TRUE, 1.00),  -- POP
-- Cơn Mưa Ngang Qua
(3, 2, TRUE, 1.00),  -- BALLAD
-- Âm Thầm Bên Em
(4, 2, TRUE, 1.00),  -- BALLAD
-- Hơn Cả Yêu
(5, 1, TRUE, 1.00),  -- POP
-- Ngắn
(6, 2, TRUE, 1.00),  -- BALLAD
-- Đúng Người Đúng Thời Điểm
(7, 1, TRUE, 1.00),  -- POP
-- Yêu
(8, 1, TRUE, 1.00),  -- POP
-- Giấc Mơ Hoa
(9, 2, TRUE, 1.00),  -- BALLAD
-- Mây Lang Thang
(10, 7, TRUE, 1.00), -- FOLK
-- Bến Đợi
(11, 7, TRUE, 1.00), -- FOLK
-- Tình Ca
(12, 12, TRUE, 1.00), -- VIETNAMESE
-- Nơi Tình Yêu Bắt Đầu
(13, 12, TRUE, 1.00), -- VIETNAMESE
-- Mùa Xuân Ơi
(14, 12, TRUE, 1.00), -- VIETNAMESE
-- Hát Với Chim Sáo
(15, 12, TRUE, 1.00), -- VIETNAMESE
-- Đường Về Quê
(16, 12, TRUE, 1.00), -- VIETNAMESE
-- Về Đây Cùng Nhau
(17, 12, TRUE, 1.00), -- VIETNAMESE
-- Thiệp Hồng
(18, 12, TRUE, 1.00), -- VIETNAMESE
-- Cô Đơn
(19, 1, TRUE, 1.00),  -- POP
-- Từ Ngày Gặp Anh
(20, 1, TRUE, 1.00);  -- POP

-- =============================================
-- SAMPLE USERS
-- =============================================
-- Password: Password123!
INSERT INTO users (email, username, password_hash, full_name, role, status, gender, email_verified_at) VALUES
('admin@musicclub.vn', 'admin', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Quản Trị Viên', 'ADMIN', 'ACTIVE', 'OTHER', NOW()),
('user@example.com', 'user1', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Nguyễn Văn A', 'MEMBER', 'ACTIVE', 'MALE', NOW()),
('user2@example.com', 'user2', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Trần Thị B', 'MEMBER', 'ACTIVE', 'FEMALE', NOW()),
('user3@example.com', 'user3', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Lê Văn C', 'MEMBER', 'ACTIVE', 'MALE', NOW());

-- =============================================
-- SAMPLE VOICE PROFILES
-- =============================================
INSERT INTO voice_profiles (user_id, voice_type, min_f0, max_f0, avg_f0, median_f0, min_midi, max_midi, range_semitones, confidence, stability_score, quality_grade, total_analyses) VALUES
(2, 'TENOR', 131.0, 523.0, 245.5, 240.0, 48, 72, 24.0, 0.85, 0.78, 'B', 5),
(3, 'MEZZO_SOPRANO', 208.0, 784.0, 392.0, 385.0, 58, 81, 23.0, 0.82, 0.75, 'B', 4),
(4, 'BARITONE', 98.0, 440.0, 196.0, 190.0, 45, 69, 24.0, 0.88, 0.80, 'A', 6);

-- =============================================
-- SAMPLE EVENTS
-- =============================================
INSERT INTO events (organizer_id, title, description, event_type, start_time, end_time, location, capacity, registered_count, status) VALUES
(1, 'Sinh hoạt câu lạc bộ tuần 1', 'Buổi sinh hoạt đầu tiên của năm học mới', 'PRACTICE', DATE_ADD(NOW(), INTERVAL 7 DAY), DATE_ADD(NOW(), INTERVAL 7 DAY + 3 HOUR), 'Phòng A101, Trường ĐH', 30, 12, 'PUBLISHED'),
(1, 'Workshop Kỹ thuật hát', 'Học cách phát âm và hơi thở đúng', 'WORKSHOP', DATE_ADD(NOW(), INTERVAL 14 DAY), DATE_ADD(NOW(), INTERVAL 14 DAY + 4 HOUR), 'Phòng B202, Trường ĐH', 20, 8, 'PUBLISHED'),
(1, 'Biểu diễn Tết Nguyên Đán', 'Chuẩn bị cho tiết mục biểu diễn Tết', 'PERFORMANCE', DATE_ADD(NOW(), INTERVAL 60 DAY), DATE_ADD(NOW(), INTERVAL 60 DAY + 5 HOUR), 'Hội trường lớn', 100, 25, 'PUBLISHED');
