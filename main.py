import pickle
from os.path import join, exists

from sklearn.mixture import GaussianMixture

gmms = {}
def main():
    root = 'C:/Users/Dell/Documents/Egyetem/Msc/Önlab 2/SPEECh Model for Study on Grid Impacts of Charging Infrastructure Access/SPEECh Model for Study on Grid Impacts of Charging Infrastructure Access/ChargingModelData/GMMs'
    for driver_group in range(1, 137):
        for segment in ["home", "mud", "public", "work"]:

            for day in ["weekday", "weekend"]:
                if not exists(join(root, f'{day}_{segment}_l2_{driver_group}.p')):
                    print(f'{day}_{segment}_l2_{driver_group}.p does not exist')
                    continue
                with open(join(root, f'{day}_{segment}_l2_{driver_group}.p'), 'rb') as f:
                    gmms[f'{day}_{segment}_{driver_group}'] = pickle.load(f)
                    print(
                        f'Loaded data for driver group {driver_group}, segment {segment}, day {day}')
    print(gmms)


if __name__ == "__main__":
    main()
