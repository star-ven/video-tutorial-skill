#!/usr/bin/env python3
"""Validate structural requirements for a video breakdown tutorial DOCX."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(f"{W}t")).strip()


def paragraph_alignment(paragraph: ET.Element) -> str:
    properties = paragraph.find(f"{W}pPr")
    if properties is None:
        return ""
    alignment = properties.find(f"{W}jc")
    return "" if alignment is None else alignment.attrib.get(f"{W}val", "")


def external_link_count(archive: zipfile.ZipFile) -> int:
    rel_path = "word/_rels/document.xml.rels"
    if rel_path not in archive.namelist():
        return 0
    root = ET.fromstring(archive.read(rel_path))
    return sum(
        1
        for rel in root.findall(f"{PKG_REL}Relationship")
        if rel.attrib.get("TargetMode") == "External"
    )


def validate(path: Path, min_images: int, require_links: bool) -> list[str]:
    failures: list[str] = []
    if not path.exists():
        return [f"文件不存在：{path}"]
    if path.suffix.lower() != ".docx":
        return ["交付文件必须是 DOCX"]

    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if "word/document.xml" not in names:
                return ["DOCX 缺少 word/document.xml"]
            root = ET.fromstring(archive.read("word/document.xml"))
            paragraphs = list(root.iter(f"{W}p"))
            full_text = "\n".join(paragraph_text(p) for p in paragraphs)
            media_files = [name for name in names if name.startswith("word/media/") and not name.endswith("/")]
            drawing_paragraphs = [p for p in paragraphs if p.find(f".//{W}drawing") is not None]
            captions = [p for p in paragraphs if re.match(r"^图\s*\d+\s*[：:]", paragraph_text(p))]

            if len(media_files) < min_images:
                failures.append(f"嵌入图片不足：{len(media_files)} < {min_images}")
            if len(drawing_paragraphs) < min_images:
                failures.append(f"正文图片不足：{len(drawing_paragraphs)} < {min_images}")

            uncentered_images = [p for p in drawing_paragraphs if paragraph_alignment(p) != "center"]
            if uncentered_images:
                failures.append(f"存在 {len(uncentered_images)} 个未居中的图片段落")

            if drawing_paragraphs and not captions:
                failures.append("未找到“图 1：……”格式的图片标题")
            uncentered_captions = [p for p in captions if paragraph_alignment(p) != "center"]
            if uncentered_captions:
                failures.append(f"存在 {len(uncentered_captions)} 个未居中的图片标题")

            evidence_terms = ("来源画面事实", "创作者披露", "官方资料", "复刻方案")
            missing_evidence = [term for term in evidence_terms if term not in full_text]
            if missing_evidence:
                failures.append("证据声明缺少：" + "、".join(missing_evidence))

            if not re.search(r"(不等于|不代表|并非).{0,18}(创作者|博主).{0,18}(原始|完整).{0,10}(流程|操作)", full_text):
                failures.append("缺少“复刻方案不等于创作者原始完整流程”的声明")

            red_box_references = re.findall(r"红框|红色框|红色方框", full_text)
            if red_box_references:
                failures.append("正文仍含 red_box 操作指引或残留说明")
            if "**" in full_text:
                failures.append("正文包含 Markdown 加粗标记 **")
            if re.search(r"<\s*(html|body|div)\b", full_text, re.I):
                failures.append("正文疑似包含 HTML 残留")
            if require_links and external_link_count(archive) == 0:
                failures.append("未找到可点击的外部来源/官方链接")
    except zipfile.BadZipFile:
        failures.append("文件不是有效的 DOCX/ZIP 包")
    except ET.ParseError as exc:
        failures.append(f"DOCX XML 无法解析：{exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="检查视频拆解复刻教程 DOCX 的关键结构")
    parser.add_argument("docx", type=Path, help="待检查的 DOCX 文件")
    parser.add_argument("--min-images", type=int, default=1, help="最少嵌入图片数")
    parser.add_argument("--require-links", action="store_true", help="要求至少一个外部超链接")
    args = parser.parse_args()

    failures = validate(args.docx, max(args.min_images, 0), args.require_links)
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        print(f"\n{len(failures)} 项检查未通过。")
        return 1
    print("PASS DOCX 结构、证据声明、图片与图片标题居中检查通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
