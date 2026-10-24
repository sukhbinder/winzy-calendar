import winzy
import calendar
import datetime


def _showmonth(year, month):
    c = calendar.TextCalendar(calendar.SUNDAY)
    print(c.formatmonth(year, month))


def _showyear(year):
    c = calendar.TextCalendar(calendar.SUNDAY)
    print(c.formatyear(year))


def parse_calendar_args(values, today=None):
    """
    Standalone parser for positional calendar arguments.

    Returns (year, month) where month may be None -> caller should print
    the whole-year calendar. For no / ambiguous / invalid input we fall
    back to (today.year, today.month).

    Accepted combos:
        []            -> current month of current year
        [M]           -> month M of current year          (1 <= M <= 12)
        [Y]           -> whole year Y                     (Y >= 13)
                        13..99 are read as 20YY (13 -> 2013)
        [M, Y]        -> month M of year Y
        [Y, M]        -> month M of year Y
        [a, b] both<=12 -> treated as [month, year]  (ambiguous; see notes)
        anything else -> default (e.g. [119, 29], 3+ values, <=0, non-numeric)
    """
    if today is None:
        today = datetime.date.today()
    default = (today.year, today.month)

    if not values:
        return default

    # Coerce to int; quietly fall back on anything non-numeric.
    try:
        nums = [int(v) for v in values]
    except (TypeError, ValueError):
        return default

    if any(n <= 0 for n in nums):
        return default

    def _is_month(v):
        return 1 <= v <= 12

    def _as_year(v):
        # 13..99 -> 20xx (e.g. 13 -> 2013); >=100 used literally
        return v + 2000 if v < 100 else v

    # single value
    if len(nums) == 1:
        n = nums[0]
        if _is_month(n):
            return (today.year, n)      # month of current year
        if n >= 13:
            return (_as_year(n), None)  # whole year
        return default

    # two values
    if len(nums) == 2:
        a, b = nums
        a_m, b_m = _is_month(a), _is_month(b)

        if a_m and not b_m and b >= 13:
            return (_as_year(b), a)     # M Y
        if b_m and not a_m and a >= 13:
            return (_as_year(a), b)     # Y M
        if a_m and b_m:
            # Ambiguous: both fit "month". Treat first as month,
            # second as year (20YY). e.g. "11 12" -> Nov 2012.
            return (_as_year(b), a)
        # Neither value is a valid month -> non-sensible (e.g. 119 29)
        return default

    # 3+ values
    return default


class HelloWorld:
    __name__ = "cal"

    @winzy.hookimpl
    def register_commands(self, subparser):
        calparser = subparser.add_parser(
            "cal", description="Calendar in Windows command line"
        )
        calparser.add_argument("-m", "--month", type=int, help="month", default=-1)
        calparser.add_argument("-y", "--year",  type=int, help="year",  default=-1)
        calparser.add_argument(
            "values",
            nargs="*",
            help="[month] [year] in any order, e.g. 'cal 10 2026', "
                 "'cal 2026 10', 'cal 13', 'cal 2026'",
        )
        calparser.set_defaults(func=self.showcalendar)

    def showcalendar(self, args):
        now = datetime.datetime.today()

        # Positional args take precedence over -m / -y.
        if getattr(args, "values", None):
            year, month = parse_calendar_args(args.values, now)
            if month is None:
                _showyear(year)
            else:
                _showmonth(year, month)
            return

        # Original flag-based fallback.
        if args.month != -1 and args.year != -1:
            _showmonth(args.year, args.month)
        elif args.year != -1:
            _showyear(args.year)
        elif args.month != -1:
            _showmonth(now.year, args.month)
        else:
            _showmonth(now.year, now.month)

    def hello(self, args):
        print("Hello! This is an example ``winzy`` plugin.")


cal_plugin = HelloWorld()
