import numpy as np



SEGMENTS = ["home", "mud", "public", "work"] #szegmensek listája


def sample_gmms(gmms, n_samples=10):
    """
    GMM-enként n_samples darab (start_time[s], energy[kWh]) mintát vesz.
    """
    samples = {}
    for key, gmm in gmms.items():
        #print(gmm.n_components)
        if gmm.n_components == 1:
            # ha csak 1 komponens van, legyen az teljes súllyal
            gmm.weights_[0] = 1.0
        X, _ = gmm.sample(n_samples)
        samples[key] = X  # shape: (n_samples, 2)
    return samples


def regroup_samples_by_segment(samples, daytype):
    """
    A mintákat szegmensenként összefűzi (csak weekday itt).

    Visszaad: egy segment dictionary-t -> np.array shape (N, 2)
      oszlopok: [start_time_sec, energy_kwh]
    """
    regrouped = {}
    for key, data in samples.items():
        # key formátum: '{day}_{segment}_{driver_group}'
        parts = key.split('_')
        day = parts[0]
        segment = parts[1]
        driver_group = parts[2]

        if day == daytype:
            seg_key = segment
            if seg_key not in regrouped:
                regrouped[seg_key] = []
            regrouped[seg_key].append(data)

    # Összefűzés driver group-ok között
    for key, data in regrouped.items():
       # print(len(regrouped[key]))
        # print(key)
        regrouped[key] = np.vstack(regrouped[key])

    return regrouped


def convert_sample_to_triple(sample, dt_minutes=60, duration_h=2.0):
    """
    Egy GMM-minta (start_time_sec, energy_kwh)
      ehhez szükséges adatok -> (start_idx, duration_steps, level_kw, n_steps)

    start_idx       : melyik időlépcsőben kezd (index a diszkrét rácson)
    duration_steps  : hány időlépcsőig tart a töltés
    chgpwr_kw       : konstans töltési teljesítmény (kW)
    n_steps         : napi időlépcsők száma (24h / dt)
    """
    start_sec = sample[0]
    energy_kwh = sample[1]

    dt_h = dt_minutes / 60.0
    n_steps = int(24 / dt_h)

    # start time 0..24h közé
    start_sec = np.clip(start_sec, 0, 24 * 3600 - 1)

    # hanyadik slot (pl. dt=60 perc -> 0..23)
    start_idx = int(start_sec / (dt_h * 3600))

    # hány slotig tart (pl. 2 óra, dt=1h -> 2)
    duration_steps = int(duration_h / dt_h)
    duration_steps = max(1, duration_steps)

    # teljesítmény (kW) – energia / idő
    if duration_h <= 0:
        chgpwr_kw = 0.0
    else:
        chgpwr_kw = energy_kwh / duration_h

    return start_idx, duration_steps, chgpwr_kw, n_steps


def samples_to_profile(segment_samples, dt_minutes=60, duration_h=2.0):

    dt_h = dt_minutes / 60.0
    n_steps = int(24 / dt_h)
    profile = np.zeros(n_steps)
    triples = []

    for sample in segment_samples:
        start_idx, duration_steps, level_kw, n_steps_check = convert_sample_to_triple(
            sample, dt_minutes=dt_minutes, duration_h=duration_h
        )
        assert n_steps == n_steps_check

        end_idx = min(start_idx + duration_steps, n_steps)
        profile[start_idx:end_idx] += level_kw
        triples.append((start_idx, duration_steps, level_kw))

    t_grid = np.arange(0, 24, dt_h)  # órában
    return t_grid, profile, triples


# 1 nap szimulációja egy adott nap-típusra (weekday / weekend)
def simulate_one_day(gmms,
                     daytype: str,
                     n_samples: int = 50,
                     dt_minutes: int = 60,
                     duration_h: float = 2.0):

    # 1) mintavétel minden GMM-ből
    samples = sample_gmms(gmms, n_samples=n_samples)

    # 2) csak az adott nap-típus (weekday/weekend), szegmensenként
    samples_by_segment = regroup_samples_by_segment(samples, daytype)

    # 3) minta -> profil
    daily_profiles = {}
    for segment, seg_samples in samples_by_segment.items():
        _, profile, _ = samples_to_profile(
            seg_samples,
            dt_minutes=dt_minutes,
            duration_h=duration_h,
        )
        daily_profiles[segment] = profile

    return daily_profiles
