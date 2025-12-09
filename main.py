from config import DT_MINUTES, YEAR
from data_loading import load_gmms
from simulations import simulate_year

from new_samples import (
    sample_gmms,
    regroup_samples_by_segment,
    samples_to_profile,
    convert_sample_to_triple,
)
from plotting import (
    plot_gmm_marginal,
    plot_segment_profiles_one_day,
    plot_daily_energy_by_segment,
    plot_mean_daily_profile_by_segment,
)


def main():
    # 1) GMM-ek betöltése a Powell-féle pickle fájlokból
    gmms = load_gmms()

    # 2) Egy konkrét GMM (weekday_home_1) marginal eloszlásainak kirajzolása
    #    dim=0 -> start time eloszlás, dim=1 -> energia eloszlás
    key = "weekday_home_1"
    gmm = gmms[key]

    plot_gmm_marginal(
        gmm,
        dim=0,
        title=f"{key} – start time",
        xlabel="Start time [h]",
    )

    plot_gmm_marginal(
        gmm,
        dim=1,
        title=f"{key} – energy",
        xlabel="Energy [kWh]",
    )

    # 3) 1 napos szimuláció: mintavétel GMM-ekből és szegmensenkénti összefésülés
    samples = sample_gmms(gmms)                         # minden GMM-ből N_SAMPLES minta
    samples_by_segment = regroup_samples_by_segment(    # csak 'weekday' minták, szegmens szerint
        samples,
        'weekday'
    )

    # 4) 1 napos szegmensprofilok előállítása (idősor: összteljesítmény [kW] 0–24h között)
    profiles = {}              # szegmens -> (t_grid, profile)
    triples_by_segment = {}    # szegmens -> list(triple-ek)

    for segment, seg_samples in samples_by_segment.items():
        t_grid, profile, triples = samples_to_profile(seg_samples)
        profiles[segment] = (t_grid, profile)
        triples_by_segment[segment] = triples

    # 5) Példa: egy konkrét 3-adatos "profil" (start_idx, duration_steps, level_kw) kiíratása
    example_segment = "home"
    example_sample = samples_by_segment[example_segment][0]   # első minta a 'home' szegmensben
    ex_start_idx, ex_duration_steps, ex_level_kw, _ = convert_sample_to_triple(
        example_sample
    )
    #print(f"Példa minta ({example_segment}):")
    #print("  raw sample (start_sec, energy_kWh, ...):", example_sample)
    #print("  triple (start_idx, duration_steps, level_kw):",
         # (ex_start_idx, ex_duration_steps, ex_level_kw))

    # 6) 1 napos szegmensprofilok kirajzolása egy közös ábrán
    plot_segment_profiles_one_day(
        profiles,
        title="Weekday – szegmensenkénti töltési profil (1 nap)"
    )

    # 7) Teljes éves szimuláció lefuttatása (év: YEAR a configból)
    #    -> time_index: időbélyegek az év összes időlépésére
    #    -> yearly_profiles: szegmensenként éves teljesítmény-idősor
    time_index, yearly_profiles = simulate_year(gmms)

    # 8) Napi összenergia [kWh/nap] szegmensenként, az év minden napjára
    plot_daily_energy_by_segment(
        yearly_profiles,
        YEAR,
    )

    # 9) Átlagos napi profil 0–24h között, az egész évből számítva, szegmensenként
    plot_mean_daily_profile_by_segment(
        yearly_profiles,
        YEAR,
    )


if __name__ == "__main__":
    main()
