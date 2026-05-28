import subprocess
import sys
import os

def cut_clips(video_path, moments, output_dir="clips", duration=20):  # FIXED: 20 seconds
    """Cut clips around each moment and merge them into one video"""
    os.makedirs(output_dir, exist_ok=True)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    print(f"Cutting {len(moments)} clips (20s each)...\n")
    
    clip_files = []
    
    for i, time in enumerate(moments):
        # FIXED: Start 10 seconds before the loud moment so it is centered
        start = max(0, time - 10)
        output = os.path.join(output_dir, f"{video_name}_clip{i+1}.mp4")
        
        cmd = [
            'ffmpeg',
            '-ss', str(start),
            '-i', video_path,
            '-t', str(duration),
            '-c', 'copy',
            '-y',  # Overwrite
            output
        ]
        
        mins = int(time // 60)
        secs = int(time % 60)
        print(f"Clip {i+1} ({mins}:{secs:02d})... ", end='', flush=True)
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            print("✓")
            clip_files.append(output)
        else:
            print("✗ FAILED")
            
    # NEW: Merge all clips into one single 20-minute video
    if clip_files:
        print(f"\n{'-'*50}")
        print("Stitching 60 clips into one 20-minute highlight video...")
        
        # ffmpeg requires a text file listing all videos to merge
        concat_file = os.path.join(output_dir, "concat_list.txt")
        with open(concat_file, "w") as f:
            for clip in clip_files:
                # Use absolute paths with forward slashes for ffmpeg safety
                safe_path = os.path.abspath(clip).replace('\\', '/')
                f.write(f"file '{safe_path}'\n")
        
        final_output = os.path.join(output_dir, f"{video_name}_FINAL_HIGHLIGHTS.mp4")
        concat_cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y',
            final_output
        ]
        
        concat_result = subprocess.run(concat_cmd, capture_output=True)
        
        if concat_result.returncode == 0:
            print(f"✓ MERGE SUCCESS! Saved to: {final_output}")
            os.remove(concat_file)  # cleanup the temporary text file
        else:
            print("✗ Merge failed. You still have the individual clips in the folder.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cutter.py <video_file> [num_clips]")
        print("Example: python cutter.py video.mp4 60")
        sys.exit(1)
    
    from finder import get_top_moments
    
    video_path = sys.argv[1]
    # Default to 60 clips (20 mins total) if not specified in terminal
    num_clips = int(sys.argv[2]) if len(sys.argv) > 2 else 60 
    
    moments = get_top_moments(video_path, num_clips=num_clips)
    
    print("\n" + "="*50)
    cut_clips(video_path, moments)