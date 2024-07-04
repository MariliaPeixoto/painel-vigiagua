# Importação das bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px

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
muni = pd.read_csv('https://raw.githubusercontent.com/andrejarenkow/csv/master/Munic%C3%ADpios%20RS%20IBGE6%20Popula%C3%A7%C3%A3o%20CRS%20Regional%20-%20P%C3%A1gina1.csv')
muni['Município'] = muni['Município'].replace("Sant'Ana do Livramento", 'Santana do Livramento')

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

# Selecionar as infos que precisa da tabela de municípios
muni_limpo = muni[['Município','IBGE6', 'CRS']].set_index(['Município','IBGE6', 'CRS'])

# Juntar tabelas dos dados dos municípios com o resultado das análises
tabela_mapa = dados_2024.merge(muni_limpo, left_on='Código IBGE', right_on='IBGE6', how='right')

#Mapa da incidência por município
map_fig = px.choropleth_mapbox(tabela_mapa,
                               geojson=tabela_mapa.geometry,
                               locations=tabela_mapa.index,  # Usando o índice como localização
                               color='Status',
                               color_continuous_scale='OrRd',
                               center={'lat': 'lat', 'lon': 'lon'},
                               zoom=zoom_ini,
                               mapbox_style="carto-positron",
                               hover_data=['Regional de Saúde'],
                               hover_name='Município',# Define as informações do hover
                               width=800,
                               height=700,
                               title='Teste')

map_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=go.layout.Margin(l=10, r=10, t=50, b=10),
                                  )
map_fig.update_traces(marker_line_width=0.2)
map_fig.update_coloraxes(colorbar={'orientation':'h'},
                         colorbar_yanchor='bottom',
                         colorbar_y=-0.13)

map_fig.show()

