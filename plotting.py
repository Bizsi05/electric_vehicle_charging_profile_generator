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


def plot_gmm_scatter_2d(gmm: GaussianMixture, title="2D GMM minták", n_samples=20000):
    """
    2D szórásdiagram a GMM-ből: start time [h] vs. energia [kWh]
    """
    X, _ = gmm.sample(n_samples)
    start_h = X[:, 0] / 3600.0  # másodperc -> óra
    energy = X[:, 1]

    plt.figure(figsize=(6, 5))
    plt.scatter(start_h, energy, s=3, alpha=0.2)
    plt.xlabel("Start time [h]")
    plt.ylabel("Energy [kWh]")
    plt.title(title)
    plt.grid(True)
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

def plot_samples_scatter_for_segment(samples_by_segment, segment, title=None):
    """
    Egy nap szintetikus mintáinak szórásdiagramja egy szegmensre.
    samples_by_segment: dict[segment] -> ndarray(N,2) [start_sec, energy_kWh]
    """
    data = samples_by_segment.get(segment)
    if data is None or len(data) == 0:
        return

    start_h = data[:, 0] / 3600.0
    energy  = data[:, 1]

    plt.figure(figsize=(6, 4))
    plt.scatter(start_h, energy, s=5, alpha=0.3)
    plt.xlabel("Start time [h]")
    plt.ylabel("Energy [kWh]")
    plt.title(title or f"{segment} – minták egy napra")
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

def plot_total_weekday_weekend(time_index, yearly_profiles):
    """
    Összes szegmens összegzett átlagos napi profilja hétköznapra és hétvégére
    """
    dt_h = DT_MINUTES / 60.0
    steps_per_day = int(24 / dt_h)

    # összteljesítmény: szegmensek összege
    total = None
    for arr in yearly_profiles.values():
        total = arr if total is None else total + arr

    total = np.asarray(total)
    num_days = len(total) // steps_per_day
    if num_days == 0:
        return

    weekday_days = []
    weekend_days = []

    for day in range(num_days):
        start_idx = day * steps_per_day
        end_idx   = start_idx + steps_per_day
        day_profile = total[start_idx:end_idx]

        first_dt = time_index[start_idx]
        if first_dt.weekday() < 5:   # 0-4 hétköznap
            weekday_days.append(day_profile)
        else:                        # 5-6 hétvége
            weekend_days.append(day_profile)

    t_day = np.arange(steps_per_day) * dt_h

    plt.figure(figsize=(8, 4))
    if weekday_days:
        mean_wd = np.vstack(weekday_days).mean(axis=0)
        plt.plot(t_day, mean_wd, label="Hétköznap")
    if weekend_days:
        mean_we = np.vstack(weekend_days).mean(axis=0)
        plt.plot(t_day, mean_we, label="Hétvége")

    plt.xlabel("Óra")
    plt.ylabel("Összteljesítmény [kW]")
    plt.title("Összesített EV-töltési profil – hétköznap vs hétvége")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
