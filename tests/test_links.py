from urllib.parse import parse_qs, urlsplit

import pytest

from itinerary import Itinerary, Stop
from links import check_booking_links, looks_safe


def stop(place="Bincho", reservable=True, url=""):
    return Stop(time="19:00", activity="Drinks", place=place, note="n", reservable=reservable, booking_url=url)


def plan(*stops):
    return Itinerary(title="T", stops=list(stops))


@pytest.mark.parametrize("url", ["https://www.chope.co/singapore-restaurants/bincho", "https://bincho.sg/reserve?x=1"])
def test_normal_https_links_are_allowed(url):
    assert looks_safe(url)


@pytest.mark.parametrize(
    "url",
    [
        "", "http://bincho.sg", "javascript:alert(1)", "https://localhost/x", "https://127.0.0.1/x",
        "https://[::1]/x", "https://10.0.0.5/", "https://bincho.sg:8080/", "https://user:pw@bincho.sg/",
        "https://intranet/", "https://printer.local/", "ftp://bincho.sg",
    ],
)
def test_unsafe_links_are_refused(url):
    assert not looks_safe(url)


def test_working_link_is_kept_and_dead_or_unsafe_ones_dropped():
    good, dead, unsafe = "https://good.example/book", "https://dead.example/book", "http://plain.example/book"
    seen = []

    def loads(url):
        seen.append(url)
        return url == good

    result = check_booking_links(plan(stop(url=good), stop(url=dead), stop(url=unsafe)), loads=loads)
    assert [s.booking_url for s in result.stops] == [good, "", ""]
    assert sorted(seen) == sorted([good, dead])  # the unsafe link is never fetched


def test_links_on_non_reservable_stops_are_dropped_without_fetching():
    seen = []
    result = check_booking_links(plan(stop(reservable=False, url="https://good.example/")), loads=seen.append)
    assert result.stops[0].booking_url == "" and seen == []


def test_reserve_button_falls_back_to_a_search_for_the_place():
    url = stop(place="Bincho at Hua Bee").reservation_url
    parts = urlsplit(url)
    assert parts.scheme == "https" and parts.netloc == "www.google.com"
    assert parse_qs(parts.query)["q"] == ["Bincho at Hua Bee reservation"]


def test_reserve_button_uses_checked_link_when_there_is_one():
    assert stop(url="https://good.example/book").reservation_url == "https://good.example/book"
