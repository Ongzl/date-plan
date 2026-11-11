"""What the page says while a plan is being made (issue #15).

Each slow step reports one of these before it starts, through a `progress`
callback, and the page shows the latest one on the button.
"""

STARTING = "Getting started…"
WRITING = "Writing your plan…"
CHECKING = "Checking the places are open…"
BOOKING = "Finding booking pages…"
TRAVEL = "Working out travel times…"
DONE = "Done! Loading your plan…"


def replacing(places: list[str]) -> str:
    """Said when the plan is written again because some places have closed."""
    names = " and ".join(places) if len(places) <= 2 else ", ".join(places[:-1]) + " and " + places[-1]
    return f"{names} {'has' if len(places) == 1 else 'have'} closed. Finding somewhere else…"


def ignore(message: str) -> None:
    """Used when nobody is watching the progress."""
