from faster_whisper import WhisperModel
import subprocess
import sys
import os

def get_duration(video_path):
    """Find total video length using ffprobe"""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 7200.0  # Fallback to 2 hours if reading fails

def extract_audio_chunk(video_path, start_time, chunk_duration, temp_audio="temp_chunk.wav"):
    """Extracts just a small 10-minute slice of audio"""
    cmd = [
        'ffmpeg', 
        '-ss', str(start_time), 
        '-i', video_path, 
        '-t', str(chunk_duration),
        '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', 
        '-y', temp_audio,
        '-loglevel', 'error'  # Keeps the console clean
    ]
    subprocess.run(cmd)
    return temp_audio

def get_top_moments(video_path, num_clips=60):
    print(f"Analyzing: {video_path}")
    
    # Trigger words
    keywords = [
        # English
        "clip that", "clutch", "oh my god", "let's go", "crazy", "insane", "what was that", "no way",
        # Malay
        "gila", "mantap", "cantik", "terbaik", "rekod", "rakam ni", "bapak ah", "weyh", "fuh", "pandai"
    ]
    
    print("Loading Whisper AI... (CPU mode)")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    
    duration = get_duration(video_path)
    chunk_size = 600  # 10 minutes (600 seconds)
    moments = []
    
    print(f"\nVideo is ~{int(duration/60)} minutes long. Scanning in 10-minute chunks to save memory...")
    print("-" * 50)
    
    # Loop through the video in 10 minute blocks
    for start_time in range(0, int(duration), chunk_size):
        chunk_end = min(start_time + chunk_size, duration)
        print(f"\n>>> Scanning timeframe: {int(start_time/60)}m to {int(chunk_end/60)}m...")
        
        temp_audio = extract_audio_chunk(video_path, start_time, chunk_size)
        
        # Safety check: if chunk is empty (end of video), skip it
        if not os.path.exists(temp_audio) or os.path.getsize(temp_audio) < 1000:
            continue
            
        segments, info = model.transcribe(temp_audio, beam_size=5)
        
        for segment in segments:
            text = segment.text.lower()
            for word in keywords:
                if word in text:
                    # Correct the timestamp by adding the chunk's start time
                    real_time = start_time + segment.start
                    mins = int(real_time // 60)
                    secs = int(real_time % 60)
                    print(f"  [{mins}:{secs:02d}] Found '{word}': \"{segment.text.strip()}\"")
                    moments.append(real_time)
                    break 
                    
        # Clean up the chunk to save hard drive space
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
            
    # Group close moments (so you don't get 3 clips for saying "gila" 3 times in a row)
    grouped = []
    if moments:
        grouped.append(moments[0])
        for time in moments[1:]:
            if time - grouped[-1] > 30:
                grouped.append(time)
                
    print("\n" + "="*50)
    print(f"Found {len(grouped)} unique hype moments.")
    return grouped[:num_clips]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_finder.py <video_file>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    get_top_moments(video_path, num_clips=60)