import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.distance import geodesic

# Função para calcular a distância entre dois pontos usando a fórmula Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    origem = (lat1, lon1)
    destino = (lat2, lon2)
    return geodesic(origem, destino).km

# Função para carregar as planilhas
@st.cache_data
def carregar_planilhas():
    try:
        frota = pd.read_excel('frota_dados.xlsx')
        pedidos = pd.read_excel('pedidos_dados.xlsx')
        # Garantindo que as datas sejam convertidas para o formato datetime
        pedidos['Data Limite Coleta'] = pd.to_datetime(pedidos['Data Limite Coleta'], errors='coerce')
        pedidos['Data Limite Entrega'] = pd.to_datetime(pedidos['Data Limite Entrega'], errors='coerce')
        return frota, pedidos
    except Exception as e:
        st.error(f"Erro ao carregar as planilhas: {e}")
        return None, None

# Função para gerar o mapa com caminhões e pedidos
def gerar_mapa(frota, pedidos):
    mapa = folium.Map(location=[-23.5, -46.6], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(mapa)

    # Adicionando caminhões no mapa
    for _, row in frota.iterrows():
        if row['Estado'] == 'Disponível':
            cor = 'green'
        elif row['Estado'] == 'Em Trânsito':
            cor = 'blue'
        else:
            cor = 'red'

        folium.Marker(
            location=[row['Latitude Atual'], row['Longitude Atual']],
            popup=f"{row['Caminhao']} - {row['Localizacao Atual']}",
            icon=folium.Icon(icon='truck', prefix='fa', color=cor)
        ).add_to(marker_cluster)

    # Adicionando pedidos no mapa
    for _, row in pedidos.iterrows():
        folium.Marker(
            location=[row['Latitude Atual'], row['Longitude Atual']],  # Latitude e Longitude de origem
            popup=f"Pedido {row['Pedido']} - {row['Cliente']}",
            icon=folium.Icon(icon='cloud', prefix='fa', color='purple')
        ).add_to(marker_cluster)

    return mapa

# Função para dividir os pedidos
def dividir_pedidos(pedidos):
    pendentes = pedidos[pedidos['Data Limite Coleta'] >= pd.Timestamp.now()]
    atrasados_coleta = pedidos[pedidos['Data Limite Coleta'] < pd.Timestamp.now()]
    atrasados_entrega = pedidos[pedidos['Data Limite Entrega'] < pd.Timestamp.now()]
    
    return pendentes, atrasados_coleta, atrasados_entrega

# Título do painel
st.title('Corelog FleetBrain')

# Logo no topo
st.image('corelog.png', width=200)

# Explicação sobre os tiers
st.info("""
Classificação de Clientes:
- **Tier 1**: Clientes mais estratégicos (prioridade máxima)
- **Tier 2**: Clientes importantes
- **Tier 3**: Clientes normais (baixa criticidade)
""")

# Carregando as planilhas
frota, pedidos = carregar_planilhas()

# Verificando se as planilhas foram carregadas corretamente
if frota is not None and pedidos is not None:
    # Exibindo as planilhas
    st.subheader("Frota Atual")
    st.dataframe(frota)

    st.subheader("Pedidos Pendentes")
    st.dataframe(pedidos)

    # Dividindo os pedidos em pendentes, atrasados na coleta e na entrega
    pendentes, atrasados_coleta, atrasados_entrega = dividir_pedidos(pedidos)

    # Exibindo pedidos divididos
    st.subheader("Pedidos Pendentes")
    st.dataframe(pendentes)

    st.subheader("Pedidos Atrasados na Coleta")
    st.dataframe(atrasados_coleta)

    st.subheader("Pedidos Atrasados na Entrega")
    st.dataframe(atrasados_entrega)

    # Gerando o mapa
    st.subheader("Mapa da Frota e Pedidos")
    mapa = gerar_mapa(frota, pedidos)
    st.markdown(mapa._repr_html_(), unsafe_allow_html=True)

    # Calculando distâncias entre caminhões e pedidos
    st.subheader("Distâncias entre Caminhões e Pedidos")
    for _, pedido in pedidos.iterrows():
        st.write(f"Pedido {pedido['Pedido']} ({pedido['Cliente']}):")
        for _, caminhao in frota.iterrows():
            distancia = calcular_distancia(caminhao['Latitude Atual'], caminhao['Longitude Atual'],
                                          pedido['Latitude Atual'], pedido['Longitude Atual'])
            st.write(f"- Caminhão {caminhao['Caminhao']} a {distancia:.2f} km")
else:
    st.warning("Não foi possível carregar as planilhas. Verifique os arquivos.")
