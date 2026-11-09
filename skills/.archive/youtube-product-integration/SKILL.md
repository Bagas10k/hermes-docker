---
name: youtube-product-integration
description: Use when building YouTube account or playback apps.
---

# YouTube product integration

1. Identify whether the user wants the actual personalized Home/YouTube Music recommendations, their subscriptions/likes/playlists, search results, or an app-specific recommender. Ask one focused question if ambiguous. Do not equate Google OAuth with access to the YouTube Home feed.
2. Check current official YouTube Data API documentation before proposing OAuth scopes. The `activities.list` `home` parameter is deprecated and does not expose authenticated personal Home recommendations; state this before suggesting login.
3. For exact personal recommendations, direct users to YouTube/YouTube Music. For an approximation, request minimal read-only OAuth scopes, fetch documented accessible user signals, rank locally, and label the result as the app's recommendations rather than YouTube's.
4. For playback, use the visible official IFrame Player API and verify current developer policies. Do not isolate/download audio or hide the player for background playback. OAuth grants neither audio analysis nor Premium; use owned/licensed audio for reactive visuals.
5. Answer in Indonesian with capability boundaries and smallest next step. Cite official docs for limitations.

Recheck: https://developers.google.com/youtube/v3/docs/activities/list ; https://developers.google.com/youtube/v3/docs ; https://developers.google.com/youtube/iframe_api_reference ; https://developers.google.com/youtube/terms/developer-policies
