# 极客风 GitHub 主页 · 使用说明

个人主页 = 一个**与用户名同名的仓库**（`rzc156/rzc156`）里的 `README.md`。
本套按「国内网络可达」重做，**不使用任何 `*.vercel.app` / komarev**（在你的网络下不加载），
所有统计/图形资源要么来自国内可达服务，要么**自托管 + jsDelivr**。

## 目录结构

```
github-profile/
├── README.md                        # 主页内容（极客风）
├── assets/
│   ├── header.svg                   # 自托管终端横幅（替代 capsule-render）
│   ├── metrics.base.svg             # 自托管统计卡 + 语言（Actions 生成）
│   ├── metrics.isocalendar.svg      # 自托管贡献日历（Actions 生成）
│   └── snake.svg                    # 自托管贡献贪吃蛇（脚本生成）
├── scripts/
│   └── snake_svg.py                 # 贪吃蛇生成器：每吃一个贡献格长一节
└── .github/workflows/
    ├── metrics.yml                  # 生成 assets/metrics.*.svg
    └── snake.yml                    # 生成 assets/snake.svg
```

## 依赖来源（已逐一实测可加载）

| 元素 | 来源 | 说明 |
|:--|:--|:--|
| 顶部横幅 | 自托管 `assets/header.svg` | jsDelivr 分发 |
| 打字机动画 | `readme-typing-svg.demolab.com` | ✅ 国内可达 |
| 统计卡 / 语言 / 日历 | 自托管 `assets/metrics.*.svg` | Actions 生成后提交 |
| 连续贡献 (streak) | `streak-stats.demolab.com` | ✅ |
| 徽章墙 | `img.shields.io` | ✅ |
| 贪吃蛇 | 自托管 `assets/snake.svg` | `scripts/snake_svg.py` 生成 |

> 自托管资源统一走 **jsDelivr**：`https://cdn.jsdelivr.net/gh/rzc156/rzc156@main/<path>`

## 贪吃蛇逻辑（scripts/snake_svg.py）

- 把贡献热力图当成 7 行 × N 周的网格，蛇按**蛇形顺序**逐格前进
  （第 0 周自上而下、第 1 周自下而上 ……）。
- 每走到一个**有贡献的绿色格子**就吃掉它，身体**长一节**：
  蛇的长度 = 绿墙里的贡献格子数，且是一节一节长出来的。
- 生成自带 SMIL 动画的 SVG（画满后停顿再循环），纯标准库、无第三方依赖。

手动生成 / 调参：

```bash
python3 scripts/snake_svg.py --user rzc156 --out assets/snake.svg
# 可选：--cell 13（格子更大） --speed 0.15（更快）
# 离线/CI：--html saved_contributions_page.html
```

> 说明：脚本读取的是 GitHub **公开**贡献页 `/users/<user>/contributions`
> （与访客看到的绿墙一致）。若开启了「包含私有仓库贡献」，公开页也会体现。

## 发布 / 更新

```bash
cd github-profile
git add -A && git commit -m "update profile" && git push
```

- `metrics.yml`（每天）与 `snake.yml`（每 12h）自动重跑并提交最新 SVG；
  也可在 Actions 页点 **Run workflow** 手动触发。
- 需在 Settings → Actions → General 将 Workflow permissions 设为
  **Read and write**（已配置好）。
- metrics 读取跨仓库数据需要 `METRICS_TOKEN` 密钥（已用 gh token 配置）；
  没有它时统计卡会退化为只读当前仓库（语言会显示 0）。

## 维护 & 排错

- **缓存**：jsDelivr 对 `@main` 最长缓存约 12h。立即刷新：
  `https://purge.jsdelivr.net/gh/rzc156/rzc156@main/assets/snake.svg`
- **换配色**：改 `assets/header.svg`、`scripts/snake_svg.py` 里的色值，
  以及 `README.md` 中各服务参数（`background=0d1117` / `color=39d353`）。
- **本地预览**：`assets/*.svg` 直接用浏览器打开即可。
