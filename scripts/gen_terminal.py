"""Generate animated terminal SVGs (dark/light) for the andromaquehere profile README.

Run from anywhere: python scripts/gen_terminal.py (needs pyfiglet).
Writes assets/terminal-dark.svg and assets/terminal-light.svg.
"""
import pyfiglet, html, re, textwrap, os
from pathlib import Path

BASE = Path(__file__).resolve().parent
repo = str(BASE.parent)
MONO = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MUTED = '#848d97'
FS, CW, LH = 14, 8.4, 14
PADX = 20

def logo(dirname, key):
    try:
        svg = open(BASE / dirname / f'{key}.svg').read()
        m = re.search(r'href="(data:image/svg\+xml;base64,[^"]+)"', svg)
        return m.group(1) if m else None
    except FileNotFoundError:
        return None

# ---------- content ----------
art = pyfiglet.figlet_format('andromaquehere', font='ansi_shadow', width=300).rstrip('\n')
art_lines = [l for l in art.split('\n') if l.strip()]
AW = max(len(l) for l in art_lines)
art_lines = [l.ljust(AW) for l in art_lines]
art_w = AW * CW

COL = 38
SKILL_COLS = [
    ('LANGUAGES & FRAMEWORKS', [('rust','Rust'),('go','Go'),('python','Python'),('typescript','TypeScript'),
                                ('nodejs','Node.js'),('dart','Dart'),('flutter','Flutter'),('swift','Swift'),('kotlin','Kotlin')]),
    ('AI', [('claude','Claude Agent SDK'),(None,'OpenAI'),(None,'Codex'),('gemini','Gemini'),
            ('langchain','LangChain'),('ollama','Ollama')]),
    ('TOOLS & INFRA', [('docker','Docker'),('postgresql','PostgreSQL'),('redis','Redis'),('linux','Linux'),('git','Git')]),
]
NCOLS = len(SKILL_COLS)
ROW_CHARS = NCOLS * COL + NCOLS + 1
CWE = art_w / ROW_CHARS
skills = ['┌' + '┬'.join(['─' * COL] * NCOLS) + '┐',
          '│' + '│'.join(' ' + h.ljust(COL - 1) for h, _ in SKILL_COLS) + '│',
          '├' + '┼'.join(['─' * COL] * NCOLS) + '┤']
icon_rows = []
for i in range(max(len(c) for _, c in SKILL_COLS)):
    cells = []
    for ci, (_h, items) in enumerate(SKILL_COLS):
        k, n = items[i] if i < len(items) else (None, '')
        cells.append('    ' + n.ljust(COL - 4))
        if k: icon_rows.append((len(skills), ci, k))
    skills.append('│' + '│'.join(cells) + '│')
skills.append('└' + '┴'.join(['─' * COL] * NCOLS) + '┘')

C1 = 9
C2 = ROW_CHARS - C1 - 3
desc = ('Memory & governance for AI agents — the open hermorah connector for Claude Code: '
        'always-loaded memory at session start, live MCP memory tools, automatic pool sync.')
desc_lines = textwrap.wrap(desc, C2 - 2)
def prow(a, b): return '│ ' + a.ljust(C1 - 1) + '│ ' + b.ljust(C2 - 1) + '│'
projects = ['┌' + '─' * C1 + '┬' + '─' * C2 + '┐',
            prow('PROJECT', 'hermorah'),
            '├' + '─' * C1 + '┼' + '─' * C2 + '┤',
            prow('site', 'hermorah.com'),
            prow('repo', 'github.com/lornn-inc/hermorah-plugin'),
            prow('about', desc_lines[0])]
for dl in desc_lines[1:]:
    projects.append(prow('', dl))
projects.append('└' + '─' * C1 + '┴' + '─' * C2 + '┘')

# ---------- mascot: sitting pixel rabbit, facing left ----------
RABBIT_ART = [
    "....#...#........",
    "...##..##........",
    "...##..##........",
    "...##..##........",
    "...##..##........",
    "...######........",
    "..########.......",
    "..#o######.......",
    "..########.......",
    "...########......",
    "...###########...",
    "...##########tt..",
    "...##..####..tt..",
    "..###..####..##..",
]
RCELL = 6
RAB_W = len(RABBIT_ART[0]) * RCELL
RAB_H = len(RABBIT_ART) * RCELL
TOP = RAB_H + 8                       # свободная полоса над окном под зайца

def rabbit_svg(fg, bg, x_land):
    body, eartip, eye = [], [], None
    for r, row in enumerate(RABBIT_ART):
        for c, ch in enumerate(row):
            if ch == '.': continue
            rect = f'<rect x="{c * RCELL}" y="{r * RCELL}" width="{RCELL}" height="{RCELL}"/>'
            if ch == 'o':
                eye = f'<rect class="eye" x="{c * RCELL}" y="{r * RCELL}" width="{RCELL}" height="{RCELL}"/>'
            elif r <= 1 and c <= 4:   # кончик левого уха
                eartip.append(rect)
            else:
                body.append(rect)
    markup = (f'<g transform="translate({x_land:.0f}, {TOP - RAB_H})"><g class="hop">'
              f'<g fill="{fg}" shape-rendering="crispEdges">{"".join(body)}'
              f'<g class="eartip">{"".join(eartip)}</g></g>{eye}</g></g>')
    css = f'''.hop {{ animation: hopin 2.2s linear 0.4s backwards; }}
    .eye {{ fill: {bg}; animation: blinkeye 4.5s steps(1, end) 3.2s infinite; }}
    .eartip {{ animation: twitch 5.5s steps(1, end) 4s infinite; }}
    @keyframes hopin {{
      0%   {{ transform: translate(300px, 0); }}
      15%  {{ transform: translate(230px, -42px); }}
      30%  {{ transform: translate(170px, 0); }}
      48%  {{ transform: translate(110px, -32px); }}
      64%  {{ transform: translate(55px, 0); }}
      80%  {{ transform: translate(16px, -18px); }}
      92%  {{ transform: translate(0, 0); }}
      100% {{ transform: translate(0, 0); }}
    }}
    @keyframes blinkeye {{ 0%, 90% {{ fill: {bg}; }} 91%, 97% {{ fill: {fg}; }} 98%, 100% {{ fill: {bg}; }} }}
    @keyframes twitch {{ 0%, 88% {{ transform: translateY(0); }} 90%, 93% {{ transform: translateY(2px); }} 95%, 100% {{ transform: translateY(0); }} }}'''
    return markup, css

P_HOME = '~ $'
P_DIR = '~/andromaquehere $'

# (prompt, command, output lines, kind, pad_above_out, pad_below)
SEQ = [
    (P_HOME, 'ls', ['andromaquehere'], 'instant', 22, 26),
    (P_HOME, 'cd andromaquehere && ls', ['README.md    projects.md  skills.md'], 'instant', 22, 26),
    (P_DIR, 'cat README.md', art_lines, 'letters', 38, 42),
    (P_DIR, 'cat skills.md', skills, 'flush', 24, 26),
    (P_DIR, 'cat projects.md', projects, 'flush', 24, 26),
]

# ---------- layout ----------
bar_h = 32
y = bar_h + 26
geo = []                                  # (cmd_y, out_y0)
for prompt, cmd, out, kind, pad_a, pad_b in SEQ:
    cmd_y = y
    out_y0 = cmd_y + pad_a
    y = out_y0 + (len(out) - 1) * LH + pad_b
    geo.append((cmd_y, out_y0))
pF_y = y
win_h = pF_y + 16
win_w = art_w + PADX * 2
rows = round((win_h - bar_h) / LH)
TITLE = f'-zsh — 120×{rows}'

# ---------- timeline ----------
CPS = 0.07
times = []                                # (t_prompt, t_type, d_type, t_out, d_out, t_hide)
t = 0.4
for i, (prompt, cmd, out, kind, *_pads) in enumerate(SEQ):
    t_prompt = t
    t_type = t_prompt + (0.6 if i else 0.1)
    d_type = len(cmd) * CPS
    t_out = t_type + d_type + 0.2
    d_out = {'instant': 0.01, 'letters': 1.6, 'flush': 0.5 if len(out) > 10 else 0.4}[kind]
    t_hide = t_out
    t = t_out + d_out + 0.3
    times.append((t_prompt, t_type, d_type, t_out, d_out, t_hide))
TF = t
print(f'scene ends at {TF:.1f}s')

def text_line(cls, x, yy, s, tl=None):
    tla = f' textLength="{tl:.0f}" lengthAdjust="spacingAndGlyphs"' if tl else ''
    return f'<text class="{cls}" x="{x:.0f}" y="{yy}"{tla} xml:space="preserve">{html.escape(s)}</text>'

def terminal(fg, bg, icon_dir):
    css, body = [], []
    for i, ((prompt, cmd, out, kind, *_p), (cmd_y, out_y0), (t_prompt, t_type, d_type, t_out, d_out, t_hide)) in enumerate(zip(SEQ, geo, times), 1):
        n = len(cmd)
        cmd_x = PADX + (len(prompt) + 1) * CW
        # prompt
        if i == 1:
            css.append(f'.p{i} {{ opacity: 1; }}')
        else:
            css.append(f'.p{i} {{ opacity: 0; animation: on 0.01s linear {t_prompt:.2f}s forwards; }}')
        # command + caret
        css.append(f'.cmd{i} {{ clip-path: inset(0 100% 0 0); animation: reveal {d_type:.2f}s steps({n}, end) {t_type:.2f}s forwards; }}')
        blink = '' if i == 1 else f'blink 1.1s steps(1, end) {t_prompt:.2f}s 1, '
        show = '' if i == 1 else f'on 0.01s linear {t_prompt:.2f}s forwards, '
        op = '' if i == 1 else ' opacity: 0;'
        css.append(f'.caret{i} {{ fill: {fg};{op} animation: {show}{blink}'
                   f'slide{i} {d_type:.2f}s steps({n}, end) {t_type:.2f}s backwards, off 0.01s linear {t_hide:.2f}s forwards; }}')
        css.append(f'@keyframes slide{i} {{ from {{ transform: translateX(0); }} to {{ transform: translateX({n * CW:.0f}px); }} }}')
        # output
        if kind == 'instant':
            css.append(f'.out{i} {{ opacity: 0; animation: on 0.01s linear {t_out:.2f}s forwards; }}')
        elif kind == 'letters':
            css.append(f'.out{i} {{ clip-path: inset(0 100% 0 0); animation: reveal {d_out}s steps(14, end) {t_out:.2f}s forwards; }}')
        else:
            css.append(f'.out{i} {{ clip-path: inset(0 0 100% 0); animation: flush {d_out}s steps({len(out)}, end) {t_out:.2f}s forwards; }}')
        # body
        body.append(f'<text class="p{i} muted" x="{PADX}" y="{cmd_y}" xml:space="preserve">{html.escape(prompt)}</text>')
        body.append(f'<text class="cmd{i}" x="{cmd_x:.0f}" y="{cmd_y}" textLength="{n * CW:.0f}" lengthAdjust="spacingAndGlyphs">{html.escape(cmd)}</text>')
        body.append(f'<rect class="caret{i}" x="{cmd_x:.0f}" y="{cmd_y - 12}" width="{CW}" height="15" />')
        lines_svg = []
        stretch = art_w if kind in ('letters', 'flush') else None
        cls = 'art' if kind == 'letters' else 'tbl'
        for j, l in enumerate(out):
            lines_svg.append(text_line(cls, PADX, out_y0 + j * LH, l, stretch))
        if kind == 'flush' and out is skills:
            for ri, ci, key in icon_rows:
                data = logo(icon_dir, key)
                if not data: continue
                cell_start = 1 + ci * (COL + 1)
                x = PADX + (cell_start + 1) * CWE
                lines_svg.append(f'<image x="{x:.1f}" y="{out_y0 + ri * LH - 11.5:.1f}" width="15" height="15" href="{data}" />')
        body.append(f'<g class="out{i}">\n    ' + '\n    '.join(lines_svg) + '\n  </g>')
    # final prompt
    fin_x = PADX + (len(P_DIR) + 1) * CW
    css.append(f'.pF {{ opacity: 0; animation: on 0.01s linear {TF:.2f}s forwards; }}')
    css.append(f'.caretF {{ fill: {fg}; opacity: 0; animation: on 0.01s linear {TF:.2f}s forwards, blink 1.1s steps(1, end) {TF:.2f}s infinite; }}')
    body.append(f'<text class="pF muted" x="{PADX}" y="{pF_y}" xml:space="preserve">{html.escape(P_DIR)}</text>')
    body.append(f'<rect class="caretF" x="{fin_x:.0f}" y="{pF_y - 12}" width="{CW}" height="15" />')

    all_cmd = ', '.join(f'.cmd{i}' for i in range(1, len(SEQ) + 1))
    all_out = ', '.join(f'.out{i}' for i in range(1, len(SEQ) + 1))
    all_caret = ', '.join(f'.caret{i}' for i in range(1, len(SEQ) + 1))
    all_p = ', '.join(f'.p{i}' for i in range(2, len(SEQ) + 1))
    css_s = '\n    '.join(css)
    body_s = '\n  '.join(body)
    rab_markup, rab_css = rabbit_svg(fg, bg, win_w - 190)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {win_w:.0f} {win_h + TOP}" role="img" aria-label="terminal session: ls, cd andromaquehere, then cat README.md, skills.md and projects.md">
  <style>
    text {{ font-family: {MONO}; font-size: {FS}px; fill: {fg}; }}
    .muted {{ fill: {MUTED}; }}
    .title {{ font-family: {SANS}; font-size: 12px; fill: {MUTED}; }}
    {css_s}
    {rab_css}
    @keyframes reveal {{ to {{ clip-path: inset(0 0 0 0); }} }}
    @keyframes flush  {{ to {{ clip-path: inset(0 0 0 0); }} }}
    @keyframes on     {{ to {{ opacity: 1; }} }}
    @keyframes off    {{ to {{ opacity: 0; }} }}
    @keyframes blink  {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{
      {all_cmd}, {all_out} {{ animation: none; clip-path: none; opacity: 1; }}
      {all_caret} {{ animation: none; opacity: 0; }}
      {all_p}, .pF, .caretF {{ animation: none; opacity: 1; }}
      .hop, .eartip, .eye {{ animation: none; }}
    }}
  </style>
  {rab_markup}
  <g transform="translate(0, {TOP})">
  <rect x="0.5" y="0.5" width="{win_w - 1:.0f}" height="{win_h - 1}" rx="10" fill="{bg}" stroke="{MUTED}" stroke-opacity="0.55" />
  <circle cx="22" cy="16" r="5.5" fill="none" stroke="{MUTED}" /><circle cx="42" cy="16" r="5.5" fill="none" stroke="{MUTED}" /><circle cx="62" cy="16" r="5.5" fill="none" stroke="{MUTED}" />
  <text class="title" x="{win_w / 2:.0f}" y="20" text-anchor="middle">{TITLE}</text>
  <line x1="0.5" y1="{bar_h + 0.5}" x2="{win_w - 0.5:.0f}" y2="{bar_h + 0.5}" stroke="{MUTED}" stroke-opacity="0.55" />

  {body_s}
  </g>
</svg>
'''

open(f'{repo}/assets/terminal-dark.svg', 'w').write(terminal('#ffffff', '#000000', 'badges'))
open(f'{repo}/assets/terminal-light.svg', 'w').write(terminal('#000000', '#ffffff', 'badges-black'))
print(f'terminal {win_w:.0f}x{win_h}, title "{TITLE}", '
      f"dark {os.path.getsize(f'{repo}/assets/terminal-dark.svg') // 1024}KB")
