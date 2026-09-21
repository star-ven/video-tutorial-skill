from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


def check(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS {message}")
    else:
        print(f"FAIL {message}")
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    required = [
        "README.md",
        "LICENSE",
        "SKILL.md",
        "agents/openai.yaml",
        "references/workflow.md",
        "references/docx-standard.md",
        "scripts/validate_article.py",
    ]
    check(all((ROOT / item).is_file() for item in required), "开源仓库文件齐全", failures)

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
    check("name: video-tutorial-skill" in skill, "Skill 名称正确", failures)
    check("$video-tutorial-skill" in metadata, "默认调用名称正确", failures)

    text_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".txt"}
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in text_files)
    account_placeholder = "<your" + "-account>"
    check(account_placeholder not in combined, "不含发布占位符", failures)
    check(not re.search(r"[A-Za-z]:[\\/]Users[\\/]", combined), "不含本机用户目录", failures)
    check(not re.search(r"(?:ghp_|github_pat_|sk-)[A-Za-z0-9_-]{12,}", combined), "不含常见令牌", failures)
    check(not list(ROOT.rglob("*.docx")), "不包含用户文章", failures)
    check(not list(ROOT.rglob("*.mp4")), "不包含用户视频", failures)
    check(not list(ROOT.rglob("*.png")) and not list(ROOT.rglob("*.jpg")), "不包含用户截图", failures)

    if failures:
        print(f"\n{len(failures)} 项检查未通过。")
        return 1
    print("\nPASS 开源仓库结构与隐私检查通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
