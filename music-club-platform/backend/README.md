# Music Club Platform - Backend API

## Mục lục
1. [Project Structure](#1-project-structure)
2. [API Endpoints](#2-api-endpoints)
3. [Database Schema](#3-database-schema)
4. [Authentication](#4-authentication)

---

## 1. Project Structure

```
backend/
├── src/main/java/com/musicclub/
│   ├── MusicClubApplication.java
│   │
│   ├── config/
│   │   ├── SecurityConfig.java
│   │   ├── JwtConfig.java
│   │   └── CorsConfig.java
│   │
│   ├── security/
│   │   ├── JwtTokenProvider.java
│   │   ├── JwtAuthenticationFilter.java
│   │   └── UserDetailsServiceImpl.java
│   │
│   ├── auth/
│   │   ├── AuthController.java
│   │   ├── AuthService.java
│   │   ├── RegisterRequest.java
│   │   ├── LoginRequest.java
│   │   └── AuthResponse.java
│   │
│   ├── user/
│   │   ├── UserController.java
│   │   ├── UserService.java
│   │   ├── User.java
│   │   └── UserRepository.java
│   │
│   ├── voice/
│   │   ├── VoiceController.java
│   │   ├── VoiceService.java
│   │   ├── VoiceAnalysis.java
│   │   ├── VoiceProfile.java
│   │   └── VoiceRepository.java
│   │
│   ├── song/
│   │   ├── SongController.java
│   │   ├── SongService.java
│   │   ├── Song.java
│   │   └── SongRepository.java
│   │
│   ├── recommendation/
│   │   ├── RecommendationController.java
│   │   ├── RecommendationService.java
│   │   └── RecommendationEngine.java
│   │
│   ├── event/
│   │   ├── EventController.java
│   │   ├── EventService.java
│   │   ├── Event.java
│   │   └── EventRepository.java
│   │
│   ├── post/
│   │   ├── PostController.java
│   │   ├── PostService.java
│   │   ├── Post.java
│   │   └── PostRepository.java
│   │
│   └── common/
│       ├── ApiResponse.java
│       ├── GlobalExceptionHandler.java
│       └── PageResponse.java
│
├── src/main/resources/
│   ├── application.yml
│   └── schema.sql
│
├── pom.xml
└── Dockerfile
```

---

## 2. API Endpoints

### 2.1 Authentication

```
POST   /api/auth/register          - Register new user
POST   /api/auth/login             - Login user
POST   /api/auth/logout            - Logout user
POST   /api/auth/refresh           - Refresh token
GET    /api/auth/me                - Get current user
```

### 2.2 User Management

```
GET    /api/users/me               - Get current user profile
PUT    /api/users/me               - Update current user
PUT    /api/users/me/password      - Change password
DELETE /api/users/me               - Delete account

# Admin endpoints
GET    /api/admin/users            - List all users
GET    /api/admin/users/{id}      - Get user by ID
PUT    /api/admin/users/{id}      - Update user
DELETE /api/admin/users/{id}      - Delete user
```

### 2.3 Voice Analysis

```
POST   /api/voice/analyze          - Analyze voice recording
GET    /api/voice/profile         - Get user's voice profile
GET    /api/voice/history         - Get analysis history
GET    /api/voice/history/{id}    - Get specific analysis
POST   /api/voice/sync            - Sync local analyses to server

# Admin endpoints
GET    /api/admin/voice-profiles  - Get all voice profiles
GET    /api/admin/voice-profiles/{userId} - Get user's voice profile
```

### 2.4 Songs

```
GET    /api/songs                  - List songs (with filters)
GET    /api/songs/{id}            - Get song by ID
POST   /api/songs                  - Create song (Admin)
PUT    /api/songs/{id}            - Update song (Admin)
DELETE /api/songs/{id}            - Delete song (Admin)
GET    /api/songs/search           - Search songs
```

### 2.5 Recommendations

```
GET    /api/recommendations        - Get personalized recommendations
GET    /api/recommendations/songs - Get song recommendations
GET    /api/recommendations/events - Get event recommendations
```

### 2.6 Events

```
GET    /api/events                 - List events
GET    /api/events/{id}           - Get event by ID
POST   /api/events                 - Create event (Admin)
PUT    /api/events/{id}           - Update event (Admin)
DELETE /api/events/{id}           - Delete event (Admin)
POST   /api/events/{id}/register   - Register for event
DELETE /api/events/{id}/register   - Cancel registration
```

### 2.7 Community/Posts

```
GET    /api/posts                 - List posts
GET    /api/posts/{id}           - Get post by ID
POST   /api/posts                 - Create post
PUT    /api/posts/{id}           - Update post
DELETE /api/posts/{id}           - Delete post
POST   /api/posts/{id}/like      - Like post
DELETE /api/posts/{id}/like      - Unlike post
POST   /api/posts/{id}/comments  - Add comment
```

---

## 3. Database Schema

### 3.1 Users Table

```sql
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
    INDEX idx_role (role)
);
```

### 3.2 Voice Profiles Table

```sql
CREATE TABLE voice_profiles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL UNIQUE,
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
    total_analyses INT DEFAULT 0,
    last_analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_voice_type (voice_type),
    INDEX idx_confidence (confidence)
);
```

### 3.3 Songs Table

```sql
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
    INDEX idx_difficulty (difficulty),
    INDEX idx_original_key (original_key),
    INDEX idx_midi_range (min_midi, max_midi),
    FULLTEXT INDEX ft_songs (title, artist, lyrics_preview)
);
```

---

## 4. Authentication

### 4.1 JWT Token Structure

```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "Bearer",
  "expiresIn": 86400,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user123",
    "fullName": "Nguyen Van A",
    "role": "MEMBER"
  }
}
```

### 4.2 Security Configuration

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {
    
    @Autowired
    private JwtAuthenticationFilter jwtAuthFilter;
    
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/health").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }
}
```

---

## 5. Voice Analysis API

### 5.1 Analyze Voice

```
POST /api/voice/analyze
Content-Type: multipart/form-data

Authorization: Bearer {token}

Parameters:
- file: Audio file (WAV, MP3, M4A)
- sessionId: (optional) Analysis session ID
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "analysisId": 123,
    "userId": 1,
    "minF0": 165.0,
    "maxF0": 587.0,
    "avgF0": 285.0,
    "medianF0": 278.5,
    "stdF0": 45.2,
    "minMidi": 48,
    "maxMidi": 65,
    "rangeSemitones": 17.0,
    "voiceType": "BARITONE",
    "confidence": 0.85,
    "voicedRatio": 0.72,
    "stabilityScore": 0.78,
    "qualityGrade": "B",
    "noteDistribution": {
      "C4": 15,
      "D4": 12,
      "E4": 20,
      "F4": 18,
      "G4": 10
    },
    "analyzedAt": "2026-09-19T15:30:00Z"
  }
}
```

### 5.2 Get Voice Profile

```
GET /api/voice/profile
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "voiceType": "BARITONE",
    "minF0": 165.0,
    "maxF0": 587.0,
    "minMidi": 48,
    "maxMidi": 65,
    "rangeSemitones": 24.0,
    "confidence": 0.85,
    "stabilityScore": 0.78,
    "qualityGrade": "B",
    "totalAnalyses": 5,
    "lastAnalyzedAt": "2026-09-19T15:30:00Z"
  }
}
```

---

## 6. Recommendation API

### 6.1 Get Song Recommendations

```
GET /api/recommendations/songs?limit=10&genre=POP
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "userVoiceType": "BARITONE",
    "userRange": {
      "minMidi": 48,
      "maxMidi": 65
    },
    "recommendations": [
      {
        "song": {
          "id": 45,
          "title": "Nơi Này Có Anh",
          "artist": "Sơn Tùng M-TP",
          "genre": "POP",
          "difficulty": "INTERMEDIATE"
        },
        "score": 0.92,
        "matchReasons": [
          "Song fits perfectly in your vocal range",
          "POP matches your favorite genre",
          "Key C is comfortable for your voice"
        ],
        "rangeCompatibility": {
          "songMinMidi": 52,
          "songMaxMidi": 64,
          "overlapPercent": 100.0,
          "comfortableSinging": true
        }
      }
    ]
  }
}
```

---

## 7. Error Handling

### 7.1 Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Email format is invalid"
      }
    ]
  },
  "timestamp": "2026-09-19T15:30:00Z"
}
```

### 7.2 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid input |
| UNAUTHORIZED | 401 | Not authenticated |
| FORBIDDEN | 403 | Not authorized |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource conflict |
| INTERNAL_ERROR | 500 | Server error |

---

**Document Version:** 1.0  
**Created:** September 19, 2026  
**Status:** Complete
