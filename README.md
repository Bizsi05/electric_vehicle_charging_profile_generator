Electric Vehicle Charging Profile Generator

Overview

This small Python project generates and visualizes simulated electric vehicle (EV) charging profiles using pre-trained Gaussian mixture models (GMMs). The GMMs describe arrival (start) times and per-session energy consumption for different user segments (e.g. home, work, public). The tool can sample the GMMs to create daily and yearly aggregated charging load time series and produces several matplotlib plots to inspect marginal distributions, daily segment profiles and annual statistics.

Key features

- Load pre-trained GMMs (pickle files) for different driver groups and segments.
- Sample from the GMMs to create per-segment daily charging profiles.
- Aggregate sampled days into an hourly (or configurable DT) yearly time series per segment.
- Plot marginal distributions (start time, energy), one-day segment profiles, daily energy scatter, and mean daily profiles.
- Optional integration with MEKH Excel data to scale energy usage to region/quarter averages.

Repository layout

- main.py              - Example driver script demonstrating the workflow and producing plots.
- config.py            - Global simulation and data-path settings.
- data_loading.py      - Routines to load GMM pickles and MEKH Excel data.
- new_samples.py       - Sampling helpers and conversion from samples to time-series profiles.
- simulations.py       - Year-long simulation logic using the calendar/daytype helper.
- plotting.py          - Matplotlib plotting helpers.
- calendar_for_daytype.py - Hungarian holiday/calendar helpers.
- LICENSE

Requirements

- Python 3.8+ (tested with 3.10/3.11)
- Packages:
  - numpy
  - pandas
  - matplotlib
  - scikit-learn
  - openpyxl (only needed if using MEKH Excel integration)

Install dependencies (recommended in a virtual environment):

# PowerShell example
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install --upgrade pip; pip install numpy pandas matplotlib scikit-learn openpyxl

Quick start

1) Place the GMM pickle files in the folder specified by `ROOT` in `config.py`.
   - Expected filename pattern: `{day}_{segment}_l2_{driver_group}.p`
   - day: `weekday` or `weekend`
   - segment: one of the segments listed in `config.SEGMENTS` (default: `home`, `mud`, `public`, `work`)
   - driver_group: integer group id used when the GMMs were created (the code searches driver_group from 1..136 by default)

2) (Optional) If you want to scale energy to regional averages using MEKH data:
   - Set `USE_MEKH_DATA = True` in `config.py`.
   - Update `MEKH_EXCEL_PATH` to point to the MEKH Excel file (XLSX) and set the `MEKH_COUNTY`.
   - The code expects the Excel to contain quarterly average energy-per-charge values; `data_loading.load_mekh_table` parses columns named like `YYYY Qn`.

3) Run the example driver that produces plots:

# PowerShell
python main.py

This will:
- Load all available GMM pickle files from the `ROOT` directory.
- Plot marginal distributions for a selected GMM (in `main.py`, key is `weekday_home_1`).
- Sample the GMMs and plot a one-day per-segment profile.
- Run a full-year simulation and produce daily energy and mean-daily profile plots.

Configuration (important variables in `config.py`)

- N_SAMPLES: Number of samples drawn per GMM (per day).
- DT_MINUTES: Time-step resolution in minutes (60 -> hourly grid).
- DURATION_H: Assumed charging duration per session in hours (used to convert energy to constant kW).
- YEAR: Year to simulate.
- MARGINAL_SAMPLES: Number of samples to draw for plotting marginal histograms.
- SEGMENTS: List of segment names expected in the pickle filenames.
- ROOT: Directory containing the GMM pickle files.
- USE_MEKH_DATA / MEKH_EXCEL_PATH / MEKH_COUNTY: MEKH scaling options.

Data expectations

- GMM pickle files: each file should contain a scikit-learn GaussianMixture object whose samples are structured as (start_time_seconds, energy_kwh). The project uses the `.sample()` method of GaussianMixture.
- MEKH Excel (optional): a table with county rows and quarterly columns titled like `2021 Q1`, containing average kWh per charge.

Internals & outputs

- Sampling: `new_samples.sample_gmms` draws `N_SAMPLES` from every loaded GMM.
- Sample format: each sample is (start_time_seconds, energy_kwh).
- Conversion to profile: `new_samples.convert_sample_to_triple` maps a sample to (start_index, duration_steps, level_kW, n_steps) given `DT_MINUTES` and `DURATION_H`.
- Daily profile: `new_samples.samples_to_profile` aggregates all samples for a segment into a 24h array (units kW) on the configured time grid.
- Yearly aggregation: `simulations.simulate_year` builds a concatenated per-segment time series covering the whole year and returns a `time_index` and `yearly_profiles` dict.
- Plotting functions in `plotting.py` show figures directly using matplotlib.

Extending / next steps

- Add a CLI (argparse or Click) to choose config overrides, output file paths, or to save figures to disk instead of showing them.
- Add tests that validate sample shapes, conversion logic, and annual aggregation.
- Add a small utility to export the yearly_profiles to CSV/Parquet for downstream analysis.
- Improve handling of missing or malformed GMM files and provide better logging.

Development notes

- The code assumes GMMs were trained with two dimensions: start time (seconds) and energy (kWh).
- The sampling code forces single-component GMMs to have full weight on the single component to avoid degenerate weights.
- When using MEKH scaling, the entire day's samples are uniformly scaled so the mean sample energy matches the MEKH target for that date/quarter.

License

See the bundled LICENSE file.

Support / Contact

If you need help running the code or want to extend it, open an issue or contact the repository owner.

