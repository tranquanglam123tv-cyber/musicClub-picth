# Song Recommendation Algorithm

## Mục lục
1. [Tổng quan](#1-tổng-quan)
2. [Recommendation Formula](#2-recommendation-formula)
3. [Range Matching](#3-range-matching)
4. [Genre Matching](#4-genre-matching)
5. [Key Compatibility](#5-key-compatibility)
6. [Difficulty Matching](#6-difficulty-matching)
7. [Implementation](#7-implementation)

---

## 1. Tổng quan

### 1.1 Recommendation Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RECOMMENDATION PIPELINE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  User Profile ──▶ Scoring ──▶ Ranking ──▶ Results                 │
│                                                                     │
│       │               │            │            │                   │
│       ▼               ▼            ▼            ▼                   │
│  Voice Type     Range Score   Sort by     Top N songs              │
│  Genre Pref     Genre Score   Final Score                          │
│  Voice Range    Key Score                                          │
│                  Diff Score                                        │
│                                                                     │
│  FinalScore = (Range × 0.6) + (Genre × 0.25) + (Key × 0.10)      │
│                      + (Difficulty × 0.05)                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Scoring Weights

| Weight | Factor | Description |
|--------|--------|-------------|
| **0.60** | Range Match | How well song fits vocal range |
| **0.25** | Genre Preference | Match with user's genre preferences |
| **0.10** | Key Compatibility | Song key suitability |
| **0.05** | Difficulty | Song difficulty vs skill level |

---

## 2. Recommendation Formula

### 2.1 Final Score Calculation

```python
def calculate_recommendation_score(
    user_profile: dict,
    song: dict,
    weights: dict = None
) -> dict:
    """
    Calculate final recommendation score for a song.
    
    Args:
        user_profile: {
            'voice_type': 'TENOR',
            'min_midi': 48,
            'max_midi': 72,
            'genre_preferences': {'POP': 5, 'ROCK': 4, 'BALLAD': 3},
            'confidence': 0.85
        }
        song: {
            'id': 1,
            'title': 'Song Title',
            'genre': 'POP',
            'original_key': 'C',
            'difficulty': 'INTERMEDIATE',
            'min_midi': 52,
            'max_midi': 64
        }
        weights: Optional custom weights
    
    Returns:
        dict with score breakdown and reasons
    """
    
    # Default weights
    if weights is None:
        weights = {
            'range': 0.60,
            'genre': 0.25,
            'key': 0.10,
            'difficulty': 0.05
        }
    
    # Calculate individual scores
    range_score = calculate_range_score(
        user_profile['min_midi'],
        user_profile['max_midi'],
        song['min_midi'],
        song['max_midi']
    )
    
    genre_score = calculate_genre_score(
        user_profile.get('genre_preferences', {}),
        song['genre']
    )
    
    key_score = calculate_key_score(
        user_profile['voice_type'],
        song['original_key']
    )
    
    difficulty_score = calculate_difficulty_score(
        user_profile.get('confidence', 0.5),
        song['difficulty']
    )
    
    # Calculate final score
    final_score = (
        range_score * weights['range'] +
        genre_score * weights['genre'] +
        key_score * weights['key'] +
        difficulty_score * weights['difficulty']
    )
    
    # Generate match reasons
    reasons = generate_match_reasons(
        range_score, genre_score, key_score, difficulty_score,
        user_profile, song
    )
    
    return {
        'song_id': song['id'],
        'score': round(final_score, 3),
        'breakdown': {
            'range_score': round(range_score, 3),
            'genre_score': round(genre_score, 3),
            'key_score': round(key_score, 3),
            'difficulty_score': round(difficulty_score, 3)
        },
        'weights': weights,
        'reasons': reasons
    }
```

---

## 3. Range Matching

### 3.1 Range Score Algorithm

```python
def calculate_range_score(
    user_min_midi: int,
    user_max_midi: int,
    song_min_midi: int,
    song_max_midi: int
) -> float:
    """
    Calculate how well a song fits within user's vocal range.
    
    Perfect match: User can sing entire song without strain
    """
    
    # Find overlap between user range and song range
    overlap_min = max(user_min_midi, song_min_midi)
    overlap_max = min(user_max_midi, song_max_midi)
    
    if overlap_min > overlap_max:
        # No overlap - song is outside user's range
        return 0.0
    
    # Calculate overlap in semitones
    overlap_semitones = overlap_max - overlap_min
    song_range_semitones = song_max_midi - song_min_midi
    
    if song_range_semitones == 0:
        return 0.0
    
    # Base score = percentage of song user can sing
    overlap_percent = overlap_semitones / song_range_semitones
    
    # Bonus for songs within user's "sweet spot"
    # Sweet spot = 3 semitones above min and below max
    user_sweet_min = user_min_midi + 3
    user_sweet_max = user_max_midi - 3
    
    in_sweet_spot = (
        song_min_midi >= user_sweet_min and
        song_max_midi <= user_sweet_max
    )
    
    if in_sweet_spot:
        overlap_percent = min(1.0, overlap_percent * 1.1)  # 10% bonus
    
    # Penalty for songs extending outside range
    user_range = user_max_midi - user_min_midi
    song_extends_below = max(0, song_min_midi - user_min_midi)
    song_extends_above = max(0, user_max_midi - song_max_midi)
    
    extension_penalty = (
        song_extends_below + song_extends_above
    ) / user_range if user_range > 0 else 0
    
    final_score = overlap_percent * (1 - extension_penalty * 0.3)
    
    return round(max(0, min(1, final_score)), 3)
```

### 3.2 Range Score Examples

| User Range | Song Range | Overlap | Score | Reason |
|------------|------------|---------|-------|--------|
| C3-G4 (48-67) | D3-F4 (50-65) | 15 semitones | 0.95 | 100% in sweet spot |
| C3-G4 (48-67) | A2-C4 (45-60) | 15 semitones | 0.75 | 75% overlap, some strain |
| C3-G4 (48-67) | G3-C5 (55-72) | 12 semitones | 0.65 | Above sweet spot |
| C3-G4 (48-67) | F2-D4 (41-62) | 21 semitones | 0.70 | Below sweet spot |
| C3-G4 (48-67) | C4-G5 (60-79) | 7 semitones | 0.35 | No overlap with sweet spot |

### 3.3 Visual Range Comparison

```
User Range: C3 - G4 (48-67)
                    │Sweet Spot│
         │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
         
Song 1:   D3 - F4 (50-65)  ✓ PERFECT MATCH
         │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
         
Song 2:   A2 - C4 (45-60)  ⚠ PARTIAL MATCH
              │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│
         
Song 3:   G3 - C5 (55-72)  ⚠ HIGH NOTES STRAIN
                        │▓▓▓▓▓▓▓▓▓▓▓│
```

---

## 4. Genre Matching

### 4.1 Genre Score Algorithm

```python
def calculate_genre_score(
    user_genre_preferences: dict[str, int],
    song_genre: str
) -> float:
    """
    Calculate genre match score based on user's preferences.
    
    Args:
        user_genre_preferences: {genre_name: preference_level (1-5)}
        song_genre: Genre of the song
    
    Returns:
        Score from 0 to 1
    """
    
    if not user_genre_preferences:
        # No preferences - neutral score
        return 0.5
    
    if song_genre not in user_genre_preferences:
        # Song genre not in user's preferences
        return 0.2
    
    # Get user's preference level (1-5)
    preference = user_genre_preferences[song_genre]
    
    # Normalize to 0-1 scale
    # 5 = favorite = 1.0
    # 1 = least favorite = 0.2
    normalized_score = 0.2 + (preference - 1) * 0.2
    
    return round(normalized_score, 3)
```

### 4.2 Genre Preference Example

```python
# User's genre preferences (1-5 scale)
user_preferences = {
    'POP': 5,        # Favorite
    'BALLAD': 5,     # Favorite
    'ROCK': 4,       # Like
    'R&B': 3,        # Neutral
    'JAZZ': 2,       # Dislike
    'CLASSICAL': 1   # Least favorite
}

# Calculate scores
calculate_genre_score(user_preferences, 'POP')      # 1.0
calculate_genre_score(user_preferences, 'ROCK')     # 0.8
calculate_genre_score(user_preferences, 'R&B')      # 0.6
calculate_genre_score(user_preferences, 'JAZZ')     # 0.4
calculate_genre_score(user_preferences, 'CLASSICAL') # 0.2
calculate_genre_score(user_preferences, 'FOLK')     # 0.2 (not in preferences)
```

### 4.3 Genre Categories

| Category | Genres |
|----------|--------|
| **Pop** | POP, BALLAD |
| **Rock** | ROCK, METAL, PUNK |
| **R&B/Hip-Hop** | R&B_SOUL, HIPHOP |
| **Jazz/Blues** | JAZZ, BLUES |
| **Classical** | CLASSICAL, MUSICAL |
| **Traditional** | VIETNAMESE, FOLK, COUNTRY |

---

## 5. Key Compatibility

### 5.1 Key Compatibility Wheel

```
                    C
                 G     F
              D           Bb
           A               Eb
        E                   Ab
    B                       Db
   F#                         C#
```

### 5.2 Key Score Algorithm

```python
# Key compatibility matrix
KEY_COMPATIBILITY = {
    # Major keys compatible with each other (circle of fifths)
    'C': ['G', 'F', 'Am', 'Dm', 'Em'],
    'G': ['D', 'C', 'Em', 'Bm', 'Am'],
    'D': ['A', 'G', 'Bm', 'F#m', 'Em'],
    'A': ['E', 'D', 'F#m', 'C#m', 'Bm'],
    'E': ['B', 'A', 'C#m', 'G#m', 'F#m'],
    'B': ['F#', 'E', 'G#m', 'D#m', 'C#m'],
    'F': ['Bb', 'C', 'Dm', 'Am', 'Gm'],
    'Bb': ['F', 'Eb', 'Gm', 'Cm', 'Dm'],
    'Eb': ['Ab', 'Bb', 'Cm', 'Fm', 'Gm'],
    'Ab': ['Eb', 'Db', 'Fm', 'Bbm', 'Cm'],
    'Db': ['Ab', 'Gb', 'Bbm', 'Ebm', 'Fm'],
    'Gb': ['Db', 'Cb', 'Ebm', 'Bbm', 'Abm'],
}

# Voice type key preferences
VOICE_TYPE_KEYS = {
    'BASS': {
        'excellent': ['C', 'D', 'E', 'F'],
        'good': ['G', 'A', 'Bb'],
        'neutral': ['B', 'Db', 'Eb', 'Ab']
    },
    'BARITONE': {
        'excellent': ['D', 'E', 'F', 'G'],
        'good': ['C', 'A', 'Bb'],
        'neutral': ['B', 'Db', 'Eb', 'Ab']
    },
    'TENOR': {
        'excellent': ['F', 'G', 'A', 'Bb'],
        'good': ['D', 'E', 'C'],
        'neutral': ['B', 'Db', 'Eb', 'Ab']
    },
    'ALTO': {
        'excellent': ['G', 'A', 'Bb', 'C'],
        'good': ['F', 'D', 'Eb'],
        'neutral': ['B', 'E', 'Ab']
    },
    'MEZZO_SOPRANO': {
        'excellent': ['A', 'Bb', 'C', 'D'],
        'good': ['G', 'F', 'Eb'],
        'neutral': ['B', 'E', 'Ab']
    },
    'SOPRANO': {
        'excellent': ['C', 'D', 'E', 'F#'],
        'good': ['G', 'A', 'B'],
        'neutral': ['F', 'Eb', 'Ab']
    }
}


def calculate_key_score(voice_type: str, song_key: str) -> float:
    """
    Calculate key compatibility score.
    
    Args:
        voice_type: User's voice type
        song_key: Song's original key
    
    Returns:
        Score from 0 to 1
    """
    
    if not song_key:
        return 0.5  # No key info - neutral
    
    # Extract root note from key (e.g., "C", "Am", "F#m")
    # Remove minor suffix
    root_note = song_key.replace('m', '').replace('#', 'sharp')
    
    # Handle sharp/flat
    if root_note in ['Db', 'C#']:
        root_note = 'C#'
    elif root_note in ['Eb', 'D#']:
        root_note = 'Eb'
    elif root_note in ['Gb', 'F#']:
        root_note = 'Gb'
    elif root_note in ['Ab', 'G#']:
        root_note = 'Ab'
    elif root_note in ['Bb', 'A#']:
        root_note = 'Bb'
    
    # Get voice type preferences
    key_prefs = VOICE_TYPE_KEYS.get(voice_type, {})
    
    if root_note in key_prefs.get('excellent', []):
        return 1.0
    elif root_note in key_prefs.get('good', []):
        return 0.8
    elif root_note in key_prefs.get('neutral', []):
        return 0.5
    else:
        # Check circle of fifths compatibility
        for excellent_key in key_prefs.get('excellent', []):
            if root_note in KEY_COMPATIBILITY.get(excellent_key, []):
                return 0.7
        
        return 0.3  # Transposition may be needed
```

### 5.3 Key Scores by Voice Type

| Song Key | Bass | Baritone | Tenor | Alto | Mezzo | Soprano |
|----------|------|----------|-------|------|-------|---------|
| C | 1.0 | 0.8 | 0.8 | 0.8 | 0.8 | 1.0 |
| D | 1.0 | 1.0 | 0.8 | 0.8 | 1.0 | 0.8 |
| E | 1.0 | 1.0 | 0.8 | 0.5 | 0.8 | 1.0 |
| F | 1.0 | 1.0 | 1.0 | 0.8 | 0.8 | 0.5 |
| G | 0.8 | 1.0 | 1.0 | 1.0 | 0.8 | 0.8 |
| A | 0.8 | 1.0 | 1.0 | 1.0 | 1.0 | 0.8 |
| Bb | 0.8 | 0.8 | 1.0 | 1.0 | 1.0 | 0.8 |

---

## 6. Difficulty Matching

### 6.1 Difficulty Score Algorithm

```python
DIFFICULTY_MAP = {
    'BEGINNER': 1,
    'INTERMEDIATE': 2,
    'ADVANCED': 3,
    'EXPERT': 4
}


def calculate_difficulty_score(user_confidence: float, song_difficulty: str) -> float:
    """
    Calculate difficulty match score.
    
    Ideal: User's skill level ≈ Song difficulty
    
    Args:
        user_confidence: User's voice analysis confidence (0-1)
        song_difficulty: Song's difficulty level
    
    Returns:
        Score from 0 to 1
    """
    
    # Estimate user's skill level from confidence
    # Confidence 0-0.3 = Beginner
    # Confidence 0.3-0.5 = Intermediate
    # Confidence 0.5-0.7 = Advanced
    # Confidence 0.7-1.0 = Expert
    
    if user_confidence < 0.3:
        user_level = 1  # Beginner
    elif user_confidence < 0.5:
        user_level = 2  # Intermediate
    elif user_confidence < 0.7:
        user_level = 3  # Advanced
    else:
        user_level = 4  # Expert
    
    # Get song difficulty level
    song_level = DIFFICULTY_MAP.get(song_difficulty, 2)
    
    # Calculate difference
    level_diff = abs(user_level - song_level)
    
    # Score mapping
    # Same level = 1.0
    # 1 level off = 0.7
    # 2 levels off = 0.4
    # 3 levels off = 0.1
    
    difficulty_scores = {0: 1.0, 1: 0.7, 2: 0.4, 3: 0.1}
    
    return difficulty_scores.get(level_diff, 0.1)
```

### 6.2 Difficulty Recommendations

| User Level | Recommended Songs | Avoid |
|------------|-------------------|-------|
| **Beginner** | BEGINNER, INTERMEDIATE | ADVANCED, EXPERT |
| **Intermediate** | BEGINNER, INTERMEDIATE, ADVANCED | EXPERT |
| **Advanced** | INTERMEDIATE, ADVANCED | BEGINNER |
| **Expert** | ADVANCED, EXPERT | BEGINNER |

---

## 7. Implementation

### 7.1 Complete Recommendation Service

```python
class RecommendationService:
    """Song recommendation service."""
    
    def __init__(self, weights: dict = None):
        self.weights = weights or {
            'range': 0.60,
            'genre': 0.25,
            'key': 0.10,
            'difficulty': 0.05
        }
    
    def get_recommendations(
        self,
        user_profile: dict,
        songs: list[dict],
        limit: int = 10
    ) -> list[dict]:
        """
        Get song recommendations for a user.
        
        Args:
            user_profile: User's voice profile
            songs: List of candidate songs
            limit: Maximum number of recommendations
        
        Returns:
            List of recommended songs with scores
        """
        
        # Calculate score for each song
        scored_songs = []
        
        for song in songs:
            score_result = calculate_recommendation_score(
                user_profile,
                song,
                self.weights
            )
            
            scored_songs.append({
                'song': song,
                **score_result
            })
        
        # Sort by score descending
        scored_songs.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top N
        return scored_songs[:limit]
    
    def get_recommendations_with_filters(
        self,
        user_profile: dict,
        songs: list[dict],
        filters: dict = None,
        limit: int = 10
    ) -> list[dict]:
        """
        Get recommendations with additional filters.
        
        Args:
            filters: {
                'genre': ['POP', 'ROCK'],
                'difficulty': ['BEGINNER', 'INTERMEDIATE'],
                'min_score': 0.5
            }
        """
        
        # Apply filters
        filtered_songs = songs
        
        if filters:
            if 'genre' in filters:
                filtered_songs = [
                    s for s in filtered_songs
                    if s.get('genre') in filters['genre']
                ]
            
            if 'difficulty' in filters:
                filtered_songs = [
                    s for s in filtered_songs
                    if s.get('difficulty') in filters['difficulty']
                ]
        
        # Get recommendations
        recommendations = self.get_recommendations(
            user_profile,
            filtered_songs,
            limit
        )
        
        # Filter by minimum score
        if filters and 'min_score' in filters:
            recommendations = [
                r for r in recommendations
                if r['score'] >= filters['min_score']
            ]
        
        return recommendations


def generate_match_reasons(
    range_score: float,
    genre_score: float,
    key_score: float,
    difficulty_score: float,
    user_profile: dict,
    song: dict
) -> list[str]:
    """Generate human-readable match reasons."""
    
    reasons = []
    
    # Range reason
    if range_score >= 0.8:
        reasons.append("Song fits perfectly in your vocal range")
    elif range_score >= 0.5:
        reasons.append("Song partially fits your vocal range")
    else:
        reasons.append("Song may require some notes outside your range")
    
    # Genre reason
    if genre_score >= 0.8:
        genre = song.get('genre', '')
        reasons.append(f"{genre} matches your favorite genre")
    elif genre_score >= 0.5:
        reasons.append("Genre is among your preferences")
    elif genre_score > 0:
        reasons.append("Genre may not be your favorite")
    
    # Key reason
    if key_score >= 0.8:
        reasons.append(f"Key {song.get('original_key', '')} is comfortable for your voice")
    elif key_score >= 0.5:
        reasons.append(f"Key {song.get('original_key', '')} is suitable")
    else:
        reasons.append("May need to transpose key for best comfort")
    
    # Difficulty reason
    if difficulty_score >= 0.8:
        reasons.append("Difficulty level matches your skill")
    elif difficulty_score >= 0.5:
        reasons.append("Difficulty level is appropriate")
    else:
        reasons.append("Song difficulty may not match your level")
    
    return reasons
```

### 7.2 Example Output

```python
# Example recommendation
recommendation = {
    'song_id': 45,
    'score': 0.92,
    'breakdown': {
        'range_score': 0.95,
        'genre_score': 1.00,
        'key_score': 1.00,
        'difficulty_score': 0.70
    },
    'weights': {
        'range': 0.60,
        'genre': 0.25,
        'key': 0.10,
        'difficulty': 0.05
    },
    'reasons': [
        'Song fits perfectly in your vocal range',
        'POP matches your favorite genre',
        'Key C is comfortable for your voice',
        'Difficulty level matches your skill'
    ],
    'song': {
        'id': 45,
        'title': 'Nơi Này Có Anh',
        'artist': 'Sơn Tùng M-TP',
        'genre': 'POP',
        'original_key': 'C',
        'difficulty': 'INTERMEDIATE',
        'min_midi': 52,
        'max_midi': 64
    }
}
```

---

## 8. Performance Optimization

### 8.1 Caching Strategy

```python
class CachedRecommendationService(RecommendationService):
    """Recommendation service with caching."""
    
    def __init__(self, cache_ttl: int = 3600):
        super().__init__()
        self.cache = {}
        self.cache_ttl = cache_ttl  # seconds
    
    def _get_cache_key(self, user_id: int, filters: dict = None) -> str:
        """Generate cache key."""
        filter_str = json.dumps(filters or {}, sort_keys=True)
        return f"recommendations:{user_id}:{filter_str}"
    
    def get_recommendations(self, user_profile, songs, limit=10):
        """Get recommendations with caching."""
        
        cache_key = self._get_cache_key(user_profile['user_id'])
        
        if cache_key in self.cache:
            cached_time, cached_result = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_result
        
        # Calculate recommendations
        result = super().get_recommendations(user_profile, songs, limit)
        
        # Cache result
        self.cache[cache_key] = (time.time(), result)
        
        return result
```

### 8.2 Batch Processing

```python
async def get_batch_recommendations(
    user_ids: list[int],
    song_candidates: list[dict],
    limit_per_user: int = 10
) -> dict[int, list[dict]]:
    """
    Get recommendations for multiple users.
    
    Uses parallel processing for efficiency.
    """
    
    async def get_user_recommendations(user_id: int) -> tuple[int, list]:
        user_profile = await get_user_profile(user_id)
        recommendations = service.get_recommendations(
            user_profile,
            song_candidates,
            limit_per_user
        )
        return user_id, recommendations
    
    # Run in parallel
    tasks = [get_user_recommendations(uid) for uid in user_ids]
    results = await asyncio.gather(*tasks)
    
    return dict(results)
```

---

**Document Version:** 1.0  
**Created:** September 19, 2026  
**Status:** Complete
