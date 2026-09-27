#!/usr/bin/env python3
import time, math, sys

class FlowEngine:
    def __init__(self, window_sec=60.0, idle_timeout=45.0):
        self.window_sec = window_sec
        self.idle_timeout = idle_timeout
        self.keystrokes = []
        self.actions = []
        self.wpm = 0.0
        self.tier = "IDLE"
        self.intensity = 0.0
        self.sleeping = True
        self.streak_start = None

    def tap_key(self, timestamp=None):
        ts = time.time() if timestamp is None else timestamp
        self.keystrokes.append(ts)
        self.sleeping = False
        if self.streak_start is None:
            self.streak_start = ts

    def tap_action(self, timestamp=None):
        ts = time.time() if timestamp is None else timestamp
        self.actions.append(ts)
        self.sleeping = False
        if self.streak_start is None:
            self.streak_start = ts

    def step(self, now=None):
        if now is None:
            now = time.time()

        # Prune sliding window
        self.keystrokes = [t for t in self.keystrokes if now - t <= self.window_sec]
        self.actions = [t for t in self.actions if now - t <= self.window_sec]

        all_events = self.keystrokes + self.actions
        latest_event = max(all_events) if all_events else 0.0
        idle_duration = now - latest_event if latest_event > 0 else 999.0

        if idle_duration > self.idle_timeout or latest_event == 0.0:
            self.sleeping = True
            self.tier = "IDLE"
            self.streak_start = None
            self.intensity = max(0.0, self.intensity - 0.15)
            self.wpm = 0.0
            return {
                "tier": self.tier,
                "wpm": 0.0,
                "intensity": round(self.intensity, 3),
                "streak_sec": 0,
                "sleeping": True
            }

        # Calculate WPM (5 keystrokes per standard word)
        self.wpm = len(self.keystrokes) / 5.0
        score = self.wpm + (len(self.actions) * 4.0)

        if score >= 50.0:
            self.tier = "HYPERFLOW"
            target_int = 1.0
        elif score >= 25.0:
            self.tier = "FLOW"
            target_int = 0.75
        elif score >= 8.0:
            self.tier = "CRUISE"
            target_int = 0.40
        else:
            self.tier = "IDLE"
            target_int = 0.10

        self.intensity += (target_int - self.intensity) * 0.25
        streak_sec = int(now - self.streak_start) if self.streak_start else 0

        return {
            "tier": self.tier,
            "wpm": round(self.wpm, 1),
            "intensity": round(self.intensity, 3),
            "streak_sec": streak_sec,
            "sleeping": False
        }

if __name__ == "__main__":
    eng = FlowEngine()
    print("Testing FlowEngine state transitions...")
    # 1. Idle check
    res = eng.step(now=10.0)
    assert res["tier"] == "IDLE" and res["sleeping"] == True
    
    # 2. Cruise check
    for t in range(50, 90):
        eng.tap_key(timestamp=float(t))
    res = eng.step(now=90.0)
    assert res["tier"] == "CRUISE" and res["sleeping"] == False
    
    # 3. Burst Hyperflow check
    for t in range(90, 110):
        for _ in range(5):
            eng.tap_key(timestamp=float(t))
        eng.tap_action(timestamp=float(t))
    res = eng.step(now=110.0)
    assert res["tier"] == "HYPERFLOW" and res["sleeping"] == False
    
    # 4. Idle timeout check (>45s idle)
    res = eng.step(now=160.0)
    assert res["tier"] == "IDLE" and res["sleeping"] == True
    print("FlowEngine Unit Test: 100% OK")
