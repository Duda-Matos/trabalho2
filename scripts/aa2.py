# -*- coding: utf-8 -*-
"""
Created on Sat Jun  7 14:51:26 2025

@author: dudad
"""

import os
import xarray as xr
import rioxarray
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import locale  # Usado para formatar os meses em português
#%%

pasta_dados = r"C:\Users\dudad\Documents\GitHub\ENS5132\trabalho_02\inputs\merra"
padrao_arquivos = os.path.join(pasta_dados, "*.nc4")

# Caminho para shapefile com municípios do Brasil para recorte geográfico
CAMINHO_SHAPEFILE = r"C:\Users\dudad\Documents\GitHub\ENS5132\desafio\inputs\BR_UF_2024\BR_UF_2024.shp"


#%%
import geopandas as gpd
import matplotlib.pyplot as plt

# Supondo que CAMINHO_SHAPEFILE já esteja definido no seu script
CAMINHO_SHAPEFILE = r"C:\Users\dudad\Documents\GitHub\ENS5132\desafio\inputs\BR_UF_2024\BR_UF_2024.shp"

print("Carregando o shapefile de estados...")
shape_estados = gpd.read_file(CAMINHO_SHAPEFILE)

# Opcional: Garante que o CRS é WGS84, como nos seus dados raster
if shape_estados.crs != "EPSG:4326":
    shape_estados = shape_estados.to_crs("EPSG:4326")

# Para exibir apenas as linhas que separam os estados:
# 1. Acesse a propriedade .boundary de cada geometria no GeoDataFrame.
#    Isso converte os polígonos dos estados em MultiLineStrings que representam seus limites.
linhas_estados = shape_estados.geometry.boundary

# 2. Crie um novo GeoDataFrame apenas com as linhas de limite
#    Isso é útil para plotar ou para análises futuras que exigem geometrias de linha
gdf_linhas_estados = gpd.GeoDataFrame(geometry=linhas_estados, crs=shape_estados.crs)

print("Exibindo apenas os limites dos estados...")
plt.figure(figsize=(10, 8))
gdf_linhas_estados.plot(ax=plt.gca(), edgecolor='blue', linewidth=1.5)
plt.title("Limites dos Estados do Brasil")
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

print("Limites dos estados plotados com sucesso.")
#%%
print(">>> Gerando Gráfico 2: Mapa da Tendência Média...")
media_temporal = data_recortado.mean(dim='time') * 86400

plt.figure(figsize=(10, 8))
ax_map = plt.gca() # Captura o Axes para plotar várias camadas
media_temporal.plot(
    ax=ax_map, # Plota no Axes capturado
    cmap='RdBu_r',
    robust=True,
    cbar_kwargs={'label': 'Tendência Média (K/dia)', 'orientation': 'horizontal', 'pad': 0.1} # Corrigido cbar_kwargs
)
# Plota os limites dos estados sobre o mapa da tendência
gdf_linhas_estados.plot(ax=ax_map, edgecolor='black', linewidth=0.7, zorder=2) # zorder garante que esteja acima

plt.title(f"Padrão Espacial da Tendência de Temperatura em {NIVEL_PRESSAO} hPa com Limites Estaduais", fontsize=16, pad=20)
plt.xlabel('Longitude', fontsize=12)
plt.ylabel('Latitude', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6) # Corrigido para não duplicar
plt.tight_layout()
plt.show()

#%%
# Variável de interesse do MERRA-2 (Tendência Total da Temperatura)
VARIAVEL_INTERESSE = "DTDTTOT"
# Nível de pressão em hPa (ex: 850 para baixa troposfera)
NIVEL_PRESSAO = 850

# Lista de variáveis de contribuição para análise comparativa
VARIAVEIS_CONTRIBUICAO = [
    'DTDTTOT', 'DTDTANA', 'DTDTDYN', 'DTDTFRI',
    'DTDTGWD', 'DTDTMST', 'DTDTRB', 'DTDTRAD']

# %% 3. Carregamento e Preparação dos Dados Raster
print("Carregando arquivos NetCDF...")
try:
    # Abre múltiplos arquivos de forma eficiente e paralela
    padrao_arquivos = os.path.join(pasta_dados, "*.nc4")
    ds = xr.open_mfdataset(padrao_arquivos, combine='by_coords', parallel=True)
    print("Arquivos carregados com sucesso.")
    print("Variáveis disponíveis:", list(ds.data_vars))
except Exception as e:
    print(f"Erro ao carregar os arquivos NetCDF: {e}")
    
# Seleciona a variável e o nível de pressão de interesse
if VARIAVEL_INTERESSE not in ds:
    raise ValueError(f"A variável '{VARIAVEL_INTERESSE}' não foi encontrada no dataset.")

# Verifica se o dado é 3D (com nível) ou 2D
if 'lev' in ds[VARIAVEL_INTERESSE].coords:
    print(f">>> Selecionando dados para o nível de {NIVEL_PRESSAO} hPa...")
    data_array = ds[VARIAVEL_INTERESSE].sel(lev=NIVEL_PRESSAO)
else:
    data_array = ds[VARIAVEL_INTERESSE]

# %% 4. Recorte Geográfico Preciso com Shapefile
print(">>> Realizando recorte com o shapefile dos municípios do Brasil...")

# Carrega e prepara o shapefile
try:
    shape = gpd.read_file(CAMINHO_SHAPEFILE)
    # Garante que o shapefile esteja no mesmo sistema de coordenadas dos dados (WGS84)
    shape = shape.to_crs("EPSG:4326")
except Exception as e:
    print(f"Erro ao carregar ou processar o shapefile: {e}")
    
# Adiciona informações geoespaciais ao DataArray do xarray
data_array = data_array.rio.write_crs("EPSG:4326")

# Informa ao rioxarray quais dimensões correspondem a 'x' e 'y'
data_array = data_array.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)

# Realiza o recorte (clip)
try:
    data_recortado = data_array.rio.clip(shape.geometry, drop=True)
    print("Recorte geográfico realizado com sucesso.")
except Exception as e:
    print(f"Erro durante o recorte com rioxarray: {e}")
    data_recortado = None

# %% 5. Análise e Visualização dos Dados
if data_recortado is not None:
    # GRÁFICO 1: Série Temporal da Média Espacial
    print(">>> Gerando Gráfico 1: Série Temporal da Média...")
    media_espacial = data_recortado.mean(dim=["lat", "lon"]) * 86400

    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        print("Aviso: Locale 'pt_BR.UTF-8' não encontrado. Usando locale padrão.")
        try:
            locale.setlocale(locale.LC_TIME, '')
        except locale.Error:
            print("Aviso: Nenhum locale pôde ser configurado. As datas podem aparecer em inglês.")

    plt.figure(figsize=(14, 6))
    media_espacial.plot(color='royalblue')
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b/%Y'))
    plt.title(f"Média da Tendência de Temperatura em {NIVEL_PRESSAO} hPa para o Brasil", fontsize=16, pad=20)
    plt.xlabel("Mês/Ano", fontsize=12)
    plt.ylabel("Tendência Média (K/dia)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

    # GRÁFICO 2: Padrão Espacial da Média Temporal
    print(">>> Gerando Gráfico 2: Mapa da Tendência Média...")
    media_temporal = data_recortado.mean(dim='time') * 86400

    plt.figure(figsize=(10, 8))
    media_temporal.plot(
        cmap='RdBu_r',
        robust=True,
        cbar_kwargs={'label': 'Tendência Média (K/dia)', 'orientation': 'horizontal', 'pad': 0.1}
    )
    shape.plot(ax=plt.gca(), facecolor='none', edgecolor='black', linewidth=0.5)
    plt.title(f"Padrão Espacial da Tendência de Temperatura em {NIVEL_PRESSAO} hPa", fontsize=16, pad=20)
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

    # GRÁFICO 3: Comparação das Forçantes Físicas
    print(">>> Gerando Gráfico 3: Comparação das Forçantes...")
    plt.figure(figsize=(14, 7))

    for var_nome in VARIAVEIS_CONTRIBUICAO:
        if var_nome in ds:
            da_contrib = ds[var_nome].sel(lev=NIVEL_PRESSAO)
            da_contrib = da_contrib.rio.write_crs("EPSG:4326").rio.set_spatial_dims(x_dim="lon", y_dim="lat")
            da_contrib_clip = da_contrib.rio.clip(shape.geometry, drop=True)
            media_contrib = da_contrib_clip.mean(dim=["lat", "lon"]) * 86400

            linewidth = 2.5 if var_nome == VARIAVEL_INTERESSE else 1.5
            linestyle = '--' if var_nome != VARIAVEL_INTERESSE else '-'
            media_contrib.plot(label=var_nome, linewidth=linewidth, linestyle=linestyle)

    plt.title(f"Componentes da Tendência de Temperatura em {NIVEL_PRESSAO} hPa (Brasil)", fontsize=16, pad=20)
    plt.ylabel("Tendência Média (K/dia)", fontsize=12)
    plt.xlabel("Tempo", fontsize=12)
    plt.legend(title="Forçantes Físicas")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

print("Análise Concluída")