import folium as fol
import geopandas as gpd
import branca



data = gpd.read_file('./rpg-bio-2023-national/rpg-bio-2023-national.shp')

print(data.info())

data = data[data.code_depar.isin(['33'])]
print(data.head())


# parcelleTest = data[data.gid.isin(["1057718"])]


# print(parcelleTest.head())



#Normalise les hectares pour obtenir un echele de couleur
min_ha = data['surface_ha'].min()
max_ha = data['surface_ha'].max()

def get_color(surface):
    norm_value = (surface - min_ha) / (max_ha - min_ha)
    return branca.colormap.linear.YlOrRd_09.scale(0, 1)(norm_value)


location = [45.31632,-0.66347]

zoom = 10

tiles = 'cartodbpositron'

Carte  = fol.Map(location=location, 
                 zoom_start=zoom,
                 tiles=tiles)

for _, row in data.iterrows():
    fol.GeoJson(
        row['geometry'],
        style_function=lambda feature, diam=row['surface_ha'] : {
            "fillColor": get_color(diam),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7
        },
        tooltip=f"Champs: {row['gid']}, Surface: {row['surface_ha']}"
    ).add_to(Carte)

#Converstion en GeoJson
data = data.to_json()

colormap = branca.colormap.linear.YlOrRd_09.scale(min_ha, max_ha)
colormap.caption = "Surface des champs"
colormap.add_to(Carte)

Carte.save('parcelle.html')
