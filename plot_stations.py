import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Rutas
data_path = Path("/home/desan/estaciones-conagua-ags/")
combined_file = data_path / 'Aguascalientes_Combined_Data.csv'
shapefile_path = data_path / 'dest2019gw' / 'dest2019gw.shp'

fz= 14
# 2. Carga y Procesamiento de Datos
df = pd.read_csv(combined_file)

# Convertir columnas a numérico y limpiar
df['Lat'] = pd.to_numeric(df['Lat'], errors='coerce')
df['Lon'] = pd.to_numeric(df['Lon'], errors='coerce')
df['Tmean'] = pd.to_numeric(df['Tmean'], errors='coerce')

# Filtro de limpieza: eliminar errores de latitud (como el 215) y valores fuera de México
df = df[(df['Lat'] > 14) & (df['Lat'] < 33) & (df['Lon'] < -80) & (df['Tmean'].notna())]

# Calcular la media anual por estación (ID)
temp_anual = df.groupby('ID').agg({
    'Lat': 'first',
    'Lon': 'first',
    'Tmean': 'mean'
}).reset_index()

# Crear GeoDataFrame
gdf_temp = gpd.GeoDataFrame(
    temp_anual, 
    geometry=gpd.points_from_xy(temp_anual.Lon, temp_anual.Lat),
    crs="EPSG:4326"
)

# 3. Carga y Homologación del Shapefile
mexico = gpd.read_file(shapefile_path)
if mexico.crs != "EPSG:4326":
    mexico = mexico.to_crs("EPSG:4326")

# Filtrar Aguascalientes
ags_shape = mexico[mexico['NOM_ENT'].str.contains('Aguascalientes', case=False, na=False)].copy()

# 4. Visualización de Doble Panel
fig, (ax_mex, ax_zoom) = plt.subplots(1, 2, figsize=(18, 9))

# --- PANEL IZQUIERDO: MÉXICO COMPLETO ---
mexico.plot(ax=ax_mex, color='#e0e0e0', edgecolor='#999999', linewidth=0.5)
if not ags_shape.empty:
    ags_shape.plot(ax=ax_mex, color='red', edgecolor='black', linewidth=1)
#ax_mex.set_title("Localización en México", fontsize=12)
ax_mex.axis('off')

# --- PANEL DERECHO: ZOOM TEMPERATURA MEDIA ---
ax_zoom.set_aspect('equal')
if not ags_shape.empty:
    # Dibujar el contorno del estado
    ags_shape.plot(ax=ax_zoom, color='#f5f5f5', edgecolor='black', linewidth=1.5, zorder=1)
    
    # Ajustar límites del zoom al polígono del estado
    minx, miny, maxx, maxy = ags_shape.total_bounds
    ax_zoom.set_xlim(minx - 0.05, maxx + 0.05)
    ax_zoom.set_ylim(miny - 0.05, maxy + 0.05)

# Graficar estaciones con código de colores por temperatura
scatter = gdf_temp.plot(
    ax=ax_zoom, 
    column='Tmean', 
    cmap='hot_r', # Rojo calor, Azul frío
    legend=True,
    markersize=80, 
    edgecolor='black',
    linewidth=0.5,
    legend_kwds={'label': "Annual mean temperature (°C)", 'orientation': "vertical", 'shrink': 0.7}, 
    zorder=3,
    aspect=None # Evita el ValueError de aspect ratio
)


# Etiquetas de ID y valor de temperatura (solo para las estaciones en la zona del zoom)
#for x, y, label, t in zip(gdf_temp.geometry.x, gdf_temp.geometry.y, gdf_temp.ID, gdf_temp.Tmean):
#    if not ags_shape.empty and (minx-0.1 < x < maxx+0.1) and (miny-0.1 < y < maxy+0.1):
#        ax_zoom.annotate(f"{label}\n{t:.1f}°C", xy=(x, y), xytext=(4, 4), 
#                        textcoords="offset points", fontsize=8, fontweight='bold')

#ax_zoom.set_title('Detalle: Temperatura Media Anual en Aguascalientes', fontsize=14)
ax_zoom.set_xlabel('Longitude', fontsize=fz)
ax_zoom.set_ylabel('Latitude', fontsize=fz)
ax_zoom.grid(linestyle='--', alpha=0.3)

# 1. Obtener el eje de la colorbar (normalmente el último creado por geopandas)
cbar_axes = fig.axes[-1]

# 2. Cambiar el tamaño del título de la barra
cbar_axes.set_ylabel("Annual mean temperature (°C)", fontsize=14)

# 3. Cambiar el tamaño de los números de la escala
cbar_axes.tick_params(labelsize=12)

plt.tight_layout()
plt.show()

print(f"Análisis completado para {len(temp_anual)} estaciones.")
