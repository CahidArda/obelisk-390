#!/usr/bin/env python3
"""Render a short clip from a cut spec with one ffmpeg run.   Usage: render.py <spec.json>

Spec (times in seconds; caption/cursor times are local to the segment AFTER speed-up):
{ "output": "full/x-final.mp4", "width": 1280, "height": 800, "fps": 30,
  "fonts": {"sans": "...ttf", "mono": "...ttf"},            # optional
  "sprites": {"cursor": "cursor.png", "press": "cursor-press.png", "ripple": "ripple/r%02d.png"},  # optional
  "segments": [
    {"src": "full/x.mp4", "start": 1.0, "end": 4.4},                         # 1x
    {"src": "full/x.mp4", "start": 4.4, "end": 134.1, "speed": 20, "badge": "20x",
     "captions": [{"text": "box_git · clone", "start": 0.7, "end": 1.6}]},
    {"src": "full/x.mp4", "start": 134.1, "end": 136.9,
     "cursor": {"rest": [1120, 700], "moves": [{"to": [230, 575], "start": 1.05, "end": 1.95, "click": 2.2}]}},
    {"src": "full/x-outcome.mp4", "start": 2.0, "end": 5.6, "pill": "https://example.com"} ] }
"""
import json, subprocess, sys
spec = json.load(open(sys.argv[1]))
W, H, FPS = spec.get('width', 1280), spec.get('height', 800), spec.get('fps', 30)
fonts = spec.get('fonts', {}); SANS = fonts.get('sans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'); MONO = fonts.get('mono', '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf')
sp = spec.get('sprites', {}); CURSOR, PRESS, RIPPLE = sp.get('cursor', 'cursor.png'), sp.get('press', 'cursor-press.png'), sp.get('ripple', 'ripple/r%02d.png')
S = spec.get('ui_scale', 1)
RIPPLE_FRAMES, TIP = 14, 3 * S
if S != 1:  # scale the cursor and ripple sprites once, next to the output
    import os
    sd = spec['output'] + '.sprites'; os.makedirs(sd + '/ripple', exist_ok=True)
    def up(src, dst): subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', f'scale=iw*{S}:ih*{S}:flags=lanczos', dst], check=True)
    up(CURSOR, sd + '/cursor.png'); up(PRESS, sd + '/press.png')
    for k in range(RIPPLE_FRAMES): up(RIPPLE % k, sd + '/ripple/r%02d.png' % k)
    CURSOR, PRESS, RIPPLE = sd + '/cursor.png', sd + '/press.png', sd + '/ripple/r%02d.png'   # ripple PNG count; cursor tip offset inside the sprite

def esc(s): return s.replace('\\', '\\\\').replace("'", "\\'").replace(':', '\\:').replace('%', '%%')
def dt(text, **kw): return 'drawtext=' + ':'.join([f"text='{esc(text)}'"] + [f'{k}={v}' for k, v in kw.items()])
def q(e): return "'" + e.replace(',', '\\,') + "'"
scale = f'scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p'

inputs = []
def inp(path):
    # One decoder per segment, even for the same file: sharing one makes ffmpeg buffer the
    # later segment's frames while it encodes the earlier one, which runs a 4 GB box out of
    # memory at 2560x1600.
    inputs.append(path)
    return len(inputs) - 1

lines, labels, offset, cursor_specs = [], [], 0.0, []
for i, s in enumerate(spec['segments']):
    k = s.get('speed', 1); length = (s['end'] - s['start']) / k
    f = [f"[{inp(s['src'])}:v]trim=start={s['start']:.3f}:end={s['end']:.3f}", f'setpts=(PTS-STARTPTS)/{k}', f'fps={FPS}', scale]
    if s.get('badge'): f.append(dt(s['badge'], fontfile=MONO, fontsize=28 * S, fontcolor='0x062b1f', x=f'w-tw-{30 * S}', y=26 * S, box=1, boxcolor='0x00d48a@0.95', boxborderw=10 * S))
    for c in s.get('captions', []):
        f.append(dt(c['text'], fontfile=SANS, fontsize=24 * S, fontcolor='0xe6edf3', x=32 * S, y=f'h-{72 * S}', box=1, boxcolor='0x0b0f14@0.75', boxborderw=12 * S, enable=q(f"between(t,{c['start']:.3f},{c['end']:.3f})")))
    if s.get('pill'): f.append(dt(s['pill'], fontfile=MONO, fontsize=22 * S, fontcolor='white', x='(w-tw)/2', y=28 * S, box=1, boxcolor='0x0b0f14@0.7', boxborderw=12 * S))
    lines.append(','.join(f) + f'[s{i}];'); labels.append(f'[s{i}]')
    if s.get('cursor'): cursor_specs.append((offset, offset + length, s['cursor']))
    offset += length
lines.append(''.join(labels) + f'concat=n={len(labels)}:v=1:a=0[base];')

cur = '[base]'; n = 0
if cursor_specs:
    ri = len(inputs); ci = ri + 1; pi = ri + 2
    for seg_start, seg_end, c in cursor_specs:
        x0, y0 = [v * S for v in c['rest']] if 'rest' in c else [W - 160 * S, H - 100 * S]; clicks = []
        # chain the moves: each starts where the previous ended; smootherstep along a quadratic Bezier bowed sideways
        xe, ye = f'{x0:.1f}+if(lt(t,{seg_start + c["moves"][0]["start"]:.3f}),2*sin(t*1.7),0)', f'{y0:.1f}'
        px, py = x0, y0
        for m in c['moves']:
            t0, t1 = seg_start + m['start'], seg_start + m['end']; x1, y1 = m['to'][0] * S, m['to'][1] * S
            xc, yc = (px + x1) / 2 + 70 * S, (py + y1) / 2 - 90 * S
            u = f'clip((t-{t0:.3f})/{t1 - t0:.3f},0,1)'; sm = f'({u}^3*({u}*(6*{u}-15)+10))'
            bez = lambda a0, ac, a1: f'((1-{sm})^2*{a0:.1f}+2*(1-{sm})*{sm}*{ac:.1f}+{sm}^2*{a1:.1f})'
            xe = f'if(lt(t,{t0:.3f}),{xe},{bez(px, xc, x1)})'; ye = f'if(lt(t,{t0:.3f}),{ye},{bez(py, yc, y1)})'
            if m.get('click') is not None: clicks.append((seg_start + m['click'], x1, y1))
            px, py = x1, y1
        for tc, x1, y1 in clicks:
            lines.append(f'[{ri}:v]format=rgba,tpad=start_duration={tc:.3f}:color=0x00000000[rp{n}];')
            lines.append(f'[{cur[1:-1]}][rp{n}]overlay=x={x1 - 36 * S:.0f}:y={y1 - 36 * S:.0f}:eof_action=pass[b{n}];'); cur = f'[b{n}]'; n += 1
        pressed = '*'.join(f'not(between(t,{tc:.3f},{tc + 0.15:.3f}))' for tc, _, _ in clicks) or '1'
        lines.append(f'{cur}[{ci}:v]overlay=eval=frame:shortest=1:enable={q(f"between(t,{seg_start:.3f},{seg_end:.3f})*{pressed}")}:x={q(xe + f"-{TIP}")}:y={q(ye + f"-{TIP}")}[b{n}];'); cur = f'[b{n}]'; n += 1
        if clicks:
            en = '+'.join(f'between(t,{tc:.3f},{tc + 0.15:.3f})' for tc, _, _ in clicks)
            lines.append(f'{cur}[{pi}:v]overlay=eval=frame:shortest=1:enable={q(en)}:x={q(xe + f"-{TIP}")}:y={q(ye + f"-{TIP}")}[b{n}];'); cur = f'[b{n}]'; n += 1
lines[-1] = lines[-1][:-1]  # drop the trailing ';'
lines[-1] = lines[-1].replace(cur, '[v]') if lines[-1].endswith(cur) else lines[-1]

script = spec['output'] + '.filter.txt'
open(script, 'w').write('\n'.join(lines) + '\n')
cmd = ['ffmpeg', '-v', 'error', '-y', '-filter_complex_threads', '1']
for p in inputs: cmd += ['-i', p]
if cursor_specs: cmd += ['-thread_queue_size', '4096', '-framerate', str(FPS), '-i', RIPPLE, '-thread_queue_size', '4096', '-framerate', str(FPS), '-loop', '1', '-i', CURSOR, '-thread_queue_size', '4096', '-framerate', str(FPS), '-loop', '1', '-i', PRESS]
cmd += ['-filter_complex_script', script, '-map', '[v]', '-r', str(FPS), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', str(spec.get('crf', 16)), '-preset', 'medium', '-threads', '4', '-movflags', '+faststart', '-an', spec['output']]
subprocess.run(cmd, check=True)
dur = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', spec['output']]).decode().strip()
print(f"{spec['output']} {float(dur):.2f}s, {len(spec['segments'])} segments")
