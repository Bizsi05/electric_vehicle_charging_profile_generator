from config import DT_MINUTES, MARGINAL_SAMPLES
import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture



def plot_gmm_marginal(gmm: GaussianMixture, dim=0,
                      title="", xlabel="Value"):
    """
    gmm:    egy GaussianMixture objektum
    dim:    melyik dimenziót rajzoljuk (0 = start time, 1 = energia)
    """

    # 1) sok minta generálása a keverékmodellből
    X, _ = gmm.sample(MARGINAL_SAMPLES)      # 50 000 minta (start time, energy)
    data = X[:, dim]              # csak az adott dimenzió
    # ha az időt rajzoljuk (0. dimenzió), váltsuk át órára
    if dim == 0:
        data = data / 3600.0  # másodperc -> óra

    # 2) hisztogram – density=True, így kb. sűrűségfüggvény, false akkor darabszám lesz
    plt.figure(figsize=(6, 4))
    plt.hist(data, bins=60, density=False, alpha=0.7)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.title(title)
    plt.tight_layout()
    plt.show()

def plot_segment_profiles_one_day(profiles,title):
    # --- Szegmensprofilok kirajzolása (1 nap) ---
    plt.figure(figsize=(10, 5))
    for segment, (t_grid, profile) in sorted(profiles.items()):
        plt.plot(t_grid, profile, label=segment)

    plt.xlabel("Óra")
    plt.ylabel("Összteljesítmény [kW]")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_daily_energy_by_segment (yearly_profiles, year):


    # === NAPI ÖSSZENERGIA SZEGMENSENKÉNT, EGÉSZ ÉVRE ===

    dt_h = DT_MINUTES / 60.0
    steps_per_day = int(24 / dt_h)

    # Tegyük fel, hogy minden szegmensnél ugyanannyi lépés van (1 év)
    # Vegyünk egyet referenciának, hogy kiszámoljuk a napok számát
    any_seg = next(iter(yearly_profiles.values()))
    num_days = len(any_seg) // steps_per_day

    days = np.arange(num_days)  # 0..num_days-1 a vízszintes tengelyre

    plt.figure(figsize=(10, 5))

    for segment, yearly in yearly_profiles.items():
        if yearly is None or len(yearly) == 0:
            continue

        # (nap, időlépés) mátrix: minden sor egy nap, oszlopok az órák
        daily_matrix = yearly[:num_days * steps_per_day].reshape(num_days, steps_per_day)

        # napi összenergia [kWh] = sum(P[kW] * dt[h]) minden napra
        daily_energy = daily_matrix.sum(axis=1) * dt_h

        plt.plot(days, daily_energy,'.', label=segment)

    plt.xlabel("Nap az évben [index, 0 ... n-1]")
    plt.ylabel("Napi összenergia [kWh/nap]")
    plt.title(f"Napi összenergia szegmensenként ({year})")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_mean_daily_profile_by_segment(yearly_profiles, year):
    # 1) home szegmens teljes éves idősorának kirajzolása
    """
    home_profile = yearly_profiles.get("home")
    if home_profile is not None:
        plt.figure(figsize=(12, 4))
        plt.plot(time_index, home_profile)
        plt.xlabel("Idő")
        plt.ylabel("Összteljesítmény [kW]")
        plt.title(f"Home szegmens – szimulált éves profil ({year})")
        plt.tight_layout()
        plt.show()
    """

    # 2) ÁTLAGOS NAPI PROFIL AZ EGÉSZ ÉVBŐL – MINDEN SZEGMENSRE

    dt_h = DT_MINUTES / 60.0
    steps_per_day = int(24 / dt_h)
    t_day = np.arange(0, 24, dt_h)

    plt.figure(figsize=(10, 5))

    for segment, yearly in yearly_profiles.items():
        if yearly is None or len(yearly) == 0:
            continue

        # hány egész napunk van
        num_days = len(yearly) // steps_per_day
        if num_days == 0:
            continue

        # (nap, időlépés) mátrix
        daily_matrix = yearly[:num_days * steps_per_day].reshape(num_days, steps_per_day)

        # átlagos napi profil
        mean_daily_profile = daily_matrix.mean(axis=0)

        plt.plot(t_day, mean_daily_profile, label=segment)

    plt.xlabel("Óra")
    plt.ylabel("Összteljesítmény [kW]")
    plt.title(f"Átlagos napi profil – szegmensenként (szimulált {year})")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()