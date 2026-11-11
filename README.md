# Date plan

Suggests a short itinerary for two people's next meet-up. See [PRODUCT_BRIEF.md](PRODUCT_BRIEF.md) for the why.

## First-time setup

1. Get an API key at [console.anthropic.com](https://console.anthropic.com) (Settings → API keys). Each plan costs about a cent.
2. In this folder, copy the example settings file:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and paste your key after `ANTHROPIC_API_KEY=`. `.env` is git-ignored, so the key never gets committed.
4. If you're on a fresh copy without the `.venv` folder, install the dependencies:
   ```bash
   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```

## Run it

```bash
.venv/bin/python app.py
```

Open http://127.0.0.1:5001, then fill in the day, start time and area, and press **Suggest a plan**. Stop it with Ctrl+C.

## Tests

```bash
.venv/bin/pytest
```

The tests use a fake Claude, so they're free and work offline.

## Files

- `itinerary.py` defines what a plan is and the rules it must follow (3–5 stops, times in order).
- `planner.py` asks Claude for a plan and turns any failure into a friendly message.
- `app.py` and `templates/index.html` are the page.
