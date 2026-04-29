import subprocess
import sys
import os

def cut_clips(video_path, moments, output_dir="clips", duration=30):
    """Cut clips around each moment"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    print(f"Cutting {len(moments)} clips...\n")
    
    for i, time in enumerate(moments):
        # Start 15 seconds before the moment
        start = max(0, time - 15)
        
        # Output filename
        output = os.path.join(output_dir, f"{video_name}_clip{i+1}.mp4")
        
        # Cut the clip
        cmd = [
            'ffmpeg',
            '-ss', str(start),
            '-i', video_path,
            '-t', str(duration),
            '-c', 'copy',
            '-y',  # Overwrite without asking
            output
        ]
        
        mins = int(time // 60)
        secs = int(time % 60)
        print(f"Clip {i+1} ({mins}:{secs:02d})... ", end='', flush=True)
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            print("✓")
        else:
            print("✗ FAILED")
    
    print(f"\nDone! Clips saved to: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cutter.py <video_file> [num_clips]")
        print("Example: python cutter.py video.mp4 10")
        sys.exit(1)
    
    from finder import get_top_moments
    
    video_path = sys.argv[1]
    num_clips = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    moments = get_top_moments(video_path, num_clips=num_clips)
    
    print("\n" + "="*50)
    cut_clips(video_path, moments)