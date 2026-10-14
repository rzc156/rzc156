# 极客风 GitHub 主页 · 使用说明

你现在的主页是空白的 —— GitHub 只有存在一个**与你用户名同名的仓库**（`rzc156/rzc156`）
且里面有 `README.md` 时，才会把它渲染到个人主页。

## 结构

```
github-profile/
├── README.md                         # 主页内容（极客风）
└── .github/workflows/snake.yml       # 生成贡献贪吃蛇动画（可选）
```

## 方式 A：一键发布（推荐，我已用 gh 登录你的账号）

在 `github-profile/` 目录下执行：

```bash
git init -b main
git add .
git commit -m "chore: init geek-style profile README"
gh repo create rzc156 --public --source=. --push
```

然后把仓库名保持为 `rzc156` 即可，主页立即生效：
👉 https://github.com/rzc156

## 方式 B：手动

1. GitHub → New repository → 名字填 **`rzc156`** → **Public** → 勾选 Add a README。
2. 用本目录 `README.md` 覆盖它。
3. （可选）把 `.github/workflows/snake.yml` 一起提交，并在
   Settings → Actions → General 里把 Workflow permissions 设为
   **Read and write**，然后手动跑一次 `generate-snake`。

## 说明 / 可改项

- 全部卡片来自公共第三方服务（capsule-render / readme-typing-svg /
  github-readme-stats / activity-graph / trophy / komarev）。首次访问偶尔会有
  缓存或短暂 503，属正常现象。
- 主题色：主绿 `#39d353`、青 `#56d4dd`、背景黑 `#0d1117`。想换风格：
  把 `bg_color=0d1117` 改成 `0d1117` 之外的值，或把 `theme=matrix` 换成
  `tokyonight` / `radical` 等。
- 想换成**英文 / 双语**、或加入邮箱/微信等联系方式，直接改 `README.md` 文本即可。
