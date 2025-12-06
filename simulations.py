import datetime as dt
import numpy as np
from calendar_for_daytype import hungarian_holidays, day_type
from new_samples import simulate_one_day
#teljes év szimulációja
def simulate_year(gmms,
                  year: int,
                  n_samples: int = 50,
                  dt_minutes: int = 60,
                  duration_h: float = 2.0):
    """
    ADDED:
    Egy teljes év szimulációja magyar ünnepnapokkal.

    - A day_type() dönti el napról napra, hogy 'weekday' vagy 'weekend'
      (ünnepnapokat hétvégének számítja).
    - Minden napra meghívjuk a simulate_one_day()-t.
    - Az így kapott napi profilokat egymás után fűzzük.

    Visszatér:
      time_index      : list[datetime.datetime], minden időlépésre 1 időpont
      yearly_profiles : dict[segment] -> np.array, hossz = év_napjai * (24h/dt)
    """
    holidays = hungarian_holidays(year)
    dt_h = dt_minutes / 60.0
    steps_per_day = int(24 / dt_h)

    segments = ["home", "mud", "public", "work"]

    # ide gyűjtjük a napi profilokat szegmensenként
    profiles_by_segment = {seg: [] for seg in segments}
    time_index = []

    current = dt.date(year, 1, 1)
    end = dt.date(year + 1, 1, 1)

    while current < end:
        # melyik nap-típus? (weekday / weekend)
        dtype = day_type(current, holidays)

        # egy napi szimuláció
        daily_profiles = simulate_one_day(
            gmms,
            daytype=dtype,
            n_samples=n_samples,
            dt_minutes=dt_minutes,
            duration_h=duration_h,
        )

        # napi profilok eltárolása
        for seg in segments:
            if seg in daily_profiles:
                profiles_by_segment[seg].append(daily_profiles[seg])

        # időindex építése (minden napra 24/dt lépés)
        for step in range(steps_per_day):
            t = dt.datetime.combine(current, dt.time()) + dt.timedelta(hours=step * dt_h)
            time_index.append(t)

        current += dt.timedelta(days=1)

    # napi listák összefűzése egy-egy hosszú éves vektorrá
    yearly_profiles = {}
    for seg, daily_list in profiles_by_segment.items():
        if not daily_list:
            continue
        yearly_profiles[seg] = np.concatenate(daily_list)

    return time_index, yearly_profiles