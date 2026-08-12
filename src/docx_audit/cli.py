from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
PLACEHOLDER_PATTERNS = (
    re.compile(r"\[[^\]\r\n]{1,120}\]"),
    re.compile(r"\{\{[^}\r\n]{1,120}\}\}"),
    re.compile(r"<[^<>\r\n]{1,120}>")
)
COLOR_NAMES = {
    "FF0000": "red",
    "0000FF": "blue",
    "FFA500": "orange",
}


def _word_xml_names(names: list[str]) -> list[str]:
    return sorted(
        name for name in names
        if name == "word/document.xml"
        or re.fullmatch(r"word/(header|footer)\d+\.xml", name)
        or name in {"word/footnotes.xml", "word/endnotes.xml", "word/comments.xml"}
    )


def audit_docx(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    if not zipfile.is_zipfile(path):
        raise ValueError("not a valid DOCX/ZIP container")

    all_text: list[str] = []
    color_chars: Counter[str] = Counter()
    parts: list[str] = []

    with zipfile.ZipFile(path) as archive:
        for name in _word_xml_names(archive.namelist()):
            parts.append(name)
            root = ET.fromstring(archive.read(name))
            for run in root.findall(".//w:r", NS):
                text = "".join(node.text or "" for node in run.findall(".//w:t", NS))
                all_text.append(text)
                color = run.find("./w:rPr/w:color", NS)
                if color is not None:
                    value = color.get(f"{{{W_NS}}}val", "").upper()
                    if value and value not in {"AUTO", "NONE"}:
                        color_chars[value] += len(text)

    text = "".join(all_text)
    placeholders = []
    for pattern in PLACEHOLDER_PATTERNS:
        placeholders.extend(pattern.findall(text))
    placeholders = list(dict.fromkeys(placeholders))

    colors = [
        {
            "hex": hex_value,
            "name": COLOR_NAMES.get(hex_value, "other"),
            "characters": count,
        }
        for hex_value, count in sorted(color_chars.items())
    ]

    return {
        "file": str(path.resolve()),
        "text_characters": len(text),
        "cjk_characters": len(CJK_RE.findall(text)),
        "placeholders": placeholders,
        "colored_text": colors,
        "parts_checked": parts,
    }


def _print_human(report: dict) -> None:
    print(f"File: {report['file']}")
    print(f"Text characters: {report['text_characters']}")
    print(f"CJK characters: {report['cjk_characters']}")
    placeholders = report["placeholders"]
    print(f"Placeholders: {len(placeholders)}")
    for value in placeholders:
        print(f"  - {value}")
    print("Colored text:")
    if not report["colored_text"]:
        print("  - none")
    for item in report["colored_text"]:
        print(f"  - {item['name']} #{item['hex']}: {item['characters']} characters")
    print(f"Parts checked: {len(report['parts_checked'])}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docx-audit",
        description="Inspect DOCX files locally without uploading their contents.",
    )
    parser.add_argument("file", type=Path, help="DOCX file to inspect")
    parser.add_argument("--json", action="store_true", help="output machine-readable JSON")
    parser.add_argument(
        "--fail-on-cjk",
        action="store_true",
        help="return exit code 2 if CJK characters remain",
    )
    parser.add_argument(
        "--fail-on-placeholders",
        action="store_true",
        help="return exit code 3 if placeholders remain",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = audit_docx(args.file)
    except (FileNotFoundError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"docx-audit: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report)

    if args.fail_on_cjk and report["cjk_characters"]:
        return 2
    if args.fail_on_placeholders and report["placeholders"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
