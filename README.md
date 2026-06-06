# video-clip-finder

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)
![ffmpeg](https://img.shields.io/badge/ffmpeg-audio_analysis-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-363739?style=flat-square)
![Status](https://img.shields.io/badge/status-complete-CCFF00?style=flat-square)

Audio energy-based highlight extractor for long OBS recordings. Finds the loudest moments in a 3-hour session and outputs a highlight reel in under 2 minutes.

No ML, no heavy dependencies. Uses FFmpeg's silence detector + peak picking on audio energy.

---

## How it works

```
raw .mp4
   │
   ▼
[finder.py]  FFmpeg silencedetect → audio events above -15dB threshold
             → group events within 30s window
             → rank by peak volume
   │
   ▼
[cutter.py]  Cut 30s clips (15s pre-roll) around each ranked peak
             → stream copy mode (no re-encode, fast)
   │
   ▼
clips/001_12m34s.mp4  clips/002_45m12s.mp4  ...
```

## Usage

```bash
# Find timestamps only (dry run)
python finder.py "path/to/recording.mp4"

# Cut clips (default: top 10)
python cutter.py "path/to/recording.mp4"

# Custom clip count
python cutter.py "path/to/recording.mp4" 5
```

Output goes to `clips/` with timestamp filenames.

## Detection parameters

| Parameter | Default | Notes |
|---|---|---|
| Audio threshold | -15 dB | Adjustable in `finder.py` |
| Grouping window | 30 s | Events within 30s = same moment |
| Clip duration | 30 s | 15s pre-roll + 15s post |
| Processing mode | Audio-only | Video stream skipped for speed |

## Performance

- 2-hour session → top 10 clips in ~2 minutes
- ~80% clip accuracy (contain actual highlight content)
- No re-encoding — stream copy for instant cuts

## Requirements

```
Python 3.12+
ffmpeg  (winget install ffmpeg)
```

No pip dependencies. Uses Python standard library only.

## Install

```bash
git clone https://github.com/arifaqyl/video-clip-finder
cd video-clip-finder
```

---

**[arifaqyl.me](https://arifaqyl.me)** · [github.com/arifaqyl](https://github.com/arifaqyl)
