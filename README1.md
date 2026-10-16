# AVIP 2026 — Cybersecurity Python Tasks

Two command-line projects implemented in Python 3 using the Task 1 and Task 2 requirements.

## Task 1 — Caesar Cipher Toolkit

Features:
- Encrypt and decrypt with any integer shift.
- Preserve case, punctuation, digits, and whitespace.
- Brute-force all 26 shifts and rank candidates using a lightweight English-word heuristic.
- Optional dictionary API checks with `--api`.

Usage:
```bash
python caesar_cipher.py encrypt "Hello, World!" --shift 3
python caesar_cipher.py decrypt "Khoor, Zruog!" --shift 3
python caesar_cipher.py crack "Khoor zruog"
python caesar_cipher.py crack "Khoor zruog" --api --threshold 0.90
```

The confidence value is a heuristic, not a calibrated statistical probability. Dictionary API checks require internet access; if unavailable, the tool falls back to its local heuristic.
