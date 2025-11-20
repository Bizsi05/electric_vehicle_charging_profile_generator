import pickle
from os.path import join, exists

import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture

def load_gmms():
    gmms = {}
    root = r'C:/Users/Dell/Documents/Egyetem/Msc/Önlab 2/SPEECh Model for Study on Grid Impacts of Charging Infrastructure Access/SPEECh Model for Study on Grid Impacts of Charging Infrastructure Access/ChargingModelData/GMMs'

    for driver_group in range(1, 137):
        for segment in ["home", "mud", "public", "work"]:
            for day in ["weekday", "weekend"]:
                fname = f'{day}_{segment}_l2_{driver_group}.p'
                path = join(root, fname)

                if not exists(path):
                    print(f'{fname} does not exist')
                    continue

                with open(path, 'rb') as f:
                    gmms[f'{day}_{segment}_{driver_group}'] = pickle.load(f)
                    print(f'Loaded {fname}')

    return gmms


def plot_gmm_marginal(gmm: GaussianMixture, dim=0,
                      title="", xlabel="Value"):
    """
    gmm:    egy GaussianMixture objektum
    dim:    melyik dimenziót rajzoljuk (0 = start time, 1 = energia)
    """

    # 1) sok minta generálása a keverékmodellből
    X, _ = gmm.sample(50000)      # 50 000 minta (start time, energy)
    data = X[:, dim]              # csak az adott dimenzió
    # ha az időt rajzoljuk (0. dimenzió), váltsuk át órára
    if dim == 0:
        data = data / 3600.0  # másodperc -> óra

    # 2) hisztogram – density=True, így kb. sűrűségfüggvény
    plt.figure(figsize=(6, 4))
    plt.hist(data, bins=60, density=False, alpha=0.7)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.title(title)
    plt.tight_layout()
    plt.show()


def main():
    gmms = load_gmms()

    # Példa: 1. driver group, home, weekday
    key = "weekday_home_1"
    gmm = gmms[key]

    # Start time eloszlás (óra)
    plot_gmm_marginal(gmm,
                      dim=0,
                      title=f"{key} – start time",
                      xlabel="Start time [h]")

    # Energia eloszlás (kWh)
    plot_gmm_marginal(gmm,
                      dim=1,
                      title=f"{key} – energy",
                      xlabel="Energy [kWh]")


if __name__ == "__main__":
    main()
