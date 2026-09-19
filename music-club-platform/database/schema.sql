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
    INDEX idx_status (status),
    INDEX idx_role_status (role, status)
);

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

CREATE TABLE voice_ranges (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE,
    min_midi INT NOT NULL,
    max_midi INT NOT NULL,
    description TEXT,
    difficulty_level ENUM('EASY', 'MEDIUM', 'HARD', 'EXPERT') DEFAULT 'MEDIUM',
    song_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_midi_range (min_midi, max_midi)
);

CREATE TABLE voice_type_ranges (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    voice_type_id BIGINT NOT NULL,
    voice_range_id BIGINT NOT NULL,
    -- MIDI values are integers (note numbers 0-127)
    typical_min_midi INT,                      -- e.g., 48 (C3)
    typical_max_midi INT,                      -- e.g., 72 (C5)
    lower_boundary_midi INT,                    -- Lowest comfortable note
    upper_boundary_midi INT,                    -- Highest comfortable note
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (voice_type_id) REFERENCES voice_types(id) ON DELETE CASCADE,
    FOREIGN KEY (voice_range_id) REFERENCES voice_ranges(id) ON DELETE CASCADE,
    UNIQUE KEY uk_type_range (voice_type_id, voice_range_id)
);

CREATE TABLE voice_profiles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL UNIQUE,
    voice_type_id BIGINT,
    voice_type VARCHAR(50),
    min_f0 DECIMAL(10,2),
    max_f0 DECIMAL(10,2),
    avg_f0 DECIMAL(10,2),
    median_f0 DECIMAL(10,2),
    min_midi INT,
    max_midi INT,
    median_midi INT,
    range_semitones DECIMAL(6,2),
    confidence DECIMAL(4,3),
    stability_score DECIMAL(4,3),
    quality_grade CHAR(1),
    metadata JSON,
    analyzed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (voice_type_id) REFERENCES voice_types(id) ON DELETE SET NULL,
    INDEX idx_voice_type (voice_type),
    INDEX idx_confidence (confidence)
);

CREATE TABLE audio_samples (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_url VARCHAR(500),
    file_size BIGINT,
    mime_type VARCHAR(100),
    duration_ms INT,
    sample_rate INT,
    channels ENUM('MONO', 'STEREO') DEFAULT 'MONO',
    audio_quality ENUM('LOW', 'MEDIUM', 'HIGH') DEFAULT 'MEDIUM',
    processing_status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED') DEFAULT 'PENDING',
    waveform_data JSON,
    recorded_at TIMESTAMP,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_samples (user_id, created_at),
    INDEX idx_status (processing_status)
);

CREATE TABLE analysis_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    session_type ENUM('SINGLE', 'SERIES', 'COMPARISON') DEFAULT 'SINGLE',
    sample_count INT DEFAULT 0,
    overall_confidence DECIMAL(4,3),
    overall_voice_type VARCHAR(50),
    session_summary JSON,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_sessions (user_id, created_at)
);

CREATE TABLE voice_analyses (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    voice_profile_id BIGINT,
    audio_sample_id BIGINT,
    session_id BIGINT,
    min_f0 DECIMAL(10,2),
    max_f0 DECIMAL(10,2),
    avg_f0 DECIMAL(10,2),
    median_f0 DECIMAL(10,2),
    std_f0 DECIMAL(10,4),
    min_midi DECIMAL(6,2),
    max_midi DECIMAL(6,2),
    median_midi DECIMAL(6,2),
    voice_type VARCHAR(50),
    confidence DECIMAL(4,3),
    voiced_ratio DECIMAL(5,4),
    octave_score DECIMAL(5,4),
    f0_contour JSON,
    note_distribution JSON,
    analysis_params JSON,
    quality_warning VARCHAR(255),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (voice_profile_id) REFERENCES voice_profiles(id) ON DELETE SET NULL,
    FOREIGN KEY (audio_sample_id) REFERENCES audio_samples(id) ON DELETE SET NULL,
    FOREIGN KEY (session_id) REFERENCES analysis_sessions(id) ON DELETE SET NULL,
    INDEX idx_user_analyzed (user_id, analyzed_at),
    INDEX idx_voice_type (voice_type)
);

CREATE TABLE genres (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(100),
    color VARCHAR(7),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    song_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_code (code),
    INDEX idx_active (is_active)
);

CREATE TABLE songs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    added_by BIGINT,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    album VARCHAR(255),
    original_key VARCHAR(10),
    original_root_midi INT,
    difficulty ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT') DEFAULT 'INTERMEDIATE',
    duration_seconds INT,
    lyrics_preview TEXT,
    vocal_intensity ENUM('LIGHT', 'MEDIUM', 'STRONG') DEFAULT 'MEDIUM',
    tempo_category ENUM('SLOW', 'MODERATE', 'FAST') DEFAULT 'MODERATE',
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
    additional_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_title (title),
    INDEX idx_artist (artist),
    INDEX idx_difficulty (difficulty),
    INDEX idx_original_key (original_key),
    INDEX idx_min_midi (min_midi),
    INDEX idx_max_midi (max_midi),
    INDEX idx_active (is_active),
    INDEX idx_midi_range (min_midi, max_midi),
    
    FULLTEXT INDEX ft_songs (title, artist, lyrics_preview)
);

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
    INDEX idx_genre (genre_id),
    INDEX idx_genre_song (genre_id, song_id)
);

CREATE TABLE song_keys (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    song_id BIGINT NOT NULL,
    key_signature VARCHAR(10),
    mode ENUM('MAJOR', 'MINOR', 'MODAL') DEFAULT 'MAJOR',
    difficulty_for_key VARCHAR(50),
    is_recommended_key BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    INDEX idx_song (song_id)
);

CREATE TABLE song_ratings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    song_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_song_user (song_id, user_id),
    INDEX idx_song (song_id)
);

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
    INDEX idx_user (user_id),
    INDEX idx_user_genre (user_id, genre_id)
);

CREATE TABLE user_songs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    song_id BIGINT NOT NULL,
    status ENUM('FAVORITE', 'PLAYED', 'LEARNING', 'MASTERED') DEFAULT 'FAVORITE',
    play_count INT DEFAULT 0,
    practice_notes TEXT,
    favorited_at TIMESTAMP NULL,
    last_played_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_song (user_id, song_id),
    INDEX idx_user_status (user_id, status)
);

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
    attachments JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organizer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_start_time (start_time),
    INDEX idx_status (status),
    INDEX idx_type (event_type),
    INDEX idx_upcoming (start_time, status)
);