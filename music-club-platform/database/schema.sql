-- Music Club Platform - Database Schema
-- MySQL 8.0+

-- =============================================
-- USERS TABLE
-- =============================================
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    role ENUM('MEMBER', 'ADMIN', 'MODERATOR') DEFAULT 'MEMBER',
    status ENUM('ACTIVE', 'INACTIVE', 'BANNED') DEFAULT 'ACTIVE',
    date_of_birth DATE,
    gender ENUM('MALE', 'FEMALE', 'OTHER') DEFAULT 'OTHER',
    email_verified_at TIMESTAMP NULL,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_status (status)
);

-- =============================================
-- VOICE TYPES TABLE
-- =============================================
CREATE TABLE voice_types (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category ENUM('HIGH', 'MIDDLE', 'LOW') DEFAULT 'MIDDLE',
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_category (category),
    INDEX idx_active (is_active)
);

-- =============================================
-- VOICE PROFILES TABLE
-- =============================================
CREATE TABLE voice_profiles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL UNIQUE,
    voice_type_id BIGINT,
    voice_type VARCHAR(50),
    min_f0 DECIMAL(10,2),
    max_f0 DECIMAL(10,2),
    avg_f0 DECIMAL(10,2),
    median_f0 DECIMAL(10,2),
    std_f0 DECIMAL(10,4),
    min_midi INT,
    max_midi INT,
    median_midi INT,
    range_semitones DECIMAL(6,2),
    confidence DECIMAL(4,3),
    stability_score DECIMAL(4,3),
    quality_grade CHAR(1),
    total_analyses INT DEFAULT 0,
    last_analyzed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (voice_type_id) REFERENCES voice_types(id) ON DELETE SET NULL,
    INDEX idx_voice_type (voice_type),
    INDEX idx_confidence (confidence)
);

-- =============================================
-- VOICE ANALYSES TABLE
-- =============================================
CREATE TABLE voice_analyses (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    voice_profile_id BIGINT,
    min_f0 DECIMAL(10,2),
    max_f0 DECIMAL(10,2),
    avg_f0 DECIMAL(10,2),
    median_f0 DECIMAL(10,2),
    std_f0 DECIMAL(10,4),
    min_midi INT,
    max_midi INT,
    median_midi INT,
    voice_type VARCHAR(50),
    confidence DECIMAL(4,3),
    voiced_ratio DECIMAL(5,4),
    stability_score DECIMAL(4,3),
    quality_grade CHAR(1),
    range_semitones DECIMAL(6,2),
    note_distribution JSON,
    f0_contour JSON,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (voice_profile_id) REFERENCES voice_profiles(id) ON DELETE SET NULL,
    INDEX idx_user_analyses (user_id, analyzed_at),
    INDEX idx_voice_type (voice_type)
);

-- =============================================
-- GENRES TABLE
-- =============================================
CREATE TABLE genres (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(100),
    color VARCHAR(7),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_code (code),
    INDEX idx_active (is_active)
);

-- =============================================
-- SONGS TABLE
-- =============================================
CREATE TABLE songs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    added_by BIGINT,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    album VARCHAR(255),
    original_key VARCHAR(10),
    difficulty ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT') DEFAULT 'INTERMEDIATE',
    duration_seconds INT,
    lyrics_preview TEXT,
    min_midi INT,
    max_midi INT,
    comfortable_min_midi INT,
    comfortable_max_midi INT,
    range_semitones DECIMAL(6,2),
    is_active BOOLEAN DEFAULT TRUE,
    view_count INT DEFAULT 0,
    favorite_count INT DEFAULT 0,
    avg_rating DECIMAL(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_title (title),
    INDEX idx_artist (artist),
    INDEX idx_difficulty (difficulty),
    INDEX idx_original_key (original_key),
    INDEX idx_midi_range (min_midi, max_midi),
    INDEX idx_active (is_active),
    FULLTEXT INDEX ft_songs (title, artist, lyrics_preview)
);

-- =============================================
-- SONG GENRES TABLE
-- =============================================
CREATE TABLE song_genres (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    song_id BIGINT NOT NULL,
    genre_id BIGINT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    weight DECIMAL(3,2) DEFAULT 1.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE,
    UNIQUE KEY uk_song_genre (song_id, genre_id),
    INDEX idx_song (song_id),
    INDEX idx_genre (genre_id)
);

-- =============================================
-- USER GENRES TABLE
-- =============================================
CREATE TABLE user_genres (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    genre_id BIGINT NOT NULL,
    preference_level INT DEFAULT 3 CHECK (preference_level BETWEEN 1 AND 5),
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_genre (user_id, genre_id),
    INDEX idx_user (user_id)
);

-- =============================================
-- EVENTS TABLE
-- =============================================
CREATE TABLE events (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    organizer_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT,
    event_type ENUM('PRACTICE', 'PERFORMANCE', 'COMPETITION', 'WORKSHOP') DEFAULT 'PRACTICE',
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location VARCHAR(255),
    location_detail VARCHAR(255),
    location_link VARCHAR(500),
    capacity INT DEFAULT 0,
    registered_count INT DEFAULT 0,
    waitlist_count INT DEFAULT 0,
    registration_deadline TIMESTAMP,
    status ENUM('DRAFT', 'PUBLISHED', 'CANCELLED', 'COMPLETED') DEFAULT 'DRAFT',
    cover_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organizer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_start_time (start_time),
    INDEX idx_status (status),
    INDEX idx_type (event_type),
    INDEX idx_upcoming (start_time, status)
);

-- =============================================
-- EVENT REGISTRATIONS TABLE
-- =============================================
CREATE TABLE event_registrations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    status ENUM('REGISTERED', 'WAITLIST', 'CANCELLED', 'ATTENDED', 'NO_SHOW') DEFAULT 'REGISTERED',
    check_in_time TIMESTAMP NULL,
    check_out_time TIMESTAMP NULL,
    notes TEXT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_event (user_id, event_id),
    INDEX idx_event_status (event_id, status)
);

-- =============================================
-- POSTS TABLE
-- =============================================
CREATE TABLE posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    author_id BIGINT NOT NULL,
    event_id BIGINT,
    title VARCHAR(255),
    content TEXT NOT NULL,
    post_type ENUM('ANNOUNCEMENT', 'NEWS', 'TIP', 'DISCUSSION', 'EVENT_REVIEW') DEFAULT 'ANNOUNCEMENT',
    status ENUM('DRAFT', 'PUBLISHED', 'HIDDEN', 'DELETED') DEFAULT 'DRAFT',
    visibility ENUM('PUBLIC', 'MEMBERS', 'ADMINS') DEFAULT 'MEMBERS',
    cover_image_url VARCHAR(500),
    view_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    published_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL,
    INDEX idx_author (author_id),
    INDEX idx_type (post_type),
    INDEX idx_status (status),
    INDEX idx_published (published_at),
    FULLTEXT INDEX ft_posts (title, content)
);

-- =============================================
-- POST COMMENTS TABLE
-- =============================================
CREATE TABLE post_comments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    parent_comment_id BIGINT,
    content TEXT NOT NULL,
    status ENUM('ACTIVE', 'HIDDEN', 'DELETED') DEFAULT 'ACTIVE',
    like_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES post_comments(id) ON DELETE CASCADE,
    INDEX idx_post (post_id),
    INDEX idx_author (author_id)
);

-- =============================================
-- POST LIKES TABLE
-- =============================================
CREATE TABLE post_likes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_post_user (post_id, user_id)
);

-- =============================================
-- RECOMMENDATION LOGS TABLE
-- =============================================
CREATE TABLE recommendation_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    recommendation_type ENUM('SONG', 'EVENT', 'CONTENT') DEFAULT 'SONG',
    item_id BIGINT NOT NULL,
    item_type VARCHAR(50),
    score DECIMAL(5,4),
    factors JSON,
    was_accepted BOOLEAN NULL,
    recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_recommendations (user_id, recommended_at)
);

-- =============================================
-- SYSTEM SETTINGS TABLE
-- =============================================
CREATE TABLE system_settings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    setting_type ENUM('STRING', 'INTEGER', 'BOOLEAN', 'JSON') DEFAULT 'STRING',
    description TEXT,
    category ENUM('GENERAL', 'AUDIO', 'RECOMMENDATION', 'EMAIL') DEFAULT 'GENERAL',
    is_public BOOLEAN DEFAULT FALSE,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_category (category),
    INDEX idx_key (setting_key)
);

-- =============================================
-- AUDIT LOGS TABLE
-- =============================================
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    action ENUM('CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'ANALYZE') NOT NULL,
    entity_type VARCHAR(100),
    entity_id BIGINT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_user_actions (user_id, created_at),
    INDEX idx_action (action)
);
