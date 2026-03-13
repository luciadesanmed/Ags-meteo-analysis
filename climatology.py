import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 1. Configuración de Paths
data_path = Path("/home/desan/estaciones-conagua-ags/")
combined_file = data_path / 'Aguascalientes_Combined_Data.csv'

# 2. Carga de datos
if not combined_file.exists():
    print(f"Error: No se encuentra el archivo {combined_file}")
else:
    # Cargamos el archivo que guardamos previamente
    df = pd.read_csv(combined_file)
    
    # Convertir fecha a datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Asegurar que las variables sean numéricas (por si quedaron strings de 'limpieza')
    vars_meteo = ['Precip', 'Tmean', 'Tmax', 'Tmin', 'Evap']
    for var in vars_meteo:
        df[var] = pd.to_numeric(df[var], errors='coerce')

    # 3. Cálculo de Climatologías
    # Creamos columnas auxiliares para agrupar
    df['Mes'] = df['Date'].dt.month
    df['Dia_Ano'] = df['Date'].dt.dayofyear

    # Climatología Mensual (Promedio de cada mes a través de todos los años)
    clim_mensual = df.groupby('Mes')[vars_meteo].mean()

    # Climatología Diaria (Promedio de cada día del año)
    clim_diaria = df.groupby('Dia_Ano')[vars_meteo].mean()

    # 4. Visualización
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    plt.subplots_adjust(hspace=0.4)

    # Gráfico A: Precipitación Mensual
    meses_nombres = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    ax2.bar(clim_mensual.index, clim_mensual['Precip'], color='royalblue', alpha=0.7, label='Precipitación Mensual')
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(meses_nombres)
    ax2.set_title('Precipitation (CONAGUA, 1980-2025)', fontsize=14)
    ax2.set_ylabel('Precipitation (mm/day)')
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    # Gráfico B: Temperaturas Mensuales
    ax1.plot(clim_mensual.index, clim_mensual['Tmax'], 'r-o', label='Max T')
    ax1.plot(clim_mensual.index, clim_mensual['Tmean'], 'g-s', label='Mean T')
    ax1.plot(clim_mensual.index, clim_mensual['Tmin'], 'b-^', label='Min T')
    
    #ax2.fill_between(clim_mensual.index, clim_mensual['Tmin'], clim_mensual['Tmax'], color='orange', alpha=0.1)
    
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(meses_nombres)
    ax1.set_title('Temperature (CONAGUA, 1980-2025)', fontsize=14)
    ax1.set_ylabel('Temperature (°C)')
    ax1.legend()
    ax1.grid(linestyle='--', alpha=0.5)

    #Evaporation:
    #ax3.plot(clim_mensual.index, clim_mensual['Evap'], 'b-')
    #ax3.set_xticks(range(1, 13))
    #ax3.set_xticklabels(meses_nombres)
    #ax3.set_title('Evaporation (CONAGUA, 1980-2025)', fontsize=14)
    #ax3.set_ylabel('Evaporation (mm/day)')
    #ax3.legend()
    #ax3.grid(linestyle='--', alpha=0.5)
    
    plt.savefig("climatology_ags2.png", dpi=300, bbox_inches="tight")
    plt.show()

    # 5. Guardar Climatologías (Opcional)
    #clim_mensual.to_csv(data_path / 'Climatologia_Mensual_Ags.csv')
    #print("Proceso completado. Climatología mensual guardada.")
