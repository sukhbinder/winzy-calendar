import pytest
import winzy_calendar as w
import datetime

def test_plugin(capsys):
    w.cal_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``winzy`` plugin." in captured.out


TODAY = datetime.date(2024, 6, 15)   # fixed reference date for determinism
DEFAULT = (2024, 6)                  # what "fall back to default" must equal

# No positional ars
class TestNoArgs:
    def test_empty_list_returns_current_month(self):
        assert w.parse_calendar_args([], TODAY) == DEFAULT

    def test_empty_tuple(self):
        assert w.parse_calendar_args((), TODAY) == DEFAULT

    def test_none_today_falls_back_to_real_today(self):
        # Smoke: must not crash and must produce a valid month.
        year, month = w.parse_calendar_args([])
        assert isinstance(year, int) and isinstance(month, int)
        assert 1 <= month <= 12


# Single value
class TestSingleValue:
    @pytest.mark.parametrize("month", range(1, 13))
    def test_month_of_current_year(self, month):
        assert w.parse_calendar_args([month], TODAY) == (2024, month)

    @pytest.mark.parametrize("month", range(1, 13))
    def test_month_as_string(self, month):
        assert w.parse_calendar_args([str(month)], TODAY) == (2024, month)

    @pytest.mark.parametrize(
        "value, expected_year",
        [
            (13, 2013),    # documented: 13 -> 2013
            (14, 2014),
            (26, 2026),
            (99, 2099),
            (100, 100),    # design decision: >=100 is used literally
            (2026, 2026),
        ],
    )
    def test_year_only(self, value, expected_year):
        assert w.parse_calendar_args([value], TODAY) == (expected_year, None)

    @pytest.mark.parametrize("value", [0, -1, -42])
    def test_non_positive_falls_back(self, value):
        assert w.parse_calendar_args([value], TODAY) == DEFAULT

    @pytest.mark.parametrize("value", ["foo", "", "abc", "3.5", None])
    def test_non_numeric_falls_back(self, value):
        assert w.parse_calendar_args([value], TODAY) == DEFAULT


# Two values
class TestTwoValues:
    @pytest.mark.parametrize(
        "values",
        [
            ["10", "2026"],
            ["2026", "10"],
            [10, 2026],
            [2026, 10],
        ],
    )
    def test_month_and_year_any_order(self, values):
        assert w.parse_calendar_args(values, TODAY) == (2026, 10)

    @pytest.mark.parametrize("values", [["10", "26"], ["26", "10"]])
    def test_two_digit_year_is_promoted(self, values):
        assert w.parse_calendar_args(values, TODAY) == (2026, 10)

    @pytest.mark.parametrize(
        "values, expected",
        [
            (["11", "12"], (2012, 11)),   # ambiguous: first=month, second=year
            (["1", "1"], (2001, 1)),
            (["12", "13"], (2013, 12)),   # month, then two-digit year
            (["13", "12"], (2013, 12)),   # reversed
        ],
    )
    def test_ambiguous_both_values_are_months(self, values, expected):
        assert w.parse_calendar_args(values, TODAY) == expected

    @pytest.mark.parametrize(
        "values",
        [
            ["119", "29"],       # neither is a month
            ["2026", "2027"],    # two years, no month
            ["13", "14"],        # both years, no month
            ["0", "10"],         # non-positive
            ["10", "-5"],        # non-positive
            ["foo", "10"],       # non-numeric
        ],
    )
    def test_non_sensible_falls_back(self, values):
        assert w.parse_calendar_args(values, TODAY) == DEFAULT


# Three or more values
class TestThreeOrMoreValues:
    @pytest.mark.parametrize(
        "values",
        [
            ["10", "2026", "5"],
            ["1", "2", "3", "4"],
            ["2026", "10", "12"],
        ],
    )
    def test_falls_back_to_default(self, values):
        assert w.parse_calendar_args(values, TODAY) == DEFAULT


# Misc
class TestTodayHandling:
    def test_accepts_datetime_object(self):
        now = datetime.datetime(2024, 6, 15, 10, 30)
        assert w.parse_calendar_args([], now) == (2024, 6)
        assert w.parse_calendar_args([3], now) == (2024, 3)

    def test_uses_today_year_for_single_month(self):
        other = datetime.date(1999, 1, 1)
        assert w.parse_calendar_args([7], other) == (1999, 7)


def test_return_types():
    year, month = w.parse_calendar_args([13], TODAY)
    assert isinstance(year, int)
    assert month is None

    year, month = w.parse_calendar_args([10], TODAY)
    assert isinstance(year, int)
    assert isinstance(month, int)
