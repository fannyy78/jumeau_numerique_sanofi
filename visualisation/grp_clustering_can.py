import os 
import pandas as pd 
import geopandas as gpd
import folium
from branca.element import MacroElement 
from jinja2 import Template 
from IPython.display import IFrame 
import webbrowser
from shapely.geometry import MultiPolygon

base_dir = "/home/oneai/jumeau_num" # chemin
if not os.path.exists(base_dir):
    raise FileNotFoundError(f"Le dossier {base_dir} n'existe pas !")

gdf_com_2024_path = os.path.join(base_dir, "gdf_com_2024.geojson")
gdf_dep_path = os.path.join(base_dir, "gdf_dep.geojson")
factors_path = os.path.join(base_dir, "tables", "factors_PCA_au_canton.csv")
codes_geo_2024_path = os.path.join(base_dir, "insee_millesime_importation", "v_commune_2024.csv")

gdf_com_2024 = gpd.read_file(gdf_com_2024_path)
gdf_dep = gpd.read_file(gdf_dep_path)
factors = pd.read_csv(factors_path)
codes_geo_2024 = pd.read_csv(codes_geo_2024_path)


# ---------- Correction canton ----------
factors['canton'] = factors['canton'].astype(str).str.replace(r'\.0$', '', regex=True)
factors['canton'] = factors['canton'].apply(lambda x: x.zfill(4) if len(x) == 3 else x)

# ---------- Fusion pour ajouter la colonne 'canton' ----------
gdf_com_2024 = gdf_com_2024.merge(
    codes_geo_2024[['COM', 'CAN']],
    left_on='COM_geojson',
    right_on='COM',
    how='left'
)
gdf_com_2024 = gdf_com_2024.drop(columns=['COM', 'COM_geojson'])
gdf_com_2024 = gdf_com_2024.rename(columns={'CAN':'canton'})

# ---------- Regrouper par canton ----------
gdf_cantons = gdf_com_2024.dissolve(by='canton', as_index=False)

# ---------- Gestion MultiPolygon ----------
def to_single_polygon(geom):
    if isinstance(geom, MultiPolygon):
        return max(geom.geoms, key=lambda a: a.area)
    return geom

gdf_cantons['geometry'] = gdf_cantons['geometry'].apply(to_single_polygon)
gdf_cantons['geometry'] = gdf_cantons['geometry'].simplify(tolerance=0.001, preserve_topology=True)

# ---------- Moyenne des facteurs par canton ----------
factors['canton'] = factors['canton'].astype(str)
gdf_cantons['canton'] = gdf_cantons['canton'].astype(str)

facteur_columns = [col for col in factors.columns if col not in ['codgeo', 'libgeo', 'cluster', 'canton']]
factors_canton = factors.groupby('canton')[facteur_columns].mean().reset_index()

# ---------- Fusion avec les géométries des cantons ----------
gdf_factors = gdf_cantons.merge(factors_canton, on='canton', how='left')

# ---------- Reprojection et calcul des centroïdes ----------
gdf_factors_proj = gdf_factors.to_crs(epsg=2154)
gdf_factors_proj['centroid'] = gdf_factors_proj.geometry.centroid
centroids_wgs84 = gdf_factors_proj.set_geometry('centroid').to_crs(epsg=4326)
gdf_factors['lon'] = centroids_wgs84.geometry.x
gdf_factors['lat'] = centroids_wgs84.geometry.y

# Palette qualitative
cluster_colors = {
    0: "green",
    1: "deeppink", 
    2: "blue",
    3:"orange"
}

legend_html = """
<div style="
    position: fixed;
    bottom: 50px;
    left: 50px;
    width: 160px;
    height: 170px;
    background-color: white;
    border:2px solid grey;
    z-index:9999;
    font-size:14px;
    padding: 10px;
">
    <b>Clusters</b><br>
    <i style="background: green; width: 10px; height: 10px; float: left; margin-right: 8px;"></i>Cluster 0<br>
    <i style="background: deeppink; width: 10px; height: 10px; float: left; margin-right: 8px;"></i>Cluster 1<br>
    <i style="background: blue; width: 10px; height: 10px; float: left; margin-right: 8px;"></i>Cluster 2<br>
    <i style="background: orange; width: 10px; height: 10px; float: left; margin-right: 8px;"></i>Cluster 3
</div>
"""

# carte
carte_france = folium.Map(
    location=[46.5, 2],
    zoom_start=6,
    min_zoom=5.9,
    max_bounds=True,
    tiles="CartoDB positron"
)

bounds_sud_ouest = [41.0, -5.0]
bounds_nord_est = [51.5, 9.5]
carte_france.fit_bounds([bounds_sud_ouest, bounds_nord_est])
carte_france.options['maxBounds'] = [bounds_sud_ouest, bounds_nord_est]

# Départements
folium.GeoJson(
    gdf_dep,
    name="Départements",
    style_function=lambda x: {"color": "black", "weight": 0.7, "fillOpacity": 0},
    tooltip=folium.GeoJsonTooltip(fields=["nom", "code"], aliases=["Département", "Code INSEE"])
).add_to(carte_france)


# S'assurer que Cluster est de type int
gdf_factors['Cluster'] = gdf_factors['Cluster'].astype(int)

# Couche GeoJson par cluster
folium.GeoJson(
    gdf_factors,
    name="Clusters",
    style_function=lambda feature: {
        'fillColor': cluster_colors.get(feature['properties']['Cluster'], 'gray'),
        'color': 'black',
        'weight': 0.2,
        'fillOpacity': 0.7
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["canton", "Cluster"],
        aliases=["Canton", "Cluster"],
        localize=True
    )
).add_to(carte_france)

carte_france.get_root().html.add_child(folium.Element(legend_html))

# LayerControl
folium.LayerControl().add_to(carte_france)
carte_france
