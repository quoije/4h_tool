# M3U to RTMP Streamer

Python script to stream M3U playlist files to RTMP servers using ffmpeg without re-encoding.

## Features

- Direct stream passthrough (no re-encoding)
- Supports M3U playlist files
- Streams to RTMP servers
- Real-time output monitoring
- Playlist looping support
- Graceful shutdown on Ctrl+C

## Requirements

- Python 3.7+
- FFmpeg installed and in PATH (or provide path with --ffmpeg)

## Installation

1. Install FFmpeg:
   - Windows: Download from https://ffmpeg.org/download.html
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

2. No Python dependencies required (uses standard library)

## Usage

### Basic Usage

```bash
# Stream M3U playlist
python stream_m3u_to_rtmp.py <m3u_file> <rtmp_url>

# Stream single video file
python stream_m3u_to_rtmp.py <video_file> <rtmp_url> --single-file
```

### Examples

```bash
# Stream M3U playlist to RTMP server
python stream_m3u_to_rtmp.py \
  "playlist.m3u" \
  "rtmp://live.twitch.tv/app/your_stream_key"

# Stream single local video file
python stream_m3u_to_rtmp.py \
  "video.mp4" \
  "rtmp://server.com/live/stream_key" \
  --single-file

# Stream single video file (auto-detected by extension)
python stream_m3u_to_rtmp.py \
  "video.mp4" \
  "rtmp://server.com/live/stream_key"

# Stream single video URL
python stream_m3u_to_rtmp.py \
  "https://example.com/video.mp4" \
  "rtmp://server.com/live/stream_key"

# Stream with absolute path
python stream_m3u_to_rtmp.py \
  "C:/path/to/playlist.m3u" \
  "rtmp://server.com/live/stream_key"

# Loop through playlist when finished
python stream_m3u_to_rtmp.py \
  "playlist.m3u" \
  "rtmp://server.com/live/key" \
  --loop-playlist

# Loop each individual video
python stream_m3u_to_rtmp.py \
  "playlist.m3u" \
  "rtmp://server.com/live/key" \
  --loop-video

# Specify custom ffmpeg path
python stream_m3u_to_rtmp.py \
  "playlist.m3u" \
  "rtmp://server.com/live/key" \
  --ffmpeg "C:/ffmpeg/bin/ffmpeg.exe"
```

## M3U Playlist Format

The script supports standard M3U playlist format:

```
#EXTM3U
#EXTINF:-1,Video Name 1
/path/to/video1.mp4
#EXTINF:-1,Video Name 2
/path/to/video2.mp4
```

- `#EXTM3U` - Playlist header (optional)
- `#EXTINF:-1,Name` - Video metadata (optional, -1 means unknown duration)
- File paths can be absolute or relative to the M3U file location

## RTMP URL Format

RTMP URLs typically follow this format:
```
rtmp://server.com:port/app/stream_key
```

Examples:
- Twitch: `rtmp://live.twitch.tv/app/YOUR_STREAM_KEY`
- YouTube: `rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY`
- Custom server: `rtmp://your-server.com:1935/live/stream_key`

## Options

- `--loop-playlist`: Loop through the entire playlist when finished (M3U only)
- `--loop-video`: Loop each individual video file indefinitely
- `--single-file`: Treat input as a single video file instead of M3U playlist
- `--ffmpeg`: Specify custom path to ffmpeg executable

## Input Types

The script supports two input types:

1. **M3U Playlist Files**: Automatically detected by file extension (.m3u, .m3u8)
2. **Single Video Files**: Automatically detected by video extensions (.mp4, .mkv, .avi, etc.) or use `--single-file` flag
3. **Video URLs**: HTTP/HTTPS URLs are automatically treated as single video files

## How It Works

The script:
1. Parses the M3U playlist file to extract video file paths
2. Streams each video sequentially to the RTMP server
3. Uses ffmpeg with `-c copy` to passthrough without re-encoding
4. Outputs in FLV format (required for RTMP)

## Notes

- The script streams videos in the order they appear in the playlist
- Relative paths in M3U files are resolved relative to the M3U file location
- No re-encoding means very low CPU usage
- Requires the source video codecs to be compatible with RTMP/FLV
- If codec compatibility issues occur, you may need to re-encode (remove `-c copy`)

## Troubleshooting

- **FFmpeg not found**: Install FFmpeg or use `--ffmpeg` to specify path
- **Connection errors**: Check RTMP URL and network connectivity
- **Codec errors**: Source codecs may not be RTMP-compatible, may need re-encoding
- **File not found**: Check video file paths in the M3U playlist are correct
- **Playlist empty**: Ensure M3U file contains valid video file paths
