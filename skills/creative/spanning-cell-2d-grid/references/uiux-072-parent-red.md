# Parent acceptance review — UIUX-072
Author: Bagas Cihuy & Hermes Agent.
Before parent repairs, executable mutations of worker evidence are accepted despite (1) the active target rectangle moved fully offscreen and (2) the opt-out comparison removed. Worker audit only checks positive rect extents, not clipping/occlusion. Its “virtual advance” immediately invokes the captured callback without advancing any clock. Parent has not accepted worker completion.

Predictions before corrective tests:
- Shared rectangle containment plus known-overlay intersection will reject offscreen/clipped/covered target, including pointer-events:none overlay.
- Recording app timer registration, controlling its deadline, and allowing the native callback to run at its deadline will verify real reset execution rather than merely a boolean.
- An old-layout/none comparison will have stable scroll offsets but moved viewport geometry; stable-layout/auto should preserve both at settlement and reset. Compare identical matrix coordinates.
- Bounding status track geometry measured separately from scroll offsets will reveal any masked reflow. No CLS score or all-browser claim follows.
- Retain all 36 coordinates, 8 phase checkpoints, native key events and prior trace rejection. New native geometry controls use the same extractor/gate as positives.
