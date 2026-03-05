"""
IPAAM - Visualização Alternativa com Plotly Express
====================================================
Módulo para criação de visualizações interativas usando Plotly,
incluindo mapas animados, gráficos de evolução temporal e dashboards.

Autor: Engenheiro de Dados GIS
Versão: 1.0.0
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional
import warnings

warnings.filterwarnings('ignore')


class VisualizadorPlotlyIPAAM:
    """
    Classe para criação de visualizações com Plotly Express.
    
    Funcionalidades:
    - Mapa animado com slider temporal
    - Gráficos de evolução por ano
    - Dashboard interativo completo
    - Exportação para HTML
    """
    
    # Cores por categoria
    CORES_CATEGORIA = {
        'Manejo Florestal': '#228B22',
        'Indústria Madeireira': '#FF8C00',
        'Indústria Mobiliária': '#4169E1',
        'Outros': '#808080'
    }
    
    # Símbolos por categoria
    SIMBOLOS_CATEGORIA = {
        'Manejo Florestal': 'triangle-up',
        'Indústria Madeireira': 'square',
        'Indústria Mobiliária': 'diamond',
        'Outros': 'circle'
    }
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o visualizador Plotly.
        
        Args:
            df: DataFrame com os dados das licenças
        """
        self.df = df.copy()
        self._preparar_dados()
    
    def _preparar_dados(self):
        """Prepara os dados para visualização."""
        # Garantir coordenadas válidas
        self.df = self.df.dropna(subset=['latitude', 'longitude'])
        
        # Converter e extrair ano
        if 'data_emissao' in self.df.columns:
            self.df['data_emissao'] = pd.to_datetime(self.df['data_emissao'], errors='coerce')
            self.df['ano'] = self.df['data_emissao'].dt.year.astype(int)
        
        # Garantir categoria
        if 'categoria' not in self.df.columns:
            self.df['categoria'] = 'Outros'
        
        # Ordenar por ano
        self.df = self.df.sort_values('ano')
        
        # Criar coluna de hover text
        self.df['hover_text'] = (
            '<b>' + self.df['razao_social'].astype(str) + '</b><br>' +
            '<b>Município:</b> ' + self.df['municipio'].astype(str) + '<br>' +
            '<b>Atividade:</b> ' + self.df['atividade'].astype(str) + '<br>' +
            '<b>Licença:</b> ' + self.df['tipo_licenca'].astype(str) + '<br>' +
            '<b>Gerência:</b> ' + self.df['gerencia'].astype(str)
        )
        
        print(f"[OK] Dados preparados para Plotly: {len(self.df)} registros")
    
    def criar_mapa_animado(
        self,
        titulo: str = "Evolução das Licenças IPAAM (2018-2025)",
        caminho_saida: str = None
    ) -> go.Figure:
        """
        Cria mapa animado com slider temporal usando Plotly Express.
        
        Args:
            titulo: Título do mapa
            caminho_saida: Caminho para salvar HTML
            
        Returns:
            Figura Plotly
        """
        # Criar figura com animação
        fig = px.scatter_mapbox(
            self.df,
            lat='latitude',
            lon='longitude',
            color='categoria',
            size_max=15,
            hover_name='razao_social',
            hover_data={
                'municipio': True,
                'tipo_licenca': True,
                'gerencia': True,
                'atividade': True,
                'ano': True,
                'latitude': False,
                'longitude': False,
                'categoria': False
            },
            animation_frame='ano',
            color_discrete_map=self.CORES_CATEGORIA,
            zoom=5,
            center={'lat': -3.4168, 'lon': -65.8561},
            title=titulo,
            mapbox_style='carto-positron'
        )
        
        # Atualizar layout
        fig.update_layout(
            height=700,
            margin={'r': 0, 't': 50, 'l': 0, 'b': 0},
            legend=dict(
                title='Categoria',
                yanchor='top',
                y=0.99,
                xanchor='left',
                x=0.01,
                bgcolor='rgba(255,255,255,0.9)'
            ),
            annotations=[
                dict(
                    text="Fonte: Dados abertos IPAAM - GECF/GELI",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.99, y=0.01,
                    xanchor='right', yanchor='bottom',
                    font=dict(size=10, color='gray')
                )
            ]
        )
        
        # Configurar slider de animação
        fig.update_layout(
            sliders=[{
                'active': 0,
                'currentvalue': {
                    'prefix': 'Ano: ',
                    'visible': True,
                    'xanchor': 'center'
                },
                'pad': {'b': 10, 't': 50}
            }],
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'y': 0,
                'x': 0.1,
                'xanchor': 'right',
                'yanchor': 'top',
                'pad': {'t': 45, 'r': 10}
            }]
        )
        
        # Salvar se caminho fornecido
        if caminho_saida:
            fig.write_html(caminho_saida, include_plotlyjs=True, full_html=True)
            print(f"[OK] Mapa animado salvo em: {caminho_saida}")
        
        return fig
    
    def criar_mapa_densidade(
        self,
        titulo: str = "Densidade de Licenças por Região",
        caminho_saida: str = None
    ) -> go.Figure:
        """
        Cria mapa de densidade (heatmap) com Plotly.
        
        Args:
            titulo: Título do mapa
            caminho_saida: Caminho para salvar HTML
            
        Returns:
            Figura Plotly
        """
        fig = px.density_mapbox(
            self.df,
            lat='latitude',
            lon='longitude',
            radius=20,
            zoom=5,
            center={'lat': -3.4168, 'lon': -65.8561},
            title=titulo,
            mapbox_style='carto-darkmatter',
            color_continuous_scale='YlOrRd'
        )
        
        fig.update_layout(
            height=600,
            margin={'r': 0, 't': 50, 'l': 0, 'b': 0},
            annotations=[
                dict(
                    text="Fonte: Dados abertos IPAAM - GECF/GELI",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.99, y=0.01,
                    xanchor='right', yanchor='bottom',
                    font=dict(size=10, color='white')
                )
            ]
        )
        
        if caminho_saida:
            fig.write_html(caminho_saida, include_plotlyjs=True, full_html=True)
            print(f"[OK] Mapa de densidade salvo em: {caminho_saida}")
        
        return fig
    
    def criar_grafico_evolucao(
        self,
        titulo: str = "Evolução Anual das Licenças",
        caminho_saida: str = None
    ) -> go.Figure:
        """
        Cria gráfico de evolução temporal das licenças.
        
        Args:
            titulo: Título do gráfico
            caminho_saida: Caminho para salvar HTML
            
        Returns:
            Figura Plotly
        """
        # Agrupar por ano e categoria
        df_agrupado = self.df.groupby(['ano', 'categoria']).size().reset_index(name='quantidade')
        
        fig = px.bar(
            df_agrupado,
            x='ano',
            y='quantidade',
            color='categoria',
            color_discrete_map=self.CORES_CATEGORIA,
            title=titulo,
            labels={'ano': 'Ano', 'quantidade': 'Quantidade de Licenças', 'categoria': 'Categoria'},
            barmode='group'
        )
        
        fig.update_layout(
            height=500,
            xaxis=dict(tickmode='linear', dtick=1),
            legend=dict(
                title='Categoria',
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        
        if caminho_saida:
            fig.write_html(caminho_saida, include_plotlyjs=True, full_html=True)
            print(f"[OK] Gráfico de evolução salvo em: {caminho_saida}")
        
        return fig
    
    def criar_grafico_municipios(
        self,
        top_n: int = 15,
        titulo: str = "Top Municípios por Número de Licenças",
        caminho_saida: str = None
    ) -> go.Figure:
        """
        Cria gráfico de barras dos principais municípios.
        
        Args:
            top_n: Número de municípios a exibir
            titulo: Título do gráfico
            caminho_saida: Caminho para salvar HTML
            
        Returns:
            Figura Plotly
        """
        # Contar por município e categoria
        df_mun = self.df.groupby(['municipio', 'categoria']).size().reset_index(name='quantidade')
        
        # Top N municípios
        top_municipios = self.df['municipio'].value_counts().head(top_n).index.tolist()
        df_mun = df_mun[df_mun['municipio'].isin(top_municipios)]
        
        fig = px.bar(
            df_mun,
            x='quantidade',
            y='municipio',
            color='categoria',
            color_discrete_map=self.CORES_CATEGORIA,
            title=titulo,
            orientation='h',
            labels={'municipio': 'Município', 'quantidade': 'Quantidade', 'categoria': 'Categoria'}
        )
        
        fig.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            legend=dict(
                title='Categoria',
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        
        if caminho_saida:
            fig.write_html(caminho_saida, include_plotlyjs=True, full_html=True)
            print(f"[OK] Gráfico de municípios salvo em: {caminho_saida}")
        
        return fig
    
    def criar_grafico_pizza(
        self,
        titulo: str = "Distribuição por Categoria",
        caminho_saida: str = None
    ) -> go.Figure:
        """
        Cria gráfico de pizza da distribuição por categoria.
        
        Args:
            titulo: Título do gráfico
            caminho_saida: Caminho para salvar HTML
            
        Returns:
            Figura Plotly
        """
        df_cat = self.df['categoria'].value_counts().reset_index()
        df_cat.columns = ['categoria', 'quantidade']
        
        fig = px.pie(
            df_cat,
            values='quantidade',
            names='categoria',
            title=titulo,
            color='categoria',
            color_discrete_map=self.CORES_CATEGORIA,
            hole=0.4
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        fig.update_layout(height=450)
        
        if caminho_saida:
            fig.write_html(caminho_saida, include_plotlyjs=True, full_html=True)
            print(f"[OK] Gráfico de pizza salvo em: {caminho_saida}")
        
        return fig
    
    def criar_timeline(
        self,
        titulo: str = "Linha do Tempo das Licenças",
        caminho_saida: str = None
    ) -> go.Figure:
        """
        Cria linha do tempo interativa das licenças.
        
        Args:
            titulo: Título da timeline
            caminho_saida: Caminho para salvar HTML
            
        Returns:
            Figura Plotly
        """
        # Preparar dados cumulativos
        df_tempo = self.df.groupby(['ano', 'categoria']).size().reset_index(name='quantidade')
        df_tempo = df_tempo.pivot(index='ano', columns='categoria', values='quantidade').fillna(0)
        df_tempo = df_tempo.cumsum()
        df_tempo = df_tempo.reset_index().melt(id_vars='ano', var_name='categoria', value_name='quantidade_acumulada')
        
        fig = px.area(
            df_tempo,
            x='ano',
            y='quantidade_acumulada',
            color='categoria',
            color_discrete_map=self.CORES_CATEGORIA,
            title=titulo,
            labels={'ano': 'Ano', 'quantidade_acumulada': 'Licenças Acumuladas', 'categoria': 'Categoria'}
        )
        
        fig.update_layout(
            height=450,
            xaxis=dict(tickmode='linear', dtick=1),
            hovermode='x unified'
        )
        
        if caminho_saida:
            fig.write_html(caminho_saida, include_plotlyjs=True, full_html=True)
            print(f"[OK] Timeline salva em: {caminho_saida}")
        
        return fig
    
    def criar_dashboard_completo(
        self,
        titulo: str = "Dashboard IPAAM - Licenças Ambientais",
        caminho_saida: str = None
    ) -> go.Figure:
        """
        Cria um dashboard completo com múltiplas visualizações.
        
        Args:
            titulo: Título do dashboard
            caminho_saida: Caminho para salvar HTML
            
        Returns:
            Figura Plotly com subplots
        """
        # Criar subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Evolução Anual',
                'Distribuição por Categoria',
                'Top Municípios',
                'Licenças Acumuladas',
                'Por Tipo de Licença',
                'Por Gerência'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'pie'}],
                [{'type': 'bar'}, {'type': 'scatter'}],
                [{'type': 'bar'}, {'type': 'bar'}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.08
        )
        
        # 1. Evolução anual (barra)
        df_ano = self.df.groupby('ano').size().reset_index(name='quantidade')
        fig.add_trace(
            go.Bar(x=df_ano['ano'], y=df_ano['quantidade'], name='Licenças/Ano',
                   marker_color='#007bff'),
            row=1, col=1
        )
        
        # 2. Pizza por categoria
        df_cat = self.df['categoria'].value_counts()
        cores = [self.CORES_CATEGORIA.get(c, '#808080') for c in df_cat.index]
        fig.add_trace(
            go.Pie(labels=df_cat.index, values=df_cat.values, hole=0.4,
                   marker_colors=cores, showlegend=False),
            row=1, col=2
        )
        
        # 3. Top municípios (horizontal bar)
        df_mun = self.df['municipio'].value_counts().head(10)
        fig.add_trace(
            go.Bar(y=df_mun.index, x=df_mun.values, orientation='h',
                   name='Por Município', marker_color='#28a745'),
            row=2, col=1
        )
        
        # 4. Licenças acumuladas (linha)
        df_acum = self.df.groupby('ano').size().cumsum().reset_index(name='acumulado')
        df_acum.columns = ['ano', 'acumulado']
        fig.add_trace(
            go.Scatter(x=df_acum['ano'], y=df_acum['acumulado'], mode='lines+markers',
                       name='Acumulado', line=dict(color='#dc3545', width=3)),
            row=2, col=2
        )
        
        # 5. Por tipo de licença
        df_tipo = self.df['tipo_licenca'].value_counts()
        cores_tipo = {'LP': '#FFD700', 'LI': '#FFA500', 'LO': '#32CD32'}
        fig.add_trace(
            go.Bar(x=df_tipo.index, y=df_tipo.values, name='Tipo Licença',
                   marker_color=[cores_tipo.get(t, '#808080') for t in df_tipo.index]),
            row=3, col=1
        )
        
        # 6. Por gerência
        df_ger = self.df['gerencia'].value_counts()
        fig.add_trace(
            go.Bar(x=df_ger.index, y=df_ger.values, name='Gerência',
                   marker_color=['#17a2b8', '#6c757d']),
            row=3, col=2
        )
        
        # Atualizar layout geral
        fig.update_layout(
            height=1000,
            showlegend=False,
            title={
                'text': f"<b>{titulo}</b><br><sub>Fonte: Dados abertos IPAAM - GECF/GELI</sub>",
                'x': 0.5,
                'xanchor': 'center'
            },
            font=dict(family='Arial', size=11)
        )
        
        # Salvar
        if caminho_saida:
            fig.write_html(caminho_saida, include_plotlyjs=True, full_html=True)
            print(f"[OK] Dashboard salvo em: {caminho_saida}")
        
        return fig


def criar_visualizacoes_plotly(df: pd.DataFrame, pasta_saida: str):
    """
    Função de conveniência para criar todas as visualizações Plotly.
    
    Args:
        df: DataFrame com os dados
        pasta_saida: Pasta para salvar os arquivos HTML
    """
    import os
    os.makedirs(pasta_saida, exist_ok=True)
    
    visualizador = VisualizadorPlotlyIPAAM(df)
    
    print("\n" + "="*50)
    print("GERANDO VISUALIZAÇÕES PLOTLY")
    print("="*50)
    
    # Gerar todas as visualizações
    visualizador.criar_mapa_animado(
        caminho_saida=os.path.join(pasta_saida, 'mapa_animado.html')
    )
    
    visualizador.criar_mapa_densidade(
        caminho_saida=os.path.join(pasta_saida, 'mapa_densidade.html')
    )
    
    visualizador.criar_grafico_evolucao(
        caminho_saida=os.path.join(pasta_saida, 'evolucao_anual.html')
    )
    
    visualizador.criar_grafico_municipios(
        caminho_saida=os.path.join(pasta_saida, 'top_municipios.html')
    )
    
    visualizador.criar_grafico_pizza(
        caminho_saida=os.path.join(pasta_saida, 'distribuicao_categorias.html')
    )
    
    visualizador.criar_timeline(
        caminho_saida=os.path.join(pasta_saida, 'timeline.html')
    )
    
    visualizador.criar_dashboard_completo(
        caminho_saida=os.path.join(pasta_saida, 'dashboard_completo.html')
    )
    
    print("="*50)
    print("[OK] TODAS AS VISUALIZAÇÕES GERADAS!")
    print("="*50)


if __name__ == "__main__":
    import os
    from processamento_dados import processar_dados_ipaam
    
    # Caminhos
    caminho_dados = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'dados',
        'licencas_ipaam_exemplo.csv'
    )
    
    pasta_saida = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'output',
        'plotly'
    )
    
    # Processar e visualizar
    if os.path.exists(caminho_dados):
        df = processar_dados_ipaam(caminho_dados)
        criar_visualizacoes_plotly(df, pasta_saida)
    else:
        print(f"Arquivo não encontrado: {caminho_dados}")
