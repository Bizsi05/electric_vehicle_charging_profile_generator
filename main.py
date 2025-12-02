import numpy as np

from data_loading import load_gmms
from plotting import plot_gmm_marginal

#gmms[f'{day}_{segment}_{driver_group}'] = pickle.load(f)

def sample_gmms(gmms, n_samples=10):
    samples = {}
    for key, gmm in gmms.items():
        print(gmm.n_components)
        if gmm.n_components==1:
            #print(gmm.weights_[0])
            gmm.weights_[0] = 1.
        X, _ = gmm.sample(n_samples)
        samples[key] = X
    #print(samples)
    return samples

def regroup_samples_by_segment(samples):
    regrouped = {}
    for key, data in samples.items():
        # key formátum: '{day}_{segment}_{driver_group}'
        parts = key.split('_')
        day = parts[0]
        segment = parts[1]
        driver_group = parts[2]
        if day=='weekday':
            seg_key = f'{segment}'
            if seg_key not in regrouped:
                regrouped[seg_key] = []
            regrouped[seg_key].append(data)

    # Összefűzés
    for key, data in regrouped.items():
        print(len(regrouped[key]))
        print(key)
        regrouped[key] = np.vstack(regrouped[key])

    return regrouped



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

    #sample_gmms(gmms, 50)
    regroup_samples_by_segment(sample_gmms(gmms, 50))


if __name__ == "__main__":
    main()


