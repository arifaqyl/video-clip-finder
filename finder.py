import subprocess
import sys
import os

def measure_loudness_audio_only(video_path, start_time, duration=20): 
    """Measure peak volume - AUDIO ONLY (fast)"""
    cmd = [
        'ffmpeg',
        '-ss', str(start_time),
        '-i', video_path,
        '-vn',  # SKIP VIDEO
        '-t', str(duration),
        '-af', 'volumedetect',
        '-f', 'null',
        '-'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    for line in result.stderr.split('\n'):
        if 'max_volume:' in line:
            try:
                volume = float(line.split('max_volume:')[1].split('dB')[0].strip())
                return volume
            except:
                return -999
    return -999

def get_top_moments(video_path, num_clips=60):
    """Find the top N LOUDEST moments"""
    print(f"Analyzing: {video_path}\n")
    
    # Step 1: Find all loud moments (audio only)
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vn',
        '-af', f'silencedetect=n=-15dB:d=1',
        '-f', 'null',
        '-'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    moments = []
    for line in result.stderr.split('\n'):
        if 'silence_end' in line:
            parts = line.split('silence_end: ')
            if len(parts) > 1:
                time = float(parts[1].split('|')[0].strip())
                moments.append(time)
    
    # Step 2: Group close moments
    grouped = []
    if moments:
        grouped.append(moments[0])
        for time in moments[1:]:
            if time - grouped[-1] > 30:
                grouped.append(time)
    
    print(f"Found {len(moments)} loud moments")
    print(f"Grouped into {len(grouped)} separate events")
    print(f"\nMeasuring loudness (audio only - fast)...\n")
    
    # Step 3: Measure loudness (audio only)
    ranked = []
    for i, time in enumerate(grouped):
        loudness = measure_loudness_audio_only(video_path, time)
        ranked.append((time, loudness))
        mins = int(time // 60)
        secs = int(time % 60)
        print(f"  {i+1}/{len(grouped)}: {mins}:{secs:02d} = {loudness:.1f} dB")
    
    # Step 4: Sort by loudness
    ranked.sort(key=lambda x: x[1], reverse=True)
    
    # Step 5: Take top N
    top_moments = [time for time, _ in ranked[:num_clips]]
    top_moments.sort()
    
    print(f"\n{'='*50}")
    print(f"Top {len(top_moments)} LOUDEST moments:\n")
    
    for i, time in enumerate(top_moments):
        mins = int(time // 60)
        secs = int(time % 60)
        volume = next(v for t, v in ranked if t == time)
        print(f"  Clip {i+1}: {mins}:{secs:02d} ({volume:.1f} dB)")
    
    return top_moments

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python finder.py <video_file>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    moments = get_top_moments(video_path, num_clips=60)  # EXACTLY 60 CLIPS