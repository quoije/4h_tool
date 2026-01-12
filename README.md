# M3U8 to RTMP Streamer

Python script to stream M3U8 (HLS) live streams to RTMP servers using ffmpeg without re-encoding.

## Features

- Direct stream passthrough (no re-encoding)
- Supports M3U8/HLS playlists
- Streams to RTMP servers
- Real-time output monitoring
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
python stream_m3u_to_rtmp.py <m3u_url> <rtmp_url>
```

### Examples

```bash
# Stream from M3U8 URL to RTMP server
python stream_m3u_to_rtmp.py \
  "https://example.com/live/stream.m3u8" \
  "rtmp://live.twitch.tv/app/your_stream_key"

# Stream from local M3U8 file (relative or absolute path)
python stream_m3u_to_rtmp.py \
  "playlist.m3u8" \
  "rtmp://server.com/live/stream_key"

# Stream from local M3U8 file with absolute path
python stream_m3u_to_rtmp.py \
  "C:/path/to/playlist.m3u8" \
  "rtmp://server.com/live/stream_key"

# Specify custom ffmpeg path
python stream_m3u_to_rtmp.py \
  "https://example.com/stream.m3u8" \
  "rtmp://server.com/live/key" \
  --ffmpeg "C:/ffmpeg/bin/ffmpeg.exe"
```

## RTMP URL Format

RTMP URLs typically follow this format:
```
rtmp://server.com:port/app/stream_key
```

Examples:
- Twitch: `rtmp://live.twitch.tv/app/YOUR_STREAM_KEY`
- YouTube: `rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY`
- Custom server: `rtmp://your-server.com:1935/live/stream_key`

## How It Works

The script uses ffmpeg with:
- `-c copy`: Copies all codecs without re-encoding (passthrough)
- `-f flv`: Outputs in FLV format (required for RTMP)
- `-re`: Reads input at native frame rate
- Direct stream from M3U8 to RTMP

## Notes

- The stream will continue until stopped (Ctrl+C) or the source ends
- No re-encoding means very low CPU usage
- Requires the source stream codecs to be compatible with RTMP/FLV
- If codec compatibility issues occur, you may need to re-encode (remove `-c copy`)

## Troubleshooting

- **FFmpeg not found**: Install FFmpeg or use `--ffmpeg` to specify path
- **Connection errors**: Check RTMP URL and network connectivity
- **Codec errors**: Source codecs may not be RTMP-compatible, may need re-encoding
- **Stream stops**: Check source M3U8 URL is accessible and valid

