"""What a meet-up plan looks like, and the rules a good one follows."""

from datetime import date, time

from pydantic import BaseModel

MIN_STOPS = 3
MAX_STOPS = 5


class PlanRequest(BaseModel):
    """What the pair tell the planner."""

    day: date
    start_time: time
    area: str


class Stop(BaseModel):
    """One activity in the plan."""

    time: str  # "HH:MM", 24-hour
    activity: str
    place: str
    note: str


class Itinerary(BaseModel):
    """The shape Claude must reply in."""

    title: str
    stops: list[Stop]


class ItineraryError(ValueError):
    """The itinerary breaks one of the rules below."""


def parse_time(text: str) -> time:
    try:
        hours, minutes = text.strip().split(":")
        return time(int(hours), int(minutes))
    except ValueError:
        raise ItineraryError(f"'{text}' is not a time like 14:30") from None


def check_itinerary(itinerary: Itinerary, request: PlanRequest) -> Itinerary:
    """Return the itinerary if it follows the rules, otherwise raise ItineraryError.

    Rules: 3-5 stops, every stop has an activity and a place, times are in
    order, and nothing starts before the pair said they're free.
    """
    stops = itinerary.stops
    if not MIN_STOPS <= len(stops) <= MAX_STOPS:
        raise ItineraryError(f"Needs {MIN_STOPS}-{MAX_STOPS} stops, got {len(stops)}")

    previous = None
    for number, stop in enumerate(stops, start=1):
        if not stop.activity.strip() or not stop.place.strip():
            raise ItineraryError(f"Stop {number} is missing an activity or a place")
        when = parse_time(stop.time)
        if when < request.start_time:
            raise ItineraryError(f"Stop {number} starts before {request.start_time:%H:%M}")
        if previous is not None and when <= previous:
            raise ItineraryError(f"Stop {number} isn't later than the stop before it")
        previous = when

    return itinerary
