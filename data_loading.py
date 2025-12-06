import pickle
from os.path import join, exists
from new_samples import SEGMENTS


def load_gmms():
    gmms = {}
    root = r'C:/Users/heviz/Documents/Egyetem/Msc/Önlab 2/SPEECh Model for Study on Grid Impacts of Charging Infrastructure Access/SPEECh Model for Study on Grid Impacts of Charging Infrastructure Access/ChargingModelData/GMMs'

    for driver_group in range(1, 137):
        for segment in SEGMENTS:
            for day in ["weekday", "weekend"]:
                fname = f'{day}_{segment}_l2_{driver_group}.p'
                path = join(root, fname)

                if not exists(path):
                   # print(f'{fname} does not exist')
                    continue

                with open(path, 'rb') as f:
                    gmms[f'{day}_{segment}_{driver_group}'] = pickle.load(f)
                  #  print(f'Loaded {fname}')

    return gmms