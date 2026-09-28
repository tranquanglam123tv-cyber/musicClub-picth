-- =====================================================================
-- Music Club Platform - Seed Data
-- =====================================================================
-- Initial data for voice types, genres, system settings
-- =====================================================================

USE music_club_db;

-- =====================================================================
-- 1. Voice Types (6 loại giọng chuẩn)
-- =====================================================================
INSERT INTO voice_types (code, name_vi, name_en, min_midi, max_midi, typical_min_hz, typical_max_hz, description, sort_order) VALUES
('SOPRANO',       'Nữ cao',              'Soprano',         55, 84, 247.50,  932.33, 'Giọng nữ cao nhất, sáng và trong trẻo',  1),
('MEZZO_SOPRANO', 'Nữ trung cao',        'Mezzo-Soprano',   57, 81, 220.00,  880.00, 'Giọng nữ trung cao, ấm áp',              2),
('ALTO',          'Nữ trung',            'Alto/Contralto',  53, 77, 174.61,  698.46, 'Giọng nữ trầm nhất, dày và ấm',         3),
('TENOR',         'Nam cao',             'Tenor',           48, 72, 130.81,  523.25, 'Giọng nam cao, sáng và mạnh',            4),
('BARITONE',      'Nam trung cao',       'Baritone',        45, 69, 110.00,  440.00, 'Giọng nam trung, dày dặn',                5),
('BASS',          'Nam trầm',            'Bass',            40, 64, 82.41,   329.63, 'Giọng nam trầm nhất, nặng và sâu',       6);

-- =====================================================================
-- 2. Genres (Thể loại nhạc phổ biến)
-- =====================================================================
INSERT INTO genres (code, name, description, color_hex, icon) VALUES
('POP',        'Pop',        'Nhạc pop đương đại, catchy, dễ nghe',          '#FF6B9D', 'music_note'),
('BALLAD',     'Ballad',     'Nhạc ballad chậm, sâu lắng, tình cảm',         '#9C27B0', 'favorite'),
('ROCK',       'Rock',       'Nhạc rock mạnh mẽ, nhiều năng lượng',         '#F44336', 'electric_bolt'),
('JAZZ',       'Jazz',       'Nhạc jazz cổ điển, phức tạp, tinh tế',         '#FF9800', 'piano'),
('RNB',        'R&B/Soul',   'Nhạc R&B, soul, groove mượt mà',               '#E91E63', 'album'),
('ACOUSTIC',   'Acoustic',   'Nhạc acoustic nhẹ nhàng, mộc mạc',            '#4CAF50', 'eco'),
('INDIE',      'Indie',      'Nhạc indie độc lập, sáng tạo',                '#00BCD4', 'explore'),
('CLASSICAL',  'Cổ điển',    'Nhạc cổ điển, thanh nhạc chuyên nghiệp',      '#795548', 'library_music'),
('FOLK',       'Folk',       'Nhạc dân ca, folk truyền thống',                '#8BC34A', 'park'),
('ELECTRONIC', 'Electronic', 'Nhạc điện tử, EDM, synth',                     '#673AB7', 'graphic_eq'),
('HIPHOP',     'Hip-hop',    'Nhạc hip-hop, rap',                            '#3F51B5', 'mic'),
('COUNTRY',    'Country',    'Nhạc đồng quê Mỹ',                             '#FFC107', 'terrain');

-- =====================================================================
-- 3. System Settings
-- =====================================================================
INSERT INTO system_settings (setting_key, setting_value, setting_type, description, is_public) VALUES
('app_name',              'Music Club Platform',    'STRING',  'Tên hệ thống',          TRUE),
('app_version',           '1.0.0',                 'STRING',  'Phiên bản hiện tại',    TRUE),
('maintenance_mode',      'false',                 'BOOLEAN', 'Chế độ bảo trì',        FALSE),
('min_recording_duration','10',                    'INTEGER', 'Thời lượng thu âm tối thiểu (giây)', FALSE),
('max_recording_duration','60',                    'INTEGER', 'Thời lượng thu âm tối đa (giây)', FALSE),
('min_confidence',        '0.40',                  'STRING',  'Confidence tối thiểu để chấp nhận', FALSE),
('recommendation_count',  '10',                    'INTEGER', 'Số bài gợi ý mỗi lần', FALSE),
('jwt_secret',            'CHANGE_ME_IN_PRODUCTION', 'STRING', 'JWT secret key',        FALSE),
('jwt_expiry_hours',      '24',                    'INTEGER', 'JWT expiry time (hours)', FALSE),
('dsp_service_url',       'http://localhost:8000', 'STRING',  'URL DSP Python service', FALSE),
('enable_voice_sync',     'true',                  'BOOLEAN', 'Cho phép sync voice data', FALSE),
('min_voiced_ratio',      '0.30',                  'STRING',  'Voiced ratio tối thiểu', FALSE),
('min_range_semitones',   '6',                     'INTEGER', 'Range tối thiểu (semitones)', FALSE);

-- =====================================================================
-- 4. Admin User mặc định (password: admin123 - hash BCrypt)
-- =====================================================================
-- BCrypt hash của "admin123" với cost=10
INSERT INTO users (username, email, password_hash, full_name, role, is_active, is_verified) VALUES
('admin', 'admin@musicclub.com', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Administrator', 'ADMIN', TRUE, TRUE);

-- =====================================================================
-- 5. Sample Voice Ranges (ví dụ quãng giọng chuẩn)
-- =====================================================================
-- Cho mỗi voice type, insert vài note đặc trưng
INSERT INTO voice_ranges (voice_type_id, note_name, midi_note, frequency, is_typical_low, is_typical_high)
SELECT id, 'C4', 60, 261.63, FALSE, FALSE FROM voice_types WHERE code IN ('SOPRANO','MEZZO_SOPRANO','ALTO')
UNION ALL
SELECT id, 'A3', 57, 220.00, TRUE,  FALSE FROM voice_types WHERE code IN ('SOPRANO','MEZZO_SOPRANO')
UNION ALL
SELECT id, 'F3', 53, 174.61, TRUE,  FALSE FROM voice_types WHERE code = 'ALTO'
UNION ALL
SELECT id, 'C3', 48, 130.81, FALSE, FALSE FROM voice_types WHERE code IN ('TENOR','BARITONE')
UNION ALL
SELECT id, 'G3', 55, 196.00, FALSE, FALSE FROM voice_types WHERE code = 'TENOR'
UNION ALL
SELECT id, 'A2', 45, 110.00, TRUE,  FALSE FROM voice_types WHERE code = 'BARITONE'
UNION ALL
SELECT id, 'E2', 40, 82.41,  TRUE,  FALSE FROM voice_types WHERE code = 'BASS'
UNION ALL
SELECT id, 'C4', 60, 261.63, FALSE, FALSE FROM voice_types WHERE code IN ('BARITONE','BASS');

-- =====================================================================
-- 6. Sample Songs (một vài bài để test)
-- =====================================================================
INSERT INTO songs (title, artist, original_key, min_midi, max_midi, difficulty, duration_seconds, bpm, lyrics, chords, created_by) VALUES
('Nơi này có anh',           'Sơn Tùng M-TP',       'C',  55, 72, 'INTERMEDIATE', 240, 95,
 'Lời bài hát Nơi này có anh...\n[Verse]\nC G Am F\n...',
 '[Verse]\nC - G - Am - F\n[Chorus]\nF - G - C - Am\n', 1),
('Hơn cả yêu',               'Đức Phúc',             'Am', 53, 69, 'BEGINNER',     280, 80,
 'Lời bài hát...\n[Verse]\nAm F C G\n...',
 '[Verse]\nAm - F - C - G\n[Chorus]\nF - G - Am - Em\n', 1),
('Chạm đáy nỗi đau',         'Erik',                 'Em', 55, 72, 'ADVANCED',     310, 72,
 'Lời bài...\n[Verse]\nEm C G D\n...',
 '[Verse]\nEm - C - G - D\n', 1),
('Đừng làm trái tim anh đau', 'Sơn Tùng M-TP',       'G',  57, 74, 'INTERMEDIATE', 220, 90,
 'Lời...\n[Verse]\nG D Em C\n...',
 '[Verse]\nG - D - Em - C\n', 1),
('Lạc',                       'Trúc Nhân',            'Am', 53, 69, 'BEGINNER',     200, 88,
 'Lời...\n[Verse]\nAm F C G\n...',
 '[Verse]\nAm - F - C - G\n', 1);

-- Gán thể loại cho các bài
INSERT INTO song_genres (song_id, genre_id)
SELECT s.id, g.id FROM songs s, genres g WHERE g.code IN ('POP','BALLAD') AND s.title = 'Nơi này có anh';
INSERT INTO song_genres (song_id, genre_id)
SELECT s.id, g.id FROM songs s, genres g WHERE g.code IN ('BALLAD','POP') AND s.title = 'Hơn cả yêu';
INSERT INTO song_genres (song_id, genre_id)
SELECT s.id, g.id FROM songs s, genres g WHERE g.code IN ('BALLAD') AND s.title = 'Chạm đáy nỗi đau';
INSERT INTO song_genres (song_id, genre_id)
SELECT s.id, g.id FROM songs s, genres g WHERE g.code IN ('POP','BALLAD') AND s.title = 'Đừng làm trái tim anh đau';
INSERT INTO song_genres (song_id, genre_id)
SELECT s.id, g.id FROM songs s, genres g WHERE g.code IN ('POP','INDIE') AND s.title = 'Lạc';

-- =====================================================================
-- END OF SEED DATA
-- =====================================================================
