/* Bagas Cihuy & Hermes Agent | MIT */
class KineticStatus {
  constructor(element) {
    if (!(element instanceof HTMLElement)) throw new TypeError('HTMLElement required');
    this.element = element; this.enabled = false; this.disposed = false;
    this.animation = null; this.lastMotion = -Infinity;
    this.media = matchMedia('(prefers-reduced-motion: reduce)');
    element.setAttribute('role', 'status'); element.setAttribute('aria-live', 'polite');
    element.setAttribute('aria-atomic', 'true');
    this.guard = () => { if (this.media.matches || document.hidden) this.cancel(); };
    this.media.addEventListener('change', this.guard);
    document.addEventListener('visibilitychange', this.guard);
  }
  cancel() { if (this.animation) { this.animation.cancel(); this.animation = null; } }
  setEnabled(value) { if (this.disposed) return; this.enabled = value === true; if (!this.enabled) this.cancel(); }
  update(kind, text) {
    if (this.disposed) return false;
    if (!['idle', 'success', 'error'].includes(kind) || typeof text !== 'string') throw new TypeError('Invalid status');
    this.cancel(); this.element.textContent = text.slice(0, 2000); this.element.dataset.kind = kind;
    const now = performance.now();
    if (!this.enabled || this.media.matches || document.hidden || kind === 'idle' || typeof this.element.animate !== 'function' || now - this.lastMotion < 1500) return true;
    this.lastMotion = now;
    const transforms = kind === 'error' ? ['translateX(0)', 'translateX(-2px)', 'translateX(1px)', 'translateX(0)'] : ['translateY(3px)', 'translateY(-0.5px)', 'translateY(0)'];
    const animation = this.element.animate(transforms.map(transform => ({transform})), {duration: kind === 'error' ? 160 : 280, easing:'ease-out', iterations:1, fill:'none'});
    this.animation = animation;
    animation.onfinish = () => { if (this.animation === animation) this.animation = null; };
    return true;
  }
  dispose() { if (this.disposed) return; this.cancel(); this.disposed = true; this.media.removeEventListener('change', this.guard); document.removeEventListener('visibilitychange', this.guard); }
}
window.KineticStatus = KineticStatus;
