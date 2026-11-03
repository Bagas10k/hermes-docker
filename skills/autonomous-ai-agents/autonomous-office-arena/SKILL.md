---
name: autonomous-office-arena
description: Use when building multi-agent office operating environments.
version: 0.2.0
author: Bagas Cihuy & Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, office-arena, simulation, spatial-canvas, game-hud, websocket, supervisor]
---

# Autonomous Office Arena

Spatial multi-agent office simulation, virtual room routing, and tactile HUD environments for Hermes Agent fleets.

## Supporting References
- `references/office-arena-full-procedure.md`: Full 36KB unabridged step-by-step implementation procedure.
- `references/office-arena-pitfalls-catalog.md`: Full 59KB exhaustive catalog of office simulation traps and failure modes.
- `references/game-hud-and-tactile-ui.md`: 2.5D isometric viewports, sprite animation, camera pan/zoom, and pixel art assets.
- `references/contracts-and-subsystems.md`: Subsystem API boundaries, event loops, and durable state transitions.
- `references/canvas-spatial-hud-and-collision.md`: Canvas 2D collision detection, spatial hashing, and A* pathfinding.

---

## Core Mental Model: One Building = One Hermes

1. **Building Scope**: One office building maps to exactly one Hermes host profile. Rooms correspond to agent workspaces or functional departments (Engineering, Finance, Marketing, QC).
2. **Floor Plans & Rooms**: Rooms have strict capacity limits, access policies, and localized transcripts. Agents physically navigate between rooms via doors and hallways.
3. **Desk Allocation**: Each desk represents an active or standby subagent process with attached terminal, workspace, and telemetry monitors.
4. **Collision & Spatial Index**: Use 2D spatial grid hashing (`cellSize = 32px`) for collision detection and agent proximity queries.
5. **Presence & State Synchronization**: Synchronize agent coordinates and activity state over WebSockets with 20Hz tick rates and client-side dead reckoning interpolation.

---

## Executive Implementation Procedure

### 1. Spatial Grid & Layout Architecture
- Define world dimensions in tile units (`1 tile = 32px`). Build tilemaps with distinct layers: Floor, Walls, Furniture/Obstacles, Agents, and Foreground Overlays.
- Pre-bake static walls and collision geometry into a bitset array (`Uint8Array`) for O(1) collision queries during agent pathfinding.

### 2. Pathfinding & Kinematics
- Use bounded A* pathfinding with Euclidean distance heuristic and 4-way Manhattan movement (diagonal movement disabled in tight hallways to prevent wall clipping).
- Clamp agent velocities (`max_speed = 4 tiles/sec`). Interpolate positions via smooth cubic hermite splines between waypoints.

### 3. Agent Lifecycle & Task Dispatch
- Map agent states: `IDLE`, `WALKING`, `WORKING`, `CONFERRING`, `RESTING`, `BLOCKED`.
- When a task is delegated, the agent moves from its break area to the designated desk, boots the terminal container, and begins execution.
- Show live speech bubbles (`.agent-speech-bubble`) above avatars displaying truncated tool calls or active status pulses.

### 4. WebSocket Synchronization & Room Telemetry
- Transmit binary or compact JSON state packets: `[agentId, posX, posY, stateId, currentRoomId]`.
- Implement client-side dead reckoning to smooth network jitter and drop frame stuttering.
- Auto-reconnect with exponential backoff on disconnect (`1s` to `15s`).

### 5. Tactical HUD & Inspector Modals
- Click on an agent avatar to open the **Agent Inspector Panel** (profile, active model, token consumption, terminal logs, and live tool calls).
- Provide room overview metrics (CPU load, memory allocation, active worker count).

---

## Critical Pitfalls (Summary)
*(Full 59KB catalog in `references/office-arena-pitfalls-catalog.md`)*

1. **Pathfinding Obstacle Squeeze Trap**: Agents getting trapped in 1-tile door bottlenecks. Enforce 2-tile minimum doorway clearance or dynamic doorway reservation locks.
2. **Unbounded Particle / Sprite Memory Leak**: Failing to dispose offscreen Canvas textures or particle emitters. Clear inactive sprites on room transitions.
3. **WebSocket Message Flooding**: Emitting raw state on every mousemove or collision tick. Coalesce state emissions to fixed 20Hz-30Hz server ticks.
4. **Z-Index Layer Inversion**: Agents rendering behind furniture or below carpets. Sort render entities dynamically by `posY + height`.
5. **Stale Subagent Ghost Avatars**: Subagents terminating on backend without sending `destroy` packets leave permanent ghost avatars at desks. Enforce ping/heartbeat reaper.

---

## Verification Checklist

- [ ] Spatial bitset collision verified with zero wall clipping.
- [ ] A* pathfinding completes within <5ms per agent route query.
- [ ] WebSocket sync runs at stable 20Hz-30Hz with dead reckoning.
- [ ] Agent inspector displays live real-time tool logs without UI freezing.
- [ ] Memory remains stable after 1,000 spawn/destroy agent cycles.
