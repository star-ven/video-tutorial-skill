# Video Tutorial Skill

一个同时面向 Codex、WorkBuddy 与兼容 Agent Skills 运行时的中文工作流：把抖音、小红书等平台上的教程或 AI 视频作品，整理为有依据、可评测、能让初学者跟做的图文教程。

## 能做什么

- 先判断来源是教程、作品展示还是工具披露，再给出推荐方案并等待确认。
- 分开记录来源画面事实、创作者披露、官方资料和复刻方案。
- 教程视频按真实步骤重建；纯作品补充人物一致性、分镜、镜头语言、剪辑与声音分析。
- 明确可复刻程度、限制、成本、失败点和替代路径。
- 提供 DOCX 图片、标题、字幕裁切和交付规范。
- 使用附带脚本检查图片居中、图片标题、证据声明和常见残留。
- 根据运行时选择公开网页、已登录内置浏览器或用户授权的 Chrome 标签页，并在无法控制 Chrome 时安全降级。

该 Skill 不会把推断冒充创作者的原始参数、模型、提示词或隐藏流程。

## 安装

### Codex / Agent Skills

把仓库克隆到个人 Skill 目录：

```bash
git clone https://github.com/star-ven/video-tutorial-skill.git ~/.codex/skills/video-tutorial-skill
```

也可以将目录放入某个项目的 `.agents/skills/video-tutorial-skill`。

### WorkBuddy

先生成 WorkBuddy 专用 ZIP。它与 Codex 版本共用同一套正文和参考资料，但使用 WorkBuddy 要求的元数据：

```bash
python scripts/build_workbuddy_package.py
```

默认生成 `dist/video-tutorial-skill-workbuddy.zip`。在 WorkBuddy 中打开“技能”→“添加技能”→“上传技能”，选择该 ZIP；也可以把 GitHub 仓库下载到本地后再运行打包脚本。

已发布版本也可直接下载：[WorkBuddy 安装包](https://github.com/star-ven/video-tutorial-skill/raw/refs/heads/main/dist/video-tutorial-skill-workbuddy.zip)。

WorkBuddy 的内置浏览器在用户本人完成登录后可持久复用该登录态。若当前客户端安装的 Browser Use、Agent Browser 或浏览器扩展明确支持用户授权的 Chrome 标签页，Skill 会优先复用现有 Chrome 会话；若没有这种正式能力，Skill 不会读取 Chrome Cookie 或伪装成已经访问，而会请用户在可受控浏览器完成一次登录，或提供视频/录屏/字幕/截图。

## 使用

显式调用：

```text
$video-tutorial-skill
请根据这个创作者链接，先推荐拆解和复刻方案；我确认后再制作图文教程。
```

Skill 默认允许自动发现。每个新作品会先返回一份简短提案，包含内容判断、工具路线、文章重点、配图与篇幅、证据缺口及推荐操作。确认后才进入正式制作。

## 目录

```text
video-tutorial-skill/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── workflow.md
│   ├── docx-standard.md
│   ├── browser-access.md
│   └── evaluation-scenarios.md
├── scripts/build_workbuddy_package.py
├── scripts/validate_article.py
└── tests/
```

## 校验 DOCX

```bash
python scripts/validate_article.py article.docx --min-images 5 --require-links
```

此脚本检查结构性要求，不能替代 DOCX 逐页渲染和人工视觉检查。

## 测试

```bash
python tests/test_repository.py
python tests/test_validator.py
python tests/test_workbuddy_package.py
```

## 许可

[MIT License](LICENSE)
