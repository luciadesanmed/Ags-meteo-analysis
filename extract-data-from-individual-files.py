import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.colors as mcolors
import pandas as pd
from pathlib import Path
from scipy import stats

#Created by: Ana Lucia de Santos Medina

#Script to extract meteorological variables from each station file and store them in one big file

#Data path:
data_path = Path("/home/desan/estaciones-conagua-ags/")

#File with each station info:
info_stat = data_path / '0_Catalogo_de_estaciones_climatologicas.csv'
#Of this file we will use:
#col 1: station id
#col 3: station latitude
#col 4: station longitude
#col 6: state
stat = pd.read_csv(info_stat, usecols=[1, 3, 4, 6], encoding='latin1')
stat.columns = ['Clave', 'Latitud', 'Longitud', 'Estado']
#Read state location of station, we will be interested in the ones that correspond to "Aguascalientes":
my_state = 'Aguascalientes'

stat_id = stat.loc[stat['Estado']==my_state, 'Clave'].astype(str) #storing the id of the stations in Ags
stat_lon = stat.loc[stat['Estado']==my_state, 'Longitud'] #store lon
stat_lat = stat.loc[stat['Estado']==my_state, 'Latitud'] #store lat

#Open each station file:

#Extract these range of dates:
start_date = pd.to_datetime('1980-01-01')
end_date = pd.to_datetime('2025-12-31')

ags_stations = stat[stat['Estado'] == my_state].copy()

# 2. Setup for Extraction
start_date = pd.to_datetime('1980-01-01')
end_date = pd.to_datetime('2025-12-31')

all_data = [] # List to store dataframes from each station

#File structure:
#col 0: date
#col 1: precipitation (mm)
#col 2: mean temperature (C)
#col 3: max temperature (C)
#col 4: min temperature (C)
#col 5: evaporation (mm)
# 3. Loop through filtered stations
for index, row in ags_stations.iterrows():
    s_id = str(row['Clave'])
    file_path = data_path / f"{s_id}.csv"

    if file_path.exists():
        print(f"Processing station: {s_id}")

        # Read the file
        dm = pd.read_csv(file_path, skiprows=8, header=None, usecols=[0, 1, 2, 3, 4, 5])

        # Clean Dates & Filter
        dm[0] = pd.to_datetime(dm[0], dayfirst=True, errors='coerce')
        dm = dm.dropna(subset=[0]) # Remove rows where date parsing failed

        date_mask = dm[0].between(start_date, end_date)
        dm_sub = dm[date_mask].copy()

        # Convert columns to numeric (handling the non-numerical values with NaN)
        for col in [1, 2, 3, 4, 5]:
            dm_sub[col] = pd.to_numeric(dm_sub[col], errors='coerce')

        # Attach location info
        dm_sub['Clave'] = s_id
        dm_sub['Latitud'] = row['Latitud']
        dm_sub['Longitud'] = row['Longitud']

        all_data.append(dm_sub)
    else:
        print(f"Warning: File {file_path} not found.")

# Merge all stations into one big DataFrame
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.columns = ['Date', 'Precip', 'Tmean', 'Tmax', 'Tmin', 'Evap', 'ID', 'Lat', 'Lon']

    # Save the result
    final_df.to_csv(data_path / 'Aguascalientes_Combined_Data.csv', index=False)
    print("Successfully created combined file")
else:
    print("No data was collected")
