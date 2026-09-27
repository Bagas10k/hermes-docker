# Theory Motion Pipeline & Visual Archetypes

Guide for translating spoken explanations of scientific, computational, and economic theories into structured Remotion motion graphics.

## The 8 Procedural Physical Archetypes

Every educational theory video maps each narrative beat into one of 8 procedural SVG physical archetypes:

### 1. `split_comparison`
- **Role:** Contrast two conflicting conditions (Paku vs Kapal, Serial vs Paralel).
- **Props:** `leftEntity: { label, value, status }`, `rightEntity: { label, value, status }`.

### 2. `cross_section`
- **Role:** Internal cutaway revealing internal chambers or densities (e.g. 90% air hull chamber).
- **Props:** `leftEntity: { label, value }` (outer hull/wall), `rightEntity: { label, value }` (internal volume/density).

### 3. `fluid_displacement`
- **Role:** Physical displacement of liquids/gases and resulting buoyant forces.
- **Props:** Main tank fluid level rise, sideways displacement arrows, and lateral graduated cylinder volume surge.

### 4. `force_vectors`
- **Role:** Vector arrows representing Newton action-reaction or equilibrium forces.
- **Props:** `leftEntity: { label, value }` (downward action vector), `rightEntity: { label, value }` (upward reaction vector), `formula`.

### 5. `bottleneck_flow`
- **Role:** Fluid or processing capacity narrowing (Amdahl bottleneck, traffic flow).
- **Props:** Wide parallel input pipe constricting to narrow serial bottleneck.

### 6. `molecular_chaos`
- **Role:** Thermodynamics, state changes, or entropy increase (Brownian motion).
- **Props:** 25-particle ordered lattice disintegrating into stochastic chaos as disorder increases.

### 7. `balance_scale`
- **Role:** Seesaw fulcrum scale comparing mass, density, or cost vs benefit.
- **Props:** Dynamic tilt angle proportional to left vs right weight.

### 8. `takeaway_summary`
- **Role:** Outro summary reinforcement.
- **Props:** 3 checklist items `[✓]`, law formula stamp, and bookmark CTA.

---

## Dynamic Remotion Props Injection

Instead of compiling new TSX code per video, use a parametric master composition (`<TheoryMotionComposition />`) that reads dynamic props:

```bash
# Render directly from a choreograph plan file
npx remotion render TheoryMotion output/video.mp4 \
  --props=/path/to/choreography_plan.json \
  --concurrency=4 \
  --gl=angle
```

### JSON Props Structure

```json
{
  "title": "Hukum Archimedes & Gaya Apung",
  "audioUrl": "theory_audio.mp3",
  "fps": 30,
  "durationInFrames": 490,
  "scenes": [
    {
      "id": "scene_hook",
      "archetype": "hook",
      "startFrame": 0,
      "durationInFrames": 110,
      "data": {
        "tag": "MEKANIKA FLUIDA",
        "headline": "Kenapa Kapal Besi Mengapung di Laut?",
        "highlightedPhrase": "Gaya Angkat ke Atas",
        "subtitle": "Hukum Archimedes menjelaskan rahasia gaya apung fluida.",
        "stampText": "ARCHIMEDES"
      }
    }
  ]
}
```

---

## Precision STT with faster-whisper

Use CPU-optimized `int8` faster-whisper to extract exact word timings without GPU dependencies:

```python
from faster_whisper import WhisperModel

model = WhisperModel("tiny", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio_path, language="id", word_timestamps=True)

words = []
for segment in segments:
    for w in segment.words:
        words.append({
            "word": w.word.strip(),
            "start": round(w.start, 2),
            "end": round(w.end, 2)
        })
```

Frame mapping formula:
`frame = Math.round(second * 30)`
Ensure adjacent scenes have contiguous frame boundaries:
`scene[i + 1].startFrame = scene[i].startFrame + scene[i].durationInFrames`
