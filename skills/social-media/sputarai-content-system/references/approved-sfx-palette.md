# Approved SputarAI sound palette

## When to Use
Use for SputarAI visual/video sound design. The owner explicitly approved the SFX in the four `copy-sfx-v3-*-sound.mp4` previews and asked to retain them. This approves the sound palette, not publication, final copy, or every future mix.

## Canonical private assets
Root: `/home/ubuntu/hermes-backup/projects/penelitian-pola-pikir-ai/assets/audio/sputarai-approved-v1/`.
- `mixkit-1109-select-click.wav`: Select click; sequential checked steps.
- `mixkit-2577-device-click.wav`: Interface device click; cursor contact/selection/review press.
- `mixkit-2573-option-select.wav`: Interface option select; request notification/quiet approval cue.
- `palette.json`: hashes, approval context, precise gain/fade recipe, cue times and approved video paths.
- `license-source.txt`: original license terms retrieved from Mixkit.

Reuse this family rather than replacing it with arbitrary synthesized beeps. Keep sounds short, restrained and tied to visible events; leave cursor travel silent. No default background music or narration. Adjust timing to the actual new animation, not blindly copying old timestamps.

## Approved mix recipe
48 kHz stereo; trim leading silence relative to source peak at threshold 0.025 with 3 ms preroll. Peak-based gain `0.32 * 10**(cue.gain_db/20) / source_peak`; short 3 ms fade-in and 25 ms fade-out. Cue gains in approved clips range from -9 to -3 dB. Read `palette.json` for per-action choices. These are the implemented recipe, not a verified loudness/mastering target.

Encode the whole WAV to AAC 192k 48 kHz after rendering the video. Combining a frame-limited image sequence and WAV in one export previously cut the audio to 0.512 seconds; remuxing the finished video with the full WAV fixed the two-second audio stream. Preserve tail silence around the loop boundary.

## Rights and delivery
Source listing: https://mixkit.co/free-sound-effects/interface/ . License: https://mixkit.co/license/modal/sfxFree/ . Mixkit permits edited integrated social/commercial video. Do not redistribute these WAVs alone, include them in public source/template bundles, claim authorship of the recordings, or register them with a rights-management service. Keep the asset bank outside served/public folders. Check terms again if the usage changes.

User review is the approval evidence for sound preference. Do not add an unsolicited QC/listening loop when the owner has disabled it. Deliver actual MP4 attachments with audio using `MEDIA:/absolute/path`, not just a report.
