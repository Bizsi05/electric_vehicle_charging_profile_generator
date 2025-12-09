import pickle
from os.path import join, exists
from config import ROOT, SEGMENTS, MEKH_EXCEL_PATH

import pandas as pd
import re

def load_gmms():
    gmms = {}
    root = ROOT
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

def load_mekh_table(path = MEKH_EXCEL_PATH) -> pd.DataFrame:

    if path is None:
        path = MEKH_EXCEL_PATH

    df_raw = pd.read_excel(path)

    # 2) első oszlop neve legyen biztosan 'megye'
    first_col = df_raw.columns[0]
    df_raw = df_raw.rename(columns={first_col: "megye"})

    records = []

    for col in df_raw.columns[1:]:
        col_str = str(col).strip()

        m = re.match(r"(\d{4})\s+Q([1-4])", col_str, flags=re.IGNORECASE)
        if not m:
            # ha nem ilyen formájú, átugorja
            continue
        year = int(m.group(1))
        quarter = int(m.group(2))

        for _, row in df_raw.iterrows():
            county = row["megye"]
            val = row[col]
            # N/A / üres cellák kihagyása
            if pd.isna(val):
                continue
            records.append({
                "megye": county,
                "year": year,
                "quarter": quarter,
                "avg_kwh": float(val),
            })

    mekh_df = pd.DataFrame(records)

    return mekh_df

def get_mekh_avg_kwh(mekh_df: pd.DataFrame, megye: str, date) -> float: # Egy adott naphoz megadja az adott megyére vonatkozó átlagos energia/töltés értéket

    year = date.year
    month = date.month
    quarter = (month - 1) // 3 + 1

    mask = (
        (mekh_df["megye"] == megye)
        & (mekh_df["year"] == year)
        & (mekh_df["quarter"] == quarter)
    )
    sub = mekh_df[mask]
    if sub.empty:
        raise ValueError(f"Nincs MEKH adat: {megye}, {year} Q{quarter}")
    return float(sub["avg_kwh"].iloc[0])
