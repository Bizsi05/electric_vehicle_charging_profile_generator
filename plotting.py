import pickle
from os.path import join, exists

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
    X, _ = gmm.sample(50000)      # 50 000 minta (start time, energy)
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