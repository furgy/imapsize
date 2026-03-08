# CLAUDE.md - Project Guidance for AI Assistants

This project uses semantic versioning. See [VERSIONING.md](./VERSIONING.md) for details.

## Project Overview
- Python Flask web application for checking IMAP email mailbox sizes
- Simple web app with login, logout, and mailbox size listing

## Key Files
- `main.py` - Flask application entry point
- `imapsize.py` - IMAP size calculation logic
- `VERSION` - Current version (X.Y.Z format)
- `VERSIONING.md` - Versioning requirements

## Development
- Run: `python main.py`
- Uses Flask, Flask-Login, Flask-Caching

## Versioning
Always check VERSION file and bump version according to VERSIONING.md before releasing.
