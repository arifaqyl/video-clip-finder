# Clip Finder

Automated highlight extraction tool for OBS recordings using audio-based detection.

## Overview

Clip Finder analyzes long gaming recordings and automatically extracts highlight moments based on audio volume analysis. Instead of manually scrubbing through hours of footage, the tool identifies and cuts the most exciting moments into shareable clips.

## Features

- **Audio-based detection**: Identifies loud moments (reactions, explosions, in-game events)
- **Smart grouping**: Prevents duplicate clips from the same event
- **Volume ranking**: Prioritizes the loudest (most exciting) moments
- **Fast processing**: Analyzes audio only, skipping video processing for speed
- **Configurable output**: Generate 5, 10, or custom number of clips

## Requirements

- Python 3.12 or higher
- FFmpeg (install via `winget install ffmpeg` on Windows)

## Installation

```bash
git clone https://github.com/arifaqyl/clip-finder.git
cd clip-finder
```

No additional dependencies required. Uses Python standard library and FFmpeg.

## Usage

### Generate clips from a recording:
```bash
python cutter.py "path/to/recording.mp4"
```

This will create 10 clips (default) in the `clips/` directory.

### Specify custom clip count:
```bash
python cutter.py "path/to/recording.mp4" 5
```

### Preview timestamps without cutting:
```bash
python finder.py "path/to/recording.mp4"
```

## How It Works

### Detection (finder.py)
1. Uses FFmpeg's `silencedetect` filter to identify audio above -15dB threshold
2. Groups events that occur within 30 seconds of each other
3. Measures peak volume for each grouped event (audio-only processing)
4. Ranks events by loudness and selects top N moments

### Extraction (cutter.py)
1. Takes timestamps from the detection phase
2. Cuts 30-second clips starting 15 seconds before each peak moment
3. Uses FFmpeg's stream copy mode for fast extraction (no re-encoding)
4. Saves clips with timestamps in the filename

## Technical Details

- **Audio threshold**: -15dB (configurable in code)
- **Grouping window**: 30 seconds
- **Clip duration**: 30 seconds
- **Pre-roll**: 15 seconds before detected moment
- **Processing mode**: Audio-only analysis for performance

## Limitations

- Audio-based detection only (no video analysis, OCR, or motion detection)
- May miss quieter strategic moments or clutch plays
- Occasionally captures loud menu/lobby audio
- Optimized for gaming content with clear audio peaks

## Performance

- **Accuracy**: ~80% of generated clips contain relevant highlight content
- **Processing speed**: Approximately 2 minutes for a 2-hour recording (hardware dependent)
- **Success rate**: 8 out of 10 clips typically require no manual filtering

## Use Case

Built to solve the problem of unused gaming footage. After recording sessions with OBS, hours of content would remain unedited due to time constraints. This tool automates the initial extraction phase, reducing a 2-hour editing task to 2 minutes of automated processing plus minimal manual review.

## Future Improvements (V2)

- Speech-to-text integration for context-aware clipping
- Game-specific detection (kill feed OCR for FPS games)
- Motion-based analysis for visual highlights
- GUI interface for non-technical users

## License

MIT License - see LICENSE file for details

## Author

**Arif Aqyl**  
Software Engineering Student, UniKL MIIT  
[GitHub](https://github.com/arifaqyl) • [Website](https://arifaqyl.me)