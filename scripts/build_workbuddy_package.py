#!/usr/bin/env python3
"""Build a clean WorkBuddy-compatible ZIP from the canonical Agent Skill."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "video-tutorial-skill"
VERSION = "1.1.0"


def skill_body() -> str:
    content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n.*?\r?\n---\r?\n", content, re.DOTALL)
    if not match:
        raise ValueError("Canonical SKILL.md is missing valid YAML frontmatter")
    return content[match.end() :].lstrip()


def workbuddy_skill() -> str:
    frontmatter = f"""---
name: {PACKAGE_NAME}
display_name: 视频拆解与复刻图文教程
display_name_en: Video Tutorial Reproduction Guide
description: Use when converting Douyin, Xiaohongshu, or other short-video sources into factual and reproducible Chinese image-and-text tutorials or DOCX articles.
description_zh: 将抖音、小红书等短视频真实拆解为可供初学者复刻的中文图文教程，并评估可复刻程度。
description_en: Convert short-video sources into evidence-based, reproducible Chinese tutorials with a feasibility review.
category: writing
version: {VERSION}
author: star-ven
---

"""
    adapter = """> WorkBuddy 运行说明：访问抖音或小红书前，先读取 @references/browser-access.md。优先复用当前受控浏览器的已登录会话；只有运行时明确支持用户授权的 Chrome 标签页时才能使用外部 Chrome。“复用已登录会话”不是“绕过登录”，不得读取 Cookie、令牌或浏览器配置。

"""
    return frontmatter + adapter + skill_body()


def add_bytes(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def build(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    prefix = f"{PACKAGE_NAME}/"
    files = [
        "LICENSE",
        "references/workflow.md",
        "references/docx-standard.md",
        "references/browser-access.md",
        "references/evaluation-scenarios.md",
        "scripts/validate_article.py",
    ]
    with zipfile.ZipFile(output, "w") as archive:
        add_bytes(archive, prefix + "SKILL.md", workbuddy_skill().encode("utf-8"))
        for relative in files:
            add_bytes(archive, prefix + relative, (ROOT / relative).read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 WorkBuddy 可上传的 Skill ZIP")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "dist" / f"{PACKAGE_NAME}-workbuddy.zip",
        help="输出 ZIP 路径",
    )
    args = parser.parse_args()
    build(args.output.resolve())
    print(f"PASS WorkBuddy Skill 已生成：{args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
