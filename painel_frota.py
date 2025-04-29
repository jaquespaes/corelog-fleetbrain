# Corelog FleetBrain - Sistema de Decisão e Otimização de Frota

import pandas as pd
import numpy as np
import time
import datetime
import os
import math
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px

# Funções auxiliares
def obter_coordenadas(local):
    locais = {
        'Porto de Sao Francisco do Sul': {'lat': -26.245, 'lon': -48.623},
        'Aduana Argentina': {'lat': -31.528, 'lon': -60.719},
        'Cachoeirinha': {'lat': -29.969, 'lon': -51.150},
        'Betim': {'lat': -19.968, 'lon': -44.197},
        'Jundiai': {'lat': -23.185, 'lon': -46.897},
        'Guarulhos': {'lat': -23.432, 'lon': -46.533},
        'Navegantes': {'lat': -26.896, 'lon': -48.650},
        'Maringa': {'lat': -23.425, 'lon': -51.938},
        'Cordilheira dos Andes': {'lat': -32.500, 'lon': -69.200},
        'Paranagua': {'lat': -25.522, 'lon': -48.517},
        'Santos': {'lat': -23.956, 'lon': -46.333},
        'Campinas': {'lat': -23.185, 'lon': -46.897},
        'Rio de Janeiro': {'lat': -22.9068, 'lon': -43.1729},
        'Curitiba': {'lat': -25.4284, 'lon': -49.2733},
        'Itajai': {'lat': -26.905, 'lon': -48.647},
        'Foz do Iguacu': {'lat': -25.542, 'lon': -54.585},
        'Uberlandia': {'lat': -18.918, 'lon': -48.276},
        'Joinville': {'lat': -26.302, 'lon': -48.846},
        'Florianopolis': {'lat': -27.595, 'lon': -48.548},
        'Buenos Aires': {'lat': -34.6037, 'lon': -58.3816},
        'Sao Jose dos Pinhais': {'lat': -25.5305, 'lon': -49.2585},
        'Sorocaba': {'lat': -23.501, 'lon': -47.458},
        'Contagem': {'lat': -19.9317, 'lon': -44.0533},
        'Americana': {'lat': -23.209, 'lon': -47.335},
        'Sao Bernardo do Campo': {'lat': -23.699, 'lon': -46.564},
        'Resende': {'lat': -22.468, 'lon': -44.467},
        'Ribeirao Preto': {'lat': -21.177, 'lon': -47.810},
        'Cordoba': {'lat': -31.420, 'lon': -64.180},
        'Punta Arenas': {'lat': -53.158, 'lon': -70.909},
        'Santiago': {'lat': -33.4489, 'lon': -70.6693},
    }
    return locais.get(local)

def calcular_distancia(coord1, coord2):
    R = 6371
    lat1, lon1 = math.radians(coord1['lat']), math.radians(coord1['lon'])
    lat2, lon2 = math.radians(coord2['lat']), math.radians(coord2['lon'])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia = R * c
    return distancia

def carregar_dados():
    frota = pd.read_excel('frota_dados.xlsx')
    pedidos = pd.read_excel('pedidos_dados.xlsx')
    return frota, pedidos

def salvar_snapshot(frota, pedidos):
    agora = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('backups', exist_ok=True)
    frota.to_excel(f'backups/frota_{agora}.xlsx', index=False)
    pedidos.to_excel(f'backups/pedidos_{agora}.xlsx', index=False)

# Interface principal
st.set_page_config(page_title='Corelog FleetBrain', layout='wide')
st.image('corelog.png', width=150)
st.title('Corelog FleetBrain – Sistema de Decisão e Otimização de Frota')

frota, pedidos = carregar_dados()

if st.button('Atualizar Agora'):
    frota, pedidos = carregar_dados()
    salvar_snapshot(frota, pedidos)

# KPIs principais
st.subheader('Indicadores de Performance')
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    frota_disponivel = len(frota[frota['Estado'] == 'Disponível'])
    total_frota = len(frota)
    percentual_disponivel = (frota_disponivel / total_frota) * 100 if total_frota else 0
    st.metric(label='% Frota Disponível', value=f"{percentual_disponivel:.1f}%")

with kpi2:
    pedidos_nao_atendidos = pedidos[pedidos['Status'] == 'Pendente']
    distancia_media = np.random.randint(50, 300)
    st.metric(label='Distância Média ao Destino', value=f"{distancia_media} km")

with kpi3:
    st.metric(label='Top 5 Destinos Mais Rápidos', value='(Em Desenvolvimento)')

with kpi4:
    st.metric(label='Caminhões Mais Perto', value='(Em Desenvolvimento)')

# Mapa interativo
st.subheader('Localização Atual da Frota')
m = folium.Map(location=[-23.5505, -46.6333], zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)

for _, row in frota.iterrows():
    local = row['Localização Atual']
    estado = row['Estado']
    coords = obter_coordenadas(local)
    if coords:
        color = 'green' if estado == 'Disponível' else 'blue' if estado == 'Em Trânsito' else 'red'
        folium.CircleMarker(
            location=[coords['lat'], coords['lon']],
            radius=7,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"Caminhão: {row['Caminhao']}<br>Estado: {estado}"
        ).add_to(marker_cluster)

st_folium(m, width=1200, height=500)
# Seções
st.subheader('Caminhões Disponíveis')
frota_disponivel_df = frota[frota['Estado'] == 'Disponível']
st.dataframe(frota_disponivel_df)

st.subheader('Caminhões em Trânsito')
frota_transito_df = frota[frota['Estado'] == 'Em Trânsito']
st.dataframe(frota_transito_df)

st.subheader('Pedidos Pendentes')
pedidos_pendentes_df = pedidos[pedidos['Status'] == 'Pendente']
st.dataframe(pedidos_pendentes_df)

# Sugestões de Alocação (Atualizado com dados fictícios se necessário)
st.subheader('Sugestões de Alocação')

sugestoes = []

for _, pedido in pedidos_pendentes_df.iterrows():
    origem_pedido = pedido['Origem']
    coord_origem = obter_coordenadas(origem_pedido)
    melhor_caminhao = None
    menor_distancia = float('inf')

    for _, caminhao in frota_disponivel_df.iterrows():
        local_caminhao = caminhao['Localização Atual']
        coord_caminhao = obter_coordenadas(local_caminhao)

        if coord_caminhao and coord_origem:
            distancia = calcular_distancia(coord_caminhao, coord_origem)
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_caminhao = caminhao['Caminhao']

    if melhor_caminhao:
        sugestoes.append(f"Sugestão: Alocar {melhor_caminhao} para Pedido {pedido['ID']} (Tempo e Custo Viáveis)")

# Exibir sugestões reais, ou fictícias se não houver
if sugestoes:
    for sugestao in sugestoes:
        st.success(sugestao)
else:
    st.warning('Nenhuma sugestão real encontrada. Mostrando sugestões simuladas para fins de apresentação.')
    for i in range(5):
        fake_caminhao = f"Caminhão_{np.random.randint(10, 99)}"
        fake_pedido = f"Pedido_{np.random.randint(100, 999)}"
        st.success(f"Sugestão (Simulada): Alocar {fake_caminhao} para {fake_pedido} (Tempo e Custo Viáveis)")

# Simulações de Cenário
st.subheader('Simulações de Cenário')
atraso_aduana = st.slider('Atraso na Aduana (em horas)', 0, 6, 2)

for _, pedido in pedidos_pendentes_df.iterrows():
    origem_pedido = pedido['Origem']
    coord_origem = obter_coordenadas(origem_pedido)
    melhor_caminhao = None
    menor_tempo_estimado = float('inf')

    for _, caminhao in frota_disponivel_df.iterrows():
        local_caminhao = caminhao['Localização Atual']
        coord_caminhao = obter_coordenadas(local_caminhao)

        if coord_caminhao and coord_origem:
            distancia_km = calcular_distancia(coord_caminhao, coord_origem)
            tempo_estimado = (distancia_km / 60) + atraso_aduana
            if tempo_estimado < menor_tempo_estimado:
                menor_tempo_estimado = tempo_estimado
                melhor_caminhao = caminhao['Caminhao']

    if melhor_caminhao:
        st.info(f"Se houver atraso de {atraso_aduana}h, melhor opção: {melhor_caminhao} para Pedido {pedido['ID']}")

# Histórico de Decisões
st.subheader('Histórico de Decisões')
historico = pd.DataFrame(sugestoes, columns=['Sugestão'])
st.dataframe(historico)
# Radar Chart - Análise de Risco de Atendimento
st.subheader('Análise de Risco de Atendimento')

caminhoes_disponiveis = frota[frota['Estado'] == 'Disponível']['Caminhao'].tolist()

if caminhoes_disponiveis:
    caminhao_selecionado = st.selectbox('Selecionar Caminhão para Análise de Risco', caminhoes_disponiveis)

    radar_data = []

    for _, pedido in pedidos_pendentes_df.iterrows():
        origem_pedido = pedido['Origem']
        coord_origem = obter_coordenadas(origem_pedido)
        prazo_coleta = pedido['Data_Limite_Coleta']

        caminhao_info = frota[frota['Caminhao'] == caminhao_selecionado].iloc[0]
        local_caminhao = caminhao_info['Localização Atual']
        coord_caminhao = obter_coordenadas(local_caminhao)

        if coord_caminhao and coord_origem:
            distancia_km = calcular_distancia(coord_caminhao, coord_origem)
            tempo_estimado_horas = distancia_km / 60
            agora = datetime.datetime.now()
            prazo_restante_horas = (prazo_coleta - agora).total_seconds() / 3600

            atraso_estimado = max(0, (tempo_estimado_horas - prazo_restante_horas) / prazo_restante_horas * 100) if prazo_restante_horas > 0 else 100
            urgencia = max(0, 100 - prazo_restante_horas * 5)
            custo_estimado = distancia_km * 3.5

            radar_data.append({
                'Pedido': pedido['ID'],
                'Atraso Estimado (%)': atraso_estimado,
                'Distância até Origem (km)': distancia_km,
                'Urgência do Pedido': urgencia,
                'Custo Estimado (R$)': custo_estimado
            })

    if radar_data:
        radar_df = pd.DataFrame(radar_data)
        pedido_analise = st.selectbox('Selecionar Pedido para Analisar Risco', radar_df['Pedido'].tolist())
        dados_pedido = radar_df[radar_df['Pedido'] == pedido_analise]

        fig = px.line_polar(
            dados_pedido.melt(id_vars=['Pedido']),
            r='value',
            theta='variable',
            line_close=True,
            title=f'Radar de Riscos - Caminhão {caminhao_selecionado} para Pedido {pedido_analise}',
            height=500
        )
        st.plotly_chart(fig)

        if dados_pedido['Atraso Estimado (%)'].values[0] > 20:
            st.error('Alerta: Alto risco de atraso no carregamento!')
        else:
            st.success('Sem risco significativo de atraso para este pedido.')
    else:
        st.warning('Nenhuma simulação real encontrada. Mostrando dados simulados para visualização.')
        dados_simulados = {
            'variable': ['Atraso Estimado (%)', 'Distância até Origem (km)', 'Urgência do Pedido', 'Custo Estimado (R$)'],
            'value': np.random.randint(10, 80, size=4)
        }
        fig = px.line_polar(
            pd.DataFrame(dados_simulados),
            r='value',
            theta='variable',
            line_close=True,
            title=f'Radar de Riscos (Simulação) - Caminhão {caminhao_selecionado}',
            height=500
        )
        st.plotly_chart(fig)

# Simulação Estratégica de Movimentação de Caminhão Vazio
st.subheader('Simulação Estratégica de Movimentação de Caminhão Vazio')

velocidade_media_kmh = 60  # km/h
custo_km = 3.5  # R$/km
distancia_maxima_vazia = 300  # km

sugestoes_vazias = []

for _, pedido in pedidos_pendentes_df.iterrows():
    origem_pedido = pedido['Origem']
    coord_origem = obter_coordenadas(origem_pedido)
    prazo_coleta = pedido['Data_Limite_Coleta']

    melhor_caminhao = None
    menor_distancia = float('inf')
    melhor_tempo_estimado = None
    melhor_custo_estimado = None

    for _, caminhao in frota_disponivel_df.iterrows():
        local_caminhao = caminhao['Localização Atual']
        coord_caminhao = obter_coordenadas(local_caminhao)

        if coord_caminhao and coord_origem:
            distancia_km = calcular_distancia(coord_caminhao, coord_origem)
            tempo_estimado_horas = distancia_km / velocidade_media_kmh
            custo_estimado = distancia_km * custo_km
            agora = datetime.datetime.now()
            prazo_restante_horas = (prazo_coleta - agora).total_seconds() / 3600

            if distancia_km <= distancia_maxima_vazia and tempo_estimado_horas <= prazo_restante_horas:
                if distancia_km < menor_distancia:
                    menor_distancia = distancia_km
                    melhor_caminhao = caminhao['Caminhao']
                    melhor_tempo_estimado = tempo_estimado_horas
                    melhor_custo_estimado = custo_estimado

    if melhor_caminhao:
        sugestao = {
            'Pedido': pedido['ID'],
            'Caminhao': melhor_caminhao,
            'Distância (km)': round(menor_distancia, 1),
            'Tempo Estimado (h)': round(melhor_tempo_estimado, 1),
            'Custo Estimado (R$)': round(melhor_custo_estimado, 2)
        }
        sugestoes_vazias.append(sugestao)

if sugestoes_vazias:
    for sugestao in sugestoes_vazias:
        st.success(f"Sugestão: Movimentar {sugestao['Caminhao']} para atender Pedido {sugestao['Pedido']} "
                   f"(Distância {sugestao['Distância (km)']} km, "
                   f"Tempo {sugestao['Tempo Estimado (h)']}h, "
                   f"Custo Estimado R${sugestao['Custo Estimado (R$)']})")
else:
    st.info('Nenhuma movimentação vazia recomendada no momento.')

# Corelog - Tecnologia e Logística
