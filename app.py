# Importação das bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px
import geopandas as gpd
from unidecode import unidecode

# Configurações da página
st.set_page_config(
    page_title="VIGIAGUA RS",
    page_icon=":potable_water:",
    layout="wide",
    initial_sidebar_state='collapsed'
)
col1, col2, col3 = st.columns([1,4,1])

col3.image('https://github.com/andrejarenkow/csv/blob/master/logo_cevs%20(2).png?raw=true', width=150)
col2.title('VIGIAGUA RS')
col1.image('https://github.com/andrejarenkow/csv/blob/master/logo_estado%20(3)%20(1).png?raw=true', width=230)

# Amostras dos dados abertos
dados_2024 = pd.read_csv('https://drive.google.com/uc?export=download&id=1aFmCeDug7eJRhTxSwIXxqw_hYHeUwKGC', sep=';')
dados_2024['Regional de Saúde'] = dados_2024['Regional de Saúde'].str.zfill(7)

# Amostras nao validadas
dados_nao_validadas = pd.read_excel('https://drive.google.com/uc?export=download&id=1-DGZAo4cCk0jIVnmDkKRBVWDtWfaBAF2')
dados_nao_validadas['Regional de Saúde'] = dados_nao_validadas['Regional de Saúde'].astype(str).str.zfill(7)
dados_nao_validadas['Data da coleta'] = pd.to_datetime(dados_nao_validadas['Data da coleta'], errors='coerce')
dados_nao_validadas['Ano'] = dados_nao_validadas['Data da coleta'].dt.year

# Carrega dados de referência dos municípios
def load_geodata(url):
    gdf = gpd.read_file(url)
    return gdf

muni = load_geodata('https://raw.githubusercontent.com/andrejarenkow/geodata/main/municipios_rs_CRS/RS_Municipios_2021.json')
# Remover acentos e converter para maiúsculo
muni['NM_MUN'] = muni['NM_MUN'].apply(lambda x: unidecode(x).upper())

col1, col2, col3, col4 = st.columns([2,1,1,1])

with col1:
    container_filtros = st.container()
    with container_filtros:
        coluna_crs, coluna_ano = st.columns([1,3])
        with coluna_crs:
            crs_selecionada = st.selectbox(label='Selecione a CRS',
                                           options=sorted(dados_2024['Regional de Saúde'].unique()))
        with coluna_ano:
            ano_selecionado = st.multiselect(label='Selecione o ano',
                                             options=sorted(dados_2024['Ano'].unique()),
                                             default=sorted(dados_2024['Ano'].unique()))

        forma_abastecimento_selecionada = st.multiselect(label='Selecione o tipo da forma',
                                                         options=sorted(dados_2024['Tipo da Forma de Abastecimento'].unique()),
                                                         default=sorted(dados_2024['Tipo da Forma de Abastecimento'].unique()))

# Cálculo da porcentagem para amostras inadequadas GERAL
with col2:
    total_rows = len(dados_2024)
    inadequate_rows = len(dados_2024[dados_2024['Status'] == 'Inadequado'])
    percentage = round(inadequate_rows / total_rows * 100, 2)
    st.metric(label='Análises insatisfatórias', value=f'{percentage}%')

# Número de análises feitas
with col3:
    numero_de_amostras = dados_2024['Número da amostra'].nunique()
    st.metric(label='Total de amostras', value=f'{numero_de_amostras}')

# Número de amostras não validadas
with col4:
    amostras_nao_validadas_total = len(dados_nao_validadas)
    st.metric(label='Amostras não validadas', value=f'{amostras_nao_validadas_total}')

# Cria uma tabela dinâmica
dados = pd.pivot_table(dados_2024, index='Município', columns='Status', aggfunc='size').reset_index().fillna(0)

# Cálculo porcentagem de insatisfatórios
dados['Insatisfatório %'] = ((dados['Inadequado'] / (dados['Adequado'] + dados['Inadequado'])) * 100).round(2)

# Cria função para categorizar os dados
def categorizar(i):
  if i == 0:
    return '0 %'
  elif 0 < i <= 10:
    return '1 % - 10 %'
  elif 10 < i <=20:
    return '11 % - 20 %'
  elif 20 < i <= 30:
    return '21 % - 30 %'
  else:
    return 'mais que 30 %'

# Categoriza os dados da coluna 'Insatisfatório %' em uma nova coluna
dados['Categorias'] = dados['Insatisfatório %'].apply(categorizar)

# Ordenar por categorias
dados = dados.sort_values(['Insatisfatório %']).reset_index(drop=True)

# Juntar tabelas
tabela_mapa = muni.merge(dados, left_on='NM_MUN', right_on='Município', how='left').fillna('Sem dados')

# Paleta de cores para cada categoria
cores = {
    'Sem dados': '#d2d2d2',        
    '0 %': '#bfe3c3',            
    '1 % - 10 %': '#ff9a52',
    '11 % - 20 %': '#ff7752',     
    '21 % - 30 %': '#ff5252',    
    'mais que 30 %': '#5e405b'     
}

# Criar o mapa
px.set_mapbox_access_token('pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw')
mapa_fig = px.choropleth_mapbox(tabela_mapa, geojson=tabela_mapa.geometry,
                                locations=tabela_mapa.index,
                                color='Categorias',
                                color_discrete_map = cores,
                                center={'lat': -30.452349861219243, 'lon': -53.55320517512141},
                                zoom=5.5,
                                mapbox_style="open-street-map",
                                hover_name='NM_MUN', hover_data = 'Insatisfatório %',
                                category_orders={'Categorias': [ 'Sem dados', '0 %', '1 % - 10 %', '11 % - 20 %', '21 % - 30 %', 'mais que 30 %']},
                                width=800,
                                height=700,
                                title='Insatisfatório %')
mapa_fig.update_layout(margin={"r": 0, "t": 5, "l": 0, "b": 0})
st.plotly_chart(mapa_fig)
