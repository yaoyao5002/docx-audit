# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a vulnerability that could expose document contents or execute untrusted input. Contact the maintainer privately through the email address listed on the maintainer's GitHub profile.

Include the affected version, a minimal reproduction, and the security impact. Do not include confidential documents, credentials, or personal data.

## Security model

`docx-audit` treats every DOCX file as untrusted input. It reads selected XML parts from the ZIP container and does not execute macros, embedded scripts, external commands, or network requests. Resource exhaustion from unusually large or highly compressed documents is not yet fully mitigated; only inspect files from sources you are authorized to handle.
