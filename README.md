# OpenDirector Day 1 — Event Core

This package contains the first production-quality OpenDirector core primitive:

`DomainEvent`

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest
python -m pytest -q
```

## Files

- `opendirector/core/event.py`
- `tests/test_event.py`
- `docs/event.md`
