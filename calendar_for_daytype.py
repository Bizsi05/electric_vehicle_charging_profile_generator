import datetime as dt

def easter_sunday(year: int) -> dt.date:
    """Húsvétvasárnap dátuma az aktuális évben (Meeus–Jones–Butcher algoritmus)."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(year, month, day)


def hungarian_holidays(year: int) -> set[dt.date]: # adott év magyar munkaszüneti napjai

    easter = easter_sunday(year)
    good_friday   = easter - dt.timedelta(days=2)
    easter_monday = easter + dt.timedelta(days=1)
    whit_monday   = easter + dt.timedelta(days=50)  # pünkösdhétfő

    holidays = {
        dt.date(year, 1, 1),    # Újév
        dt.date(year, 3, 15),   # Nemzeti ünnep
        good_friday,            # Nagypéntek
        easter_monday,          # Húsvéthétfő
        dt.date(year, 5, 1),    # A munka ünnepe
        whit_monday,            # Pünkösdhétfő
        dt.date(year, 8, 20),   # Államalapítás
        dt.date(year, 10, 23),  # 1956-os forradalom
        dt.date(year, 11, 1),   # Mindenszentek
        dt.date(year, 12, 25),  # Karácsony
        dt.date(year, 12, 26),  # Karácsony másnapja
    }
    return holidays


def day_type(date: dt.date, holidays: set[dt.date]) -> str: # adott dátum nap-típusa: 'weekday' vagy 'weekend'

    if date in holidays:
        return "weekend"
    # hétfő=0 ... vasárnap=6
    if date.weekday() >= 5:
        return "weekend"
    return "weekday"
