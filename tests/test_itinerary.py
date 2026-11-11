from datetime import date, time

import pytest

from itinerary import Itinerary, ItineraryError, PlanRequest, Stop, check_itinerary

REQUEST = PlanRequest(day=date(2026, 11, 14), start_time=time(14, 0), area="Tiong Bahru")


def make(*times, activity="Coffee", place="Tiong Bahru Bakery"):
    stops = [Stop(time=t, activity=activity, place=place, note="") for t in times]
    return Itinerary(title="Saturday", stops=stops)


def test_good_itinerary_passes():
    plan = make("14:00", "15:30", "17:00")
    assert check_itinerary(plan, REQUEST) is plan


@pytest.mark.parametrize("times", [("14:00", "15:00"), ("14:00", "15", "16", "17", "18", "19")])
def test_too_few_or_too_many_stops(times):
    times = tuple(t if ":" in t else f"{t}:00" for t in times)
    with pytest.raises(ItineraryError, match="3-5 stops"):
        check_itinerary(make(*times), REQUEST)


def test_times_must_go_forward():
    with pytest.raises(ItineraryError, match="Stop 3"):
        check_itinerary(make("14:00", "16:00", "15:00"), REQUEST)


def test_same_time_twice_is_rejected():
    with pytest.raises(ItineraryError, match="Stop 2"):
        check_itinerary(make("14:00", "14:00", "15:00"), REQUEST)


def test_nothing_before_start_time():
    with pytest.raises(ItineraryError, match="before 14:00"):
        check_itinerary(make("13:30", "15:00", "16:00"), REQUEST)


def test_bad_time_text():
    with pytest.raises(ItineraryError, match="not a time"):
        check_itinerary(make("2pm", "15:00", "16:00"), REQUEST)


def test_blank_place_is_rejected():
    with pytest.raises(ItineraryError, match="missing"):
        check_itinerary(make("14:00", "15:00", "16:00", place="  "), REQUEST)
