// Virtual clock: the page's time only moves when the recorder calls __step(ms).
(() => {
  let vt = 0, rafQ = [], rafId = 1, tid = 1; const timers = new Map(), anims = new Map();
  const D0 = Date.now();
  const RRAF = window.requestAnimationFrame.bind(window);
  window.__present = () => new Promise(r => RRAF(() => RRAF(r)));   // a real frame, so the WebGL canvas is on screen
  performance.now = () => vt; Date.now = () => D0 + vt;
  window.requestAnimationFrame = cb => { const id = rafId++; rafQ.push([id, cb]); return id; };
  window.cancelAnimationFrame = id => { rafQ = rafQ.filter(x => x[0] !== id); };
  window.setTimeout = (cb, ms = 0, ...a) => { const id = tid++; timers.set(id, { t: vt + (+ms || 0), cb, a }); return id; };
  window.clearTimeout = id => timers.delete(id);
  const st = Element.prototype.scrollTo;
  Element.prototype.scrollTo = function (o) {
    if (o && typeof o === 'object' && o.behavior === 'smooth') {
      const el = this, from = el.scrollTop, to = o.top ?? from, t0 = vt, D = 650;
      const tick = () => { const u = Math.min(1, (vt - t0) / D), e = u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
        st.call(el, { top: from + (to - from) * e }); if (u < 1) window.requestAnimationFrame(tick); };
      window.requestAnimationFrame(tick); return;
    }
    return st.apply(this, arguments);
  };
  window.__vt = () => vt;
  window.__step = dt => {
    vt += dt;
    for (let again = true; again;) { again = false;
      for (const [id, t] of [...timers]) if (t.t <= vt) { timers.delete(id); again = true; try { typeof t.cb === 'function' && t.cb(...t.a); } catch (e) { console.error(e); } } }
    const q = rafQ; rafQ = []; for (const [, cb] of q) { try { cb(vt); } catch (e) { console.error(e); } }
    for (const a of document.getAnimations()) { if (!anims.has(a)) { anims.set(a, vt - dt); a.pause(); } a.currentTime = vt - anims.get(a); }
  };
})();
