import datetime as dt
import holidays


def hungarian_holidays(year: int) -> set[dt.date]:

    hu = holidays.country_holidays("HU", years=year)
    return set(hu.keys())


def day_type(date: dt.date, holidays_set: set[dt.date]) -> str:
    """
    Adott dátum nap-típusa: 'weekday' vagy 'weekend'.

    'weekend'-nek számít:
      - ha a 'holidays' szerint ünnepnap,
      - vagy ha szombat / vasárnap.
    """
    if date in holidays_set:
        return "weekend"
    # hétfő=0 ... vasárnap=6
    if date.weekday() >= 5:
        return "weekend"
    return "weekday"
