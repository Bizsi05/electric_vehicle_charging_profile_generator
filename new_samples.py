from config import N_SAMPLES, DT_MINUTES, CHARGING_POWER_KW,EV_COUNT
import numpy as np

def sample_gmms(gmms): #  GMM-enként n_samples darab (start_time[s], energy[kWh]) mintát vesz

    samples = {}
    for key, gmm in gmms.items():
        #print(gmm.n_components)
        if gmm.n_components == 1:
            # ha csak 1 komponens van, legyen az teljes súllyal
            gmm.weights_[0] = 1.0
        X, _ = gmm.sample(N_SAMPLES)
        samples[key] = X  # shape: (n_samples, 2)
    return samples


def regroup_samples_by_segment(samples, daytype):
    """
    A mintákat szegmensenként összefűzi az adott naptípusra (weekday/weekend).
    Visszaad: egy segment dictionary-t -> np.array shape (N, 2)
    oszlopok: [start_time_sec, energy_kwh]
    """
    regrouped = {}
    for key, data in samples.items(): #key formátum: '{day}_{segment}_{driver_group}'
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


def convert_sample_to_triple(sample):
    """
    Egy GMM-minta (start_time_sec, energy_kwh) -> (start_idx, duration_steps, level_kw, n_steps)

    start_idx       : melyik időlépcsőben kezd (index a diszkrét rácson)
    duration_steps  : hány időlépcsőig tart a töltés
    chgpwr_kw       : konstans töltési teljesítmény (kW) – configból (CHARGING_POWER_KW)
    n_steps         : napi időlépcsők száma (24h / dt)

    """
    start_sec = sample[0]
    energy_kwh = sample[1]

    dt_h = DT_MINUTES / 60.0
    n_steps = int(24 / dt_h)

    # start time 0..24h közé vágása
    start_sec = np.clip(start_sec, 0, 24 * 3600 - 1)

    # hanyadik slot (pl. dt=60 perc -> 0..23)
    start_idx = int(start_sec / (dt_h * 3600))

    # ha nincs energia vagy 0 a teljesítmény, tegyük minimális 1 lépés hosszú, 0 kW-al
    if energy_kwh <= 0 or CHARGING_POWER_KW <= 0:
        duration_steps = 1
        chgpwr_kw = 0.0
    else:
        # időtartam órában
        duration_h = energy_kwh / CHARGING_POWER_KW
        # hány dt_h lépés ez?
        duration_steps = int(np.ceil(duration_h / dt_h))
        duration_steps = max(1, duration_steps)
        chgpwr_kw = CHARGING_POWER_KW

    return start_idx, duration_steps, chgpwr_kw, n_steps



def samples_to_profile(segment_samples):

    dt_h = DT_MINUTES / 60.0
    n_steps = int(24 / dt_h)
    profile = np.zeros(n_steps)
    triples = []

    for sample in segment_samples:
        start_idx, duration_steps, level_kw, n_steps_check = convert_sample_to_triple(sample)
        assert n_steps == n_steps_check

        end_idx = min(start_idx + duration_steps, n_steps)
        profile[start_idx:end_idx] += level_kw
        triples.append((start_idx, duration_steps, level_kw))

    t_grid = np.arange(0, 24, dt_h)  # órában
    return t_grid, profile, triples


# 1 nap szimulációja egy adott nap-típusra (weekday / weekend)
def simulate_one_day(gmms, daytype: str, target_mean_kwh: float):

    # 1) mintavétel minden GMM-ből
    samples = sample_gmms(gmms)

    # 2) csak az adott nap-típus (weekday/weekend), szegmensenként
    samples_by_segment = regroup_samples_by_segment(samples, daytype)

    # 3) MEKH skálázás (ha kérjük)
    if target_mean_kwh is not None:
        # összes szegmens mintáinak összefűzése
        all_arrays = list(samples_by_segment.values())
        if all_arrays:
            all_samples = np.vstack(all_arrays)
            current_mean = all_samples[:, 1].mean()  # energia átlag
            if current_mean > 0:
                scale = target_mean_kwh / current_mean
                # minden szegmens energiáját ugyanazzal a szorzóval skálázza
                for seg in samples_by_segment:
                    samples_by_segment[seg][:, 1] *= scale

    # 3/b) EV-darabszámra való skálázás (ha kérjük)
        if EV_COUNT and EV_COUNT > 0:
            # az adott napra generált összes töltési esemény száma
            total_sessions = sum(arr.shape[0] for arr in samples_by_segment.values())
        if total_sessions > 0:
            factor_ev = EV_COUNT / total_sessions
            # minden esemény energiáját ugyanazzal a faktorral szorozzuk
            for seg in samples_by_segment:
                samples_by_segment[seg][:, 1] *= factor_ev

    # 4) minta -> profil
    daily_profiles = {}
    for segment, seg_samples in samples_by_segment.items():
        _, profile, _ = samples_to_profile(seg_samples)
        daily_profiles[segment] = profile
    return daily_profiles
