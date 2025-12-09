
# ---- SZIMULÁCIÓS BEÁLLÍTÁSOK ----
N_SAMPLES  = 50    # hány mintát húzunk GMM-enként naponta
DT_MINUTES = 60    # időfelbontás percben (60 = órás rács)
DURATION_H = 2.0   # feltételezett töltési idő egy sessionre [óra]
YEAR=2021         # melyik év szimulációja
MARGINAL_SAMPLES = 50000  # hány minta a marginal ábrákhoz
SEGMENTS = ["home", "mud", "public", "work"] #szegmensek listája
ROOT=r'C:/Users/heviz/Documents/Egyetem/Msc/Önlab 2/SPEECh Model for Study on Grid Impacts of Charging Infrastructure Access/SPEECh Model for Study on Grid Impacts of Charging Infrastructure Access/ChargingModelData/GMMs'
# ---------------------------------

# ---- MEKH INTEGRÁCIÓ ----
USE_MEKH_DATA   = False   # ha True, akkor skáláz a MEKH átlagok alapján
MEKH_EXCEL_PATH = r"C:\Users\heviz\Documents\Egyetem\Msc\Önlab 2\Avg_energy_used_for_charging_Hungary.xlsx"   # AZ EXCEL ÚTJA
MEKH_COUNTY     = "Budapest"   # melyik megye sorát használjuk
# -------------------------