import matplotlib.pyplot as plt

from data_loading import load_gmms
from plotting import plot_gmm_marginal
from new_samples import (
    sample_gmms,
    regroup_samples_by_segment,
    samples_to_profile,
    convert_sample_to_triple,
)


def main():
    gmms = load_gmms()

    # --- Példa: 1. driver group, home, weekday – marginal ábrák ---
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

    # Mintavétel + szegmensenkénti összefésülés
    samples = sample_gmms(gmms, n_samples=50)
    samples_by_segment = regroup_samples_by_segment(samples)

    #Minta -> töltési időfüggvény
    dt_minutes = 60      # órás felbontás
    duration_h = 2.0     # feltételezzük, hogy mindenki 2 órát tölt

    profiles = {}
    triples_by_segment = {}

    for segment, seg_samples in samples_by_segment.items():
        t_grid, profile, triples = samples_to_profile(
            seg_samples,
            dt_minutes=dt_minutes,
            duration_h=duration_h,
        )
        profiles[segment] = (t_grid, profile)
        triples_by_segment[segment] = triples

    # konkrét 3 adatos minta
    example_segment = "home"
    example_sample = samples_by_segment[example_segment][0]
    ex_start_idx, ex_duration_steps, ex_level_kw, _ = convert_sample_to_triple(
        example_sample,
        dt_minutes=dt_minutes,
        duration_h=duration_h,
    )
    print(f"Példa minta ({example_segment}):")
    print("  raw sample (start_sec, energy_kWh):", example_sample)
    print("  triple (start_idx, duration_steps, level_kw):",
          (ex_start_idx, ex_duration_steps, ex_level_kw))

    # --- Szegmensprofilok kirajzolása ---
    plt.figure(figsize=(10, 5))
    for segment, (t_grid, profile) in profiles.items():
        plt.plot(t_grid, profile, label=segment)

    plt.xlabel("Óra")
    plt.ylabel("Összteljesítmény [kW]")
    plt.title("Weekday – szegmensenkénti töltési profil")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
