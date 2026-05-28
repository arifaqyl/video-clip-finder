import re
import os
import subprocess

def time_to_sec(time_str):
    """Converts [MM:SS] into raw seconds"""
    m, s = time_str.split(':')
    return int(m) * 60 + int(s)

def create_jumpcut_video(video_path, transcript_path, blocks):
    print("Reading transcript to build precision jump-cuts...")
    
    valid_cuts = []
    
    # Open the transcript file you already generated
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Look for the [MM:SS -> MM:SS] pattern
            match = re.search(r"\[(\d{2}:\d{2}) -> (\d{2}:\d{2})\]", line)
            if match:
                start_sec = time_to_sec(match.group(1))
                end_sec = time_to_sec(match.group(2))
                
                # Check if this sentence belongs in our Viral Story Arcs
                for block_start, block_end in blocks:
                    if start_sec >= block_start and end_sec <= block_end:
                        # Add a 0.2s buffer so the cuts don't sound too robotic
                        valid_cuts.append((max(0, start_sec - 0.2), end_sec + 0.2))
                        break
                        
    # Clean up overlapping cuts (if you speak fast, the 0.2s buffers might overlap)
    merged_cuts = []
    if valid_cuts:
        merged_cuts.append(valid_cuts[0])
        for current in valid_cuts[1:]:
            last = merged_cuts[-1]
            if current[0] <= last[1]: # They overlap
                merged_cuts[-1] = (last[0], max(last[1], current[1]))
            else:
                merged_cuts.append(current)

    output_dir = "final_edits"
    os.makedirs(output_dir, exist_ok=True)
    concat_file = os.path.join(output_dir, "jump_cuts.txt")
    safe_video_path = os.path.abspath(video_path).replace('\\', '/')
    
    print(f"Found {len(merged_cuts)} spoken sentences within the target clips.")
    print("Stripping all dead air and silence...")
    
    # Write the FFmpeg instructions
    with open(concat_file, "w", encoding='utf-8') as f:
        for start, end in merged_cuts:
            f.write(f"file '{safe_video_path}'\n")
            f.write(f"inpoint {start:.3f}\n")
            f.write(f"outpoint {end:.3f}\n")
            
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    final_output = os.path.join(output_dir, f"{video_name}_JUMP_CUT_MASTER.mp4")
    
    # Fast copy without re-encoding
    cmd = [
        'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file,
        '-c', 'copy', '-y', final_output
    ]
    
    print("Stitching the final jump-cut video... (This takes a few seconds)")
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode == 0:
        print(f"\n✓ SUCCESS! Fast-paced Jump-cut video saved to: {final_output}")
    else:
        print("\n✗ Error stitching video:")
        print(result.stderr.decode('utf-8')[-500:])

if __name__ == "__main__":
    # ---------------------------------------------------------
    # YOUR FILES (Make sure these paths are correct!)
    # ---------------------------------------------------------
    video = r"D:\obs\2026-04-29 23-47-16.mp4"
    transcript = r"D:\clip-finder\2026-04-29 23-47-16_transcript.txt"
    
    # ---------------------------------------------------------
    # DEEPSEEK MASTER CUT (With Closure)
    # ---------------------------------------------------------
    story_arcs = [
        (0, 329),         # Early Lore: Blinded by love / simping for Akil
        (3412, 3604),     # Jut crush & the "tembakan" incident
        (3882, 3915),     # Ayan's memory roast (ganjut burn)
        (3965, 4155),     # Hilarious Jubah fetish confession
        (4718, 4973),     # Spicy hijab disgust story with closure
        (5046, 5361),     # Performative hiking argument (full version)
        (6154, 6259),     # Awkward roommate praying dilemma
        (6399, 6446)      # Video closure (goodbyes)
    ]
    
    create_jumpcut_video(video, transcript, story_arcs)