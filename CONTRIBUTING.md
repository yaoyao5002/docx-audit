# Contributing

Thank you for helping improve `docx-audit`.

## Before opening an issue

- Confirm the behavior with the latest version.
- Remove all confidential, personal, and proprietary content.
- Prefer a minimal synthetic DOCX that reproduces the problem.
- Explain the expected result and the actual result.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Keep runtime dependencies at zero unless a feature cannot reasonably be implemented with the Python standard library. New checks should include a focused test and should avoid collecting or transmitting document content.

## Pull requests

Use a short, descriptive title. Explain the user-facing problem, the implementation, and how you tested it. Do not commit real contracts or other sensitive documents.
