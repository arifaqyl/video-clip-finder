import subprocess
import os

def cut_highlights(video_path, highlights):
    """
    highlights should be a list of tuples with start and end times in SECONDS.
    Example: [(120, 150), (400, 460)]
    """
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = "final_edits"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Cutting {len(highlights)} highlight segments...")
    concat_file = os.path.join(output_dir, "concat_list.txt")
    safe_video_path = os.path.abspath(video_path).replace('\\', '/')
    
    # We use FFmpeg's inpoint/outpoint to instantly cut without re-encoding
    with open(concat_file, "w") as f:
        for start, end in highlights:
            f.write(f"file '{safe_video_path}'\n")
            f.write(f"inpoint {start:.3f}\n")
            f.write(f"outpoint {end:.3f}\n")
            
    final_output = os.path.join(output_dir, f"{video_name}_AI_EDIT.mp4")
    
    cmd = [
        'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file,
        '-c', 'copy', '-y', final_output
    ]
    
    print("Stitching final video... (This is very fast!)")
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode == 0:
        print(f"\n✓ SUCCESS! Your final AI edit is ready: {final_output}")
    else:
        print("\n✗ Failed to stitch video.")
        print(result.stderr.decode('utf-8')[-500:])
        
    if os.path.exists(concat_file):
        os.remove(concat_file)

if __name__ == "__main__":
    # ---------------------------------------------------------
    # PUT YOUR VIDEO FILE PATH HERE
    # ---------------------------------------------------------
    video_file = r"D:\obs\2026-04-29 23-47-16.mp4"
    
    # ---------------------------------------------------------
    # PUT THE TIMESTAMPS THE AI GIVES YOU HERE (In seconds!)
    # Example: If I say 1:00 to 1:30, that is (60, 90)
    # ---------------------------------------------------------
    ai_timestamps = [
        (60, 90),     # Highlight 1
        (300, 345),   # Highlight 2
        (1200, 1260)  # Highlight 3
    ]
    
    cut_highlights(video_file, ai_timestamps)