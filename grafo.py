# Cria a interface gráfica (GUI).
import tkinter as tk
# Mostra alertas em janelas popup
from tkinter import messagebox
# Biblioteca para baixar mapas do OpenStreetMap como grafos de ruas
import osmnx as ox
# Manipula grafos (e calcula rotas)
import networkx as nx
# Cria pontos geográficos
from shapely.geometry import Point 
# Operações numéricas
import numpy as np
# Algoritmo de Dijkstra
from networkx.algorithms.shortest_paths.weighted import dijkstra_path
# Gera mapas interativos
import plotly.graph_objects as go
# Sorteia eventos aleatórios nas rotas
import random

def simplify_multidigraph(G_multi):
    G_simple = nx.DiGraph()
    for u, v, data in G_multi.edges(data=True):
        # Tenta obter o valor do atributo length da aresta.Se não existir, assume 1 como valor padrão.
        length = data.get('length', 1)
        # Verifica se já existe uma aresta entre u e v no grafo simples.
        if G_simple.has_edge(u, v):
            # Se já existir uma aresta entre u e v, ele só substitui se o novo length for menor do que o atual.Assim, entre todas as múltiplas arestas do multigrafo, só a de menor comprimento será mantida no grafo simples.
            if length < G_simple[u][v]['length']:
                G_simple[u][v]['length'] = length
        # Se não existir nenhuma aresta ainda entre u e v no grafo simples, ele adiciona uma com o valor atual de length
        else:
            G_simple.add_edge(u, v, length=length)
    for n, data in G_multi.nodes(data=True):
    # Usa **data para adicionar todos os atributos do nó no grafo simples (G_simple)
        G_simple.add_node(n, **data)
    return G_simple

# verifica se as coordenadas de origem e destino estão dentro da cidade de Maricá 
def esta_dentro_de_marica(lat, lon, area_marica):
    ponto = Point(lon, lat)
    return area_marica.contains(ponto)

# Calcula o custo total da rota, somando os pesos ('length') de cada trecho entre os nós consecutivos da rota.
def custo_rota(G, rota):
    return sum(G.edges[u, v]['length'] for u, v in zip(rota[:-1], rota[1:]))

# Formata o tempo na forma xh ym 
def formatar_tempo(minutos):
    horas = int(minutos // 60)
    minutos = int(minutos % 60)
    return f"{horas}h {minutos}min" if horas > 0 else f"{minutos}min"

try:
    G_multi = ox.graph_from_place("Maricá, Rio de Janeiro, Brazil", network_type='drive')
    G = simplify_multidigraph(G_multi)
    # copia o CRS (Coordinate Reference System) do grafo original para o grafo simplificado, para manter a coerência geográfica
    G.graph['crs'] = G_multi.graph['crs']
    #  une todos os pontos (nós) em uma única geometria (área de Maricá)
    nodes_gdf = ox.graph_to_gdfs(G, edges=False)
    area_marica = nodes_gdf.unary_union.convex_hull
except Exception as e:
    print(f"Erro ao carregar o grafo: {e}")
    messagebox.showerror("Erro", "Falha ao carregar os dados do mapa.")
    exit()

# Lê as entradas do usuário, calcula e exibe rotas.
def calcular_rota():
    # Obtém os valores dos campos da interface gráfica.
    try:
        lat1 = float(entry_lat1.get())
        lon1 = float(entry_lon1.get())
        lat2 = float(entry_lat2.get())
        lon2 = float(entry_lon2.get())
        velocidade = float(entry_velocidade.get())

        # Valida se a velocidade é positiva.
        if velocidade <= 0:
            messagebox.showerror("Erro", "A velocidade deve ser maior que zero.")
            return

        # Verifica se os dois pontos estão dentro de Maricá.
        if not esta_dentro_de_marica(lat1, lon1, area_marica) or not esta_dentro_de_marica(lat2, lon2, area_marica):
            messagebox.showerror("Erro", "Coordenadas fora de Maricá.")
            return

        # Encontra os nós mais próximos às coordenadas fornecidas.
        orig_node = ox.distance.nearest_nodes(G, X=lon1, Y=lat1)
        dest_node = ox.distance.nearest_nodes(G, X=lon2, Y=lat2)

        # Calcula a rota mais curta com Dijkstra.
        rota_eficiente = dijkstra_path(G, orig_node, dest_node, weight='length')

        # Tenta encontrar até 4 rotas alternativas penalizando a anterior em 20%.
        G_temp = G.copy()
        rotas_alternativas = []
        for _ in range(10):
            try:
                rota = dijkstra_path(G_temp, orig_node, dest_node, weight='length')
                """ 
                    A rota encontrada não seja repetida. E não seja igual à rota mais eficiente
                """
                if rota not in rotas_alternativas and rota != rota_eficiente:
                    rotas_alternativas.append(rota)
                """
                    Faz um "castigo" nos trechos da rota recém-encontrada: aumenta o custo (length) em 20%. 
                    Isso reduz a chance de que a próxima execução do Dijkstra encontre a mesma rota
                """
                for u, v in zip(rota[:-1], rota[1:]):
                    G_temp[u][v]['length'] *= 1.2
                if len(rotas_alternativas) >= 4:
                    break
            except nx.NetworkXNoPath:
                break

        # Junta a melhor rota com até 4 alternativas.
        rotas_finais = [rota_eficiente] + rotas_alternativas[:4]

        # Calcula o custo de cada rota e identifica a mais cara.
        custos_originais = [custo_rota(G, r) for r in rotas_finais]
        pior_idx = int(np.argmax(custos_originais))

        # Define aleatoriamente qual rota terá evento (obra/acidente).
        rotas_com_eventos = random.sample([i for i in range(len(rotas_finais)) if i != 0], 1)
        if pior_idx not in rotas_com_eventos:
            rotas_com_eventos.append(pior_idx)

        # Penaliza os trechos das rotas afetadas e marca o tipo de evento.
        G_penalizado = G.copy()
        penalizadas_idx = []

        for idx in rotas_com_eventos:
            rota = rotas_finais[idx]
            tipo_evento = random.choice(['obra', 'acidente']) if idx != pior_idx else 'acidente'
            penalizadas_idx.append(idx)
            for u, v in zip(rota[:-1], rota[1:]):
                if tipo_evento == 'obra':
                    G_penalizado[u][v]['length'] *= 1.5
                    G_penalizado[u][v]['evento'] = 'obra'
                elif tipo_evento == 'acidente':
                    G_penalizado[u][v]['length'] *= 2.0
                    G_penalizado[u][v]['evento'] = 'acidente'

        # Calcula os custos pós-eventos e identifica a melhor e pior rota.
        custos_finais = [custo_rota(G_penalizado if i in penalizadas_idx else G, r) for i, r in enumerate(rotas_finais)]
        melhor_idx = int(np.argmin(custos_finais))
        pior_idx = int(np.argmax(custos_finais))

        # Cria o gráfico e adiciona os marcadores de origem e destino.
        cores = ['green', 'red', 'blue', 'orange', 'purple']
        fig = go.Figure()

        fig.add_trace(go.Scattermapbox(
            lon=[lon1], lat=[lat1], mode='markers+text',
            marker=dict(size=20, color='gray'), text=["Origem"], name="Origem"
        ))
        fig.add_trace(go.Scattermapbox(
            lon=[lon2], lat=[lat2], mode='markers+text',
            marker=dict(size=20, color='black'), text=["Destino"], name="Destino"
        ))

        """
        Para cada rota:

            Extrai as coordenadas.

            Calcula distância e tempo.

            Verifica se há evento (obra/acidente).

            Cria uma legenda personalizada.
        """ 
        for i, rota in enumerate(rotas_finais):
            coords = [(G.nodes[n]['x'], G.nodes[n]['y']) for n in rota]
            lon, lat = zip(*coords)

            distancia_km = custos_finais[i] / 1000
            tempo_horas = distancia_km / velocidade
            tempo_formatado = formatar_tempo(tempo_horas * 60)

            grafo = G_penalizado if i in penalizadas_idx else G
            eventos = [grafo[u][v].get('evento') for u, v in zip(rota[:-1], rota[1:])]
            contem_obra = any(ev == 'obra' for ev in eventos)
            contem_acidente = any(ev == 'acidente' for ev in eventos)

            if contem_obra and contem_acidente:
                legenda_evento = " - Com obra e acidente"
            elif contem_obra:
                legenda_evento = " - Com obra"
            elif contem_acidente:
                legenda_evento = " - Com acidente"
            else:
                legenda_evento = " - Sem eventos"

            titulo = f"Rota {i+1} - {distancia_km:.2f} km - {tempo_formatado}{legenda_evento}"
            if i == melhor_idx:
                titulo += " (Mais eficiente)"
            elif i == pior_idx:
                titulo += " (Menos eficiente)"

            fig.add_trace(go.Scattermapbox(
                lon=lon, lat=lat, mode='lines+markers',
                marker=dict(size=4, color=cores[i % len(cores)]),
                line=dict(width=4 if i == melhor_idx else 2, color=cores[i % len(cores)]),
                name=titulo
            ))

        # Ajusta o layout e exibe o mapa com as rotas.
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=14,
            mapbox_center={"lat": np.mean([lat1, lat2]), "lon": np.mean([lon1, lon2])},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            title="Rotas com e sem penalizações"
        )
        fig.show()

    # Captura erros na entrada ou problemas inesperados.
    except ValueError:
        messagebox.showerror("Erro", "Insira valores válidos.")
    except Exception as e:
        messagebox.showerror("Erro inesperado", str(e))


# Interface

# Inicia a janela principal.
root = tk.Tk()
root.title("Calculadora de Rotas - Maricá")

# Cria os campos de entrada (lat/long origem, destino, velocidade).
campos = [
    ("Latitude Origem:", 0), ("Longitude Origem:", 1),
    ("Latitude Destino:", 2), ("Longitude Destino:", 3),
    ("Velocidade média (km/h):", 4)
]

entradas = []
for texto, linha in campos:
    tk.Label(root, text=texto).grid(row=linha, column=0)
    entry = tk.Entry(root)
    entry.grid(row=linha, column=1)
    entradas.append(entry)

# Desempacota os campos e define a velocidade padrão.
entry_lat1, entry_lon1, entry_lat2, entry_lon2, entry_velocidade = entradas
entry_velocidade.insert(0, "40")

# Cria o botão que chama calcular_rota().
tk.Button(root, text="Calcular Rotas", command=calcular_rota).grid(row=5, columnspan=2, pady=10)

# Inicia o loop da interface gráfica.
root.mainloop()


