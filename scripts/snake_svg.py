#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""snake_svg.py —— 自托管「贡献贪吃蛇」生成器

逻辑
----
把贡献热力图看成 7 行 × N 周的网格，蛇沿「蛇形路径」逐格前进：
    第 0 周自上而下 → 底部横移一格到第 1 周 → 自下而上 → 顶部横移 → ……
路径**只有上下左右四个方向**（正交），没有斜线。

蛇的身体贴着这条路径滑动：
- 头和尾一起沿路径前进（尾巴跟着走，而不是画一条不动的线）；
- 每吃掉一个「有贡献的绿色格子」，身体就**长一节**（尾巴暂停一拍）。

实现用一个 `stroke-dasharray` 窗口在路径上滑动来表现蛇身，
纯标准库生成自带动画（SMIL）的 SVG，无第三方依赖。

用法
----
    python3 snake_svg.py --user rzc156 --out snake.svg
    python3 snake_svg.py --user rzc156 --out snake.svg --cell 13 --base 4 --speed 0.09
    python3 snake_svg.py --html saved.html --frame 120 --out frame.svg   # 调试：静帧
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request

ROWS = 7  # 一周固定 7 天

LEVEL_COLORS = {0: "#161b22", 1: "#0e4429", 2: "#006d32", 3: "#26a641", 4: "#39d353"}
BIG_GAP = 1_000_000  # dash 的 gap：足够大，保证整条路径上只出现一段蛇身


# --------------------------------------------------------------------------- #
def fetch_html(user: str, timeout: int) -> str:
    url = f"https://github.com/users/{user}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "snake-svg/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def parse_grid(html: str) -> dict[tuple[int, int], int]:
    """返回 {(row, col): level}，row=星期(0..6)，col=周(0..N-1)。"""
    grid: dict[tuple[int, int], int] = {}
    id_re = re.compile(r'id="contribution-day-component-(\d+)-(\d+)"')
    for tag in re.findall(r"<td\b[^>]*>", html):
        if "data-date" not in tag:
            continue
        m, lvl = id_re.search(tag), re.search(r'data-level="(\d)"', tag)
        if m and lvl:
            grid[(int(m.group(1)), int(m.group(2)))] = int(lvl.group(1))
    if not grid:
        raise SystemExit("错误：没解析到贡献数据（检查 --user / 网络 / 页面结构）。")
    return grid


def serpentine(weeks: int):
    """正交蛇形顺序：偶数列自上而下、奇数列自下而上。"""
    for col in range(weeks):
        order = range(ROWS) if col % 2 == 0 else range(ROWS - 1, -1, -1)
        for row in order:
            yield row, col


# --------------------------------------------------------------------------- #
def render(grid, *, cell=12, base=4, speed=0.09, frame=None, user="") -> str:
    weeks = max(c for _, c in grid) + 1
    gap, pad = 3, 24
    step = cell + gap
    w = pad * 2 + weeks * step - gap
    h = pad * 2 + ROWS * step - gap

    def center(row, col):
        return (pad + col * step + cell / 2.0, pad + row * step + cell / 2.0)

    order = list(serpentine(weeks))
    n = len(order)
    plen = n - 1  # pathLength：每段 1 格

    bg = "".join(
        f'<rect x="{pad + col * step}" y="{pad + row * step}" '
        f'width="{cell}" height="{cell}" rx="2.5" '
        f'fill="{LEVEL_COLORS.get(lvl, LEVEL_COLORS[0])}"/>'
        for (row, col), lvl in grid.items()
    )

    pts = [center(r, c) for (r, c) in order]
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)

    # 每步的蛇身「长度(按段算) ON[i]」与尾端位置 S[i]
    # 蛇身覆盖格子 [i-li+1 .. i]，对应路径区间 [S, S+ON]，其中 ON = li-1
    eaten = 0
    ON, S = [], []
    for i, (r, c) in enumerate(order):
        if grid.get((r, c), 0) > 0:
            eaten += 1
        li = base + eaten
        on = max(0.6, min(float(li - 1), float(i)))  # 不能长过已走过的距离
        ON.append(on)
        S.append(max(0.0, i - on))
    total_eaten = eaten

    sw = max(5.0, cell * 0.60)
    head_r = sw * 0.70
    footer = (f'<text x="{pad}" y="{h - 7}" font-size="11" fill="#8b949e">'
              f'{user} · {total_eaten} contributions eaten</text>')

    def dash(on, s):
        return f"{on} {BIG_GAP}", f"{(on + BIG_GAP) - s}"

    # ── 静帧（调试）──────────────────────────────────────────────────
    if frame is not None:
        i = max(0, min(frame, n - 1))
        da, do = dash(ON[i], S[i])
        hx, hy = pts[i]
        return _svg(w, h, plen, bg, d, sw, head_r, da, do, hx, hy, "", "", footer)

    # ── 动画 ─────────────────────────────────────────────────────────
    frac = 0.82
    kt = [f"{i / plen * frac:.6f}" for i in range(n)] + ["1"]
    vL, vS = ON + [ON[-1]], S + [S[-1]]
    arr = [dash(on, s)[0] for on, s in zip(vL, vS)]
    off = [dash(on, s)[1] for on, s in zip(vL, vS)]
    dur = max(6.0, min(45.0, n * speed))

    body_anim = (
        f'<animate attributeName="stroke-dasharray" dur="{dur:.2f}s" '
        f'repeatCount="indefinite" calcMode="linear" '
        f'values="{";".join(arr)}" keyTimes="{";".join(kt)}"/>'
        f'<animate attributeName="stroke-dashoffset" dur="{dur:.2f}s" '
        f'repeatCount="indefinite" calcMode="linear" '
        f'values="{";".join(off)}" keyTimes="{";".join(kt)}"/>'
    )
    head_anim = (
        f'<animateMotion dur="{dur:.2f}s" repeatCount="indefinite" '
        f'calcMode="linear" keyPoints="0;1;1" keyTimes="0;{frac};1" path="{d}"/>'
    )
    da0, do0 = dash(ON[0], S[0])
    hx, hy = pts[0]
    return _svg(w, h, plen, bg, d, sw, head_r, da0, do0, hx, hy,
                body_anim, head_anim, footer)


def _svg(w, h, plen, bg, d, sw, head_r, dasharray, dashoffset, hx, hy,
         body_anim, head_anim, footer) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" role="img" aria-label="contribution snake">
  <defs>
    <linearGradient id="body" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#39d353"/>
      <stop offset="100%" stop-color="#7ee787"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect x="0" y="0" width="{w}" height="{h}" rx="8" fill="#0d1117"/>
  <g>{bg}</g>

  <path d="{d}" fill="none" stroke="#0d1117" stroke-width="{sw + 3.5:.1f}"
        stroke-linecap="round" stroke-linejoin="round" pathLength="{plen}"
        stroke-dasharray="{dasharray}" stroke-dashoffset="{dashoffset}">{body_anim}</path>
  <path d="{d}" fill="none" stroke="url(#body)" stroke-width="{sw:.1f}"
        stroke-linecap="round" stroke-linejoin="round" pathLength="{plen}"
        stroke-dasharray="{dasharray}" stroke-dashoffset="{dashoffset}" filter="url(#glow)">{body_anim}</path>

  <circle cx="{hx:.1f}" cy="{hy:.1f}" r="{head_r:.1f}" fill="#d2ffd2"
          stroke="#39d353" stroke-width="1.5" filter="url(#glow)">{head_anim}</circle>

  {footer}
</svg>
'''


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="生成自托管贡献贪吃蛇 SVG")
    p.add_argument("--user", required=True, help="GitHub 用户名")
    p.add_argument("--out", default="snake.svg", help="输出文件")
    p.add_argument("--cell", type=int, default=12, help="格子边长（默认 12）")
    p.add_argument("--base", type=int, default=4, help="初始蛇长（默认 4）")
    p.add_argument("--speed", type=float, default=0.09, help="每格秒数（默认 0.09）")
    p.add_argument("--timeout", type=int, default=30, help="抓取超时秒数")
    p.add_argument("--html", default=None, help="改用本地已保存的贡献页面 HTML")
    p.add_argument("--frame", type=int, default=None,
                   help="调试：只画第 N 步的静帧（不带动画）")
    args = p.parse_args(argv)

    if args.html:
        with open(args.html, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
    else:
        html = fetch_html(args.user, args.timeout)
    grid = parse_grid(html)

    svg = render(grid, cell=args.cell, base=args.base, speed=args.speed,
                 frame=args.frame, user=args.user)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)

    weeks = max(c for _, c in grid) + 1
    greens = sum(1 for v in grid.values() if v > 0)
    sys.stderr.write(f"已写出 {args.out}：{weeks} 周 × 7 天，"
                     f"{greens} 个贡献格（蛇长 = {args.base} + 吃掉数）\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
