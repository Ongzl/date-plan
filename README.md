# Date plan

Suggests a short itinerary for two people's next meet-up. See [PRODUCT_BRIEF.md](PRODUCT_BRIEF.md) for the why.

## First-time setup

1. Plans are written by the GLM-5.3 Flash model through OpenCode. Sign in at [opencode.ai](https://opencode.ai), add credit, then go to **Account → Personal API keys → Add API key**. The key is only shown once. Each plan costs well under a cent.
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
- `planner.py` asks GLM-5.3 Flash for a plan, rejects replies from any other model, and turns any failure into a friendly message.
- `links.py` checks the reservation links the model suggests. Stops the model thinks take bookings get a **Reserve** button that opens the place's booking page in a new tab. Without a Google key, the model's links are guesses: any that don't load are dropped, and the button searches for the place's booking page instead.
- `reservations.py` is the reservation check, used when `GOOGLE_PLACES_API_KEY` is set. For each bookable-looking stop, the model looks the place up on Google Places and reads its website for a booking link, using tools. The harness then checks the answer itself: the place must be one Google returned, and a booking link must be one actually found on a page (never typed by the model) and look like a booking page. Whether the stop gets a **Reserve** button follows Google's "takes reservations" answer or a found booking page. With no booking page, the button opens the place on Google Maps.

## Checking reservations (optional)

To have the app check which stops really take bookings, add a Google Places key to `.env`:

1. In [Google Cloud Console](https://console.cloud.google.com), create a project with billing on, and enable **Places API (New)**.
2. Under **APIs & Services → Credentials**, create an API key. Restrict it to Places API (New).
3. Paste it after `GOOGLE_PLACES_API_KEY=` in `.env` and restart the app.

Each bookable stop costs about 3–4 US cents with Google, plus a few model calls, and adds a few seconds to planning.
- `app.py` and `templates/index.html` are the page.
