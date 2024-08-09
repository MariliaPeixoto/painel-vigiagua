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
ref_muni = pd.read_csv('https://raw.githubusercontent.com/andrejarenkow/csv/master/Munic%C3%ADpios%20RS%20IBGE6%20Popula%C3%A7%C3%A3o%20CRS%20Regional%20-%20P%C3%A1gina1.csv')
ref_muni['CRS'] = (ref_muni['CRS'].astype(str).str.zfill(2) + 'ª CRS')
ref_muni['Município'] = ref_muni['Município'].apply(lambda x: unidecode(x).upper())

# Carrega dados dos limites das CRS
geojson_url = "https://raw.githubusercontent.com/andrejarenkow/geodata/main/RS_por_CRS/RS_por_CRS.json"

# Cria variavel para mudar o zoom
zoom_ini = 5.5

col1, col2, col3, col4 = st.columns([2,1,1,1])

with col1:
    container_filtros = st.container()
    with container_filtros:
        coluna_crs, coluna_ano = st.columns([1,3])
        with coluna_crs:
            opcoes_crs = sorted(dados_2024['Regional de Saúde'].unique())
            # inserir na lista opcoes_crs o item TODAS
            opcoes_crs.insert(0, 'Todas')
            
            crs_selecionada = st.selectbox(label='Selecione a CRS',
                                           options= opcoes_crs)
        with coluna_ano:
            ano_selecionado = st.multiselect(label='Selecione o ano',
                                             options=sorted(dados_2024['Ano'].unique()),
                                             default=sorted(dados_2024['Ano'].unique()))

        forma_abastecimento_selecionada = st.multiselect(label='Selecione o tipo da forma',
                                                         options=sorted(dados_2024['Tipo da Forma de Abastecimento'].unique()),
                                                         default=sorted(dados_2024['Tipo da Forma de Abastecimento'].unique()))
        parametro = st.selectbox(label='Selecione o parâmetro', options=dados_2024['Parâmetro'].unique(), index=3)
        
# Criar filtro para selecionar dados da Regional de Saúde específica
filtro_crs = dados_2024['Regional de Saúde'] == crs_selecionada

# Criar filtro para selecionar referência de municípios da CRS específica
filtro_muni = ref_muni['CRS'] == crs_selecionada

# Filtrar os municípios da referência que pertencem à CRS selecionada
municipios_muni = ref_muni[filtro_muni]

# Criar uma lista dos municípios da referência da CRS selecionada
lista_municipios_muni = municipios_muni['Município']

# Verificar se a CRS selecionada não é 'Todas'
if crs_selecionada != 'Todas':
    # Filtrar os dados de 2024 apenas para a CRS selecionada
    dados_2024 = dados_2024[filtro_crs]
    
    # Criar filtro para selecionar os dados geográficos (muni) cujo nome do município está na lista de municípios da CRS selecionada
    filtro_geodata_crs = muni['NM_MUN'].isin(lista_municipios_muni)

    # Aplicar o filtro aos dados geográficos (muni)
    muni = muni[filtro_geodata_crs]

    # Alterar o zoom para aproximar da CRS
    zoom_ini = 7

#parametro = st.selectbox(label='Selecione o parâmetro', options=dados_2024['Parâmetro'].unique(), index=3)
filtro = dados_2024['Parâmetro'] == parametro
dados = pd.pivot_table(dados_2024[filtro], index='Município', columns='Status', aggfunc='size').reset_index().fillna(0)

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

# Ajuste de estilo CSS para centralizar os textos
st.markdown(
    """
    <style>
    .stMetric {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# Juntar tabelas
tabela_mapa = muni.merge(dados, left_on='NM_MUN', right_on='Município', how='left').fillna('Sem dados')

# Paleta de cores para cada categoria
cores = {
    #'Sem dados': '#d2d2d2',        
    #'0 %': '#F7C623',            
    #'1 % - 10 %': '#ff9a52',
    #'11 % - 20 %': '#ff7752',     
    #'21 % - 30 %': '#ff5252',    
    #'mais que 30 %': '#5e405b' 
    'Cloro residual livre (mg/L)': {
        'Sem dados': '#d2d2d2',
        '0 %': '#EEF3AD',
        '1 % - 10 %': '#ADEBBE',
        '11 % - 20 %': '#75B79E',
        '21 % - 30 %': '#74BEC1',
        'mais que 30 %': '#516091'
    },
    'Escherichia coli': {
        'Sem dados': '#d2d2d2',
        '0 %': '#F7C623',
        '1 % - 10 %': '#de8531',
        '11 % - 20 %': '#b32900',
        '21 % - 30 %': '#6c1305',
        'mais que 30 %': '#330a04'
    },
    'Fluoreto (mg/L)': {
        'Sem dados': '#d2d2d2',
        '0 %': '#B2C9D7',
        '1 % - 10 %': '#9BC3DC',
        '11 % - 20 %': '#6596B4',
        '21 % - 30 %': '#317197',
        'mais que 30 %': '#00517E'
    },
    'Turbidez (uT)': {
        'Sem dados': '#d2d2d2',
        '0 %': '#DCC595',
        '1 % - 10 %': '#B68E56',
        '11 % - 20 %': '#A37940',
        '21 % - 30 %': '#90682F',
        'mais que 30 %': '#5F021F'
    }
}

# Calcular os limites (min e max) das geometrias
min_x, min_y, max_x, max_y = tabela_mapa.total_bounds

# Calcular o ponto médio das geometrias
centro_x = (min_x + max_x) / 2
centro_y = (min_y + max_y) / 2

col_mapa, col2 = st.columns([3,2])

with col_mapa:
    filtro = dados_2024['Parâmetro'] == parametro
    dados = pd.pivot_table(dados_2024[filtro], index='Município', columns='Status', aggfunc='size').reset_index().fillna(0)
    # Criar o mapa
    px.set_mapbox_access_token('pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw')
    mapa_fig = px.choropleth_mapbox(tabela_mapa, geojson=tabela_mapa.geometry,
                                    locations=tabela_mapa.index,
                                    color='Categorias',
                                    color_discrete_map = cores[parametro],
                                    center={'lat': centro_y, 'lon': centro_x},
                                    zoom=zoom_ini,
                                    mapbox_style="open-street-map",
                                    hover_name='NM_MUN', hover_data = 'Insatisfatório %',
                                    category_orders={'Categorias': [ 'Sem dados', '0 %', '1 % - 10 %', '11 % - 20 %', '21 % - 30 %', 'mais que 30 %']},
                                    width=800,
                                    height=700,
                                    title=f'{parametro} Insatisfatório %')
    # Altera a espessura da linha da camada das CRS
    mapa_fig.update_traces(marker_line_width=0.3)
    mapa_fig.update_layout(margin={"r": 0, "t": 25, "l": 0, "b": 0})
    # Insere no mapa a camada das CRS
    mapa_fig.update_layout(mapbox_layers = [dict(sourcetype = 'geojson',
                                            source = geojson_url,
                                            color='black',
                                            type = 'line',   
                                            line=dict(width=1))])
                                                                                              
    st.plotly_chart(mapa_fig)
# Agrupar os dados por CRS
dados_crs = dados_2024[filtro].groupby(['Município', 'Regional de Saúde', 'Status']).size().unstack(fill_value=0).reset_index()

# Cálculo porcentagem de insatisfatórios
dados_crs['Insatisfatório %'] = ((dados_crs['Inadequado'] / (dados_crs['Adequado'] + dados_crs['Inadequado'])) * 100).round(2)

# Gráfico de dispersão
fig = px.strip(dados_crs.sort_values('Regional de Saúde'), x="Regional de Saúde", y="Insatisfatório %",
              color="Regional de Saúde", hover_name="Município", range_y=[0,100],
               title='Porcentagem de amostras insatisfatórias por CRS')
# Centralizar o título e ajustar o layout
fig.update_layout(
    title={
        'text': f'Porcentagem de amostras insatisfatórias de {parametro} por CRS',
        'x': 0.5,  # Centralizar horizontalmente
        'xanchor': 'center'  # Ancorar no centro horizontal
    },
    xaxis_title='Regional de Saúde',
    yaxis_title='Insatisfatório %',
    showlegend=False
)
st.plotly_chart(fig)
