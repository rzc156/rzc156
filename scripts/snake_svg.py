#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""snake_svg.py —— 自托管「贡献贪吃蛇」生成器

逻辑
----
把 GitHub 贡献热力图看成一个 7 行 × N 周的网格，蛇沿「蛇形顺序」逐格前进：
    第 0 周自上而下，第 1 周自下而上，第 2 周再自上而下 …… 依次类推。
每当蛇走到一个「有贡献的绿色格子」，它就吃掉这块、身体「长一节」。
所以蛇的长度 = 你绿墙里的贡献格子数，且是一节一节长出来的。

输出是一张自带 SMIL 动画的 SVG：蛇在绿墙上蜿蜒前进并逐渐变长，
到末尾停顿一下再循环。纯标准库实现，无第三方依赖。

用法
----
    python3 snake_svg.py --user rzc156 --out snake.svg
    python3 snake_svg.py --user rzc156 --out snake.svg --cell 13 --speed 0.22
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request

ROWS = 7  # 周一列，固定 7 天


# --------------------------------------------------------------------------- #
# 抓取 & 解析
# --------------------------------------------------------------------------- #
def fetch_html(user: str, timeout: int) -> str:
    url = f"https://github.com/users/{user}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "snake-svg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def parse_grid(html: str) -> dict[tuple[int, int], int]:
    """返回 {(row, col): level}，level 0..4。row=星期(0..6)，col=周(0..N-1)。"""
    grid: dict[tuple[int, int], int] = {}
    # id = contribution-day-component-<row>-<col>
    id_re = re.compile(r'id="contribution-day-component-(\d+)-(\d+)"')
    for tag in re.findall(r"<td\b[^>]*>", html):
        if "data-date" not in tag:
            continue
        m = id_re.search(tag)
        lvl = re.search(r'data-level="(\d)"', tag)
        if not (m and lvl):
            continue
        row, col = int(m.group(1)), int(m.group(2))
        grid[(row, col)] = int(lvl.group(1))
    if not grid:
        raise SystemExit(
            "错误：没解析到任何贡献数据。\n"
            "可能是网络失败或 GitHub 页面结构变化，请检查 --user / 网络。"
        )
    return grid


def serpentine(weeks: int):
    """蛇形遍历顺序：偶数列自上而下、奇数列自下而上。"""
    for col in range(weeks):
        order = range(ROWS) if col % 2 == 0 else range(ROWS - 1, -1, -1)
        for row in order:
            yield row, col


# --------------------------------------------------------------------------- #
# 渲染
# --------------------------------------------------------------------------- #
LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}


def render(grid: dict[tuple[int, int], int], *, cell: int, speed: float) -> str:
    weeks = max(c for _, c in grid) + 1
    gap = 3
    pad = 24
    step = cell + gap
    w = pad * 2 + weeks * step - gap
    h = pad * 2 + ROWS * step - gap

    def cx(row: int, col: int) -> tuple[float, float]:
        return (pad + col * step + cell / 2.0,
                pad + row * step + cell / 2.0)

    # 绿墙背景
    cells = []
    for (row, col), lvl in grid.items():
        x = pad + col * step
        y = pad + row * step
        cells.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'rx="2.5" fill="{LEVEL_COLORS.get(lvl, LEVEL_COLORS[0])}"/>'
        )

    # 蛇的路径：按蛇形顺序穿过所有「有贡献」的格子
    greens = [(r, c) for (r, c) in serpentine(weeks) if grid.get((r, c), 0) > 0]

    if len(greens) >= 2:
        pts = [cx(r, c) for (r, c) in greens]
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    elif len(greens) == 1:
        x, y = cx(*greens[0])
        d = f"M {x:.1f} {y:.1f} L {x + 0.01:.1f} {y:.1f}"
    else:
        d = "M 0 0 L 0 0"

    n = max(len(greens), 1)
    dur = max(6.0, min(26.0, n * speed))
    hold = 0.78  # 画满后停顿的比例

    sw = max(5.0, cell * 0.62)
    head_r = sw * 0.72

    anim = (
        f'values="1000;0;0" keyTimes="0;{hold};1" '
        f'dur="{dur:.2f}s" repeatCount="indefinite" calcMode="linear"'
    )
    motion = (
        f'dur="{dur:.2f}s" repeatCount="indefinite" '
        f'keyPoints="0;1;1" keyTimes="0;{hold};1" calcMode="linear" path="{d}"'
    )

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
  <g>{''.join(cells)}</g>

  <!-- 蛇身：蛇皮 = 一层深色描边 + 一层亮绿，随吃随长 -->
  <path d="{d}" fill="none" stroke="#0d1117" stroke-width="{sw + 3.5:.1f}"
        stroke-linecap="round" stroke-linejoin="round" pathLength="1000"
        stroke-dasharray="1000" stroke-dashoffset="1000">
    <animate attributeName="stroke-dashoffset" {anim}/>
  </path>
  <path d="{d}" fill="none" stroke="url(#body)" stroke-width="{sw:.1f}"
        stroke-linecap="round" stroke-linejoin="round" pathLength="1000"
        stroke-dasharray="1000" stroke-dashoffset="1000" filter="url(#glow)">
    <animate attributeName="stroke-dashoffset" {anim}/>
  </path>

  <!-- 蛇头 -->
  <circle r="{head_r:.1f}" fill="#d2ffd2" stroke="#39d353" stroke-width="1.5" filter="url(#glow)">
    <animateMotion {motion}/>
  </circle>

  <text x="{pad}" y="{h - 7}" font-size="11" fill="#8b949e">rzc156 · {len(greens)} contributions eaten</text>
</svg>
'''


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="生成自托管贡献贪吃蛇 SVG")
    p.add_argument("--user", required=True, help="GitHub 用户名")
    p.add_argument("--out", default="snake.svg", help="输出文件（默认 snake.svg）")
    p.add_argument("--cell", type=int, default=12, help="格子边长（默认 12）")
    p.add_argument("--speed", type=float, default=0.22,
                   help="每吃一节的秒数（默认 0.22，越小越快）")
    p.add_argument("--timeout", type=int, default=30, help="抓取超时秒数")
    p.add_argument("--html", default=None,
                   help="改用本地已保存的贡献页面 HTML（离线/测试用）")
    args = p.parse_args(argv)

    if args.html:
        with open(args.html, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
    else:
        html = fetch_html(args.user, args.timeout)
    grid = parse_grid(html)
    svg = render(grid, cell=args.cell, speed=args.speed)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)

    weeks = max(c for _, c in grid) + 1
    greens = sum(1 for v in grid.values() if v > 0)
    print(f"已写出 {args.out}：{weeks} 周 × 7 天，"
          f"{greens} 个贡献格（蛇长 {greens} 节）", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
