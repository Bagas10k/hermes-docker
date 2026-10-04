"""Deterministic lifecycle oracle, not a DOM observer implementation."""
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class ViewportLifecycle:
    disposed: bool = False
    connected: bool = True
    active: bool = False
    observer_connected: bool = True
    listeners: Dict[Tuple[str, str], int] = field(default_factory=dict)
    pending_raf: int = 0
    in_callback: bool = False

    def start(self):
        self.active = not self.disposed and self.connected
        if self.active:
            self.pending_raf = 1
        return self.active

    def resize(self):
        return self.observer_connected and self.connected and not self.disposed

    def detach(self):
        self.connected = False
        self.active = False
        self.pending_raf = 0

    def reconnect(self):
        self.connected = True

    def attach_listener(self, target: str, event: str):
        if self.disposed:
            return False
        key = (target, event)
        self.listeners[key] = self.listeners.get(key, 0) + 1
        return True

    def remove_listener(self, target: str, event: str):
        key = (target, event)
        if key in self.listeners:
            if self.listeners[key] <= 1:
                del self.listeners[key]
            else:
                self.listeners[key] -= 1
            return True
        return False

    def listener_count(self) -> int:
        return sum(self.listeners.values())

    def trigger_callback_and_dispose(self):
        """Simulate reentrant disposal triggered synchronously from inside selection callback."""
        if not self.active or self.disposed:
            return False
        self.in_callback = True
        try:
            self.dispose()
        finally:
            self.in_callback = False
        return True

    def dispose(self):
        self.disposed = True
        self.active = False
        self.observer_connected = False
        self.pending_raf = 0
        self.listeners.clear()
