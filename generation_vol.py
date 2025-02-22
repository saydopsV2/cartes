import folium as fol
import geopandas as gpd
import branca
from folium.plugins import HeatMap, FeatureGroupSubGroup

# Charger les données
data = gpd.read_file('./2022/cambriolageslogementsechelleinfracommunale.2022.shp')

# Vérifier le CRS actuel
print(f"CRS actuel : {data.crs}")

# A décommenter pour filtrer la ville que l'on veut et remplacer data par dataTest pour la suite du fichier
#dataTest = data[data["libelle_uu"] == "Montbéliard"].copy()

# Convertir la colonne "classe" en valeurs numériques
data["classe"] = data["classe"].str.replace(',', '.').str.extract(r'([\d.]+)').astype(float)

# Reprojeter en Lambert 93 pour calculs précis
data = data.to_crs(epsg=2154)

# Reprojeter les centroïdes en WGS84 (EPSG:4326) pour affichage sur la carte
data["latitude"] = data.geometry.centroid.to_crs(epsg=4326).y
data["longitude"] = data.geometry.centroid.to_crs(epsg=4326).x

# Repasser en WGS84 pour folium
data = data.to_crs(epsg=4326)

# Créer la carte centrée sur Montbéliard
m = fol.Map(location=[46.6, 2.5], zoom_start=6, tiles="cartodbpositron")

# Ajouter les groupes de couches
heatmap_layer = fol.FeatureGroup(name="HeatMap", show=True)  # Activée par défaut
polygons_layer = fol.FeatureGroup(name="Polygones", show=False)  # Désactivé par défaut

# Ajouter la HeatMap
heat_data = list(zip(data["latitude"], data["longitude"], data["classe"]))
HeatMap(heat_data, radius=15, blur=10, max_zoom=12).add_to(heatmap_layer)

# Définir une échelle de couleurs pour les polygones
colormap = branca.colormap.linear.YlOrRd_09.scale(data["classe"].min(), data["classe"].max())
colormap.caption = "Intensité des cambriolages"

# Ajouter les polygones colorés selon la classe
for _, row in data.iterrows():
    fol.GeoJson(
        row["geometry"],
        style_function=lambda feature, classe=row["classe"]: {
            "fillColor": colormap(classe),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7
        },
        tooltip=f"Ville: {row['libelle_uu']}, Classe: {row['classe']}"
    ).add_to(polygons_layer)

# Ajouter les couches à la carte
m.add_child(heatmap_layer)
m.add_child(polygons_layer)

# Ajouter le LayerControl pour basculer entre les vues
fol.LayerControl().add_to(m)

# Ajouter la légende (attachée aux polygones)
colormap.add_to(m)

# Sauvegarder la carte
m.save('vol.html')
