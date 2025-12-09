from config import  DT_MINUTES, YEAR, SEGMENTS, USE_MEKH_DATA, MEKH_COUNTY
import datetime as dt
import numpy as np
from calendar_for_daytype import hungarian_holidays, day_type
from new_samples import simulate_one_day
from data_loading import load_mekh_table, get_mekh_avg_kwh

_MEKH_DF = None

def simulate_year(gmms): #teljes év szimulációja

    global _MEKH_DF

    holidays = hungarian_holidays(YEAR)
    dt_h = DT_MINUTES / 60.0
    steps_per_day = int(24 / dt_h)

    # ide gyűjtjük a napi profilokat szegmensenként
    profiles_by_segment = {seg: [] for seg in SEGMENTS}
    time_index = []

    current = dt.date(YEAR, 1, 1)
    end = dt.date(YEAR + 1, 1, 1)

    # MEKH tábla betöltése, ha szükséges
    mekh_df = None
    if USE_MEKH_DATA:
        if _MEKH_DF is None:
            _MEKH_DF = load_mekh_table()  # path a configból jön
        mekh_df = _MEKH_DF

    while current < end:

        dtype = day_type(current, holidays) # melyik nap-típus? (weekday / weekend)

        # ha MEKH-et használunk, kérünk egy célt átlag energiára
        if USE_MEKH_DATA:
            target_mean_kwh = get_mekh_avg_kwh(mekh_df, MEKH_COUNTY, current)
        else:
            target_mean_kwh = None

        daily_profiles = simulate_one_day(gmms,daytype=dtype,target_mean_kwh=target_mean_kwh)  # egy napi szimuláció

        # napi profilok eltárolása
        for seg in SEGMENTS:
            if seg in daily_profiles:
                profiles_by_segment[seg].append(daily_profiles[seg])

        # időindex (minden napra 24/dt lépés)
        for step in range(steps_per_day):
            t = dt.datetime.combine(current, dt.time()) + dt.timedelta(hours=step * dt_h)
            time_index.append(t)

        current += dt.timedelta(days=1)

    # napi listák összefűzése egy hosszú éves vektorrá
    yearly_profiles = {}
    for seg, daily_list in profiles_by_segment.items():
        if not daily_list:
            continue
        yearly_profiles[seg] = np.concatenate(daily_list)

    return time_index, yearly_profiles