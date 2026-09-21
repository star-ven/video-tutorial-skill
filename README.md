# Video Tutorial Skill

一个面向 Codex/Agent Skills 的中文工作流：把抖音、小红书等平台上的教程或 AI 视频作品，整理为有依据、可评测、能让初学者跟做的图文教程。

## 能做什么

- 先判断来源是教程、作品展示还是工具披露，再给出推荐方案并等待确认。
- 分开记录来源画面事实、创作者披露、官方资料和复刻方案。
- 教程视频按真实步骤重建；纯作品补充人物一致性、分镜、镜头语言、剪辑与声音分析。
- 明确可复刻程度、限制、成本、失败点和替代路径。
- 提供 DOCX 图片、标题、字幕裁切和交付规范。
- 使用附带脚本检查图片居中、图片标题、证据声明和常见残留。

该 Skill 不会把推断冒充创作者的原始参数、模型、提示词或隐藏流程。

## 安装

把仓库克隆到个人 Skill 目录：

```bash
git clone https://github.com/<your-account>/video-tutorial-skill.git ~/.codex/skills/video-tutorial-skill
```

也可以将目录放入某个项目的 `.agents/skills/video-tutorial-skill`。

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
│   └── evaluation-scenarios.md
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
```

## 许可

[MIT License](LICENSE)
