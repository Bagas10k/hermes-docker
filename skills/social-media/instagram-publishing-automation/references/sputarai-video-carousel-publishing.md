# SputarAI video carousel publication

## When to Use
Use when the owner explicitly authorizes one SputarAI motion-feed publication. Approval of a design or generator is not permission to publish.

## Existing working path
- Confirm `GET https://graph.instagram.com/v26.0/me?fields=id,username` returns `sputarai`, using the existing protected token file. Never log credentials, authenticated URLs or paging URLs.
- Preserve a private job receipt before API writes, including asset hashes, four ordered children, parent container, publication-attempt flag and exact published ID/permalink. The exercised one-off job is `/home/ubuntu/hermes-backup/projects/penelitian-pola-pikir-ai/content-studio/publications/first-motion-feed/`; do not run that job again to create a new post.
- Public media hosting is the active `/home/ubuntu/penelitian-pola-pikir-ai/public/ig-cache/`, not the backup project's public directory. Host only the exact authorized exported files, with hash-based filenames, then verify HTTPS 200 and downloaded bytes against their hashes. Never expose raw SFX, credentials or the whole preview directory. No server restart is needed for this static route.
- For each child POST `/<IG_ID>/media` JSON with `media_type=VIDEO`, `is_carousel_item=true`, `video_url` and `thumb_offset=0`. Poll saved container IDs until FINISHED; publishing has not occurred merely because children are ready.
- A parent request with JSON children string, `share_to_feed=true`, and `is_ai_generated=true` was rejected with HTTP400/code100/subcode2207023 and user message unknown CAROUSEL_V2. The successful bounded alternative was form-encoded POST `/me/media` containing only `media_type=CAROUSEL`, comma-joined children and caption. Multiple parameters changed, so the exact cause is not isolated; do not assert that a specific flag is universally unsupported. AI assistance was disclosed in the actual caption. Do not set is_ai_generated on child containers.
- Check parent FINISHED, persist a publishing-attempt flag BEFORE POST `/<IG_ID>/media_publish` with creation_id. Never blindly retry after ambiguous publish outcomes; reconcile the saved parent/media first.
- Read back the exact published media with id, username, media_type, permalink, timestamp, caption and children. Require username sputarai, CAROUSEL_ALBUM, exactly four VIDEO children, expected caption, and an actual permalink before telling the owner it is live.

## Motion and audio adaptation
The approved local animation cycle is two seconds. The exercised publish files repeated it twice into four-second H264/AAC MP4s, 1080x1350 at 30fps, audio 128k/48kHz, closed GOP and faststart. Four seconds was a conservative ingest adaptation; documentation's explicit three-second minimum was for Reels/Stories, not independently established as a universal carousel requirement. Do not silently replace motion slides with static images or publish four separate posts.

## Delivery
Return the exact Instagram permalink immediately after successful readback. Report verified publication separately from untested app playback, audio perception, engagement, reusable-generator readiness or live DM automation. No unrelated legacy npm suite or independent QC loop is needed to prove this explicit one-off upload.

Primary references: https://developers.facebook.com/documentation/instagram-platform/content-publishing and https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media . Recheck specifications when adapting future uploads.
