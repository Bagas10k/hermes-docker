# Headless Video Rendering & Studio Daemon Operations

Production procedures for compiling and rendering Remotion videos on Linux servers.

## PM2 Daemon for Remotion Studio

Remotion Studio provides live timeline inspection, scrubbing, and frame previews.

```bash
# Start Remotion Studio on dedicated port (e.g. 3300)
pm2 start "npx remotion studio --port=3300 --no-open" --name "hermes-motion-studio"

# Verify healthy startup
curl -sI http://127.0.0.1:3300 | head -n 1
# Expected: HTTP/1.1 200 OK

# Check memory and uptime
pm2 status hermes-motion-studio
```

## Still Frame Inspection Before Full Render

Always render and inspect 2-3 key frames before committing to a full video render:
```bash
# Render hook frame (e.g. frame 60)
npx remotion still src/index.ts MaduAbadi output/frame_hook.png --frame=60 --gl=angle

# Render data visualization frame (e.g. frame 450)
npx remotion still src/index.ts MaduAbadi output/frame_data.png --frame=450 --gl=angle
```
Inspect generated still frames with image analysis tools to verify typography, zero-emoji compliance, and layout contrast.

## Full Video Production Render

```bash
npx remotion render src/index.ts <CompositionName> output/video.mp4 \
  --gl=angle \
  --concurrency=4 \
  --quality=85 \
  --image-format=jpeg \
  --pixel-format=yuv420p
```

### Parameter Reference

| Flag | Recommended Value | Reason |
|------|-------------------|--------|
| `--gl` | `angle` | Uses Google ANGLE OpenGL ES emulator; prevents WebGL crashes on headless Linux. |
| `--concurrency` | `4` (or CPU cores / 2) | Balances render throughput against server RAM usage. |
| `--pixel-format` | `yuv420p` | Maximum compatibility across mobile platforms (TikTok, Instagram, WhatsApp). |
| `--quality` | `80-90` | Optimal visual sharpness without bloated file size (<10 MB for 30s). |
