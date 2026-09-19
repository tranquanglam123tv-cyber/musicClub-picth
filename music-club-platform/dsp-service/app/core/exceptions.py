"""
DSP Exceptions
==============
"""


class DSPError(Exception):
    """Base DSP error."""
    pass


class AudioValidationError(DSPError):
    """Audio file validation failed."""
    pass


class F0ExtractionError(DSPError):
    """F0 extraction failed."""
    pass


class InsufficientDataError(DSPError):
    """Not enough voiced data for analysis."""
    pass


# Error responses
ERROR_RESPONSES = {
    'FILE_NOT_FOUND': {
        'error': 'Audio file not found',
        'code': 'FILE_NOT_FOUND'
    },
    'INVALID_FORMAT': {
        'error': 'Invalid audio format. Must be WAV.',
        'code': 'INVALID_FORMAT'
    },
    'WRONG_SAMPLE_RATE': {
        'error': 'Sample rate must be 44100 Hz',
        'code': 'WRONG_SAMPLE_RATE'
    },
    'WRONG_CHANNELS': {
        'error': 'Audio must be mono (1 channel)',
        'code': 'WRONG_CHANNELS'
    },
    'FILE_TOO_LARGE': {
        'error': 'File size exceeds 10 MB limit',
        'code': 'FILE_TOO_LARGE'
    },
    'DURATION_TOO_SHORT': {
        'error': 'Recording too short. Minimum 10 seconds.',
        'code': 'DURATION_TOO_SHORT'
    },
    'DURATION_TOO_LONG': {
        'error': 'Recording too long. Maximum 60 seconds.',
        'code': 'DURATION_TOO_LONG'
    },
    'NO_VOICED_DATA': {
        'error': 'No voiced speech detected in recording',
        'code': 'NO_VOICED_DATA'
    },
    'LOW_QUALITY': {
        'error': 'Audio quality too low for analysis',
        'code': 'LOW_QUALITY'
    }
}
