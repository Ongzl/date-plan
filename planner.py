"""Ask Claude for a suggested meet-up plan."""

import os

import anthropic
import pydantic

from itinerary import MAX_STOPS, MIN_STOPS, Itinerary, ItineraryError, PlanRequest, check_itinerary

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = f"""\
You plan a next meet-up for two people in Singapore who met recently and are \
still getting to know each other.

Suggest {MIN_STOPS} to {MAX_STOPS} activities for one afternoon or evening, \
lasting about 3 to 4 hours in total. Mix something you do side by side (a walk, \
a class, a game) with somewhere quiet enough to talk. Keep it low-pressure and \
moderately priced, and use real places in or near the area they give, with \
realistic travel time between stops.

For each stop give: the start time as HH:MM in 24-hour time, the activity, the \
place, and a one-line note on why it helps them get to know each other. The \
first stop starts at the time they give. Give the plan a short, friendly title."""


class PlanError(Exception):
    """Something went wrong. The message is safe to show the pair."""


def build_prompt(request: PlanRequest) -> str:
    return (
        f"Day: {request.day:%A %-d %B %Y}\n"
        f"Free from: {request.start_time:%H:%M}\n"
        f"Area: {request.area}"
    )


def suggest_plan(request: PlanRequest, client=None) -> Itinerary:
    """Return a checked itinerary, or raise PlanError with a friendly message."""
    if client is None and not os.environ.get("ANTHROPIC_API_KEY"):
        raise PlanError("No Anthropic API key found. Add it to your .env file.")
    try:
        client = client or anthropic.Anthropic()
        response = client.beta.messages.parse(
            model=MODEL,
            max_tokens=16000,
            output_config={"effort": "low"},
            # If Claude declines, Anthropic retries on a suitable other model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_prompt(request)}],
            output_format=Itinerary,
        )
    except anthropic.AuthenticationError:
        raise PlanError("The Anthropic API key is missing or wrong. Check your .env file.") from None
    except anthropic.RateLimitError:
        raise PlanError("Too many requests just now. Wait a minute and try again.") from None
    except anthropic.APIConnectionError:
        raise PlanError("Couldn't reach Claude. Check your internet connection and try again.") from None
    except (anthropic.AnthropicError, pydantic.ValidationError):
        raise PlanError("Couldn't make a plan this time. Please try again.") from None

    if response.stop_reason == "refusal" or response.parsed_output is None:
        raise PlanError("Couldn't make a plan this time. Please try again.")

    try:
        return check_itinerary(response.parsed_output, request)
    except ItineraryError:
        raise PlanError("The suggested plan didn't quite add up. Please try again.") from None
