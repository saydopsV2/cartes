import folium as fol
import geopandas as gpd
import branca


data = gpd.read_file('./reseauoehc@datacorsica/reseauoehc.shp')

print(data.head())

communeTest = data[data.commune.isin(["VESCOVATO"])] 

#Normalise les diametres pour obtenir une echele de couleur
min_diam = communeTest['diametre'].min()
max_diam = communeTest['diametre'].max()


def get_color(diametre):
    norm_value = (diametre - min_diam) / (max_diam - min_diam)  # Normalisation [0,1]
    return branca.colormap.linear.YlOrRd_09.scale(0, 1)(norm_value)  # Dégradé de Jaune -> Rouge

# Créer la carte centrée sur la zone d'intérêt
m = fol.Map(location=[42.51597, 9.48909], zoom_start=12, tiles="cartodbpositron")

# Ajouter les polygones avec une couleur en fonction du diamètre
for _, row in communeTest.iterrows():
    fol.GeoJson(
        row["geometry"],
        style_function=lambda feature, diam=row["diametre"]: {
            "fillColor": get_color(diam),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7
        },
        tooltip=f"Commune: {row['commune']}, Diamètre: {row['diametre']}"
    ).add_to(m)

# Ajouter une légende pour l'échelle des couleurs
colormap = branca.colormap.linear.YlOrRd_09.scale(min_diam, max_diam)
colormap.caption = "Diamètre des canalisations"
colormap.add_to(m)

m.save('map.html')
