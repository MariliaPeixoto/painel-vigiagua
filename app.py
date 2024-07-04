# Importação das bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px
from unidecode import unidecode
import geopandas as gpd

# Configurações da página
st.set_page_config(
    page_title="VIGIAGUA RS",
    page_icon="	:potable_water:",
    layout="wide",
    initial_sidebar_state='collapsed'
)
col1, col2, col3 = st.columns([1,4,1], vertical_alignment="center")

col3.image('https://github.com/andrejarenkow/csv/blob/master/logo_cevs%20(2).png?raw=true', width=150)
col2.title('VIGIAGUA RS')
col1.image('https://github.com/andrejarenkow/csv/blob/master/logo_estado%20(3)%20(1).png?raw=true', width=230)

# Amostras dos dados abertos
dados_2024 = pd.read_csv('https://drive.google.com/uc?export=download&id=1aFmCeDug7eJRhTxSwIXxqw_hYHeUwKGC', sep=';')
dados_2024['Regional de Saúde'] = dados_2024['Regional de Saúde'].str.zfill(7)

# Amostras nao validadas
dados_nao_validadas = pd.read_excel('https://drive.google.com/uc?export=download&id=1-DGZAo4cCk0jIVnmDkKRBVWDtWfaBAF2')
dados_nao_validadas['Regional de Saúde'] = dados_nao_validadas['Regional de Saúde'].str.zfill(7)
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
    container_filtros = st.container(border=True)
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
    with st.container(border=True):
        st.metric(label = 'Análises insatisfatórias', value=f'{percentage}%')

# Número de análises feitas
with col3:
    numero_de_amostras = dados_2024['Número da amostra'].nunique()
    with st.container(border=True):
        st.metric(label = 'Total de amostras', value=f'{numero_de_amostras}')

# Número de amostras não validadas
with col4:
    amostras_nao_validadas_total = len(dados_nao_validadas)
    with st.container(border=True):
        st.metric(label = 'Amostras não validadas', value=f'{amostras_nao_validadas_total}')

# Transformar a tabela em dinâmica
parametros = pd.pivot_table(dados_2024, index='Município', aggfunc='size').reset_index()
parametros

# Juntar tabelas dos dados dos municípios com o resultado das análises
#tabela_mapa = parametros.merge(muni, left_on='Código IBGE', right_on='IBGE6', how='right')
#tabela_mapa
