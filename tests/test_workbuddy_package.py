import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_workbuddy_package.py"


def frontmatter_fields(content: str) -> dict[str, str]:
    if not content.startswith("---\n"):
        raise ValueError("missing frontmatter start")
    block, separator, _ = content[4:].partition("\n---\n")
    if not separator:
        raise ValueError("missing frontmatter end")
    fields: dict[str, str] = {}
    for line in block.splitlines():
        key, separator, value = line.partition(":")
        if not separator or not key.strip():
            raise ValueError(f"invalid frontmatter line: {line}")
        fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / "video-tutorial-skill-workbuddy.zip"
        result = subprocess.run(
            [sys.executable, str(BUILDER), "--output", str(output)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            print("FAIL WorkBuddy 打包脚本执行失败")
            print(result.stdout, result.stderr)
            return 1
        if not output.is_file():
            print("FAIL 未生成 WorkBuddy ZIP")
            return 1

        with zipfile.ZipFile(output) as archive:
            names = set(archive.namelist())
            prefix = "video-tutorial-skill/"
            required = {
                prefix + "SKILL.md",
                prefix + "LICENSE",
                prefix + "references/workflow.md",
                prefix + "references/docx-standard.md",
                prefix + "references/browser-access.md",
                prefix + "references/evaluation-scenarios.md",
                prefix + "scripts/validate_article.py",
            }
            missing = sorted(required - names)
            if missing:
                print("FAIL WorkBuddy ZIP 缺少文件：" + ", ".join(missing))
                return 1

            skill = archive.read(prefix + "SKILL.md").decode("utf-8")
            try:
                metadata = frontmatter_fields(skill)
            except ValueError as exc:
                print(f"FAIL WorkBuddy YAML frontmatter 无法解析：{exc}")
                return 1
            required_frontmatter = (
                "name",
                "description",
                "description_zh",
                "description_en",
                "version",
                "author",
            )
            missing_fields = [item for item in required_frontmatter if not metadata.get(item)]
            if missing_fields:
                print("FAIL WorkBuddy 元数据缺少：" + ", ".join(missing_fields))
                return 1
            if "绕过登录" not in skill or "已登录会话" not in skill:
                print("FAIL WorkBuddy Skill 未说明登录边界")
                return 1

    print("PASS WorkBuddy 兼容包结构与元数据检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
