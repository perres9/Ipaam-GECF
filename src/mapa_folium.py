"""
IPAAM - Geração de Mapa Interativo com Folium
==============================================
Módulo para criação de mapas interativos com:
- Time Slider (Linha do tempo)
- Mapa de Calor (Heatmap)
- Marcadores personalizados por categoria
- Controles de camadas

Autor: Engenheiro de Dados GIS
Versão: 1.0.0
"""

import folium
from folium import plugins
from folium.plugins import TimestampedGeoJson, HeatMapWithTime, MarkerCluster
import pandas as pd
import numpy as np
from datetime import datetime
import json
from typing import List, Dict, Optional
import warnings

warnings.filterwarnings('ignore')


class GeradorMapaIPAAM:
    """
    Classe para geração de mapas interativos das licenças do IPAAM.
    
    Funcionalidades:
    - Mapa base com diferentes estilos (Terrain, Satellite, etc.)
    - Marcadores personalizados por tipo de atividade
    - Time Slider para evolução temporal
    - Heatmap de densidade
    - Controle de camadas
    """
    
    # Centro do Amazonas
    CENTRO_AMAZONAS = [-3.4168, -65.8561]
    ZOOM_INICIAL = 6
    
    # Cores e ícones por categoria
    ESTILOS_CATEGORIA = {
        'Manejo Florestal': {
            'cor': 'green',
            'icone': 'tree',
            'prefixo': 'fa',
            'cor_hex': '#228B22'
        },
        'Indústria Madeireira': {
            'cor': 'orange',
            'icone': 'industry',
            'prefixo': 'fa',
            'cor_hex': '#FF8C00'
        },
        'Indústria Mobiliária': {
            'cor': 'blue',
            'icone': 'chair',
            'prefixo': 'fa',
            'cor_hex': '#4169E1'
        },
        'Outros': {
            'cor': 'gray',
            'icone': 'info-circle',
            'prefixo': 'fa',
            'cor_hex': '#808080'
        }
    }
    
    # Cores por tipo de licença
    CORES_LICENCA = {
        'LP': '#FFD700',  # Amarelo - Licença Prévia
        'LI': '#FFA500',  # Laranja - Licença de Instalação
        'LO': '#32CD32'   # Verde - Licença de Operação
    }
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o gerador de mapas.
        
        Args:
            df: DataFrame com os dados das licenças
        """
        self.df = df.copy()
        self.mapa = None
        self._preparar_dados()
    
    def _preparar_dados(self):
        """Prepara e valida os dados para visualização."""
        # Garantir que temos coordenadas válidas
        self.df = self.df.dropna(subset=['latitude', 'longitude'])
        
        # Converter datas
        if 'data_emissao' in self.df.columns:
            self.df['data_emissao'] = pd.to_datetime(self.df['data_emissao'], errors='coerce')
        
        # Garantir coluna de categoria
        if 'categoria' not in self.df.columns:
            self.df['categoria'] = 'Outros'
        
        # Garantir coluna de ano
        if 'ano' not in self.df.columns and 'data_emissao' in self.df.columns:
            self.df['ano'] = self.df['data_emissao'].dt.year
        
        print(f"[OK] Dados preparados: {len(self.df)} registros validos")
    
    def criar_mapa_base(self, estilo: str = 'terrain') -> folium.Map:
        """
        Cria o mapa base com o estilo especificado.
        
        Args:
            estilo: 'terrain', 'satellite', 'openstreetmap', 'cartodb'
            
        Returns:
            Objeto Map do Folium
        """
        # Criar mapa base
        self.mapa = folium.Map(
            location=self.CENTRO_AMAZONAS,
            zoom_start=self.ZOOM_INICIAL,
            control_scale=True
        )
        
        # Camadas de tiles para trabalho florestal
        
        # Google Satélite - Análise de cobertura florestal
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name='Satélite',
            overlay=False
        ).add_to(self.mapa)
        
        # Google Híbrido - Satélite com identificação de localidades
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            attr='Google',
            name='Satélite + Rótulos',
            overlay=False
        ).add_to(self.mapa)
        
        # Topográfico - Relevo e hidrografia
        folium.TileLayer(
            tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            attr='OpenTopoMap',
            name='Topográfico',
            overlay=False
        ).add_to(self.mapa)
        
        # OpenStreetMap - Estradas e infraestrutura
        folium.TileLayer(
            tiles='openstreetmap',
            name='Ruas',
            overlay=False
        ).add_to(self.mapa)
        
        print("[OK] Mapa base criado com multiplas camadas de tiles")
        return self.mapa
    
    def adicionar_marcadores(self, agrupar: bool = True) -> folium.Map:
        """
        Adiciona marcadores ao mapa com ícones personalizados.
        
        Args:
            agrupar: Se True, agrupa marcadores próximos em clusters
            
        Returns:
            Mapa com marcadores
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        # Criar grupos de camadas por categoria
        grupos = {}
        for categoria in self.df['categoria'].unique():
            grupo = folium.FeatureGroup(name=categoria)
            grupos[categoria] = grupo
        
        # Adicionar marcadores
        for _, row in self.df.iterrows():
            categoria = row.get('categoria', 'Outros')
            estilo = self.ESTILOS_CATEGORIA.get(categoria, self.ESTILOS_CATEGORIA['Outros'])
            
            # Criar popup com informações
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 250px;">
                <h4 style="color: {estilo['cor_hex']}; margin-bottom: 10px;">
                    {row.get('razao_social', 'N/A')}
                </h4>
                <table style="width: 100%; font-size: 12px;">
                    <tr><td><b>Município:</b></td><td>{row.get('municipio', 'N/A')}</td></tr>
                    <tr><td><b>Atividade:</b></td><td>{row.get('atividade', 'N/A')}</td></tr>
                    <tr><td><b>Tipo Licença:</b></td><td>{row.get('tipo_licenca', 'N/A')}</td></tr>
                    <tr><td><b>Gerência:</b></td><td>{row.get('gerencia', 'N/A')}</td></tr>
                    <tr><td><b>Data Emissão:</b></td><td>{str(row.get('data_emissao', 'N/A'))[:10]}</td></tr>
                    <tr><td><b>Validade:</b></td><td>{str(row.get('data_validade', 'N/A'))[:10]}</td></tr>
                </table>
            </div>
            """
            
            # Criar marcador
            marcador = folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row.get('razao_social', 'N/A')} ({row.get('ano', 'N/A')})",
                icon=folium.Icon(
                    color=estilo['cor'],
                    icon=estilo['icone'],
                    prefix=estilo['prefixo']
                )
            )
            
            marcador.add_to(grupos[categoria])
        
        # Adicionar grupos ao mapa
        for grupo in grupos.values():
            grupo.add_to(self.mapa)
        
        print(f"[OK] Adicionados {len(self.df)} marcadores em {len(grupos)} categorias")
        return self.mapa
    
    def adicionar_time_slider(self) -> folium.Map:
        """
        Adiciona controle deslizante de tempo (Time Slider) ao mapa.
        
        Returns:
            Mapa com Time Slider
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        # Preparar dados para TimestampedGeoJson
        features = []
        
        for _, row in self.df.iterrows():
            categoria = row.get('categoria', 'Outros')
            estilo = self.ESTILOS_CATEGORIA.get(categoria, self.ESTILOS_CATEGORIA['Outros'])
            
            # Formatar data para o time slider
            if pd.notna(row.get('data_emissao')):
                data_str = pd.to_datetime(row['data_emissao']).strftime('%Y-%m-%d')
            else:
                data_str = f"{row.get('ano', 2020)}-01-01"
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row['longitude'], row['latitude']]
                },
                "properties": {
                    "time": data_str,
                    "popup": f"<b>{row.get('razao_social', 'N/A')}</b><br>{row.get('municipio', 'N/A')}<br>{row.get('atividade', 'N/A')}",
                    "icon": "circle",
                    "iconstyle": {
                        "fillColor": estilo['cor_hex'],
                        "fillOpacity": 0.8,
                        "stroke": True,
                        "color": "#000000",
                        "weight": 1,
                        "radius": 8
                    },
                    "style": {
                        "weight": 2,
                        "color": estilo['cor_hex']
                    }
                }
            }
            features.append(feature)
        
        # Criar GeoJSON temporal
        geojson_temporal = {
            "type": "FeatureCollection",
            "features": features
        }
        
        # Adicionar ao mapa
        TimestampedGeoJson(
            geojson_temporal,
            period='P1M',  # Período de 1 mês
            duration='P1M',
            add_last_point=True,
            auto_play=False,
            loop=False,
            max_speed=5,
            loop_button=True,
            date_options='YYYY-MM',
            time_slider_drag_update=True,
            transition_time=500
        ).add_to(self.mapa)
        
        print("[OK] Time Slider adicionado ao mapa")
        return self.mapa
    
    def adicionar_heatmap(self, por_tempo: bool = True) -> folium.Map:
        """
        Adiciona mapa de calor ao mapa.
        
        Args:
            por_tempo: Se True, cria heatmap animado por ano
            
        Returns:
            Mapa com heatmap
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        if por_tempo:
            # Heatmap animado por ano
            anos = sorted(self.df['ano'].dropna().unique())
            
            heat_data = []
            index_time = []
            
            for ano in anos:
                df_ano = self.df[self.df['ano'] == ano]
                pontos = [[row['latitude'], row['longitude'], 1] for _, row in df_ano.iterrows()]
                if pontos:
                    heat_data.append(pontos)
                    index_time.append(str(int(ano)))
            
            if heat_data:
                heatmap_layer = HeatMapWithTime(
                    heat_data,
                    index=index_time,
                    auto_play=False,
                    max_opacity=0.8,
                    min_opacity=0.3,
                    use_local_extrema=True,
                    radius=25,
                    gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1: 'red'}
                )
                heatmap_layer.add_to(self.mapa)
                print(f"[OK] Heatmap temporal adicionado ({len(anos)} anos)")
        else:
            # Heatmap estático
            from folium.plugins import HeatMap
            
            heat_data = [[row['latitude'], row['longitude']] for _, row in self.df.iterrows()]
            
            heatmap_group = folium.FeatureGroup(name="Mapa de Calor")
            HeatMap(
                heat_data,
                radius=20,
                blur=15,
                max_zoom=13,
                gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1: 'red'}
            ).add_to(heatmap_group)
            
            heatmap_group.add_to(self.mapa)
            print("[OK] Heatmap estatico adicionado")
        
        return self.mapa
    
    def adicionar_legenda(self) -> folium.Map:
        """
        Adiciona legenda compacta ao mapa.
        
        Returns:
            Mapa com legenda
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        # HTML da legenda - compacta e profissional
        legenda_html = """
        <div id="legenda-panel" style="
            position: fixed; 
            bottom: 30px; 
            left: 10px; 
            z-index: 1000;
            background: rgba(255,255,255,0.95);
            padding: 10px 12px;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11px;
            max-width: 160px;
            border-left: 3px solid #228B22;
        ">
            <div style="font-weight: 600; margin-bottom: 6px; color: #333;">Categorias</div>
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="width: 10px; height: 10px; background: #228B22; border-radius: 50%; margin-right: 6px;"></span>
                <span>Manejo Florestal</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="width: 10px; height: 10px; background: #FF8C00; border-radius: 50%; margin-right: 6px;"></span>
                <span>Ind. Madeireira</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="width: 10px; height: 10px; background: #4169E1; border-radius: 50%; margin-right: 6px;"></span>
                <span>Ind. Mobiliária</span>
            </div>
            <div style="border-top: 1px solid #ddd; margin: 8px 0 6px 0;"></div>
            <div style="font-weight: 600; margin-bottom: 4px; color: #333;">Licenças</div>
            <div style="display: flex; gap: 6px;">
                <span style="background: #FFD700; padding: 1px 6px; border-radius: 3px; font-size: 10px;">LP</span>
                <span style="background: #FFA500; padding: 1px 6px; border-radius: 3px; font-size: 10px;">LI</span>
                <span style="background: #32CD32; padding: 1px 6px; border-radius: 3px; font-size: 10px;">LO</span>
            </div>
        </div>
        """
        
        self.mapa.get_root().html.add_child(folium.Element(legenda_html))
        print("[OK] Legenda adicionada")
        return self.mapa
    
    def adicionar_creditos(self) -> folium.Map:
        """
        Adiciona créditos discretos no mapa.
        
        Returns:
            Mapa com créditos
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        creditos_html = """
        <div style="
            position: fixed; 
            bottom: 5px; 
            right: 10px; 
            z-index: 900;
            background: rgba(255,255,255,0.8);
            padding: 4px 8px;
            border-radius: 3px;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 9px;
            color: #666;
        ">
            IPAAM - GECF/GELI | 
            <a href="https://www.ipaam.am.gov.br/transparencia-tecnica/" target="_blank" style="color: #0066cc;">Transparência Técnica</a>
        </div>
        """
        
        self.mapa.get_root().html.add_child(folium.Element(creditos_html))
        print("[OK] Creditos adicionados")
        return self.mapa
    
    def adicionar_estatisticas(self) -> folium.Map:
        """
        Adiciona painel de estatísticas compacto ao mapa.
        
        Returns:
            Mapa com painel de estatísticas
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        # Calcular estatísticas
        total = len(self.df)
        por_categoria = self.df['categoria'].value_counts().to_dict()
        por_ano = self.df['ano'].value_counts().sort_index().to_dict()
        municipios = self.df['municipio'].nunique()
        
        anos_list = sorted(por_ano.keys())
        periodo = f"{int(min(anos_list))}" if len(anos_list) == 1 else f"{int(min(anos_list))}-{int(max(anos_list))}"
        
        # Criar HTML das estatísticas - compacto
        stats_html = f"""
        <div id="stats-panel" style="
            position: fixed; 
            top: 10px; 
            left: 50px; 
            z-index: 1000;
            background: rgba(255,255,255,0.95);
            padding: 8px 12px;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11px;
            border-left: 3px solid #007bff;
        ">
            <div style="display: flex; gap: 15px; align-items: center;">
                <div><span style="font-weight: 600; color: #007bff;">{total}</span> Licenças</div>
                <div><span style="font-weight: 600; color: #007bff;">{municipios}</span> Municípios</div>
                <div><span style="font-weight: 600; color: #007bff;">{periodo}</span></div>
            </div>
        </div>
        """
        
        self.mapa.get_root().html.add_child(folium.Element(stats_html))
        print("[OK] Painel de estatisticas adicionado")
        return self.mapa
    
    def adicionar_seletor_municipio(self) -> folium.Map:
        """
        Adiciona dropdown para selecionar e ir para um município.
        
        Returns:
            Mapa com seletor de município
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        # Obter coordenadas médias por município
        municipios_coords = self.df.groupby('municipio').agg({
            'latitude': 'mean',
            'longitude': 'mean'
        }).to_dict('index')
        
        # Criar lista de opções ordenada
        opcoes_html = '<option value="">Selecione um município...</option>\n'
        for mun in sorted(municipios_coords.keys()):
            coords = municipios_coords[mun]
            opcoes_html += f'<option value="{coords["latitude"]},{coords["longitude"]}">{mun}</option>\n'
        
        seletor_html = f"""
        <div id="municipio-selector" style="
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
            background: rgba(255,255,255,0.95);
            padding: 8px 12px;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
        ">
            <label style="font-weight: 600; margin-right: 8px;">Ir para:</label>
            <select id="municipio-select" onchange="irParaMunicipio(this.value)" style="
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 12px;
                min-width: 180px;
                cursor: pointer;
            ">
                {opcoes_html}
            </select>
        </div>
        
        <script>
        function irParaMunicipio(coords) {{
            if (coords) {{
                var parts = coords.split(',');
                var lat = parseFloat(parts[0]);
                var lng = parseFloat(parts[1]);
                
                // Encontrar o objeto mapa do Leaflet
                var mapElement = document.querySelector('.folium-map');
                if (mapElement && mapElement._leaflet_map) {{
                    mapElement._leaflet_map.setView([lat, lng], 12, {{animate: true, duration: 1}});
                }} else {{
                    // Fallback: buscar em variáveis globais
                    for (var key in window) {{
                        if (window[key] && window[key]._leaflet_id && window[key].setView) {{
                            window[key].setView([lat, lng], 12, {{animate: true, duration: 1}});
                            break;
                        }}
                    }}
                }}
            }}
        }}
        </script>
        """
        
        self.mapa.get_root().html.add_child(folium.Element(seletor_html))
        print("[OK] Seletor de municipio adicionado")
        return self.mapa
    
    def adicionar_botao_print(self) -> folium.Map:
        """
        Adiciona botão para gerar screenshot em alta resolução.
        
        Returns:
            Mapa com botão de print
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        print_html = """
        <div id="print-controls" style="
            position: fixed;
            top: 50px;
            right: 10px;
            z-index: 1000;
            display: flex;
            gap: 5px;
        ">
            <button onclick="capturarMapa()" style="
                background: #28a745;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            " onmouseover="this.style.background='#218838'" onmouseout="this.style.background='#28a745'">
                Capturar Mapa
            </button>
            <button onclick="imprimirMapa()" style="
                background: #0066cc;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            " onmouseover="this.style.background='#0052a3'" onmouseout="this.style.background='#0066cc'">
                Imprimir
            </button>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script>
        function capturarMapa() {
            // Mostrar loading
            var btn = event.target;
            var textoOriginal = btn.innerHTML;
            btn.innerHTML = 'Processando...';
            btn.disabled = true;
            
            // Capturar o mapa
            var mapContainer = document.querySelector('.folium-map');
            if (!mapContainer) {
                mapContainer = document.querySelector('#map');
            }
            if (!mapContainer) {
                mapContainer = document.querySelector('[class*="leaflet-container"]');
            }
            
            html2canvas(mapContainer, {
                useCORS: true,
                allowTaint: true,
                scale: 2, // Alta resolução (2x)
                logging: false,
                backgroundColor: '#ffffff'
            }).then(function(canvas) {
                // Criar link de download
                var link = document.createElement('a');
                var data = new Date();
                var nomeArquivo = 'IPAAM_Mapa_' + data.getFullYear() + '-' + 
                    String(data.getMonth()+1).padStart(2,'0') + '-' + 
                    String(data.getDate()).padStart(2,'0') + '_' +
                    String(data.getHours()).padStart(2,'0') + 'h' +
                    String(data.getMinutes()).padStart(2,'0') + '.png';
                
                link.download = nomeArquivo;
                link.href = canvas.toDataURL('image/png', 1.0);
                link.click();
                
                // Restaurar botão
                btn.innerHTML = textoOriginal;
                btn.disabled = false;
                
                alert('Imagem salva: ' + nomeArquivo + '\\nResolucao: ' + canvas.width + 'x' + canvas.height + ' pixels');
            }).catch(function(error) {
                console.error('Erro ao capturar:', error);
                btn.innerHTML = textoOriginal;
                btn.disabled = false;
                alert('Erro ao capturar. Tente usar Ctrl+P para imprimir.');
            });
        }
        
        function imprimirMapa() {
            window.print();
        }
        </script>
        
        <style>
        @media print {
            #municipio-selector, #print-controls, #stats-panel, #legenda-panel,
            .leaflet-control-zoom, .leaflet-control-layers, .leaflet-control-fullscreen {
                display: none !important;
            }
            .folium-map, .leaflet-container {
                width: 100% !important;
                height: 100vh !important;
            }
        }
        </style>
        """
        
        self.mapa.get_root().html.add_child(folium.Element(print_html))
        print("[OK] Botao de captura/print adicionado")
        return self.mapa
    
    def adicionar_controle_camadas(self) -> folium.Map:
        """
        Adiciona controle de camadas ao mapa.
        
        Returns:
            Mapa com controle de camadas
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        folium.LayerControl(collapsed=False).add_to(self.mapa)
        print("[OK] Controle de camadas adicionado")
        return self.mapa
    
    def adicionar_minimap(self) -> folium.Map:
        """
        Adiciona mini mapa de navegação.
        
        Returns:
            Mapa com mini mapa
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        minimap = plugins.MiniMap(toggle_display=True)
        self.mapa.add_child(minimap)
        print("[OK] Mini mapa adicionado")
        return self.mapa
    
    def adicionar_fullscreen(self) -> folium.Map:
        """
        Adiciona botão de tela cheia.
        
        Returns:
            Mapa com botão fullscreen
        """
        if self.mapa is None:
            self.criar_mapa_base()
        
        plugins.Fullscreen().add_to(self.mapa)
        print("[OK] Botao fullscreen adicionado")
        return self.mapa
    
    def gerar_mapa_completo(
        self,
        com_marcadores: bool = True,
        com_time_slider: bool = True,
        com_heatmap: bool = True,
        com_legenda: bool = True,
        com_estatisticas: bool = True,
        caminho_saida: str = None
    ) -> folium.Map:
        """
        Gera o mapa completo com todas as funcionalidades selecionadas.
        
        Args:
            com_marcadores: Adicionar marcadores
            com_time_slider: Adicionar time slider
            com_heatmap: Adicionar mapa de calor
            com_legenda: Adicionar legenda
            com_estatisticas: Adicionar painel de estatísticas
            caminho_saida: Caminho para salvar o HTML
            
        Returns:
            Mapa completo
        """
        print("\n" + "="*50)
        print("GERANDO MAPA INTERATIVO IPAAM")
        print("="*50)
        
        # Criar mapa base
        self.criar_mapa_base()
        
        # Adicionar componentes
        if com_marcadores:
            self.adicionar_marcadores()
        
        if com_time_slider:
            self.adicionar_time_slider()
        
        if com_heatmap:
            self.adicionar_heatmap(por_tempo=False)  # Heatmap estático (time slider já é temporal)
        
        if com_legenda:
            self.adicionar_legenda()
        
        if com_estatisticas:
            self.adicionar_estatisticas()
        
        # Adicionar controles
        self.adicionar_creditos()
        self.adicionar_controle_camadas()
        self.adicionar_minimap()
        self.adicionar_fullscreen()
        self.adicionar_seletor_municipio()
        self.adicionar_botao_print()
        
        # Salvar se caminho fornecido
        if caminho_saida:
            self.mapa.save(caminho_saida)
            print(f"\n[OK] Mapa salvo em: {caminho_saida}")
        
        print("="*50)
        print("MAPA GERADO COM SUCESSO!")
        print("="*50)
        
        return self.mapa
    
    def get_mapa(self) -> folium.Map:
        """Retorna o objeto mapa."""
        return self.mapa


if __name__ == "__main__":
    # Exemplo de uso
    import os
    from processamento_dados import processar_dados_ipaam
    
    # Caminhos
    caminho_dados = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'dados',
        'licencas_ipaam_exemplo.csv'
    )
    
    caminho_saida = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'output',
        'mapa_ipaam.html'
    )
    
    # Criar pasta output se não existir
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    
    # Processar dados
    if os.path.exists(caminho_dados):
        df = processar_dados_ipaam(caminho_dados)
        
        # Gerar mapa
        gerador = GeradorMapaIPAAM(df)
        mapa = gerador.gerar_mapa_completo(caminho_saida=caminho_saida)
    else:
        print(f"Arquivo não encontrado: {caminho_dados}")
