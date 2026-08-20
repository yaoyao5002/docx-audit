from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile

from docx_audit.cli import audit_docx, main


def make_docx(path: Path) -> None:
    cjk_text = "\u5f85\u786e\u8ba4"
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:body><w:p>
        <w:r><w:t>Agreement [Employer Name] </w:t></w:r>
        <w:r><w:rPr><w:color w:val="FF0000"/></w:rPr><w:t>{cjk_text}</w:t></w:r>
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

    def test_directory_batch_scan(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            make_docx(root / "first.docx")
            make_docx(root / "second.docx")
            with patch("builtins.print") as mocked_print:
                self.assertEqual(main([str(root)]), 0)
            output = "\n".join(str(call.args[0]) for call in mocked_print.call_args_list if call.args)
            self.assertIn("first.docx", output)
            self.assertIn("second.docx", output)

    def test_recursive_scan(self):
        with TemporaryDirectory() as directory:
            nested = Path(directory) / "nested"
            nested.mkdir()
            make_docx(nested / "sample.docx")
            self.assertEqual(main([directory]), 1)
            self.assertEqual(main([directory, "--recursive"]), 0)

