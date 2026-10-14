# 极客风 GitHub 主页 · 使用说明

个人主页 = 一个**与用户名同名的仓库**（`rzc156/rzc156`）里的 `README.md`。
本套已按「国内网络可达」重做，**不再使用任何 `*.vercel.app`**（capsule-render /
github-readme-stats / activity-graph / trophy 在国内常被墙）。

## 目录结构

```
github-profile/
├── README.md                        # 主页内容（极客风）
├── assets/
│   └── header.svg                   # 自托管终端横幅（替代 capsule-render）
└── .github/workflows/
    ├── metrics.yml                  # 生成 assets/metrics.*.svg（自托管统计卡）
    └── snake.yml                    # 生成 output 分支的贡献贪吃蛇
```

## 依赖来源（已逐一实测可加载）

| 元素 | 来源 | 说明 |
|:--|:--|:--|
| 顶部横幅 | **本仓库自托管** `assets/header.svg` | 经 jsDelivr 分发 |
| 打字机动画 | `readme-typing-svg.demolab.com` | ✅ 国内可达 |
| 统计卡 / 语言 / 日历 | **本仓库自托管** `assets/metrics.*.svg` | 由 Actions 生成后提交 |
| 连续贡献 (streak) | `streak-stats.demolab.com` | ✅ |
| 徽章墙 | `img.shields.io` | ✅ |
| 访问计数 | `komarev.com` | ✅ |
| 贪吃蛇 | **本仓库自托管** `output` 分支 | 经 jsDelivr 分发 |

> 自托管资源统一走 **jsDelivr**：`https://cdn.jsdelivr.net/gh/rzc156/rzc156@main/<path>`
> （国内可访问；若偶尔 404，等几秒再刷新，CDN 首次会去回源 GitHub）。

## 发布 / 更新

```bash
cd github-profile
git add -A
git commit -m "update profile"
git push
```

- `metrics.yml` 与 `snake.yml` 每天定时自动重跑并提交最新 SVG；
  也可在 Actions 页面点 **Run workflow** 手动触发。
- 首次部署需已在 Settings → Actions → General 将
  Workflow permissions 设为 **Read and write**（已配置好）。

## 维护 & 排错

- **缓存**：jsDelivr 对 `@main` 分支最长缓存约 12h。想立即刷新：
  `https://purge.jsdelivr.net/gh/rzc156/rzc156@main/assets/metrics.base.svg`
- **换配色**：改 `README.md` 里各服务参数（`background=0d1117` /
  `color=39d353`）以及 `assets/header.svg` 里的色值即可。
- **本地预览**：`assets/header.svg` 可直接用浏览器打开。
