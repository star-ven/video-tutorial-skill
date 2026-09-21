import base64
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_article.py"
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def paragraph(text: str, centered: bool = False, drawing: bool = False) -> str:
    props = '<w:pPr><w:jc w:val="center"/></w:pPr>' if centered else ""
    body = '<w:r><w:drawing/></w:r>' if drawing else f"<w:r><w:t>{text}</w:t></w:r>"
    return f"<w:p>{props}{body}</w:p>"


def make_docx(path: Path, valid: bool) -> None:
    disclosure = (
        "本文依据来源画面事实、创作者披露与官方资料整理；以下步骤为我们的复刻方案，"
        "不等于创作者原始完整流程。"
        if valid
        else "完全照搬原作者的精确流程，按红框操作。"
    )
    body = "".join(
        [
            paragraph("AI视频拆解与复刻教程", centered=True),
            paragraph(disclosure),
            paragraph("", centered=valid, drawing=True),
            paragraph("图1：操作界面", centered=valid),
        ]
    )
    document = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>{body}<w:sectPr/></w:body>
</w:document>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("word/document.xml", document)
        archive.writestr("word/media/image1.png", PNG)


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(VALIDATOR), str(path), "--min-images", "1"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        good = temp / "good.docx"
        bad = temp / "bad.docx"
        make_docx(good, True)
        make_docx(bad, False)
        good_result = run_validator(good)
        bad_result = run_validator(bad)
        if good_result.returncode != 0:
            print("FAIL 合格文档被拒绝")
            print(good_result.stdout, good_result.stderr)
            return 1
        if bad_result.returncode == 0:
            print("FAIL 不合格文档未被拒绝")
            return 1
    print("PASS DOCX 校验器正反例测试通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
