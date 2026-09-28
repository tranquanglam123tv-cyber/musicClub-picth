-- =====================================================================
-- Music Club Platform - Database Schema
-- =====================================================================
-- Database: MySQL 8.0+
-- Charset:  utf8mb4 / utf8mb4_unicode_ci
-- Engine:   InnoDB
-- Author:   Music Club Team
-- =====================================================================

CREATE DATABASE IF NOT EXISTS music_club_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE music_club_db;

SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================================
-- 1. BẢNG THAM CHIẾU (Reference Tables)
-- =====================================================================

-- 1.1. Voice Types - Loại giọng (6 loại chuẩn)
DROP TABLE IF EXISTS voice_types;
CREATE TABLE voice_types (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(20) NOT NULL UNIQUE,           -- SOPRANO, MEZZO_SOPRANO, ALTO, TENOR, BARITONE, BASS
    name_vi VARCHAR(100) NOT NULL,              -- Nữ cao, Nữ trung cao, Nữ trung, Nam cao, Nam trung cao, Nam trầm
    name_en VARCHAR(100) NOT NULL,              -- Soprano, Mezzo-Soprano, Alto, Tenor, Baritone, Bass
    min_midi INT NOT NULL,
    max_midi INT NOT NULL,
    typical_min_hz DECIMAL(10,2),
    typical_max_hz DECIMAL(10,2),
    description TEXT,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code (code)
) ENGINE=InnoDB;

-- 1.2. Genres - Thể loại nhạc
DROP TABLE IF EXISTS genres;
CREATE TABLE genres (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color_hex VARCHAR(7),                       -- Màu hiển thị UI
    icon VARCHAR(50),                           -- Icon class
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 1.3. Voice Ranges - Quãng giọng chuẩn (chi tiết)
DROP TABLE IF EXISTS voice_ranges;
CREATE TABLE voice_ranges (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    voice_type_id BIGINT NOT NULL,
    note_name VARCHAR(10) NOT NULL,             -- C4, D4, ...
    midi_note INT NOT NULL,
    frequency DECIMAL(10,2) NOT NULL,
    is_typical_low BOOLEAN DEFAULT FALSE,
    is_typical_high BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (voice_type_id) REFERENCES voice_types(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================================
-- 2. BẢNG NGƯỜI DÙNG
-- =====================================================================

-- 2.1. Users - Tài khoản người dùng
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    date_of_birth DATE,
    gender ENUM('MALE','FEMALE','OTHER') DEFAULT 'OTHER',
    role ENUM('ADMIN','MEMBER','GUEST') NOT NULL DEFAULT 'MEMBER',
    student_id VARCHAR(20),
    class_name VARCHAR(100),
    faculty VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_active (is_active)
) ENGINE=InnoDB;

-- 2.2. User Genres - Sở thích thể loại (N-N)
DROP TABLE IF EXISTS user_genres;
CREATE TABLE user_genres (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    genre_id BIGINT NOT NULL,
    preference_level TINYINT DEFAULT 3,          -- 1-5
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_genre (user_id, genre_id)
) ENGINE=InnoDB;

-- 2.3. User Songs - Bài hát yêu thích
DROP TABLE IF EXISTS user_songs;
CREATE TABLE user_songs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    song_id BIGINT NOT NULL,
    is_favorite BOOLEAN DEFAULT TRUE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_song (user_id, song_id)
) ENGINE=InnoDB;

-- 2.4. API Tokens - Quản lý token cho mobile
DROP TABLE IF EXISTS api_tokens;
CREATE TABLE api_tokens (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    token VARCHAR(500) NOT NULL UNIQUE,
    refresh_token VARCHAR(500),
    device_id VARCHAR(100),
    device_name VARCHAR(100),
    expires_at TIMESTAMP NOT NULL,
    refresh_expires_at TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token(191)),
    INDEX idx_user (user_id)
) ENGINE=InnoDB;

-- =====================================================================
-- 3. BẢNG HỒ SƠ GIỌNG HÁT
-- =====================================================================

-- 3.1. Vocal Profiles - Hồ sơ giọng hát tổng hợp (1 user - 1 profile)
DROP TABLE IF EXISTS vocal_profiles;
CREATE TABLE vocal_profiles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL UNIQUE,
    voice_type_id BIGINT,
    voice_type VARCHAR(50),                     -- Cache text: TENOR, ALTO...
    min_f0 DECIMAL(10,2),
    max_f0 DECIMAL(10,2),
    min_midi INT,
    max_midi INT,
    avg_f0 DECIMAL(10,2),
    median_f0 DECIMAL(10,2),
    range_semitones DECIMAL(6,2),
    confidence DECIMAL(4,3),
    stability_score DECIMAL(4,3),
    quality_grade CHAR(1),                      -- A, B, C, D, E, F
    recommended_genres JSON,                    -- ["Pop","Ballad"]
    total_sessions INT DEFAULT 0,
    last_analyzed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (voice_type_id) REFERENCES voice_types(id) ON DELETE SET NULL,
    INDEX idx_voice_type (voice_type),
    INDEX idx_confidence (confidence)
) ENGINE=InnoDB;

-- 3.2. Voice Analyses - Lịch sử phân tích (chi tiết từng session)
DROP TABLE IF EXISTS voice_analyses;
CREATE TABLE voice_analyses (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    session_id VARCHAR(100),                    -- UUID từ mobile
    min_f0 DECIMAL(10,2),
    max_f0 DECIMAL(10,2),
    avg_f0 DECIMAL(10,2),
    median_f0 DECIMAL(10,2),
    range_semitones DECIMAL(6,2),
    voiced_ratio DECIMAL(4,3),
    confidence DECIMAL(4,3),
    audio_duration_seconds DECIMAL(8,2),
    sample_rate INT,
    audio_file_url VARCHAR(500),
    analysis_metadata JSON,                     -- Extra info
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- =====================================================================
-- 4. BẢNG BÀI HÁT
-- =====================================================================

-- 4.1. Songs - Kho bài hát CLB
DROP TABLE IF EXISTS songs;
CREATE TABLE songs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    composer VARCHAR(255),
    lyricist VARCHAR(255),
    original_key VARCHAR(10),                   -- C, Am, G...
    min_midi INT,
    max_midi INT,
    difficulty ENUM('BEGINNER','INTERMEDIATE','ADVANCED','EXPERT') DEFAULT 'INTERMEDIATE',
    duration_seconds INT,
    bpm INT,
    lyrics TEXT,
    chords TEXT,                                -- [Verse] Am G F...
    sheet_url VARCHAR(500),
    audio_preview_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    view_count INT DEFAULT 0,
    rating_avg DECIMAL(3,2) DEFAULT 0,
    rating_count INT DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    created_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_title (title),
    INDEX idx_difficulty (difficulty)
) ENGINE=InnoDB;

-- 4.2. Song Genres - Phân loại bài hát (N-N)
DROP TABLE IF EXISTS song_genres;
CREATE TABLE song_genres (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    song_id BIGINT NOT NULL,
    genre_id BIGINT NOT NULL,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE,
    UNIQUE KEY uk_song_genre (song_id, genre_id)
) ENGINE=InnoDB;

-- 4.3. Song Ratings - Đánh giá bài hát
DROP TABLE IF EXISTS song_ratings;
CREATE TABLE song_ratings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    song_id BIGINT NOT NULL,
    rating TINYINT NOT NULL,                    -- 1-5
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_song_rating (user_id, song_id),
    CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB;

-- =====================================================================
-- 5. BẢNG SỰ KIỆN
-- =====================================================================

-- 5.1. Events - Lịch sinh hoạt CLB
DROP TABLE IF EXISTS events;
CREATE TABLE events (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    event_type ENUM('REHEARSAL','PERFORMANCE','WORKSHOP','COMPETITION','SOCIAL','OTHER') DEFAULT 'REHEARSAL',
    max_participants INT,
    requires_registration BOOLEAN DEFAULT TRUE,
    cover_image_url VARCHAR(500),
    status ENUM('UPCOMING','ONGOING','COMPLETED','CANCELLED') DEFAULT 'UPCOMING',
    created_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_start_time (start_time),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- 5.2. Event Registrations - Đăng ký sự kiện
DROP TABLE IF EXISTS event_registrations;
CREATE TABLE event_registrations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    registration_status ENUM('REGISTERED','WAITLIST','CANCELLED') DEFAULT 'REGISTERED',
    note TEXT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_event (user_id, event_id)
) ENGINE=InnoDB;

-- 5.3. Attendance - Điểm danh
DROP TABLE IF EXISTS attendance;
CREATE TABLE attendance (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    status ENUM('ATTENDED','ABSENT','LATE','EXCUSED') DEFAULT 'ABSENT',
    check_in_time TIMESTAMP NULL,
    check_out_time TIMESTAMP NULL,
    notes TEXT,
    recorded_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY uk_user_event (user_id, event_id),
    INDEX idx_event (event_id)
) ENGINE=InnoDB;

-- =====================================================================
-- 6. BẢNG CỘNG ĐỒNG
-- =====================================================================

-- 6.1. Posts - Bài viết cộng đồng
DROP TABLE IF EXISTS posts;
CREATE TABLE posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    image_url VARCHAR(500),
    event_id BIGINT,                            -- Optional: liên kết sự kiện
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_hidden BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- 6.2. Post Comments
DROP TABLE IF EXISTS post_comments;
CREATE TABLE post_comments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    parent_id BIGINT,                           -- Reply comment
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES post_comments(id) ON DELETE CASCADE,
    INDEX idx_post (post_id)
) ENGINE=InnoDB;

-- 6.3. Post Likes
DROP TABLE IF EXISTS post_likes;
CREATE TABLE post_likes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_post_user (post_id, user_id)
) ENGINE=InnoDB;

-- =====================================================================
-- 7. BẢNG GỢI Ý & HỆ THỐNG
-- =====================================================================

-- 7.1. Recommendation Logs - Log gợi ý (để cải thiện thuật toán)
DROP TABLE IF EXISTS recommendation_logs;
CREATE TABLE recommendation_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    algorithm_version VARCHAR(20),               -- v1.0, v2.0...
    recommended_song_ids JSON,
    clicked_song_id BIGINT,
    feedback_rating TINYINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
) ENGINE=InnoDB;

-- 7.2. Notifications - Thông báo
DROP TABLE IF EXISTS notifications;
CREATE TABLE notifications (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('INFO','WARNING','SUCCESS','EVENT','SYSTEM') DEFAULT 'INFO',
    related_url VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_unread (user_id, is_read)
) ENGINE=InnoDB;

-- 7.3. Audit Logs - Nhật ký hành động
DROP TABLE IF EXISTS audit_logs;
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id BIGINT,
    old_value JSON,
    new_value JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- 7.4. System Settings
DROP TABLE IF EXISTS system_settings;
CREATE TABLE system_settings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    setting_type ENUM('STRING','INTEGER','BOOLEAN','JSON') DEFAULT 'STRING',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    updated_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 7.5. File Uploads
DROP TABLE IF EXISTS file_uploads;
CREATE TABLE file_uploads (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    file_name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255),
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    file_type ENUM('AUDIO','IMAGE','DOCUMENT','OTHER') DEFAULT 'OTHER',
    related_entity VARCHAR(50),
    related_id BIGINT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_related (related_entity, related_id)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- END OF SCHEMA
-- =====================================================================
