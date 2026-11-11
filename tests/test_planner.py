from datetime import date, time
from types import SimpleNamespace

import anthropic
import httpx2
import pytest

from itinerary import Itinerary, PlanRequest, Stop
from planner import PlanError, build_prompt, suggest_plan

REQUEST = PlanRequest(day=date(2026, 11, 14), start_time=time(14, 0), area="Tiong Bahru")

GOOD = Itinerary(
    title="A slow Saturday in Tiong Bahru",
    stops=[
        Stop(time="14:00", activity="Coffee", place="Tiong Bahru Bakery", note="Easy start"),
        Stop(time="15:00", activity="Mural walk", place="Tiong Bahru estate", note="Side by side"),
        Stop(time="16:30", activity="Bookshop browse", place="BooksActually", note="Swap picks"),
    ],
)


class FakeClient:
    """Stands in for anthropic.Anthropic so tests run offline and free."""

    def __init__(self, parsed=GOOD, stop_reason="end_turn", error=None):
        self.calls = []
        self._parsed, self._stop_reason, self._error = parsed, stop_reason, error
        self.beta = SimpleNamespace(messages=SimpleNamespace(parse=self._parse))

    def _parse(self, **kwargs):
        self.calls.append(kwargs)
        if self._error:
            raise self._error
        return SimpleNamespace(stop_reason=self._stop_reason, parsed_output=self._parsed)


def api_error(cls, status):
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    return cls("boom", response=httpx2.Response(status, request=request), body=None)


def test_returns_checked_plan():
    assert suggest_plan(REQUEST, client=FakeClient()) == GOOD


def test_sends_pair_details_and_asks_for_itinerary_shape():
    client = FakeClient()
    suggest_plan(REQUEST, client=client)
    call = client.calls[0]
    assert call["model"] == "claude-opus-5-5"
    assert call["output_format"] is Itinerary
    assert call["fallbacks"] == "default"
    prompt = call["messages"][0]["content"]
    assert "Saturday 14 November 2026" in prompt
    assert "14:00" in prompt
    assert "Tiong Bahru" in prompt


def test_prompt_text():
    assert build_prompt(REQUEST) == "Day: Saturday 14 November 2026\nFree from: 14:00\nArea: Tiong Bahru"


def test_refusal_becomes_friendly_error():
    with pytest.raises(PlanError, match="try again"):
        suggest_plan(REQUEST, client=FakeClient(parsed=None, stop_reason="refusal"))


def test_plan_breaking_rules_becomes_friendly_error():
    bad = Itinerary(title="Too short", stops=GOOD.stops[:1])
    with pytest.raises(PlanError, match="didn't quite add up"):
        suggest_plan(REQUEST, client=FakeClient(parsed=bad))


def test_missing_key_becomes_friendly_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(PlanError, match="No Anthropic API key"):
        suggest_plan(REQUEST)


@pytest.mark.parametrize(
    "error, message",
    [
        (api_error(anthropic.AuthenticationError, 401), "API key"),
        (api_error(anthropic.RateLimitError, 429), "Too many requests"),
        (anthropic.APIConnectionError(request=httpx2.Request("POST", "https://x")), "internet"),
        (api_error(anthropic.InternalServerError, 500), "try again"),
    ],
)
def test_api_errors_become_friendly_errors(error, message):
    with pytest.raises(PlanError, match=message):
        suggest_plan(REQUEST, client=FakeClient(error=error))
