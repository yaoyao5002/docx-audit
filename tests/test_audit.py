from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from zipfile import ZIP_DEFLATED, ZipFile

from docx_audit.cli import audit_docx, main


def make_docx(path: Path) -> None:
    document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:body><w:p>
        <w:r><w:t>Agreement [Employer Name] </w:t></w:r>
        <w:r><w:rPr><w:color w:val="FF0000"/></w:rPr><w:t>寰呯‘璁?/w:t></w:r>
      </w:p></w:body>
    </w:document>"""
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
      <Default Extension="xml" ContentType="application/xml"/>
    </Types>"""
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("word/document.xml", document)


class AuditTests(TestCase):
    def test_audit_finds_cjk_placeholder_and_color(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "sample.docx"
            make_docx(path)
            report = audit_docx(path)
            self.assertEqual(report["cjk_characters"], 3)
            self.assertEqual(report["placeholders"], ["[Employer Name]"])
            self.assertEqual(
                report["colored_text"],
                [{"hex": "FF0000", "name": "red", "characters": 3}],
            )

    def test_fail_flags(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "sample.docx"
            make_docx(path)
            self.assertEqual(main([str(path), "--fail-on-cjk"]), 2)
            self.assertEqual(main([str(path), "--fail-on-placeholders"]), 3)
