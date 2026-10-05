/* Pedestal drawings for Dikilitaş (obelisk-390). Generated from work/*.js; see the comments in each section. */
window.RPANELS = window.RPANELS || {};
/* Relief line drawings for the pedestal of the Obelisk of Theodosius.
   Every figure is placed from measurements on Francesco Bini's photographs (Wikimedia Commons, CC BY-SA 4.0):
   head position, head size, turn of the head, hair, garment and gesture are recorded per figure.
   Coordinates are percentages of the panel (x of width, y of height); radii are percentages of the width. */
(function(){
const RINK = '#3b332d', RFILL = '#efe9dd', RBG = '#dcd4c5', HAIR = '#e2d8c6', SHADE = '#d3cab9', GRANITE = '#d6a48f', MARBLE = '#e4ddcf';
const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
let x, CW, CH, LWS = 1;
const X = p => p / 100 * CW, Y = p => p / 100 * CH, R = p => p / 100 * CW;
const lw = v => { x.lineWidth = v * LWS; };
function P(fn, fill){ x.beginPath(); fn(); if (fill !== false){ if (fill) { x.save(); x.fillStyle = fill; x.fill(); x.restore(); } else x.fill(); } x.stroke(); }
function L(pts){ x.beginPath(); x.moveTo(pts[0], pts[1]); for (let i = 2; i < pts.length; i += 2) x.lineTo(pts[i], pts[i + 1]); x.stroke(); }
function Q(a, b, c, d, e, f){ x.beginPath(); x.moveTo(a, b); x.quadraticCurveTo(c, d, e, f); x.stroke(); }
const sgn = v => v < 0 ? -1 : 1;

/* ---------- heads ---------- */
// t: turn of the head, -1 = facing the viewer's left, 1 = facing right. hair: cap | long | diadem | curly | bare | helmet
function head(cx, cy, r, t = 0, hair = 'cap', o = {}){
  const fx = cx + t * r * .42, hx = cx - t * r * .1;
  // face
  P(() => x.ellipse(cx, cy + r * .06, r * .86, r * 1.04, 0, 0, 6.283));
  // ear on the side turned away from
  if (Math.abs(t) > .25 && hair !== 'long'){ const s = -sgn(t); P(() => x.ellipse(cx + s * r * .82, cy + r * .12, r * .16, r * .26, 0, 0, 6.283)); }
  // hair
  x.save(); x.fillStyle = HAIR;
  if (hair === 'cap' || hair === 'diadem' || hair === 'helmet'){
    const fr = cy - r * (hair === 'helmet' ? .2 : .34);
    P(() => { x.moveTo(hx - r * .9, cy + r * .12); x.bezierCurveTo(hx - r * 1.02, cy - r * 1.32, hx + r * 1.02, cy - r * 1.32, hx + r * .9, cy + r * .12);
      x.lineTo(hx + r * .8, cy + r * .1); x.quadraticCurveTo(hx + r * .8, fr, hx + r * .55, fr + r * .02); x.quadraticCurveTo(hx, fr - r * .1, hx - r * .55, fr + r * .02); x.quadraticCurveTo(hx - r * .8, fr, hx - r * .8, cy + r * .1); x.closePath(); });
    if (hair === 'cap'){ lw(1.2); Q(hx - r * .62, fr - r * .12, hx - t * r * .2, fr - r * .5, hx + r * .5, fr - r * .62); Q(hx - r * .3, fr - r * .08, hx + r * .2, fr - r * .3, hx + r * .66, fr - r * .2); lw(2.4); }
    if (hair === 'diadem'){ lw(1.6); Q(hx - r * .86, fr - r * .12, hx, fr - r * .3, hx + r * .86, fr - r * .12); Q(hx - r * .86, fr - r * .3, hx, fr - r * .48, hx + r * .86, fr - r * .3);
      for (let k = -3; k <= 3; k++){ const a = hx + k * r * .24; P(() => x.arc(a, fr - r * .22 - (3 - Math.abs(k)) * r * .03, r * .07, 0, 6.283), RFILL); } lw(2.4); }
    if (hair === 'helmet'){ P(() => x.rect(hx - r * .25, cy - r * 1.35, r * .5, r * .22)); }
  } else if (hair === 'long'){
    P(() => { x.moveTo(hx - r * .98, cy + r * .78); x.bezierCurveTo(hx - r * 1.12, cy - r * 1.4, hx + r * 1.12, cy - r * 1.4, hx + r * .98, cy + r * .78);
      x.lineTo(hx + r * .7, cy + r * .76); x.quadraticCurveTo(hx + r * .78, cy - r * .3, hx + r * .5, cy - r * .36); x.lineTo(hx - r * .5, cy - r * .36);
      x.quadraticCurveTo(hx - r * .78, cy - r * .3, hx - r * .7, cy + r * .76); x.closePath(); });
    lw(1.2); [-.6, -.2, .2, .6].forEach(k => L([hx + k * r, cy - r * .4, hx + k * r * 1.05, cy - r * .68])); lw(2.4);
  } else if (hair === 'curly'){
    P(() => { const n = 9; x.moveTo(hx - r * .9, cy + r * .1);
      for (let k = 0; k <= n; k++){ const a = Math.PI * (1.05 + k / n * .9), b = Math.PI * (1.05 + (k + .5) / n * .9);
        x.quadraticCurveTo(hx + Math.cos(b) * r * 1.18, cy - r * .05 + Math.sin(b) * r * 1.22, hx + Math.cos(a) * r * .98, cy - r * .05 + Math.sin(a) * r * 1.05); }
      x.lineTo(hx + r * .78, cy - r * .2); x.quadraticCurveTo(hx, cy - r * .5, hx - r * .78, cy - r * .2); x.closePath(); });
  }
  x.restore();
  if (o.beard){ x.save(); x.fillStyle = HAIR; P(() => { x.moveTo(cx - r * .8, cy + r * .2); x.quadraticCurveTo(cx - r * .7, cy + r * 1.25, fx, cy + r * 1.3); x.quadraticCurveTo(cx + r * .7, cy + r * 1.25, cx + r * .8, cy + r * .2);
      x.quadraticCurveTo(fx + r * .3, cy + r * .75, fx, cy + r * .72); x.quadraticCurveTo(fx - r * .3, cy + r * .75, cx - r * .8, cy + r * .2); x.closePath(); }); x.restore(); }
  // features, drawn finer
  if (r > 7 && Math.abs(t) > .6){                 // profile: one eye, the nose breaks the contour
    const s = sgn(t), ex = cx + s * r * .45;
    lw(1.3); L([ex - r * .1, cy - r * .04, ex + r * .12, cy - r * .04]);
    if (!o.beard) L([cx + s * r * .45, cy + r * .6, cx + s * r * .7, cy + r * .6]);
    lw(2.4); P(() => { x.moveTo(cx + s * r * .8, cy - r * .1); x.lineTo(cx + s * r * 1.02, cy + r * .3); x.lineTo(cx + s * r * .78, cy + r * .36); x.closePath(); });
  } else if (r > 7){
    lw(1.3);
    const e = r * .3, ey = cy - r * .04, k1 = 1 - Math.max(0, t) * .55, k2 = 1 + Math.min(0, t) * .55;
    L([fx - e - r * .12 * k2, ey, fx - e + r * .1 * k2, ey]); L([fx + e - r * .1 * k1, ey, fx + e + r * .12 * k1, ey]);
    L([fx + t * r * .04, ey + r * .05, fx + t * r * .2, cy + r * .38, fx - t * r * .02, cy + r * .42]);
    if (!o.beard) L([fx - r * .15, cy + r * .62, fx + r * .15, cy + r * .62]);
    lw(2.4);
  }
}

/* ---------- bodies ---------- */
// cx: centre, ys: shoulder line (px), sw: half shoulder width (px), yb: bottom (px)
function shoulders(cx, ys, sw, yb, r, flare = 1.06, tilt = 0){
  P(() => { x.moveTo(cx - sw * flare, yb); x.lineTo(cx - sw, ys + r * .95 - tilt); x.bezierCurveTo(cx - sw * .98, ys + r * .25 - tilt, cx - sw * .7, ys - r * .05 - tilt, cx - r * .4, ys - r * .32);
    x.lineTo(cx + r * .4, ys - r * .32); x.bezierCurveTo(cx + sw * .7, ys - r * .05 + tilt, cx + sw * .98, ys + r * .25 + tilt, cx + sw, ys + r * .95 + tilt); x.lineTo(cx + sw * flare, yb); x.closePath(); });
}
function neck(cx, cy, r){ P(() => x.rect(cx - r * .34, cy + r * .6, r * .68, r * .8)); }
function drape(kind, cx, ys, sw, yb, r, o){
  const len = yb - ys;
  lw(1.6);
  if (kind === 'chlamys'){            // cloak pinned on the wearer's right shoulder
    const s = o.pin || -1, fxp = cx + s * sw * .62, fyp = ys + r * .45;
    Q(fxp, fyp, cx - s * sw * .1, ys + len * .32, cx - s * sw * .96, ys + len * Math.min(.62, r * 6 / len));
    L([fxp - s * r * .05, fyp + r * .3, fxp + s * sw * .06, yb]);
    if (len > r * 3){ L([cx - s * sw * .25, ys + len * .5, cx - s * sw * .3, yb]); L([cx + s * sw * .05, ys + len * .55, cx + s * sw * .02, yb]); }
    if (o.tablion) P(() => x.rect(cx - s * sw * .05 - sw * .3, ys + len * .2, sw * .3 * 1, len * .16), SHADE);
    lw(2.4); P(() => x.arc(fxp, fyp, r * .17, 0, 6.283));
  } else if (kind === 'pallium'){    // wrapped mantle: a curved swag across the chest
    const s = o.pin || 1;
    Q(cx - s * sw * .85, ys + r * .5, cx - s * sw * .05, ys + Math.min(len * .55, r * 2.6), cx + s * sw * .92, ys + Math.min(len * .35, r * 1.5));
    if (len > r * 2.2) Q(cx - s * sw * .6, ys + Math.min(len * .45, r * 2.3), cx + s * sw * .1, ys + Math.min(len * .8, r * 3.6), cx + s * sw * .88, ys + Math.min(len * .6, r * 2.8));
    if (len > r * 4){ L([cx - sw * .2, ys + len * .6, cx - sw * .24, yb]); L([cx + sw * .28, ys + len * .55, cx + sw * .3, yb]); }
    lw(2.4);
  } else if (kind === 'tunic'){
    L([cx - sw * .55, ys + len * .42, cx + sw * .55, ys + len * .42]);
    for (let k = -2; k <= 2; k++) L([cx + k * sw * .25, ys + len * .46, cx + k * sw * .3, yb - r * .1]);
    lw(2.4);
  } else lw(2.4);
}
function limb(ax, ay, bx, by, w){
  const dx = bx - ax, dy = by - ay, l = Math.hypot(dx, dy) || 1, nx = -dy / l * w / 2, ny = dx / l * w / 2, a = Math.atan2(dy, dx);
  P(() => { x.moveTo(ax + nx, ay + ny); x.lineTo(bx + nx, by + ny); x.arc(bx, by, w / 2, a + Math.PI / 2, a - Math.PI / 2, true); x.lineTo(ax - nx, ay - ny); x.arc(ax, ay, w / 2, a - Math.PI / 2, a + Math.PI / 2, true); x.closePath(); });
}
const hand = (hx, hy, r) => P(() => x.ellipse(hx, hy, r * .32, r * .3, 0, 0, 6.283));
function arms(list, cx, ys, sw, yb, r){
  const len = yb - ys, w = r * .62;
  for (const a of list || []){
    if (a === 'chest' || a === 'chestL'){            // forearm across the chest, hand near the middle
      const s = a === 'chest' ? 1 : -1, y = ys + Math.min(len * .45, r * 2.3);
      limb(cx - s * sw * .8, y + r * .25, cx + s * sw * .12, y, w); hand(cx + s * sw * .18, y - r * .05, r);
    } else if (a === 'clasp'){                       // both forearms meeting, hands together
      const y = ys + Math.min(len * .45, r * 2.3);
      limb(cx - sw * .82, y + r * .3, cx - r * .25, y, w); limb(cx + sw * .82, y + r * .3, cx + r * .25, y, w);
      P(() => x.ellipse(cx, y - r * .02, r * .5, r * .34, 0, 0, 6.283));
    } else if (a.raise || a.hold){                   // { raise | hold: [x%, y%], side }
      const p = a.raise || a.hold, hx = X(p[0]), hy = Y(p[1]), sx = cx + a.side * sw * .82, sy = ys + r * .45;
      const ex = a.raise ? (sx + hx) / 2 + a.side * r * .9 : cx + a.side * sw * 1.02, ey = a.raise ? (sy + hy) / 2 + r * .4 : Math.min(hy + r * .2, sy + r * 2.6);
      limb(sx, sy, ex, ey, w * 1.05); limb(ex, ey, hx, hy, w); hand(hx, hy, r);
    }
  }
}
// bust or standing figure. f = { x, y, r, t, hair, sw (half shoulder width, % of W), b (bottom, % of H), g (garment), arms, feet, beard }
function figure(f){
  const cx = X(f.x), cy = Y(f.y), r = R(f.r) * 1.14, sw = f.sw != null ? R(f.sw) : r * 1.85, yb = Y(f.b);
  const ys = cy + r * 1.45;
  if (f.spear) spear(f.spear[0], f.spear[1], f.spear[2]);
  if (f.feet){ const fy = Y(f.feet); lw(2.4); P(() => x.rect(cx - sw * .55, yb - 2, sw * .4, fy - yb)); P(() => x.rect(cx + sw * .15, yb - 2, sw * .4, fy - yb));
    P(() => x.ellipse(cx - sw * .38, fy, sw * .3, r * .2, 0, 0, 6.283)); P(() => x.ellipse(cx + sw * .38, fy, sw * .3, r * .2, 0, 0, 6.283)); }
  neck(cx, cy, r);
  shoulders(cx, ys, sw, yb, r, f.flare || (f.feet ? 1.1 : 1.03), f.tilt ? R(f.tilt) : 0);
  drape(f.g || 'pallium', cx, ys, sw, yb, r, f);
  arms(f.arms, cx, ys, sw, yb, r);
  head(cx, cy, r, f.t || 0, f.hair || 'cap', f);
}
// seated figure: torso to the lap (lap, % H), lower legs to the feet (feet, % H)
function seatedFig(f){
  const cx = X(f.x), cy = Y(f.y), r = R(f.r) * 1.14, sw = R(f.sw), lap = Y(f.lap), fy = Y(f.feet), ys = cy + r * 1.45;
  const kw = sw * (f.knees || 1.08);
  P(() => { x.moveTo(cx - kw * .86, lap); x.lineTo(cx - kw * .8, fy); x.lineTo(cx + kw * .8, fy); x.lineTo(cx + kw * .86, lap); x.closePath(); });
  lw(1.6); L([cx, lap + r * .4, cx, fy]); [-.5, .45].forEach(k => L([cx + k * kw, lap + r * .6, cx + k * kw * 1.04, fy])); lw(2.4);
  P(() => x.ellipse(cx - kw * .42, fy, kw * .3, r * .2, 0, 0, 6.283)); P(() => x.ellipse(cx + kw * .42, fy, kw * .3, r * .2, 0, 0, 6.283));
  neck(cx, cy, r);
  shoulders(cx, ys, sw, lap, r, 1.02);
  P(() => x.roundRect(cx - kw, lap - r * .55, kw * 2, r * 1.1, r * .5));           // thighs and knees, seen from the front
  lw(1.6); Q(cx - kw * .9, lap - r * .2, cx, lap + r * .45, cx + kw * .9, lap - r * .2); lw(2.4);
  drape(f.g || 'chlamys', cx, ys, sw, lap - r * .55, r, f);
  arms(f.arms, cx, ys, sw, lap, r);
  head(cx, cy, r, f.t || 0, f.hair || 'cap', f);
}
function spear(sx, top, bot){
  const a = X(sx), t = Y(top), b = Y(bot);
  lw(2); L([a, b, a, t + 14]); lw(2.4);
  P(() => { x.moveTo(a, t); x.quadraticCurveTo(a + 7, t + 9, a, t + 18); x.quadraticCurveTo(a - 7, t + 9, a, t); });
}
function shield(cx, cy, rx, ry){
  const a = X(cx), b = Y(cy), u = R(rx), v = Y(ry);
  P(() => x.ellipse(a, b, u, v, 0, 0, 6.283)); lw(1.6); x.beginPath(); x.ellipse(a, b, u * .84, v * .87, 0, 0, 6.283); x.stroke(); lw(2.4);
  P(() => x.arc(a, b, u * .2, 0, 6.283));
}
function column(cx, y0, y1, w = 1.4){
  const a = X(cx), t = Y(y0), b = Y(y1), hw = R(w) / 2;
  P(() => x.rect(a - hw, t + R(1.5), hw * 2, b - t - R(2.4)));
  P(() => { x.moveTo(a - hw * 1.9, t); x.lineTo(a + hw * 1.9, t); x.lineTo(a + hw * 1.1, t + R(1.5)); x.lineTo(a - hw * 1.1, t + R(1.5)); x.closePath(); });
  lw(1.4); [.35, .7, 1.05].forEach(k => L([a - hw * 1.9 + hw * k, t + 3, a - hw * 1.1 + hw * .4 * k, t + R(1.5) - 3])); lw(2.4);
  P(() => x.rect(a - hw * 1.6, b - R(.9), hw * 3.2, R(.9)));
}
// lattice screen. style: 'cross' (diagonal grid) | 'x' (one saltire per bay) | 'scale' (fish-scale)
function lattice(x0, y0, x1, y1, posts, style = 'cross', step = 2.6){
  const styles = Array.isArray(style) ? style : null;
  const a = X(x0), t = Y(y0), b = X(x1), u = Y(y1);
  x.save(); P(() => x.rect(a, t, b - a, u - t), RFILL);
  const ps = [x0, ...(posts || []), x1];
  for (let i = 0; i < ps.length - 1; i++){
    const p = X(ps[i]) + (i ? R(.5) : 4), q = X(ps[i + 1]) - (i < ps.length - 2 ? R(.5) : 4), it = t + 5, iu = u - 5;
    lw(1.6); x.strokeRect(p, it, q - p, iu - it);
    x.save(); x.beginPath(); x.rect(p, it, q - p, iu - it); x.clip(); x.beginPath();
    const st = styles ? styles[i] : style;
    if (st === 'plain'){}
    else if (st === 'x'){ x.moveTo(p, it); x.lineTo(q, iu); x.moveTo(q, it); x.lineTo(p, iu); }
    else if (st === 'scale'){ const s = R(step); let row = 0; for (let yy = it; yy < iu + s; yy += s * .55, row++) for (let xx = p - s; xx < q + s; xx += s){ const ox = xx + (row % 2) * s * .5; x.moveTo(ox + s / 2, yy); x.arc(ox, yy, s / 2, 0, Math.PI); } }
    else if (st === 'bars'){ const s = R(step) * .6; for (let k = p + s / 2; k < q; k += s){ x.moveTo(k, it); x.lineTo(k, iu); } }
    else { const s = R(step), h = iu - it; for (let k = p - h; k < q + h; k += s){ x.moveTo(k, it); x.lineTo(k + h, iu); x.moveTo(k, iu); x.lineTo(k + h, it); } }
    x.stroke(); x.restore(); lw(2.4);
  }
  for (const pp of posts || []) P(() => x.rect(X(pp) - R(.5), t, R(1), u - t));
  x.restore();
}
function hline(x0, y, x1){ L([X(x0), Y(y), X(x1), Y(y)]); }
function band(x0, y0, x1, y1, fill = RFILL){ P(() => x.rect(X(x0), Y(y0), X(x1) - X(x0), Y(y1) - Y(y0)), fill); }
function archway(cx, base, rOut, rIn, top){
  const a = X(cx), b = Y(base), ro = R(rOut), ri = R(rIn), cy = Y(top) + ro;
  P(() => { x.moveTo(a - ro, b); x.lineTo(a - ro, cy); x.arc(a, cy, ro, Math.PI, 0); x.lineTo(a + ro, b); x.lineTo(a + ri, b); x.lineTo(a + ri, cy); x.arc(a, cy, ri, 0, Math.PI, true); x.lineTo(a - ri, b); x.closePath(); });
  P(() => { x.moveTo(a - ri, b); x.lineTo(a - ri, cy); x.arc(a, cy, ri, Math.PI, 0); x.lineTo(a + ri, b); }, SHADE);
}
function steps(x0, x1, ys){ ys.forEach(([t, u]) => P(() => x.rect(X(x0), Y(t), X(x1) - X(x0), Y(u) - Y(t)), RFILL)); }

// small dancer or musician in a short belted tunic. f = { x, y (head), r, feet, arms: [[hx%, hy%], [hx%, hy%]] (left, right hands), t }
function dancer(f){
  const cx = X(f.x), cy = Y(f.y), r = R(f.r) * 1.14, fy = Y(f.feet), ys = cy + r * 1.4, sw = r * 1.45, hip = ys + (fy - ys) * .36, hem = ys + (fy - ys) * .66;
  lw(2.4);
  const kx = f.step || 0;
  limb(cx - sw * .38, hem - r * .2, cx - sw * .5 - R(kx), fy - r * .2, r * .62); limb(cx + sw * .38, hem - r * .2, cx + sw * .5 + R(kx), fy - r * .2, r * .62);
  P(() => x.ellipse(cx - sw * .5 - R(kx) - r * .2, fy - r * .1, r * .4, r * .2, 0, 0, 6.283)); P(() => x.ellipse(cx + sw * .5 + R(kx) + r * .2, fy - r * .1, r * .4, r * .2, 0, 0, 6.283));
  (f.arms || []).forEach(([hx, hy], i) => { const s = i ? 1 : -1, sx = cx + s * sw * .75, sy = ys + r * .35, H = X(hx), V = Y(hy), ex = (sx + H) / 2 + s * r * .5, ey = (sy + V) / 2 + r * .35;
    limb(sx, sy, ex, ey, r * .55); limb(ex, ey, H, V, r * .5); P(() => x.arc(H, V, r * .26, 0, 6.283)); });
  neck(cx, cy, r);
  P(() => { x.moveTo(cx - sw * .62, hip); x.lineTo(cx - sw * .78, hem); x.lineTo(cx + sw * .78, hem); x.lineTo(cx + sw * .62, hip); x.closePath(); });
  shoulders(cx, ys, sw * .72, hip + 2, r, .9);
  lw(1.6); L([cx - sw * .62, hip, cx + sw * .62, hip]); [-.35, 0, .35].forEach(k => L([cx + k * sw, hip + r * .3, cx + k * sw * 1.15, hem - 2])); lw(2.4);
  head(cx, cy, r, f.t || 0, f.hair || 'cap');
}
// draw several shapes as one silhouette: outline everything thickly, then fill, so only the outer contour stays inked
function silhouette(parts){
  x.save(); x.lineWidth = 4.8 * LWS; parts.forEach(f => { x.beginPath(); f(); x.stroke(); }); x.restore();
  parts.forEach(f => { x.beginPath(); f(); x.fill(); });
}
const capsule = (ax, ay, bx, by, w0, w1 = w0) => () => {
  const dx = bx - ax, dy = by - ay, l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l, a = Math.atan2(dy, dx);
  x.moveTo(ax + nx * w0 / 2, ay + ny * w0 / 2); x.lineTo(bx + nx * w1 / 2, by + ny * w1 / 2); x.arc(bx, by, w1 / 2, a + Math.PI / 2, a - Math.PI / 2, true);
  x.lineTo(ax - nx * w0 / 2, ay - ny * w0 / 2); x.arc(ax, ay, w0 / 2, a - Math.PI / 2, a + Math.PI / 2, true); x.closePath();
};
// kneeling barbarian bringing gifts, in profile. k = { h: [x, y], r, d (1 faces right), hair, beard, sh, hip, kf, ff, kb, fb, hand, bowl: [cx, cy, w] }
function kneeler(k){
  const p = a => [X(a[0]), Y(a[1])], r = R(k.r) * 1.14, d = k.d, [hx, hy] = p(k.h);
  const [sx, sy] = p(k.sh), [ix, iy] = p(k.hip), [kfx, kfy0] = p(k.kf), [ffx, ffy] = p(k.ff), [kbx, kby] = p(k.kb), [fbx, fby] = p(k.fb), [ax, ay] = p(k.hand);
  const kfy = kfy0 - r * .9, th = r * 1.2, sh = r * .82, kbY = kby - sh * .5, fbY = fby - sh * .4, ffY = ffy - sh * .45;
  lw(2.4);
  // torso leaning toward the emperor; cloak hanging from the back
  const torso = () => { const ux = sx - ix, uy = sy - iy, l = Math.hypot(ux, uy), nx = -uy / l, ny = ux / l, w0 = r * 1.45, w1 = r * 1.05;
    x.moveTo(ix + nx * w0, iy + ny * w0); x.quadraticCurveTo((ix + sx) / 2 + nx * w0 * 1.1, (iy + sy) / 2 + ny * w0 * 1.1, sx + nx * w1, sy + ny * w1);
    x.quadraticCurveTo(sx + ux / l * r * .9, sy + uy / l * r * .9, sx - nx * w1, sy - ny * w1); x.quadraticCurveTo((ix + sx) / 2 - nx * w0 * .9, (iy + sy) / 2 - ny * w0 * .9, ix - nx * w0, iy - ny * w0); x.closePath(); };
  silhouette([capsule(ix, iy, kbx, kbY, th, sh), capsule(kbx, kbY, fbx, fbY, sh, sh * .7), torso,
              capsule(ix + d * r * .3, iy - r * .3, kfx, kfy, th * 1.05, sh * 1.05), capsule(kfx, kfy, ffx, ffY, sh, sh * .85),
              () => x.ellipse(ffx + d * r * .4, ffy - r * .2, r * .62, r * .22, 0, 0, 6.283)]);
  // tunic hem across the thigh, belt
  lw(1.6);
  { const ux = sx - ix, uy = sy - iy, l = Math.hypot(ux, uy), nx = -uy / l, ny = ux / l, bx = ix + ux * .3, by = iy + uy * .3; L([bx + nx * r * 1.4, by + ny * r * 1.4, bx - nx * r * 1.25, by - ny * r * 1.25]); }
  { const hx2 = ix + (kfx - ix) * .45, hy2 = iy + (kfy - iy) * .45; x.beginPath(); x.moveTo(hx2 - th * .55, hy2 - th * .3); x.quadraticCurveTo(hx2, hy2 + th * .4, hx2 + th * .55, hy2 - th * .2); x.stroke(); }
  lw(2.4);
  if (k.bowl){ const [bx, by] = p(k.bowl), bw = R(k.bowl[2]) / 2;
    P(() => { x.moveTo(bx - bw, by - bw * .25); x.lineTo(bx + bw, by - bw * .25); x.quadraticCurveTo(bx + bw * .9, by + bw * .55, bx, by + bw * .55); x.quadraticCurveTo(bx - bw * .9, by + bw * .55, bx - bw, by - bw * .25); x.closePath(); });
    x.beginPath(); x.ellipse(bx, by - bw * .25, bw, bw * .16, 0, 0, 6.283); x.stroke(); }
  const ex = (sx + ax) / 2 - d * r * .1, ey = Math.max(sy, ay) + r * .9;
  silhouette([capsule(sx, sy + r * .3, ex, ey, r * .78, r * .66), capsule(ex, ey, ax, ay, r * .66, r * .56), () => x.ellipse(ax, ay, r * .36, r * .3, 0, 0, 6.283)]);
  neck(hx, hy, r);
  head(hx, hy, r, k.t != null ? k.t : d * .75, k.hair || 'curly', { beard: k.beard });
}
function pike(x0, y0, x1, y1){
  const a = X(x0), b = Y(y0), c = X(x1), d = Y(y1), l = Math.hypot(c - a, d - b), ux = (c - a) / l, uy = (d - b) / l;
  lw(2); L([a, b, c - ux * 14, d - uy * 14]); lw(2.4);
  P(() => { x.moveTo(c, d); x.lineTo(c - ux * 18 - uy * 6, d - uy * 18 + ux * 6); x.lineTo(c - ux * 14, d - uy * 14); x.lineTo(c - ux * 18 + uy * 6, d - uy * 18 - ux * 6); x.closePath(); });
}
// a row of arches on a cornice: list of [cx, r]; top of the arches at y0, springing at y1, cornice y1..y2
function arcade(list, x0, x1, y0, y1, y2){
  band(x0, y1, x1, y2, RFILL);
  for (const [cx, rr] of list){ const a = X(cx), w = R(rr), sy = Y(y1);
    x.save(); x.fillStyle = SHADE; x.beginPath(); x.moveTo(a - w, sy); x.lineTo(a - w, Y(y0) + w); x.arc(a, Y(y0) + w, w, Math.PI, 0); x.lineTo(a + w, sy); x.fill(); x.restore();
    lw(2.4); x.beginPath(); x.moveTo(a - w, sy); x.lineTo(a - w, Y(y0) + w); x.arc(a, Y(y0) + w, w, Math.PI, 0); x.lineTo(a + w, sy); x.stroke();
    lw(1.6); x.beginPath(); x.moveTo(a - w * .82, sy); x.lineTo(a - w * .82, Y(y0) + w); x.arc(a, Y(y0) + w, w * .82, Math.PI, 0); x.lineTo(a + w * .82, sy); x.stroke(); lw(2.4); }
}
// water organ: pipes rising in steps over a box on a stand
function organ(x0, x1, y0, y1){
  const a = X(x0), b = X(x1), t = Y(y0), u = Y(y1), w = b - a, n = 9;
  P(() => x.rect(a + w * .2, t + (u - t) * .62, w * .6, (u - t) * .38));
  P(() => x.rect(a, t + (u - t) * .5, w, (u - t) * .14));
  for (let k = 0; k < n; k++){ const px = a + w * (.06 + k * .88 / n), ph = (u - t) * (.5 - Math.abs(k - (n - 1) / 2) * .035); P(() => x.rect(px, t + (u - t) * .5 - ph, w * .8 / n, ph)); }
}
function canvasFor(W, H, draw, bg = RBG){
  const c = mk(W, H); x = c.getContext('2d'); CW = W; CH = H; LWS = W / 1148;
  x.fillStyle = bg; x.fillRect(0, 0, W, H);
  x.lineJoin = 'round'; x.lineCap = 'round'; x.strokeStyle = RINK; x.fillStyle = RFILL; lw(2.4);
  draw();
  lw(4); x.strokeRect(2, 2, W - 4, H - 4);
  return c;
}
window.RLIB = { shoulders, neck, drape, silhouette, capsule, kneeler, dancer, pike, arcade, organ, limb, head, figure, seatedFig, spear, shield, column, lattice, hline, band, archway, steps, canvasFor, P, L, Q, X, Y, R, lw, ctx: () => x, C: { RINK, RFILL, RBG, HAIR, SHADE, GRANITE, MARBLE } };
})();
// SOUTH — Theodosius and the imperial family in the kathisma; guards and courtiers; two officials on the steps; spectators.
RPANELS.u0 = () => { const { figure: F, seatedFig: S, shield, column, lattice, steps, archway, spear, band, hline, lw, L, X, Y, R, C, P, ctx } = RLIB; const x = ctx();
  // arch springing from the columns of the box
  lw(2.4); x.beginPath(); x.arc(X(47.8), Y(36), R(20.4), Math.PI * 1.04, Math.PI * 1.96); x.stroke(); x.beginPath(); x.arc(X(47.8), Y(36), R(19.2), Math.PI * 1.04, Math.PI * 1.96); x.stroke();
  // back row, left: courtiers behind the guards
  F({ x: 18.6, y: 15.3, r: 2.0, t: .2, b: 32 }); F({ x: 23.2, y: 15.0, r: 1.95, b: 32 });
  // back row, right
  spear(94.5, 7, 30);
  F({ x: 85.6, y: 17.3, r: 1.6, b: 34 });
  F({ x: 72.5, y: 16.9, r: 2.1, b: 34 }); F({ x: 77.3, y: 17.3, r: 2.0, t: .2, b: 34 }); F({ x: 82.2, y: 18.3, r: 2.0, t: -.1, b: 34 });
  F({ x: 90.1, y: 18.9, r: 2.2, t: -.1, hair: 'long', b: 36, g: 'chlamys' }); F({ x: 95.9, y: 19.3, r: 2.3, hair: 'long', b: 36, g: 'chlamys' });
  // the box: columns and the seated imperial family
  column(27.3, 8, 39); column(68.2, 8, 39);
  S({ x: 32.5, y: 9.3, r: 1.9, t: -.1, sw: 3.3, lap: 30, feet: 39, arms: ['clasp'] });
  S({ x: 40.1, y: 8.3, r: 1.85, sw: 3.5, lap: 28.5, feet: 39, arms: ['chestL'] });
  S({ x: 60.7, y: 8.6, r: 1.85, sw: 4.7, lap: 30, feet: 39, arms: ['clasp'] });
  S({ x: 49.8, y: 7.3, r: 1.95, sw: 4.6, lap: 28.5, feet: 39, hair: 'diadem', arms: [{ hold: [51.4, 27.6], side: -1 }] });
  lattice(27.3, 39, 68.2, 51.5, [45.5, 61.3], 'cross', 3.4);
  // guards with shields, courtiers in front
  F({ x: 4.6, y: 14.3, r: 2.2, t: -.3, hair: 'long', sw: 3.2, b: 50, g: 'chlamys' });
  F({ x: 10.1, y: 14.0, r: 2.4, hair: 'long', sw: 4.2, b: 50, g: 'chlamys' });
  shield(4.5, 38.5, 4.4, 12.3);
  F({ x: 17.6, y: 25.6, r: 2.3, sw: 4.1, b: 50, g: 'chlamys' }); F({ x: 23.4, y: 24.9, r: 2.4, sw: 3.8, b: 50, g: 'chlamys' });
  F({ x: 84.6, y: 29.6, r: 2.0, t: -.2, sw: 3.0, b: 50 });
  F({ x: 72.9, y: 28.6, r: 2.3, sw: 3.6, b: 50, g: 'chlamys' }); F({ x: 78.7, y: 29.2, r: 2.4, sw: 3.4, b: 50, g: 'chlamys' });
  shield(95.3, 40, 4.8, 10.5);
  // the long screen in front of the stands, and the stairs
  lattice(1.5, 49.5, 98.5, 66.5, [14.5, 39.1, 55.3, 85.5], 'cross', 3.6);
  band(1.5, 66.5, 98.5, 68.2);
  steps(36, 64, [[68.2, 70.3], [75.2, 77.2], [81.6, 83.6], [88, 91.5]]);
  archway(48.6, 104, 10.5, 9.2, 87.2);
  // spectators, left
  F({ x: 7.9, y: 73.2, r: 1.9, b: 90, arms: [{ raise: [9.4, 67.6], side: 1 }] }); F({ x: 12.7, y: 72.6, r: 2.1, b: 90 }); F({ x: 18.4, y: 71.6, r: 2.0, t: -.1, b: 90 }); F({ x: 24.2, y: 71.9, r: 2.0, b: 90 });
  F({ x: 4.4, y: 79.2, r: 1.9, t: -.5, b: 100, sw: 3.0, arms: [{ raise: [3.0, 67.6], side: -1 }] });
  F({ x: 13.5, y: 83.9, r: 2.1, t: .1, b: 100 }); F({ x: 19.0, y: 84.5, r: 2.1, b: 100 }); F({ x: 24.8, y: 82.9, r: 2.0, t: -.1, b: 100, sw: 3.4 });
  // spectators, right
  F({ x: 77.7, y: 74.2, r: 2.1, t: .1, b: 92 }); F({ x: 82.6, y: 74.6, r: 2.2, b: 92 }); F({ x: 88.4, y: 74.9, r: 2.1, t: -.15, b: 92 }); F({ x: 93.5, y: 74.6, r: 2.1, b: 92 });
  F({ x: 75.9, y: 86.5, r: 2.3, t: .1, b: 100 }); F({ x: 81.8, y: 86.9, r: 2.3, b: 100 }); F({ x: 87.8, y: 87.9, r: 2.2, t: -.15, b: 100 }); F({ x: 93.1, y: 87.2, r: 2.3, t: .1, b: 100 });
  // the two officials on the stairs
  F({ x: 32.5, y: 44.8, r: 1.92, t: .15, sw: 5.0, b: 89, feet: 91.8, flare: 1.0, g: 'chlamys' });
  F({ x: 69.4, y: 46.8, r: 1.8, t: .3, sw: 4.4, b: 94.5, feet: 96.6, flare: .95, g: 'tunic', arms: [{ hold: [73.4, 63.5], side: 1 }, { hold: [62.8, 70], side: -1 }] });
};
// EAST — Theodosius stands in the box holding out the victor's wreath; courtiers under arcades; two rows of spectators; dancers between two water organs.
RPANELS.u1 = () => { const { figure: F, dancer: D, pike, arcade, organ, column, lattice, band, spear, P, X, Y, R, C, lw, ctx } = RLIB; const x = ctx();
  // arcades over the side stands, with the guards' pikes
  arcade([[5.3, 2.3], [13, 2.9], [21.7, 2.1], [27.9, 2.2]], 0, 33.4, 1.5, 7.6, 10.2);
  arcade([[73.1, 2.6], [79.4, 3.0], [85.8, 2.4], [93.3, 3.0]], 66.3, 100, 1.5, 7.6, 10.2);
  pike(17.5, 22, 19.5, 6.5); pike(30.5, 22, 32, 7); pike(70.5, 22, 68.8, 8); pike(82, 22, 81, 7.5);
  // left stand: courtiers behind, three standing in front
  F({ x: 2.1, y: 15.3, r: 1.8, t: -.3, b: 40 }); F({ x: 23.0, y: 15.0, r: 1.6, b: 40 });
  F({ x: 9.2, y: 17.6, r: 1.9, b: 40 }); F({ x: 19.4, y: 19.6, r: 2.1, b: 40 }); F({ x: 29.9, y: 18.6, r: 1.9, t: .3, b: 40 });
  F({ x: 5.1, y: 19.9, r: 2.4, t: -.1, sw: 4.3, b: 52.5, g: 'chlamys', tablion: true, arms: [{ hold: [2.6, 42], side: -1 }] });
  F({ x: 13.9, y: 20.3, r: 2.4, sw: 4.6, b: 52.5, g: 'chlamys', tablion: true, arms: ['chest'] });
  F({ x: 25.3, y: 21.3, r: 2.3, t: .2, sw: 4.8, b: 52.5, g: 'chlamys', tablion: true, arms: [{ hold: [30.1, 43.2], side: 1 }] });
  // right stand
  F({ x: 69.5, y: 22.3, r: 2.0, t: -.4, b: 42 }); F({ x: 79.8, y: 22.6, r: 2.2, b: 42 }); F({ x: 90.5, y: 21.3, r: 2.1, t: -.1, b: 42 });
  F({ x: 74.5, y: 23.3, r: 2.4, sw: 3.7, b: 52.5, g: 'chlamys', tablion: true });
  F({ x: 85.2, y: 23.6, r: 2.3, sw: 3.6, b: 52.5, g: 'chlamys', tablion: true, arms: [{ hold: [80, 39], side: -1 }] });
  F({ x: 95.7, y: 23.3, r: 2.3, sw: 3.6, b: 52.5, g: 'chlamys', tablion: true, arms: [{ hold: [91, 41], side: -1 }] });
  lattice(1, 52, 33, 63.5, [6, 12.8, 19.5, 26.2], ['x', 'scale', 'cross', 'scale', 'x'], 2.2);
  lattice(67.2, 52, 99, 63.5, [73, 79.3, 86.4, 92.7], ['bars', 'scale', 'cross', 'scale', 'cross'], 2.2);
  // the imperial box
  P(() => x.rect(X(34.6), Y(2.6), X(65.2) - X(34.6), Y(38.5) - Y(2.6)), C.SHADE);
  spear(59.8, 4, 22);
  F({ x: 36.6, y: 14.3, r: 1.9, t: -.3, b: 38 }); F({ x: 41.9, y: 15.6, r: 2.2, t: .2, b: 38 });
  F({ x: 56.0, y: 16.6, r: 2.1, t: -.2, b: 38 }); F({ x: 63.1, y: 16.0, r: 2.0, t: -.1, b: 38 });
  F({ x: 49.2, y: 9.6, r: 2.9, sw: 6.3, b: 38.5, hair: 'diadem', g: 'chlamys', tablion: true, arms: [{ hold: [47.6, 39.5], side: -1 }] });
  F({ x: 39.1, y: 23.3, r: 2.2, sw: 4.4, b: 38.5, g: 'chlamys' }); F({ x: 59.3, y: 23.6, r: 2.1, t: -.1, sw: 4.4, b: 38.5, g: 'chlamys' });
  lattice(34.6, 38.5, 65.2, 62.5, [44.5, 56], ['cross', 'plain', 'cross'], 2.6);
  lw(4.5); x.beginPath(); x.arc(X(47.5), Y(42.6), R(2.2), 0, 6.283); x.stroke(); lw(1.4); x.beginPath(); x.arc(X(47.5), Y(42.6), R(2.2), 0, 6.283); x.strokeStyle = C.RFILL; x.stroke(); x.strokeStyle = C.RINK; lw(2.4);
  column(33.9, 1, 63.5, 1.6); column(66, 1, 63.5, 1.6);
  band(0, 63.5, 100, 66.2);
  // spectators: two rows
  [[4.0, 70.3, -.2], [8.5, 70.3, .1], [13.1, 70.6, -.1], [17.6, 70.9], [21.6, 69.9, .3], [25.9, 69.3], [30.1, 69.3, -.2], [34.3, 69.5], [38.3, 69.3], [43.9, 69.3], [48.2, 69.9],
   [52.8, 70.9], [57.5, 70.3], [62.7, 69.9], [67.0, 70.2], [71.1, 70.6], [75.9, 70.9], [80.2, 70.6], [84.8, 70.6], [89.3, 70.6], [94.5, 70.3]]
    .forEach(([cx, cy, t]) => F({ x: cx, y: cy, r: 2.05, t: t || 0, sw: 2.2, b: 82 }));
  [[6.3, 79.6], [10.5, 79.2], [15.0, 79.2], [19.6, 79.9], [24.2, 79.2], [28.5, 79.2], [32.9, 79.9], [37.9, 79.2], [43.9, 79.2], [49.4, 79.9], [54.6, 81.2],
   [59.9, 79.9], [65.1, 80.9], [69.5, 79.9], [73.1, 79.9], [77.9, 79.9], [82.2, 79.9], [86.6, 79.9], [91.3, 79.9], [95.3, 79.9]]
    .forEach(([cx, cy, t]) => F({ x: cx, y: cy, r: 1.95, t: t || 0, sw: 2.15, b: 91 }));
  // musicians, organs and a chain of dancers
  organ(7.4, 14.6, 87.5, 99.5); organ(80.8, 87.6, 87.5, 99.5);
  D({ x: 4.2, y: 85.6, r: 1.25, feet: 99.3, arms: [[3, 93], [6, 92]] });
  D({ x: 17.5, y: 87.5, r: 1.25, feet: 99.3, step: .4, arms: [[15.6, 92.5], [20, 93]] });
  D({ x: 22.5, y: 86.8, r: 1.25, feet: 99.3, t: .3, arms: [[20, 93], [25.2, 93.4]] });
  D({ x: 28, y: 87, r: 1.25, feet: 99.3, arms: [[25.2, 93.4], [30.8, 93]] });
  D({ x: 33.5, y: 87.5, r: 1.25, feet: 99.3, step: .5, arms: [[30.8, 93], [36, 92.6]] });
  D({ x: 38.5, y: 87.5, r: 1.25, feet: 99.3, t: .4, arms: [[36, 92.6], [41.2, 92.8]] });
  D({ x: 43.5, y: 88, r: 1.25, feet: 99.3, arms: [[41.2, 92.8], [45.6, 94]] });
  D({ x: 54, y: 88, r: 1.25, feet: 99.3, arms: [[52, 94], [56.2, 93]] });
  D({ x: 58.5, y: 87.5, r: 1.25, feet: 99.3, step: .4, arms: [[56.2, 93], [61, 91.5]] });
  D({ x: 63.5, y: 87, r: 1.25, feet: 99.3, arms: [[61, 91.5], [66, 90.8]] });
  D({ x: 69, y: 87.5, r: 1.25, feet: 99.3, t: -.3, arms: [[66.6, 92.5], [71.4, 93]] });
  D({ x: 73.5, y: 87, r: 1.25, feet: 99.3, arms: [[71.4, 93], [75.8, 92.8]] });
  D({ x: 78.3, y: 88, r: 1.25, feet: 99.3, arms: [[75.8, 92.8], [80, 94.5]] });
  D({ x: 91.2, y: 88, r: 1.25, feet: 99.3, arms: [[89.6, 92], [92.4, 91.8]] });
};
// NORTH — the emperor among his court and guards; spectators below. A later channel has been cut through the middle of this side.
RPANELS.u2 = () => { const { figure: F, column, lattice, band, spear, pike, archway, P, L, X, Y, R, C, lw, ctx } = RLIB; const x = ctx();
  // guards' pikes behind the back row
  pike(8.8, 15, 10.4, 1.5); pike(16.2, 15, 17.7, 1.5); pike(24.5, 15, 26, 1.5);
  pike(76, 15, 77.5, 1.2); pike(82.1, 15, 83.6, 1.2); pike(90.7, 15, 92.2, 1.2);
  spear(53.2, .8, 16);
  // left: guards behind, courtiers in front
  F({ x: 5.9, y: 8.0, r: 2.4, b: 30 }); F({ x: 13.9, y: 8.6, r: 2.4, b: 30 }); F({ x: 22.4, y: 9.0, r: 2.3, b: 30 }); F({ x: 29.9, y: 8.3, r: 2.3, b: 30 });
  F({ x: 6.3, y: 18.6, r: 2.3, sw: 4.6, b: 45.5, g: 'chlamys' }); F({ x: 17.4, y: 19.6, r: 2.2, sw: 4.8, b: 45.5, g: 'chlamys' }); F({ x: 25.5, y: 19.9, r: 2.3, sw: 5.6, b: 45.5, g: 'chlamys' });
  column(34.1, 2, 45.5, 1.6);
  // centre: the emperor between two pairs of courtiers
  F({ x: 41.5, y: 8.6, r: 2.3, b: 30 }); F({ x: 56.2, y: 7.6, r: 2.2, b: 30 });
  F({ x: 49.4, y: 6.3, r: 2.3, sw: 5.2, b: 45.5, hair: 'diadem', g: 'chlamys', tablion: true, arms: ['clasp'] });
  F({ x: 38.9, y: 19.9, r: 2.2, sw: 4.4, b: 45.5, g: 'chlamys' }); F({ x: 58.4, y: 18.4, r: 2.2, sw: 4.6, b: 45.5, g: 'chlamys' });
  // right: guards behind, courtiers in front
  F({ x: 73.1, y: 8.6, r: 2.3, b: 30 }); F({ x: 79.2, y: 9.3, r: 2.3, t: -.1, b: 30 }); F({ x: 87.2, y: 9.0, r: 2.3, b: 30 }); F({ x: 95.1, y: 9.3, r: 2.3, t: -.1, b: 30 });
  F({ x: 74.1, y: 21.9, r: 2.3, sw: 5.1, b: 45.5, g: 'chlamys' }); F({ x: 83.4, y: 21.3, r: 2.4, sw: 4.6, b: 45.5, g: 'chlamys' }); F({ x: 91.7, y: 21.9, r: 2.3, sw: 4.5, b: 45.5, g: 'chlamys', arms: ['chest'] });
  band(1, 45.5, 99, 51);
  lattice(1, 51, 99, 61, [34.1, 66], ['x', 'cross', 'x'], 2.4);
  band(1, 61, 99, 64);
  // spectators, left
  F({ x: 5.1, y: 67.9, r: 2.0, b: 84 }); F({ x: 13.1, y: 67.9, r: 2.0, b: 84 }); F({ x: 19.8, y: 67.6, r: 2.0, b: 84 }); F({ x: 27.1, y: 67.6, r: 2.0, b: 84 });
  F({ x: 8.9, y: 68.2, r: 1.8, b: 84, arms: [{ raise: [9.8, 65.6], side: 1 }] });
  F({ x: 34.4, y: 66.3, r: 2.0, sw: 3.3, b: 91.5, feet: 94.5 });
  F({ x: 4.4, y: 84.2, r: 2.2, b: 100 }); F({ x: 10.3, y: 84.5, r: 2.0, b: 100 }); F({ x: 19.8, y: 85.2, r: 2.1, b: 100 }); F({ x: 27.7, y: 84.9, r: 2.1, b: 100 });
  // the eroded centre with the outline of an arch
  lw(1.6); x.beginPath(); x.arc(X(52.5), Y(82.6) + R(9), R(9), Math.PI, 0); x.stroke(); lw(2.4);
  // spectators, right
  F({ x: 78.7, y: 67.9, r: 2.1, b: 84, arms: [{ raise: [82.2, 66], side: 1 }] }); F({ x: 87.4, y: 67.9, r: 2.0, b: 84 });
  F({ x: 95.7, y: 67.3, r: 2.0, b: 84, arms: [{ raise: [92.5, 66.4], side: -1 }] });
  F({ x: 72.3, y: 66.6, r: 2.0, sw: 3.3, b: 91.5, feet: 94.5 });
  F({ x: 79.7, y: 85.1, r: 2.1, b: 100 }); F({ x: 87.0, y: 85.1, r: 2.1, b: 100 }); F({ x: 94.4, y: 85.1, r: 2.1, b: 100 });
  // the later channel: two openings, and the stone with a cross set above
  const cut = (x0, y0, x1, y1) => P(() => x.roundRect(X(x0), Y(y0), X(x1) - X(x0), Y(y1) - Y(y0), R(2.2)), '#a99f8f');
  cut(61.9, 12, 68.9, 49.5); cut(61.9, 56.5, 67.6, 95.5);
  P(() => x.rect(X(61.4), Y(1.4), X(68.4) - X(61.4), Y(12.4) - Y(1.4)), C.RFILL);
  lw(3.5); L([X(64.9), Y(3.4), X(64.9), Y(10.4)]); L([X(63.2), Y(6.9), X(66.6), Y(6.9)]); lw(2.4);
};
// WEST — Theodosius and his co-emperors enthroned in the box; guards and courtiers; barbarians kneel with gifts.
RPANELS.u3 = () => { const { figure: F, seatedFig: S, kneeler: K, column, lattice, band, pike, P, X, Y, R, C, lw, ctx } = RLIB; const x = ctx();
  lw(2.4); x.beginPath(); x.arc(X(44.7), Y(46), R(23.1), Math.PI * 1.06, Math.PI * 1.94); x.stroke(); x.beginPath(); x.arc(X(44.7), Y(46), R(21.9), Math.PI * 1.06, Math.PI * 1.94); x.stroke();
  pike(11, 14, 12.2, 3.5); pike(15.4, 16, 18.3, 6.5);
  // left: guards and courtiers
  F({ x: 4.0, y: 15.3, r: 2.3, t: -.1, hair: 'curly', beard: true, b: 34 });
  F({ x: 16.4, y: 14.5, r: 2.0, t: .6, hair: 'helmet', b: 34 });
  F({ x: 10.5, y: 15.3, r: 2.4, hair: 'long', b: 34 });
  F({ x: 5.9, y: 27.2, r: 2.3, hair: 'curly', beard: true, sw: 3.8, b: 50, g: 'chlamys' });
  F({ x: 16.0, y: 26.6, r: 2.2, sw: 4.4, b: 50, g: 'chlamys' });
  column(21.6, 6, 51, 1.6); column(67.6, 3, 51, 1.6);
  // the four emperors enthroned, Theodosius larger at the centre
  S({ x: 28.5, y: 12.6, r: 2.1, sw: 3.9, lap: 28, feet: 47.8, hair: 'diadem', arms: ['chest'] });
  S({ x: 38.3, y: 10.0, r: 2.1, sw: 4.7, lap: 29.9, feet: 47.8, hair: 'diadem', arms: ['chestL'] });
  S({ x: 60.7, y: 8.0, r: 2.3, sw: 5.3, lap: 31.2, feet: 48.5, hair: 'diadem', arms: ['clasp'] });
  S({ x: 50.4, y: 5.3, r: 2.6, sw: 6.1, lap: 31.2, feet: 48.5, hair: 'diadem', arms: [{ hold: [50.2, 28.6], side: -1 }] });
  // right: courtiers and bearded guards
  F({ x: 72.3, y: 14.3, r: 2.2, t: -.3, hair: 'curly', beard: true, b: 34 }); F({ x: 77.5, y: 14.6, r: 2.3, b: 34 });
  F({ x: 86.4, y: 15.0, r: 2.2, hair: 'long', b: 34 }); F({ x: 93.3, y: 14.3, r: 2.3, hair: 'long', b: 34 });
  F({ x: 74.1, y: 27.9, r: 2.4, hair: 'curly', beard: true, sw: 5.0, b: 50, g: 'chlamys' });
  F({ x: 83.0, y: 29.6, r: 2.4, hair: 'curly', beard: true, sw: 4.4, b: 50, g: 'chlamys' });
  F({ x: 91.3, y: 29.9, r: 2.3, t: -.1, hair: 'curly', sw: 4.7, b: 50, g: 'chlamys' });
  lattice(1.7, 49.7, 97, 65.8, [21.6, 37.5, 54, 70.3, 82.8], ['x', 'cross', 'cross', 'cross', 'x', 'x'], 2.8);
  band(1, 65.8, 99, 67.2);
  // barbarians kneeling with gifts: from the left, facing right
  F({ x: 12.9, y: 69.6, r: 1.7, t: .7, hair: 'curly', b: 80 }); F({ x: 26, y: 70.9, r: 1.8, t: .6, hair: 'curly', b: 82 });
  K({ h: [7.8, 69.6], r: 2.0, d: 1, sh: [8.2, 75.5], hip: [4.5, 86.6], kb: [3.8, 99], fb: [.8, 99], kf: [9.9, 93.4], ff: [12.1, 99], hand: [12.4, 80.4], bowl: [13.4, 79.8, 3.4] });
  K({ h: [18.9, 70.2], r: 1.9, d: 1, sh: [18.6, 76], hip: [14.4, 88.6], kb: [12.8, 99], fb: [9.9, 99], kf: [19.6, 93.2], ff: [21.4, 99], hand: [23.4, 81.2], bowl: [24.4, 80.4, 3.8] });
  K({ h: [36.6, 70.6], r: 2.0, d: 1, beard: true, sh: [35, 76.5], hip: [29.3, 88.7], kb: [27.2, 99], fb: [24.2, 99], kf: [37.5, 92.4], ff: [38.6, 99], hand: [40.8, 81.6], bowl: [42.2, 80.4, 3.8] });
  // from the right, facing left
  F({ x: 68.1, y: 71.4, r: 2.0, t: -.8, hair: 'curly', beard: true, b: 84 }); F({ x: 82.3, y: 71.4, r: 2.0, t: -.8, hair: 'curly', b: 82 });
  K({ h: [59.5, 72.7], r: 2.3, d: -1, beard: true, hair: 'long', sh: [62.1, 76.6], hip: [66.4, 90.6], kb: [67.6, 99], fb: [71.3, 99], kf: [59.5, 91.9], ff: [57.8, 99], hand: [56.4, 82.4], bowl: [54.7, 82.0, 7] });
  K({ h: [75.4, 72.0], r: 2.2, d: -1, beard: true, sh: [76.7, 77.3], hip: [78.6, 91.6], kb: [82.8, 99], fb: [85.8, 99], kf: [73.3, 93.2], ff: [71.6, 99], hand: [71.6, 83.4], bowl: [70.2, 83.2, 5] });
  K({ h: [87.9, 70.8], r: 2.2, d: -1, hair: 'long', sh: [90.5, 76.4], hip: [92.2, 91.6], kb: [96.4, 99], fb: [98.6, 99], kf: [89.7, 94.4], ff: [88.2, 99], hand: [86.2, 80.4], bowl: [83.4, 78.6, 5] });
};
/* ---------- lower block ---------- */
// SOUTH: above, the spina with its monuments; below, the chariot race (layout kept from the earlier measured drawing)
(function(){
const { head, shoulders, neck, drape } = RLIB, GRANITE = RLIB.C.GRANITE;
const RINK = RLIB.C.RINK, RFILL = RLIB.C.RFILL, RBG = RLIB.C.RBG;
function P(x, fn){ x.beginPath(); fn(); x.fill(); x.stroke(); }
// a small cloaked figure standing on base, h px tall
function fig(x, cx, base, h){
  const r = h * .12, cy = base - h + r * 1.1, ys = cy + r * 1.45;
  neck(cx, cy, r); shoulders(cx, ys, r * 1.7, base, r, 1.08); drape('pallium', cx, ys, r * 1.7, base, r, {}); head(cx, cy, r, 0, 'cap');
}
const LX = p => p / 100 * 1344, LY = p => p / 100 * 320;
function obeliskShape(x, x0, x1, yc, h, angle = 0){
  x.save(); x.translate((x0 + x1) / 2, yc); x.rotate(angle); const L = (x1 - x0) / 2;
  x.fillStyle = GRANITE;
  P(x, () => { x.moveTo(-L, -h / 2); x.lineTo(L - h * .9, -h * .38); x.lineTo(L, 0); x.lineTo(L - h * .9, h * .38); x.lineTo(-L, h / 2); x.closePath(); });
  x.restore();
}
// a galloping horse in profile, facing d (1 = right); s = body length in px
function horse(x, cx, cy, s, d){
  x.save(); x.translate(cx, cy); x.scale(d * s, s);
  const lw = x.lineWidth; x.lineWidth = lw / s;
  x.save(); x.lineWidth = 7 / s;                                  // legs: thick ink strokes
  x.beginPath();
  x.moveTo(.24, .06); x.lineTo(.42, .2); x.lineTo(.54, .24);
  x.moveTo(.18, .08); x.lineTo(.34, .24); x.lineTo(.4, .33);
  x.moveTo(-.24, .06); x.lineTo(-.4, .2); x.lineTo(-.55, .22);
  x.moveTo(-.18, .08); x.lineTo(-.28, .26); x.lineTo(-.38, .34);
  x.stroke(); x.restore();
  x.beginPath(); x.moveTo(-.3, -.05); x.quadraticCurveTo(-.46, -.06, -.52, .06); x.stroke();          // tail
  P(x, () => x.ellipse(0, 0, .32, .12, -.05, 0, 6.283));                                            // body
  P(x, () => { x.moveTo(.2, -.07); x.quadraticCurveTo(.3, -.24, .4, -.3); x.lineTo(.46, -.35); x.lineTo(.47, -.3);
    x.quadraticCurveTo(.56, -.27, .6, -.2); x.lineTo(.56, -.16); x.quadraticCurveTo(.46, -.18, .4, -.16); x.quadraticCurveTo(.34, -.04, .3, .03); x.closePath(); });
  x.restore();
}
function quadriga(x, cxp, basep, s, d){
  const cx = LX(cxp), base = LY(basep), cy = base - s * .36;
  for (let k = 2; k >= 0; k--) horse(x, cx + d * (s * .12 * k), cy - s * .03 * k, s, d);
  const wx = cx - d * s * .72, wr = s * .19;
  P(x, () => x.rect(wx - s * .12, cy - s * .2, s * .24, s * .2));                                  // car
  P(x, () => x.arc(wx, base - wr, wr, 0, 6.283)); x.beginPath(); x.arc(wx, base - wr, wr * .25, 0, 6.283); x.stroke();
  fig(x, wx + d * s * .02, cy - s * .12, s * .42);                                               // charioteer
  x.beginPath(); x.moveTo(wx + d * s * .12, cy - s * .38); x.lineTo(cx + d * s * .48, cy - s * .2); x.stroke(); // reins
}
function statue(x, cxp, basep, h){ const cx = LX(cxp), base = LY(basep);
  P(x, () => x.rect(cx - h * .22, base - h * .18, h * .44, h * .18)); fig(x, cx, base - h * .18, h * .82); }
function meta(x, cxp, basep, h){ const cx = LX(cxp), base = LY(basep);
  P(x, () => x.rect(cx - h * .45, base - h * .14, h * .9, h * .14));
  for (let k = -1; k <= 1; k++) P(x, () => { x.moveTo(cx + k * h * .26 - h * .11, base - h * .14); x.lineTo(cx + k * h * .26, base - h); x.lineTo(cx + k * h * .26 + h * .11, base - h * .14); x.closePath(); }); }
function columnL(x, cxp, basep, h, top){ const cx = LX(cxp), base = LY(basep), w = h * .1;
  P(x, () => x.rect(cx - w, base - h, w * 2, h)); P(x, () => x.rect(cx - w * 1.8, base - h - 8, w * 3.6, 8));
  if (top === 'statue') fig(x, cx, base - h - 8, h * .5); }
function capstanL(x, cxp, basep, h){
  const cx = LX(cxp), base = LY(basep);
  P(x, () => x.rect(cx - 7, base - h, 14, h));
  x.save(); x.lineWidth = 5; x.beginPath(); x.moveTo(cx - h * .55, base - h * .95); x.lineTo(cx + h * .55, base - h * .35); x.moveTo(cx + h * .55, base - h * .95); x.lineTo(cx - h * .55, base - h * .35); x.stroke(); x.restore();
  [-1, 1].forEach(sd => { x.save(); x.translate(cx + sd * h * .62, base); x.rotate(-sd * .32); fig(x, 0, 0, h * .78); x.restore(); });
}RPANELS.l0 = () => { const x = RLIB.ctx(); x.lineWidth = 3;
    P(x, () => x.rect(LX(7), LY(40), LX(86), LY(7)));
    meta(x, 9, 40, 92); meta(x, 91, 40, 92);
    statue(x, 17, 40, 76); columnL(x, 23, 40, 56, 'statue'); columnL(x, 31, 40, 84);
    x.save(); x.fillStyle = RFILL; P(x, () => { x.rect(LX(35), LY(12), LX(7), LY(28)); }); x.restore();
    x.save(); x.fillStyle = RBG; P(x, () => { x.moveTo(LX(36.4), LY(40)); x.lineTo(LX(36.4), LY(22)); x.arc(LX(38.5), LY(22), LX(2.1), Math.PI, 0); x.lineTo(LX(40.6), LY(40)); }); x.restore();
    P(x, () => { x.moveTo(LX(34.4), LY(12)); x.lineTo(LX(38.5), LY(4)); x.lineTo(LX(42.6), LY(12)); x.closePath(); });
    statue(x, 46, 40, 70); columnL(x, 52, 40, 60, 'statue'); statue(x, 57, 40, 74); statue(x, 61, 40, 74);
    obeliskShape(x, LX(64.2), LX(67.8), LY(22), 22, -Math.PI / 2);
    statue(x, 71, 40, 76); columnL(x, 76, 40, 90);
    horse(x, LX(82), LY(28), 70, 1); x.save(); x.fillStyle = RFILL; P(x, () => x.rect(LX(79), LY(36), LX(6), LY(4))); x.restore();
    x.beginPath(); x.moveTo(LX(3), LY(52)); x.lineTo(LX(97), LY(52)); x.stroke();
    quadriga(x, 22, 94, 110, -1); quadriga(x, 44, 94, 110, -1); quadriga(x, 70, 94, 110, 1); quadriga(x, 91, 94, 104, 1);
    x.beginPath(); x.moveTo(LX(3), LY(95)); x.lineTo(LX(97), LY(95)); x.stroke();
};
})();
// NORTH: above, the obelisk lying on its side, point to the left, roped and watched from above, inside its curved frame;
// below, crews at the capstans and onlookers. Measured on F. Bini's photograph; the channel cut later runs through the lower register.
RPANELS.l2 = () => { const { dancer: D, figure: F, P, L, Q, X, Y, R, C, lw, ctx } = RLIB; const x = ctx();
  // ropes from the point of the obelisk to the left
  lw(1.6); [[3, 26], [9, 40], [16, 22], [24, 44], [31, 30], [39, 41]].forEach(([a, b]) => Q(X(51.5), Y(35), X((51.5 + a) / 2), Y(Math.max(35, b) + 4), X(a), Y(b))); lw(2.4);
  // men on and behind the obelisk
  D({ x: 43.5, y: 18, r: .85, feet: 47.5, arms: [[41.5, 30], [46, 31]] });
  F({ x: 52.2, y: 8.5, r: .95, sw: 1.7, b: 28 }); F({ x: 61.3, y: 7, r: .95, sw: 1.7, b: 25 }); F({ x: 70.8, y: 7.5, r: .95, sw: 1.7, b: 25 });
  // the curved frame at the base end
  P(() => { x.arc(X(91), Y(33), R(6.6), -Math.PI * .55, Math.PI * .55); x.arc(X(91), Y(33), R(5.3), Math.PI * .55, -Math.PI * .55, true); x.closePath(); }, C.RFILL);
  // the obelisk, point to the left
  P(() => { x.moveTo(X(92.5), Y(21)); x.lineTo(X(92.5), Y(48.5)); x.lineTo(X(55.5), Y(47)); x.lineTo(X(51), Y(37)); x.lineTo(X(55.5), Y(26.5)); x.closePath(); }, C.GRANITE);
  lw(1.6); L([X(55.5), Y(26.5), X(55.5), Y(47)]); lw(2.4);
  L([X(2), Y(49.5), X(98), Y(49.5)]);
  // lower register: two capstans worked by crews
  const capstan = (cx) => { P(() => x.rect(X(cx) - R(.55), Y(60), R(1.1), Y(90) - Y(60))); lw(5); L([X(cx - 4.6), Y(61), X(cx + 4.6), Y(75)]); L([X(cx + 4.6), Y(61), X(cx - 4.6), Y(75)]); lw(2.4); };
  capstan(9.9); capstan(25.7);
  D({ x: 8.7, y: 55.5, r: .95, feet: 90, arms: [[7.2, 63], [10.6, 64]] }); D({ x: 21.7, y: 56, r: .95, feet: 90, t: .3, arms: [[22, 64], [24.4, 63]] });
  D({ x: 5.9, y: 58, r: 1.0, feet: 90.5, t: .4, step: .5, arms: [[6.8, 64.5], [7.8, 64]] }); D({ x: 12.6, y: 57.5, r: 1.0, feet: 90.5, t: -.3, arms: [[11.4, 66], [12.2, 67]] });
  D({ x: 15.4, y: 59, r: 1.0, feet: 90.5, t: -.4, step: .5, arms: [[13.8, 69], [14.2, 70]] });
  D({ x: 19.4, y: 58, r: 1.0, feet: 90.5, t: .4, arms: [[20.6, 66], [21.6, 67]] }); D({ x: 28.1, y: 58, r: 1.0, feet: 90.5, t: -.4, arms: [[27.2, 65], [27.6, 66]] });
  D({ x: 30.2, y: 59.5, r: 1.0, feet: 90.5, t: -.3, step: .4, arms: [[29.2, 69], [29.8, 70]] });
  // onlookers and overseers
  D({ x: 35.2, y: 57.5, r: 1.05, feet: 90.5, arms: [[33.9, 73], [36.4, 73]] });
  D({ x: 40, y: 57.5, r: 1.05, feet: 90.5, t: .2, arms: [[38.8, 73], [41.4, 66]] }); D({ x: 42.4, y: 58.5, r: 1.0, feet: 90.5, t: -.2, arms: [[41.4, 66], [43.6, 73]] });
  D({ x: 50.6, y: 58, r: 1.05, feet: 90.5, arms: [[48.6, 66], [52.6, 66]] }); D({ x: 56.1, y: 58, r: 1.05, feet: 90.5, t: -.2, arms: [[54.8, 70], [57.4, 70]] });
  // right of the channel: a man stooping, a ladder, two more
  D({ x: 67.6, y: 68, r: 1.0, feet: 90.5, t: .5, arms: [[69.6, 76], [70.2, 77]] });
  lw(2.4); L([X(70.8), Y(90.5), X(73), Y(55)]); L([X(72.6), Y(90.5), X(74.8), Y(55)]); lw(1.6); for (let k = 1; k < 9; k++){ const f = k / 9; L([X(70.8 + 2.2 * f), Y(90.5 - 35.5 * f), X(72.6 + 2.2 * f), Y(90.5 - 35.5 * f)]); } lw(2.4);
  D({ x: 78.7, y: 56.5, r: 1.05, feet: 90.5, arms: [[77.2, 72], [80.2, 72]] }); D({ x: 85.8, y: 57.5, r: 1.05, feet: 90.5, t: .2, arms: [[84.4, 72], [87.6, 51]] });
  L([X(2), Y(91.5), X(98), Y(91.5)]);
  P(() => x.roundRect(X(58.9), Y(50.5), X(64.4) - X(58.9), Y(104) - Y(50.5), R(1.4)), '#a99f8f');
};
/* ---------- inscribed faces of the lower block (east: Latin, west: Greek) ---------- */
// Tabula ansata as on the stone: a moulded frame with dovetail handles reaching toward the block edges.
// Text as cut: no word spaces; the Greek with lunate sigma (C) and cursive omega (ω).
RPANELS.face = (lines, kind) => {
  const W = 1400, H = 460, c = document.createElement('canvas'); c.width = W; c.height = H;
  const x = c.getContext('2d'), INK = '#2b2420';
  x.fillStyle = RLIB.C.MARBLE; x.fillRect(0, 0, W, H);
  x.strokeStyle = INK; x.lineCap = 'round'; x.lineJoin = 'round';
  const line = (a, b, c2, d, w = 2) => { x.lineWidth = w; x.beginPath(); x.moveTo(a, b); x.lineTo(c2, d); x.stroke(); };
  line(0, 8, W, 8, 2); line(0, 418, W, 418, 2); line(0, 446, W, 446, 2);
  x.fillStyle = 'rgba(43,36,32,.06)'; x.fillRect(0, 418, W, 28);
  // frame: outer edge, moulding, field
  const fy0 = kind === 'greek' ? 22 : 30, fy1 = kind === 'greek' ? 334 : 350, fx0 = 232, fx1 = 1180, m = 16;
  x.fillStyle = 'rgba(43,36,32,.05)'; x.fillRect(fx0, fy0, fx1 - fx0, fy1 - fy0);
  x.lineWidth = 2.6; x.strokeRect(fx0, fy0, fx1 - fx0, fy1 - fy0);
  x.lineWidth = 1.4; x.strokeRect(fx0 + m * .45, fy0 + m * .45, fx1 - fx0 - m * .9, fy1 - fy0 - m * .9);
  x.fillStyle = RLIB.C.MARBLE; x.fillRect(fx0 + m, fy0 + m, fx1 - fx0 - 2 * m, fy1 - fy0 - 2 * m);
  x.lineWidth = 2; x.strokeRect(fx0 + m, fy0 + m, fx1 - fx0 - 2 * m, fy1 - fy0 - 2 * m);
  // dovetail handles: two raised edges each, from the frame toward the corners of the block
  const hh = fy1 - fy0, a0 = fy0 + hh * .26, a1 = fy0 + hh * .64, o0 = fy0 + hh * .0 + 4, o1 = fy0 + hh * 1.02;
  [[fx0, 40], [fx1, W - 40]].forEach(([e, o]) => {
    const s = Math.sign(o - e);
    line(e, a0, o, o0, 2.4); line(e, a0 + 12, o - s * 6, o0 + 14, 1.4);
    line(e, a1, o, o1, 2.4); line(e, a1 - 12, o - s * 6, o1 - 14, 1.4);
  });
  // text
  const txt = lines.map(l => kind === 'greek' ? l.replace(/ /g, '').replace(/Σ/g, 'C').replace(/Ω/g, 'ω') : l.replace(/ /g, ''));
  const ix0 = fx0 + m + 26, ix1 = fx1 - m - 26, iw = ix1 - ix0;
  x.fillStyle = '#3a312b'; x.textBaseline = 'middle';
  const font = s => `500 ${s}px "EB Garamond", "Noto Serif", serif`;
  let size = 60; x.font = font(size);
  const widest = () => Math.max(...txt.map(t => x.measureText(t).width + (t.length - 1) * size * (kind === 'greek' ? .16 : .1)));
  while (widest() > iw && size > 12){ size--; x.font = font(size); }
  const top = fy0 + m, ih = fy1 - fy0 - 2 * m, n = txt.length;
  txt.forEach((t, i) => {
    const cy = kind === 'greek' ? top + ih * (.15 + i * .2) : top + ih * (.12 + i * .19);
    const chars = [...t], wsum = chars.reduce((a, ch) => a + x.measureText(ch).width, 0);
    // Latin: every line justified to the field; Greek: set from the left at one spacing, as on the stone
    const gap = kind === 'greek' ? size * .16 : (iw - wsum) / (chars.length - 1);
    let px = ix0;
    const k = kind === 'greek' ? 1.45 : 1.3;
    chars.forEach(ch => { x.save(); x.translate(px, cy); x.scale(1, k); x.fillText(ch, 0, 0); x.restore(); px += x.measureText(ch).width + gap; });
  });
  return c;
};
window.RELIEF = {
  upper: i => RLIB.canvasFor(1148, 684, RPANELS['u' + i]),
  lower: i => RLIB.canvasFor(1344, 320, RPANELS['l' + i]),
  face: (lines, kind) => RPANELS.face(lines, kind),
};
