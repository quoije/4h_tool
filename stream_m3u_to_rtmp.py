#!/usr/bin/env python3
"""
Stream M3U8 (HLS) live stream to RTMP server using ffmpeg without re-encoding.
"""

import subprocess
import sys
import signal
import os
import argparse

def stream_m3u_to_rtmp(m3u_url, rtmp_url, ffmpeg_path='ffmpeg'):
    """
    Stream M3U8 playlist to RTMP server without re-encoding.
    
    Args:
        m3u_url: URL or path to M3U8 playlist file
        rtmp_url: RTMP server URL (e.g., rtmp://server/live/stream_key)
        ffmpeg_path: Path to ffmpeg executable (default: 'ffmpeg')
    """
    
    # FFmpeg command for direct stream (no re-encoding)
    # -i: input M3U8 URL
    # -c copy: copy codecs without re-encoding
    # -f flv: output format FLV (required for RTMP)
    # -flvflags no_duration_filesize: avoid issues with FLV format
    # -re: read input at native frame rate (important for live streams)
    # -stream_loop -1: loop the stream indefinitely (for live streams, this might not be needed)
    
    ffmpeg_cmd = [
        ffmpeg_path,
        '-i', m3u_url,
        '-c', 'copy',  # Copy all streams without re-encoding
        '-f', 'flv',   # RTMP requires FLV format
        '-flvflags', 'no_duration_filesize',
        '-re',         # Read input at native frame rate
        rtmp_url
    ]
    
    print(f"Starting stream from: {m3u_url}")
    print(f"Streaming to: {rtmp_url}")
    print(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")
    print("\nPress Ctrl+C to stop streaming...\n")
    
    try:
        # Start ffmpeg process
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print ffmpeg output in real-time
        def print_output(pipe):
            for line in iter(pipe.readline, ''):
                if line:
                    print(line.strip())
        
        # Monitor both stdout and stderr
        import threading
        stdout_thread = threading.Thread(target=print_output, args=(process.stdout,))
        stderr_thread = threading.Thread(target=print_output, args=(process.stderr,))
        
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()
        
        # Wait for process to complete
        process.wait()
        
        if process.returncode != 0:
            print(f"\nError: FFmpeg exited with code {process.returncode}")
            return False
        else:
            print("\nStream ended successfully")
            return True
            
    except KeyboardInterrupt:
        print("\n\nStopping stream...")
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("Stream stopped")
        return False
    except FileNotFoundError:
        print(f"Error: FFmpeg not found at '{ffmpeg_path}'")
        print("Please install FFmpeg or provide the correct path")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Stream M3U8 (HLS) live stream to RTMP server without re-encoding'
    )
    parser.add_argument(
        'm3u_url',
        help='URL or path to M3U8 playlist file'
    )
    parser.add_argument(
        'rtmp_url',
        help='RTMP server URL (e.g., rtmp://server/live/stream_key)'
    )
    parser.add_argument(
        '--ffmpeg',
        default='ffmpeg',
        help='Path to ffmpeg executable (default: ffmpeg)'
    )
    
    args = parser.parse_args()
    
    success = stream_m3u_to_rtmp(args.m3u_url, args.rtmp_url, args.ffmpeg)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

