# docx-audit

`docx-audit` is a small, privacy-first command-line tool for checking Microsoft Word `.docx` files locally. It is intended for contract, translation, and document-production workflows where accidental residual text or formatting can create real review risk.

The tool never uploads document content and has no runtime dependencies.

## Checks

- Counts CJK characters, useful for English-only delivery checks.
- Detects common unresolved placeholders such as `[Employer Name]`, `{{date}}`, and `<amount>`.
- Reports text colored red, blue, orange, or any other explicit RGB color.
- Inspects the main document plus headers, footers, footnotes, endnotes, and comments when present.
- Produces human-readable or JSON output.

This is a structural/text audit. It does not prove that page layout, pagination, fonts, or tracked changes render correctly in Microsoft Word.

## Install

```bash
python -m pip install .
```

## Use

```bash
docx-audit contract.docx
docx-audit contract.docx --json
docx-audit contract.docx --fail-on-cjk --fail-on-placeholders
```

Exit codes are `0` for success, `1` for an unreadable input, `2` when `--fail-on-cjk` finds CJK text, and `3` when `--fail-on-placeholders` finds placeholders.

## Privacy and safety

All parsing happens on the local machine using Python's standard library. The tool does not execute macros, scripts, embedded objects, or external commands from the document. It reads only selected WordprocessingML XML parts inside the DOCX package.

Do not publish confidential sample documents. Use synthetic fixtures for issues and tests.

## Contributing

Bug reports and focused pull requests are welcome. Please include a minimal synthetic DOCX or XML example that contains no private or proprietary information.

## License

MIT
