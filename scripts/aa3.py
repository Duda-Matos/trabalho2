# -*- coding: utf-8 -*-
"""
Created on Sat Jun  7 15:27:43 2025

@author: dudad
"""

import geopandas as gpd
import matplotlib.pyplot as plt

# Supondo que CAMINHO_SHAPEFILE já esteja definido no seu script
# Este shapefile deve conter os limites dos estados (ou municípios, se preferir)
CAMINHO_SHAPEFILE = r"C:\Users\dudad\Documents\GitHub\ENS5132\desafio\inputs\BR_UF_2024\BR_UF_2024.shp"

print("Carregando o shapefile de estados...")
shape_estados = gpd.read_file(CAMINHO_SHAPEFILE)

# Opcional: Garante que o CRS é WGS84, como nos seus dados raster
if shape_estados.crs != "EPSG:4326":
    print("Reprojetando para EPSG:4326 (WGS84)...")
    shape_estados = shape_estados.to_crs("EPSG:4326")

# Dissolver todos os polígonos dos estados em um único polígono do Brasil
# Isso remove as fronteiras internas dos estados, criando um único contorno para o país.
print("Dissolvendo polígonos para obter o contorno do Brasil...")
contorno_brasil = shape_estados.unary_union

# Para plotar, é melhor ter um GeoDataFrame, mesmo que seja de uma única geometria
gdf_contorno_brasil = gpd.GeoDataFrame(geometry=[contorno_brasil], crs=shape_estados.crs)

print("Exibindo o contorno externo do Brasil...")
plt.figure(figsize=(10, 8))

# Plotar o contorno do Brasil. Você pode definir a cor da linha e preenchimento.
# edgecolor define a cor da linha de contorno
# facecolor define a cor de preenchimento (pode ser 'none' para apenas o contorno)
gdf_contorno_brasil.plot(ax=plt.gca(), edgecolor='blue', linewidth=1.5, facecolor='lightgray')

plt.title("Contorno do Brasil")
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

print("Contorno do Brasil plotado com sucesso.")