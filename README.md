# Date plan

Suggests a short itinerary for two people's next meet-up. See [PRODUCT_BRIEF.md](PRODUCT_BRIEF.md) for the why.

## First-time setup

1. Plans are written by the Kimi K3 model through OpenCode. Sign in at [opencode.ai](https://opencode.ai), add credit, then go to **Account → Personal API keys → Add API key**. The key is only shown once. Each plan costs a few cents at most.
2. In this folder, copy the example settings file:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and paste your key after `OPENCODE_API_KEY=`. `.env` is git-ignored, so the key never gets committed.
4. If you're on a fresh copy without the `.venv` folder, install the dependencies (needs Python 3.10 or newer; check with `python3 --version`):
   ```bash
   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```

> **On Windows:** use `py -3.11` (or another 3.10+ version) instead of `python3`, and `.venv\Scripts\` instead of `.venv/bin/` in every command here. For example, `py -3.11 -m venv .venv` then `.venv\Scripts\pip install -r requirements.txt`, and run the app with `.venv\Scripts\python app.py`.

## Run it

```bash
.venv/bin/python app.py
```

Open http://127.0.0.1:5001, then fill in the day, start time and area, and press **Suggest a plan**. Stop it with Ctrl+C.

## Tests

```bash
.venv/bin/pytest
```

The tests use a fake model, so they're free and work offline.

## Files

- `itinerary.py` defines what a plan is and the rules it must follow (3–5 stops, times in order).
- `planner.py` asks Kimi K3 for a plan, rejects replies from any other model, and turns any failure into a friendly message.
- `app.py` and `templates/index.html` are the page.
