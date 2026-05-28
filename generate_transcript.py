import os
# --- FIX FOR WINDOWS SYMLINK CRASH ---
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

from faster_whisper import WhisperModel
import subprocess
import sys

def get_duration(video_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try: return float(result.stdout.strip())
    except: return 7200.0

def extract_audio_chunk(video_path, start_time, chunk_duration, temp_audio="temp_chunk.wav"):
    cmd = [
        'ffmpeg', '-ss', str(start_time), '-i', video_path, '-t', str(chunk_duration),
        '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', 
        '-y', temp_audio, '-loglevel', 'error'
    ]
    subprocess.run(cmd)
    return temp_audio

def generate_transcript(video_path):
    print(f"Generating full transcript for: {video_path}")
    
    # --- FIX: RYZEN 5 3600 CPU FALLBACK ---
    # We use CPU and int8 to bypass the missing NVIDIA dll files. 
    model = WhisperModel("small", device="cpu", compute_type="int8")
    
    duration = get_duration(video_path)
    chunk_size = 600
    
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_file = f"{video_name}_transcript.txt"
    
    print(f"Video is ~{int(duration/60)} minutes long. Writing to {output_file}...")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"--- FULL TRANSCRIPT FOR {video_name} ---\n\n")
        
        for start_time in range(0, int(duration), chunk_size):
            chunk_end = min(start_time + chunk_size, duration)
            print(f"Processing {int(start_time/60)}m to {int(chunk_end/60)}m...")
            
            temp_audio = extract_audio_chunk(video_path, start_time, chunk_size)
            if not os.path.exists(temp_audio) or os.path.getsize(temp_audio) < 1000:
                continue
                
            # Manglish Instruction
            segments, info = model.transcribe(
                temp_audio, 
                beam_size=5,
                initial_prompt="Ini perbualan santai campur bahasa Melayu dan English. Manglish lepak Discord."
            )
            
            for segment in segments:
                real_start = start_time + segment.start
                real_end = start_time + segment.end
                
                start_m, start_s = int(real_start // 60), int(real_start % 60)
                end_m, end_s = int(real_end // 60), int(real_end % 60)
                
                line = f"[{start_m:02d}:{start_s:02d} -> {end_m:02d}:{end_s:02d}] {segment.text.strip()}\n"
                f.write(line)
                
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
                
    print(f"\n✓ DONE! Open {output_file} to see your transcript.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_transcript.py <video_file>")
        sys.exit(1)
        
    generate_transcript(sys.argv[1])