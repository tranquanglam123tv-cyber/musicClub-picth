# Music Club Platform - Flutter Mobile App

## Mục lục
1. [Project Structure](#1-project-structure)
2. [Features](#2-features)
3. [Screens](#3-screens)
4. [Services](#4-services)
5. [Models](#5-models)

---

## 1. Project Structure

```
music_club_app/
├── lib/
│   ├── main.dart
│   │
│   ├── app/
│   │   ├── app.dart                    # App widget
│   │   ├── routes.dart               # Route configuration
│   │   └── theme.dart                # Theme configuration
│   │
│   ├── core/
│   │   ├── constants/
│   │   │   ├── api_constants.dart
│   │   │   ├── app_constants.dart
│   │   │   └── audio_constants.dart
│   │   │
│   │   ├── utils/
│   │   │   ├── validators.dart
│   │   │   └── helpers.dart
│   │   │
│   │   └── errors/
│   │       └── exceptions.dart
│   │
│   ├── data/
│   │   ├── repositories/
│   │   │   ├── auth_repository.dart
│   │   │   ├── user_repository.dart
│   │   │   ├── voice_repository.dart
│   │   │   ├── song_repository.dart
│   │   │   ├── event_repository.dart
│   │   │   └── post_repository.dart
│   │   │
│   │   ├── services/
│   │   │   ├── api_service.dart
│   │   │   ├── auth_service.dart
│   │   │   ├── audio_service.dart
│   │   │   └── storage_service.dart
│   │   │
│   │   └── models/
│   │       ├── user_model.dart
│   │       ├── voice_profile_model.dart
│   │       ├── song_model.dart
│   │       ├── event_model.dart
│   │       └── post_model.dart
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── screens/
│   │   │   │   ├── login_screen.dart
│   │   │   │   ├── register_screen.dart
│   │   │   │   └── splash_screen.dart
│   │   │   │
│   │   │   └── widgets/
│   │   │       └── auth_form.dart
│   │   │
│   │   ├── home/
│   │   │   ├── screens/
│   │   │   │   └── home_screen.dart
│   │   │   │
│   │   │   └── widgets/
│   │   │       ├── quick_actions.dart
│   │   │       ├── upcoming_events.dart
│   │   │       └── recommended_songs.dart
│   │   │
│   │   ├── voice/
│   │   │   ├── screens/
│   │   │   │   ├── recording_screen.dart
│   │   │   │   ├── analysis_result_screen.dart
│   │   │   │   └── voice_profile_screen.dart
│   │   │   │
│   │   │   └── widgets/
│   │   │       ├── pitch_visualizer.dart
│   │   │       ├── voice_range_chart.dart
│   │   │       └── recording_button.dart
│   │   │
│   │   ├── songs/
│   │   │   ├── screens/
│   │   │   │   ├── song_list_screen.dart
│   │   │   │   ├── song_detail_screen.dart
│   │   │   │   └── recommendations_screen.dart
│   │   │   │
│   │   │   └── widgets/
│   │   │       ├── song_card.dart
│   │   │       └── song_filter.dart
│   │   │
│   │   ├── events/
│   │   │   ├── screens/
│   │   │   │   ├── event_list_screen.dart
│   │   │   │   ├── event_detail_screen.dart
│   │   │   │   └── registration_screen.dart
│   │   │   │
│   │   │   └── widgets/
│   │   │       └── event_card.dart
│   │   │
│   │   ├── community/
│   │   │   ├── screens/
│   │   │   │   ├── post_list_screen.dart
│   │   │   │   ├── post_detail_screen.dart
│   │   │   │   └── create_post_screen.dart
│   │   │   │
│   │   │   └── widgets/
│   │   │       ├── post_card.dart
│   │   │       └── comment_section.dart
│   │   │
│   │   └── profile/
│   │       ├── screens/
│   │       │   ├── profile_screen.dart
│   │       │   ├── settings_screen.dart
│   │       │   └── history_screen.dart
│   │       │
│   │       └── widgets/
│   │           └── profile_header.dart
│   │
│   └── widgets/
│       ├── loading_indicator.dart
│       ├── error_widget.dart
│       └── empty_state.dart
│
├── pubspec.yaml
└── README.md
```

---

## 2. Features

### 2.1 Core Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Authentication** | Login, Register, Logout | HIGH |
| **Voice Recording** | Record audio for analysis | HIGH |
| **Voice Analysis** | Display F0 results, voice type | HIGH |
| **Song List** | Browse songs with filters | MEDIUM |
| **Recommendations** | Personalized song recommendations | MEDIUM |
| **Events** | View and register for events | MEDIUM |
| **Community** | Posts, comments, likes | LOW |
| **Profile** | View/edit profile, history | MEDIUM |

### 2.2 Audio Recording Requirements

```dart
class AudioRecorderConfig {
  static const int sampleRate = 44100;      // Hz
  static const int bitDepth = 16;            // bits
  static const int channels = 1;             // Mono
  static const String codec = 'pcm16bit';    // WAV format
  
  // Duration limits
  static const int minDurationSeconds = 10;
  static const int maxDurationSeconds = 60;
  
  // File size limit
  static const int maxFileSizeMB = 10;
}
```

---

## 3. Screens

### 3.1 Home Screen

```dart
// lib/features/home/screens/home_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Music Club'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () => Navigator.pushNamed(context, '/notifications'),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          // Refresh data
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome section
              _buildWelcomeSection(context),
              const SizedBox(height: 24),
              
              // Quick actions
              _buildQuickActions(context),
              const SizedBox(height: 24),
              
              // Voice profile summary
              _buildVoiceProfileCard(context),
              const SizedBox(height: 24),
              
              // Recommended songs
              _buildRecommendedSongs(context),
              const SizedBox(height: 24),
              
              // Upcoming events
              _buildUpcomingEvents(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeSection(BuildContext context) {
    final user = context.read<UserRepository>().currentUser;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Chào mừng, ${user?.fullName ?? "bạn"}!',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        const SizedBox(height: 4),
        Text(
          'Hãy khám phá bài hát phù hợp với giọng hát của bạn',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _QuickActionCard(
            icon: Icons.mic,
            title: 'Phân tích giọng',
            subtitle: 'Đo quãng giọng',
            color: Colors.blue,
            onTap: () => Navigator.pushNamed(context, '/voice/record'),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _QuickActionCard(
            icon: Icons.music_note,
            title: 'Gợi ý bài hát',
            subtitle: 'Dựa trên giọng hát',
            color: Colors.green,
            onTap: () => Navigator.pushNamed(context, '/recommendations'),
          ),
        ),
      ],
    );
  }

  Widget _buildVoiceProfileCard(BuildContext context) {
    return Consumer<VoiceRepository>(
      builder: (context, voiceRepo, _) {
        final profile = voiceRepo.currentProfile;
        
        if (profile == null) {
          return Card(
            child: ListTile(
              leading: const Icon(Icons.mic_off, size: 40),
              title: const Text('Chưa có hồ sơ giọng hát'),
              subtitle: const Text('Hãy phân tích giọng hát của bạn'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () => Navigator.pushNamed(context, '/voice/record'),
            ),
          );
        }
        
        return Card(
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.blue,
              child: Text(
                profile.voiceType?.substring(0, 1) ?? '?',
                style: const TextStyle(color: Colors.white),
              ),
            ),
            title: Text(profile.voiceType ?? 'Unknown'),
            subtitle: Text(
              '${profile.minMidiName ?? "?"} - ${profile.maxMidiName ?? "?"}',
            ),
            trailing: Text(
              '${profile.confidence ?? 0}%',
              style: TextStyle(
                color: Colors.green[700],
                fontWeight: FontWeight.bold,
              ),
            ),
            onTap: () => Navigator.pushNamed(context, '/voice/profile'),
          ),
        );
      },
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, color: color, size: 32),
              const SizedBox(height: 12),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### 3.2 Voice Recording Screen

```dart
// lib/features/voice/screens/recording_screen.dart

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:record/record.dart';
import 'package:audioplayers/audioplayers.dart';

class RecordingScreen extends StatefulWidget {
  const RecordingScreen({super.key});

  @override
  State<RecordingScreen> createState() => _RecordingScreenState();
}

class _RecordingScreenState extends State<RecordingScreen> {
  final AudioRecorder _recorder = AudioRecorder();
  final AudioPlayer _player = AudioPlayer();
  
  RecordingState _state = RecordingState.idle;
  Duration _duration = Duration.zero;
  Duration _position = Duration.zero;
  String? _recordedFilePath;
  
  // Recording configuration
  static const int _sampleRate = 44100;
  static const int _minDurationSeconds = 10;
  static const int _maxDurationSeconds = 60;

  @override
  void dispose() {
    _recorder.dispose();
    _player.dispose();
    super.dispose();
  }

  Future<void> _startRecording() async {
    try {
      // Check permission
      if (!await _recorder.hasPermission()) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Vui lòng cấp quyền ghi âm')),
        );
        return;
      }

      // Configure recorder
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: _sampleRate,
          numChannels: 1,
        ),
        path: _getRecordingPath(),
      );

      setState(() {
        _state = RecordingState.recording;
        _duration = Duration.zero;
      });

      // Start duration timer
      _startDurationTimer();
    } catch (e) {
      debugPrint('Error starting recording: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Lỗi: $e')),
      );
    }
  }

  Future<void> _stopRecording() async {
    try {
      final path = await _recorder.stop();
      
      setState(() {
        _state = RecordingState.stopped;
        _recordedFilePath = path;
      });
    } catch (e) {
      debugPrint('Error stopping recording: $e');
    }
  }

  void _startDurationTimer() {
    Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_state != RecordingState.recording) {
        timer.cancel();
        return;
      }

      setState(() {
        _duration += const Duration(seconds: 1);
      });

      // Auto-stop if max duration reached
      if (_duration.inSeconds >= _maxDurationSeconds) {
        _stopRecording();
        timer.cancel();
      }
    });
  }

  String _getRecordingPath() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    return '${_getAppDirectory()}/recording_$timestamp.wav';
  }

  String _getAppDirectory() {
    // Implementation depends on platform
    return '/data/user/0/com.musicclub.app/cache';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Thu âm'),
        actions: [
          if (_state == RecordingState.recording)
            TextButton(
              onPressed: _stopRecording,
              child: const Text('Dừng'),
            ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Duration display
            Text(
              _formatDuration(_duration),
              style: Theme.of(context).textTheme.displayMedium,
            ),
            
            // Recording status
            Text(
              _getStatusText(),
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Progress bar
            LinearProgressIndicator(
              value: _duration.inSeconds / _maxDurationSeconds,
              backgroundColor: Colors.grey[300],
            ),
            
            const SizedBox(height: 8),
            
            // Min duration warning
            if (_duration.inSeconds < _minDurationSeconds)
              Text(
                'Tối thiểu ${_minDurationSeconds} giây để phân tích',
                style: TextStyle(color: Colors.orange[700], fontSize: 12),
              ),
            
            const Spacer(),
            
            // Recording visualization
            _buildWaveformVisualization(),
            
            const Spacer(),
            
            // Controls
            _buildControls(),
            
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildControls() {
    switch (_state) {
      case RecordingState.idle:
        return _RecordButton(
          onPressed: _startRecording,
          icon: Icons.mic,
          label: 'Bắt đầu thu âm',
        );
      
      case RecordingState.recording:
        return _RecordButton(
          onPressed: _stopRecording,
          icon: Icons.stop,
          label: 'Dừng thu âm',
          isRecording: true,
        );
      
      case RecordingState.stopped:
        return Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _RecordButton(
              onPressed: _startRecording,
              icon: Icons.refresh,
              label: 'Thu lại',
            ),
            const SizedBox(width: 24),
            _RecordButton(
              onPressed: _analyzeRecording,
              icon: Icons.send,
              label: 'Phân tích',
              isPrimary: true,
            ),
          ],
        );
      
      case RecordingState.analyzing:
        return const Column(
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Đang phân tích...'),
          ],
        );
    }
  }
}
```

### 3.3 Analysis Result Screen

```dart
// lib/features/voice/screens/analysis_result_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/voice_range_chart.dart';
import '../widgets/pitch_visualizer.dart';

class AnalysisResultScreen extends StatelessWidget {
  final VoiceAnalysisResult result;

  const AnalysisResultScreen({
    super.key,
    required this.result,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Kết quả phân tích'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () => _shareResult(context),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Voice type card
            _buildVoiceTypeCard(context),
            const SizedBox(height: 24),
            
            // Voice range chart
            _buildVoiceRangeChart(context),
            const SizedBox(height: 24),
            
            // F0 statistics
            _buildStatisticsCard(context),
            const SizedBox(height: 24),
            
            // Quality metrics
            _buildQualityCard(context),
            const SizedBox(height: 24),
            
            // Note distribution
            _buildNoteDistribution(context),
            const SizedBox(height: 24),
            
            // Recommendations
            _buildRecommendations(context),
          ],
        ),
      ),
    );
  }

  Widget _buildVoiceTypeCard(BuildContext context) {
    return Card(
      color: Theme.of(context).primaryColor,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text(
              result.voiceType ?? 'Unknown',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.verified, color: Colors.white70, size: 16),
                const SizedBox(width: 4),
                Text(
                  'Độ tin cậy: ${((result.confidence ?? 0) * 100).toStringAsFixed(0)}%',
                  style: const TextStyle(color: Colors.white70),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVoiceRangeChart(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Quãng giọng',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            VoiceRangeChart(
              minMidi: result.minMidi ?? 0,
              maxMidi: result.maxMidi ?? 0,
              voiceType: result.voiceType,
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  result.minNoteName ?? '?',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                Text(
                  '${result.rangeSemitones?.toStringAsFixed(0) ?? "?"} semitones',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  result.maxNoteName ?? '?',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatisticsCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Thống kê F0',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            _StatRow(label: 'F0 thấp nhất', value: '${result.minF0?.toStringAsFixed(1)} Hz'),
            _StatRow(label: 'F0 cao nhất', value: '${result.maxF0?.toStringAsFixed(1)} Hz'),
            _StatRow(label: 'F0 trung bình', value: '${result.avgF0?.toStringAsFixed(1)} Hz'),
            _StatRow(label: 'F0 trung vị', value: '${result.medianF0?.toStringAsFixed(1)} Hz'),
            _StatRow(label: 'Độ lệch chuẩn', value: '${result.stdF0?.toStringAsFixed(1)} Hz'),
          ],
        ),
      ),
    );
  }

  Widget _buildQualityCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Chất lượng',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                _QualityBadge(
                  label: 'Điểm',
                  value: result.qualityGrade ?? '?',
                  color: _getGradeColor(result.qualityGrade),
                ),
                const SizedBox(width: 16),
                _QualityBadge(
                  label: 'Tỷ lệ voiced',
                  value: '${((result.voicedRatio ?? 0) * 100).toStringAsFixed(0)}%',
                  color: _getVoicedRatioColor(result.voicedRatio),
                ),
                const SizedBox(width: 16),
                _QualityBadge(
                  label: 'Độ ổn định',
                  value: '${((result.stabilityScore ?? 0) * 100).toStringAsFixed(0)}%',
                  color: _getStabilityColor(result.stabilityScore),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 4. Services

### 4.1 Audio Service

```dart
// lib/data/services/audio_service.dart

import 'dart:io';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';

class AudioService {
  final AudioRecorder _recorder = AudioRecorder();
  
  // Configuration
  static const int sampleRate = 44100;
  static const int minDurationSeconds = 10;
  static const int maxDurationSeconds = 60;
  static const int maxFileSizeMB = 10;

  Future<bool> hasPermission() async {
    return await _recorder.hasPermission();
  }

  Future<String> startRecording() async {
    final directory = await getTemporaryDirectory();
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final path = '${directory.path}/recording_$timestamp.wav';
    
    await _recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.wav,
        sampleRate: sampleRate,
        numChannels: 1,
        bitRate: 705600, // 44100 * 16
      ),
      path: path,
    );
    
    return path;
  }

  Future<String?> stopRecording() async {
    return await _recorder.stop();
  }

  Future<void> cancelRecording() async {
    await _recorder.cancel();
  }

  bool validateFile(String path) {
    final file = File(path);
    if (!file.existsSync()) return false;
    
    final fileSizeMB = file.lengthSync() / (1024 * 1024);
    if (fileSizeMB > maxFileSizeMB) return false;
    
    return true;
  }

  Future<void> dispose() async {
    await _recorder.dispose();
  }
}
```

### 4.2 Voice Analysis Repository

```dart
// lib/data/repositories/voice_repository.dart

import 'dart:io';
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/voice_profile_model.dart';

class VoiceRepository extends ChangeNotifier {
  final ApiService _apiService;
  
  VoiceProfile? _currentProfile;
  List<VoiceAnalysisResult> _analysisHistory = [];
  bool _isLoading = false;

  VoiceRepository(this._apiService);

  VoiceProfile? get currentProfile => _currentProfile;
  List<VoiceAnalysisResult> get analysisHistory => _analysisHistory;
  bool get isLoading => _isLoading;

  Future<VoiceAnalysisResult?> analyzeAudio(String filePath) async {
    _isLoading = true;
    notifyListeners();

    try {
      final file = File(filePath);
      final result = await _apiService.analyzeVoice(file);
      
      if (result != null) {
        _analysisHistory.insert(0, result);
        
        // Update current profile
        _currentProfile = VoiceProfile(
          userId: result.userId,
          voiceType: result.voiceType,
          minF0: result.minF0,
          maxF0: result.maxF0,
          avgF0: result.avgF0,
          minMidi: result.minMidi,
          maxMidi: result.maxMidi,
          rangeSemitones: result.rangeSemitones,
          confidence: result.confidence,
          stabilityScore: result.stabilityScore,
          qualityGrade: result.qualityGrade,
          lastAnalyzedAt: DateTime.now(),
        );
      }
      
      return result;
    } catch (e) {
      debugPrint('Error analyzing voice: $e');
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadProfile() async {
    _isLoading = true;
    notifyListeners();

    try {
      _currentProfile = await _apiService.getVoiceProfile();
    } catch (e) {
      debugPrint('Error loading profile: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadHistory() async {
    try {
      _analysisHistory = await _apiService.getAnalysisHistory();
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading history: $e');
    }
  }
}
```

---

## 5. Models

### 5.1 Voice Profile Model

```dart
// lib/data/models/voice_profile_model.dart

class VoiceProfile {
  final int userId;
  final String? voiceType;
  final double? minF0;
  final double? maxF0;
  final double? avgF0;
  final int? minMidi;
  final int? maxMidi;
  final double? rangeSemitones;
  final double? confidence;
  final double? stabilityScore;
  final String? qualityGrade;
  final DateTime? lastAnalyzedAt;

  VoiceProfile({
    required this.userId,
    this.voiceType,
    this.minF0,
    this.maxF0,
    this.avgF0,
    this.minMidi,
    this.maxMidi,
    this.rangeSemitones,
    this.confidence,
    this.stabilityScore,
    this.qualityGrade,
    this.lastAnalyzedAt,
  });

  String? get minNoteName => _midiToNoteName(minMidi);
  String? get maxNoteName => _midiToNoteName(maxMidi);

  String? _midiToNoteName(int? midi) {
    if (midi == null) return null;
    final noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    final octave = (midi ~/ 12) - 1;
    final note = noteNames[midi % 12];
    return '$note$octave';
  }

  factory VoiceProfile.fromJson(Map<String, dynamic> json) {
    return VoiceProfile(
      userId: json['userId'] ?? 0,
      voiceType: json['voiceType'],
      minF0: json['minF0']?.toDouble(),
      maxF0: json['maxF0']?.toDouble(),
      avgF0: json['avgF0']?.toDouble(),
      minMidi: json['minMidi'],
      maxMidi: json['maxMidi'],
      rangeSemitones: json['rangeSemitones']?.toDouble(),
      confidence: json['confidence']?.toDouble(),
      stabilityScore: json['stabilityScore']?.toDouble(),
      qualityGrade: json['qualityGrade'],
      lastAnalyzedAt: json['lastAnalyzedAt'] != null 
          ? DateTime.parse(json['lastAnalyzedAt']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'userId': userId,
    'voiceType': voiceType,
    'minF0': minF0,
    'maxF0': maxF0,
    'avgF0': avgF0,
    'minMidi': minMidi,
    'maxMidi': maxMidi,
    'rangeSemitones': rangeSemitones,
    'confidence': confidence,
    'stabilityScore': stabilityScore,
    'qualityGrade': qualityGrade,
    'lastAnalyzedAt': lastAnalyzedAt?.toIso8601String(),
  };
}

class VoiceAnalysisResult {
  final int? analysisId;
  final int? userId;
  final double? minF0;
  final double? maxF0;
  final double? avgF0;
  final double? medianF0;
  final double? stdF0;
  final int? minMidi;
  final int? maxMidi;
  final int? medianMidi;
  final String? voiceType;
  final double? confidence;
  final double? voicedRatio;
  final double? stabilityScore;
  final String? qualityGrade;
  final double? rangeSemitones;
  final Map<String, int>? noteDistribution;
  final DateTime? analyzedAt;

  VoiceAnalysisResult({
    this.analysisId,
    this.userId,
    this.minF0,
    this.maxF0,
    this.avgF0,
    this.medianF0,
    this.stdF0,
    this.minMidi,
    this.maxMidi,
    this.medianMidi,
    this.voiceType,
    this.confidence,
    this.voicedRatio,
    this.stabilityScore,
    this.qualityGrade,
    this.rangeSemitones,
    this.noteDistribution,
    this.analyzedAt,
  });

  String? get minNoteName {
    if (minMidi == null) return null;
    final noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    final octave = (minMidi! ~/ 12) - 1;
    return '${noteNames[minMidi! % 12]}$octave';
  }

  String? get maxNoteName {
    if (maxMidi == null) return null;
    final noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    final octave = (maxMidi! ~/ 12) - 1;
    return '${noteNames[maxMidi! % 12]}$octave';
  }

  factory VoiceAnalysisResult.fromJson(Map<String, dynamic> json) {
    return VoiceAnalysisResult(
      analysisId: json['analysisId'],
      userId: json['userId'],
      minF0: json['minF0']?.toDouble(),
      maxF0: json['maxF0']?.toDouble(),
      avgF0: json['avgF0']?.toDouble(),
      medianF0: json['medianF0']?.toDouble(),
      stdF0: json['stdF0']?.toDouble(),
      minMidi: json['minMidi'],
      maxMidi: json['maxMidi'],
      medianMidi: json['medianMidi'],
      voiceType: json['voiceType'],
      confidence: json['confidence']?.toDouble(),
      voicedRatio: json['voicedRatio']?.toDouble(),
      stabilityScore: json['stabilityScore']?.toDouble(),
      qualityGrade: json['qualityGrade'],
      rangeSemitones: json['rangeSemitones']?.toDouble(),
      noteDistribution: json['noteDistribution'] != null
          ? Map<String, int>.from(json['noteDistribution'])
          : null,
      analyzedAt: json['analyzedAt'] != null 
          ? DateTime.parse(json['analyzedAt']) 
          : null,
    );
  }
}
```

---

**Document Version:** 1.0  
**Created:** September 19, 2026  
**Status:** Complete
