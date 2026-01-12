#!/usr/bin/env python3
"""
Stream M3U playlist files to RTMP server using ffmpeg without re-encoding.
"""

import subprocess
import sys
import os
import argparse

def parse_m3u_playlist(m3u_path):
    """
    Parse M3U playlist file and extract video file paths.
    
    Args:
        m3u_path: Path to M3U playlist file
        
    Returns:
        List of video file paths
    """
    videos = []
    try:
        with open(m3u_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_name = None
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#EXTM3U'):
                continue
            
            if line.startswith('#EXTINF'):
                # Extract name from #EXTINF line: #EXTINF:-1,Video Name
                parts = line.split(',', 1)
                if len(parts) > 1:
                    current_name = parts[1].strip()
                else:
                    current_name = None
            elif line and not line.startswith('#'):
                # This is a file path or URL
                video_path = line.strip()
                
                # Check if it's a URL (http, https, rtmp, etc.)
                is_url = (video_path.startswith('http://') or 
                         video_path.startswith('https://') or
                         video_path.startswith('rtmp://') or
                         video_path.startswith('rtsp://') or
                         video_path.startswith('udp://') or
                         video_path.startswith('tcp://'))
                
                # Only resolve relative paths for local files, not URLs
                if not is_url and not os.path.isabs(video_path):
                    m3u_dir = os.path.dirname(os.path.abspath(m3u_path))
                    video_path = os.path.join(m3u_dir, video_path)
                    video_path = os.path.normpath(video_path)
                
                # For URLs, use the URL as-is. For local files, check existence later
                videos.append({
                    'name': current_name or (os.path.basename(video_path) if not is_url else video_path),
                    'path': video_path,
                    'is_url': is_url
                })
                current_name = None
    except Exception as e:
        print(f"Error parsing M3U file: {e}")
        return []
    
    return videos

def stream_video_to_rtmp(video_path, rtmp_url, ffmpeg_path='ffmpeg', loop=False, is_url=False):
    """
    Stream a single video file or URL to RTMP server without re-encoding.
    
    Args:
        video_path: Path to video file or URL
        rtmp_url: RTMP server URL
        ffmpeg_path: Path to ffmpeg executable
        loop: Whether to loop the video
        is_url: Whether video_path is a URL (not a local file)
        
    Returns:
        True if successful, False otherwise
    """
    # Only check file existence for local files, not URLs
    if not is_url and not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return False
    
    ffmpeg_cmd = [
        ffmpeg_path,
        '-re',  # Read input at native frame rate
        '-i', video_path,
        '-c', 'copy',  # Copy all streams without re-encoding
        '-f', 'flv',   # RTMP requires FLV format
        '-flvflags', 'no_duration_filesize',
        rtmp_url
    ]
    
    if loop:
        ffmpeg_cmd.insert(2, '-stream_loop')
        ffmpeg_cmd.insert(3, '-1')
    
    try:
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
        
        import threading
        stdout_thread = threading.Thread(target=print_output, args=(process.stdout,))
        stderr_thread = threading.Thread(target=print_output, args=(process.stderr,))
        
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()
        
        process.wait()
        
        if process.returncode != 0:
            print(f"\nError: FFmpeg exited with code {process.returncode}")
            return False
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
    except Exception as e:
        print(f"Error: {e}")
        return False

def stream_m3u_to_rtmp(m3u_path, rtmp_url, ffmpeg_path='ffmpeg', loop_playlist=False, loop_video=False):
    """
    Stream M3U playlist to RTMP server without re-encoding.
    
    Args:
        m3u_path: Path to M3U playlist file
        rtmp_url: RTMP server URL (e.g., rtmp://server/live/stream_key)
        ffmpeg_path: Path to ffmpeg executable (default: 'ffmpeg')
        loop_playlist: Loop through the entire playlist when finished
        loop_video: Loop each individual video
    """
    
    # Convert to absolute path
    m3u_path = os.path.abspath(m3u_path)
    if not os.path.exists(m3u_path):
        print(f"Error: M3U playlist file not found: {m3u_path}")
        return False
    
    print(f"Parsing M3U playlist: {m3u_path}")
    videos = parse_m3u_playlist(m3u_path)
    
    if not videos:
        print("Error: No videos found in M3U playlist")
        return False
    
    print(f"Found {len(videos)} video(s) in playlist:")
    for i, video in enumerate(videos, 1):
        print(f"  {i}. {video['name']} ({video['path']})")
    
    print(f"\nStreaming to: {rtmp_url}")
    print("Press Ctrl+C to stop streaming...\n")
    
    try:
        while True:
            for i, video in enumerate(videos, 1):
                print(f"\n{'='*60}")
                print(f"Streaming video {i}/{len(videos)}: {video['name']}")
                print(f"Source: {video['path']}")
                print(f"{'='*60}\n")
                
                success = stream_video_to_rtmp(
                    video['path'], 
                    rtmp_url, 
                    ffmpeg_path, 
                    loop_video,
                    video.get('is_url', False)
                )
                
                if not success:
                    print(f"Failed to stream: {video['name']}")
                    if not loop_playlist:
                        return False
                    continue
            
            if not loop_playlist:
                print("\nPlaylist finished streaming")
                return True
            
            print("\nRestarting playlist...")
            
    except KeyboardInterrupt:
        print("\n\nStreaming stopped by user")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Stream M3U playlist files to RTMP server without re-encoding'
    )
    parser.add_argument(
        'm3u_file',
        help='Path to M3U playlist file'
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
    parser.add_argument(
        '--loop-playlist',
        action='store_true',
        help='Loop through the entire playlist when finished'
    )
    parser.add_argument(
        '--loop-video',
        action='store_true',
        help='Loop each individual video file'
    )
    
    args = parser.parse_args()
    
    success = stream_m3u_to_rtmp(
        args.m3u_file,
        args.rtmp_url,
        args.ffmpeg,
        args.loop_playlist,
        args.loop_video
    )
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
