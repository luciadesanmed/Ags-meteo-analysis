import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from sklearn.neighbors import NearestNeighbors

# 1. CONFIGURACIÓN DE RUTAS
data_path = Path("/home/desan/estaciones-conagua-ags/")
combined_file = data_path / 'Aguascalientes_Combined_Data.csv'
shapefile_path = data_path / 'dest2019gw' / 'dest2019gw.shp'

# 2. CARGA Y LIMPIEZA INICIAL DE DATOS
df = pd.read_csv(combined_file)
df['Lat'] = pd.to_numeric(df['Lat'], errors='coerce')
df['Lon'] = pd.to_numeric(df['Lon'], errors='coerce')
df['Precip'] = pd.to_numeric(df['Precip'], errors='coerce')

# Filtro geográfico estricto para eliminar errores de captura (como Lat 215)
# Rango para México: Lat (14 a 33), Lon (-118 a -86)
df_limpio = df[
    (df['Lat'] > 14) & (df['Lat'] < 33) & 
    (df['Lon'] < -80) & (df['Precip'].notna())
].copy()

# Calcular media anual por estación única
temp_anual = df_limpio.groupby('ID').agg({
    'Lat': 'first',
    'Lon': 'first',
    'Precip': 'mean'
}).reset_index()

# Crear GeoDataFrame
gdf_temp = gpd.GeoDataFrame(
    temp_anual, 
    geometry=gpd.points_from_xy(temp_anual.Lon, temp_anual.Lat),
    crs="EPSG:4326"
)

# 3. FILTRO DE VECINOS CERCANOS (OUTLIERS ESPACIALES)
n_vecinos = 5  
umbral_tolerancia = 0.5  # Diferencia máxima permitida en °C respecto al promedio local

coords = gdf_temp[['Lon', 'Lat']].values
nbrs = NearestNeighbors(n_neighbors=n_vecinos + 1).fit(coords)
distancias, indices = nbrs.kneighbors(coords)

valores_Tmean = gdf_temp['Precip'].values
outliers_indices = []

for i in range(len(gdf_temp)):
    idx_vecinos = indices[i][1:] # Saltamos la estación misma
    promedio_local = np.mean(valores_Tmean[idx_vecinos])
    if abs(valores_Tmean[i] - promedio_local) > umbral_tolerancia:
        outliers_indices.append(i)

# Remover estaciones inconsistentes
gdf_final = gdf_temp.drop(gdf_temp.index[outliers_indices]).copy()
print(f"Estaciones eliminadas por discrepancia con vecinos: {len(outliers_indices)}")

# 4. CARGA Y HOMOLOGACIÓN DEL SHAPEFILE
mexico = gpd.read_file(shapefile_path)
if mexico.crs != "EPSG:4326":
    mexico = mexico.to_crs("EPSG:4326")

ags_shape = mexico[mexico['NOM_ENT'].str.contains('Aguascalientes', case=False, na=False)].copy()

# 5. VISUALIZACIÓN DE DOBLE PANEL
fig, (ax_mex, ax_zoom) = plt.subplots(1, 2, figsize=(18, 9))

# --- PANEL IZQUIERDO: MÉXICO ---
mexico.plot(ax=ax_mex, color='#e0e0e0', edgecolor='#999999', linewidth=0.5)
if not ags_shape.empty:
    ags_shape.plot(ax=ax_mex, color='red', edgecolor='black', linewidth=1)
#ax_mex.set_title("Localización en México", fontsize=12)
ax_mex.axis('off')

# --- PANEL DERECHO: ZOOM AGUASCALIENTES ---
ax_zoom.set_aspect('equal')
if not ags_shape.empty:
    ags_shape.plot(ax=ax_zoom, color='#f9f9f9', edgecolor='black', linewidth=1.5, zorder=1)
    minx, miny, maxx, maxy = ags_shape.total_bounds
    ax_zoom.set_xlim(minx - 0.05, maxx + 0.05)
    ax_zoom.set_ylim(miny - 0.05, maxy + 0.05)

# Plotear estaciones con colormap
scatter = gdf_final.plot(
    ax=ax_zoom, 
    column='Precip', 
    cmap='gist_earth_r', 
    legend=True,
    markersize=90, 
    edgecolor='black',
    linewidth=0.6,
    legend_kwds={'label': "Precipipitation (mm/day)", 'orientation': "vertical", 'shrink': 0.7},
    zorder=3
)

# Ajustar tamaño de fuente de la BARRA DE COLOR
cax = fig.axes[-1]
cax.yaxis.label.set_size(15)  # Tamaño del título de la barra
cax.tick_params(labelsize=12)  # Tamaño de los números de la escala

# Etiquetas de ID y valor
#for x, y, label, t in zip(gdf_final.geometry.x, gdf_final.geometry.y, gdf_final.ID, gdf_final.Tmean):
#    if not ags_shape.empty and (minx-0.1 < x < maxx+0.1) and (miny-0.1 < y < maxy+0.1):
#        ax_zoom.annotate(f"{label}\n{t:.1f}°", xy=(x, y), xytext=(4, 4), 
#                        textcoords="offset points", fontsize=8, fontweight='bold')

ax_zoom.set_title('Annual mean precipitation (CONAGUA, 1980-2025)', fontsize=16)
ax_zoom.grid(linestyle='--', alpha=0.3)
ax_zoom.set_xlabel('Longitude', fontsize=12)
ax_zoom.set_ylabel('Latitude', fontsize=12)


plt.tight_layout()
plt.savefig('Mapa_prec_AGS.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"Análisis finalizado: {len(gdf_final)} estaciones graficadas.")
