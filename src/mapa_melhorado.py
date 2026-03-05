"""
IPAAM - Mapa Interativo MELHORADO
=================================
Versão aprimorada com:
- Ícones personalizados (DivIcon com emoji)
- Popups modernos com CSS
- Filtros interativos
- Busca por empresa/município
- Estatísticas dinâmicas
- Clustering de marcadores
- Design responsivo

Autor: Engenheiro de Dados GIS
Versão: 2.0.0
"""

import folium
from folium import plugins
from folium.plugins import MarkerCluster, Search, Fullscreen, MiniMap
import pandas as pd
import json
from branca.element import Template, MacroElement


class GeradorMapaMelhorado:
    """Gerador de mapa interativo melhorado para IPAAM."""
    
    CENTRO_AMAZONAS = [-3.4168, -65.8561]
    ZOOM_INICIAL = 6
    
    # Emojis e cores por categoria
    ESTILOS = {
        'Manejo Florestal': {
            'emoji': '*',
            'cor': '#228B22',
            'cor_clara': '#90EE90',
            'nome_curto': 'Florestal'
        },
        'Indústria Madeireira': {
            'emoji': '*',
            'cor': '#FF6B35',
            'cor_clara': '#FFB299',
            'nome_curto': 'Madeireira'
        },
        'Indústria Mobiliária': {
            'emoji': '*',
            'cor': '#4169E1',
            'cor_clara': '#87CEEB',
            'nome_curto': 'Mobiliária'
        },
        'Outros': {
            'emoji': '*',
            'cor': '#808080',
            'cor_clara': '#D3D3D3',
            'nome_curto': 'Outros'
        }
    }
    
    # Cores por tipo de licença
    CORES_LICENCA = {
        'LP': {'cor': '#FFD700', 'nome': 'Licença Prévia'},
        'LI': {'cor': '#FFA500', 'nome': 'Licença de Instalação'},
        'LO': {'cor': '#32CD32', 'nome': 'Licença de Operação'}
    }
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df = self.df.dropna(subset=['latitude', 'longitude'])
        self.mapa = None
        print(f"[OK] {len(self.df)} registros carregados para o mapa melhorado")
    
    def _criar_icone_customizado(self, categoria: str, tipo_licenca: str = 'LO') -> folium.DivIcon:
        """Cria ícone customizado com emoji e borda colorida."""
        estilo = self.ESTILOS.get(categoria, self.ESTILOS['Outros'])
        cor_licenca = self.CORES_LICENCA.get(tipo_licenca, self.CORES_LICENCA['LO'])['cor']
        
        html = f'''
        <div style="
            font-size: 24px;
            text-align: center;
            line-height: 36px;
            width: 36px;
            height: 36px;
            background: white;
            border: 3px solid {estilo['cor']};
            border-radius: 50%;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: transform 0.2s;
        " onmouseover="this.style.transform='scale(1.2)'" 
           onmouseout="this.style.transform='scale(1)'">
            {estilo['emoji']}
        </div>
        '''
        return folium.DivIcon(
            html=html,
            icon_size=(36, 36),
            icon_anchor=(18, 18)
        )
    
    def _criar_popup_moderno(self, row: pd.Series) -> folium.Popup:
        """Cria popup moderno com design melhorado."""
        categoria = row.get('categoria', 'Outros')
        estilo = self.ESTILOS.get(categoria, self.ESTILOS['Outros'])
        tipo_lic = row.get('tipo_licenca', 'LO')
        info_lic = self.CORES_LICENCA.get(tipo_lic, self.CORES_LICENCA['LO'])
        
        # Formatar datas
        data_emissao = str(row.get('data_emissao', 'N/A'))[:10]
        data_validade = str(row.get('data_validade', 'N/A'))[:10]
        
        html = f'''
        <div style="
            font-family: 'Segoe UI', Arial, sans-serif;
            width: 300px;
            padding: 0;
            margin: 0;
        ">
            <!-- Cabeçalho -->
            <div style="
                background: linear-gradient(135deg, {estilo['cor']} 0%, {estilo['cor_clara']} 100%);
                color: white;
                padding: 12px 15px;
                border-radius: 8px 8px 0 0;
                margin: -1px -1px 0 -1px;
            ">
                <div style="font-size: 14px; opacity: 0.9;">{estilo['emoji']} {categoria}</div>
                <div style="font-size: 16px; font-weight: bold; margin-top: 5px;">
                    {row.get('razao_social', 'N/A')[:40]}
                </div>
            </div>
            
            <!-- Conteúdo -->
            <div style="padding: 15px; background: #f9f9f9;">
                <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <tr>
                        <td style="padding: 6px 0; color: #666;">Municipio</td>
                        <td style="padding: 6px 0; font-weight: 500; text-align: right;">{row.get('municipio', 'N/A')}</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="padding: 6px 0; color: #666;">Licenca</td>
                        <td style="padding: 6px 0; text-align: right;">
                            <span style="
                                background: {info_lic['cor']};
                                color: #333;
                                padding: 2px 8px;
                                border-radius: 12px;
                                font-weight: 600;
                                font-size: 12px;
                            ">{tipo_lic}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; color: #666;">Gerencia</td>
                        <td style="padding: 6px 0; font-weight: 500; text-align: right;">{row.get('gerencia', 'N/A')}</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="padding: 6px 0; color: #666;">Emissao</td>
                        <td style="padding: 6px 0; text-align: right;">{data_emissao}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; color: #666;">Validade</td>
                        <td style="padding: 6px 0; text-align: right;">{data_validade}</td>
                    </tr>
                </table>
                
                <!-- Atividade -->
                <div style="
                    margin-top: 12px;
                    padding: 10px;
                    background: white;
                    border-radius: 6px;
                    border-left: 3px solid {estilo['cor']};
                    font-size: 12px;
                    color: #555;
                ">
                    <strong>Atividade:</strong><br>
                    {str(row.get('atividade', 'N/A'))[:150]}...
                </div>
            </div>
            
            <!-- Rodapé -->
            <div style="
                padding: 8px 15px;
                background: #eee;
                border-radius: 0 0 8px 8px;
                font-size: 11px;
                color: #888;
                text-align: center;
            ">
                Ano: <strong>{int(row.get('ano', 0))}</strong> | 
                Coords: {row.get('latitude', 0):.4f}, {row.get('longitude', 0):.4f}
            </div>
        </div>
        '''
        return folium.Popup(html, max_width=320)
    
    def criar_mapa(self) -> folium.Map:
        """Cria o mapa base com tiles melhorados."""
        self.mapa = folium.Map(
            location=self.CENTRO_AMAZONAS,
            zoom_start=self.ZOOM_INICIAL,
            control_scale=True,
            prefer_canvas=True
        )
        
        # Tiles
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='ESRI',
            name='Satelite',
            overlay=False
        ).add_to(self.mapa)
        
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            attr='CartoDB',
            name='Claro',
            overlay=False
        ).add_to(self.mapa)
        
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            attr='CartoDB',
            name='Escuro',
            overlay=False
        ).add_to(self.mapa)
        
        folium.TileLayer(
            tiles='openstreetmap',
            name='OpenStreetMap',
            overlay=False
        ).add_to(self.mapa)
        
        return self.mapa
    
    def adicionar_marcadores_agrupados(self) -> folium.Map:
        """Adiciona marcadores com clustering por categoria."""
        if self.mapa is None:
            self.criar_mapa()
        
        # Criar clusters por categoria
        clusters = {}
        for categoria in self.df['categoria'].unique():
            estilo = self.ESTILOS.get(categoria, self.ESTILOS['Outros'])
            
            # Cluster customizado
            cluster = MarkerCluster(
                name=f"{estilo['emoji']} {categoria}",
                overlay=True,
                control=True,
                icon_create_function=f'''
                function(cluster) {{
                    var count = cluster.getChildCount();
                    var size = count < 10 ? 'small' : count < 50 ? 'medium' : 'large';
                    var sizes = {{'small': 30, 'medium': 40, 'large': 50}};
                    return L.divIcon({{
                        html: '<div style="background: {estilo['cor']}; color: white; border-radius: 50%; width: ' + sizes[size] + 'px; height: ' + sizes[size] + 'px; display: flex; align-items: center; justify-content: center; font-weight: bold; box-shadow: 0 2px 6px rgba(0,0,0,0.3); border: 2px solid white;">' + count + '</div>',
                        className: 'marker-cluster',
                        iconSize: L.point(sizes[size], sizes[size])
                    }});
                }}
                '''
            )
            clusters[categoria] = cluster
        
        # Adicionar marcadores
        for _, row in self.df.iterrows():
            categoria = row.get('categoria', 'Outros')
            
            marcador = folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=self._criar_popup_moderno(row),
                tooltip=f"<b>{row.get('razao_social', 'N/A')[:30]}</b><br>{row.get('municipio', '')}<br>{categoria}",
                icon=self._criar_icone_customizado(categoria, row.get('tipo_licenca', 'LO'))
            )
            
            marcador.add_to(clusters[categoria])
        
        # Adicionar clusters ao mapa
        for cluster in clusters.values():
            cluster.add_to(self.mapa)
        
        print(f"[OK] {len(self.df)} marcadores agrupados em {len(clusters)} categorias")
        return self.mapa
    
    def adicionar_painel_controle(self) -> folium.Map:
        """Adiciona painel de controle lateral com estatísticas."""
        if self.mapa is None:
            self.criar_mapa()
        
        # Calcular estatísticas
        total = len(self.df)
        por_categoria = self.df['categoria'].value_counts().to_dict()
        por_ano = self.df['ano'].value_counts().sort_index().to_dict()
        municipios = self.df['municipio'].nunique()
        
        # Criar barras de progresso para categorias
        barras_html = ""
        for cat, qtd in por_categoria.items():
            estilo = self.ESTILOS.get(cat, self.ESTILOS['Outros'])
            pct = (qtd / total) * 100
            barras_html += f'''
            <div style="margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 2px;">
                    <span>{estilo['emoji']} {estilo['nome_curto']}</span>
                    <span><b>{qtd}</b></span>
                </div>
                <div style="background: #eee; border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background: {estilo['cor']}; width: {pct}%; height: 100%;"></div>
                </div>
            </div>
            '''
        
        # Criar mini gráfico de anos
        anos_html = ""
        max_ano = max(por_ano.values()) if por_ano else 1
        for ano, qtd in sorted(por_ano.items()):
            altura = (qtd / max_ano) * 50
            anos_html += f'''
            <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
                <div style="background: #4CAF50; width: 100%; height: {altura}px; border-radius: 2px 2px 0 0;"></div>
                <div style="font-size: 9px; margin-top: 2px;">{int(ano)}</div>
                <div style="font-size: 8px; color: #666;">{qtd}</div>
            </div>
            '''
        
        painel_html = f'''
        <div id="painel-stats" style="
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            font-family: 'Segoe UI', Arial, sans-serif;
            width: 220px;
            max-height: 90vh;
            overflow-y: auto;
        ">
            <!-- Header -->
            <div style="
                text-align: center;
                padding-bottom: 10px;
                border-bottom: 2px solid #4CAF50;
                margin-bottom: 15px;
            ">
                <div style="font-size: 20px;">IPAAM</div>
                <div style="font-weight: bold; color: #333;">IPAAM</div>
                <div style="font-size: 11px; color: #666;">Licenças Ambientais</div>
            </div>
            
            <!-- Contadores -->
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 24px; font-weight: bold; color: #4CAF50;">{total}</div>
                    <div style="font-size: 10px; color: #666;">Licenças</div>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 24px; font-weight: bold; color: #2196F3;">{municipios}</div>
                    <div style="font-size: 10px; color: #666;">Municípios</div>
                </div>
            </div>
            
            <!-- Por Categoria -->
            <div style="margin-bottom: 15px;">
                <div style="font-weight: 600; font-size: 12px; color: #333; margin-bottom: 8px;">
                    Por Categoria
                </div>
                {barras_html}
            </div>
            
            <!-- Por Ano -->
            <div style="margin-bottom: 15px;">
                <div style="font-weight: 600; font-size: 12px; color: #333; margin-bottom: 8px;">
                    Evolucao Anual
                </div>
                <div style="display: flex; gap: 2px; align-items: flex-end; height: 70px; padding-top: 10px;">
                    {anos_html}
                </div>
            </div>
            
            <!-- Legenda Licenças -->
            <div style="
                padding-top: 10px;
                border-top: 1px solid #eee;
                font-size: 11px;
            ">
                <div style="font-weight: 600; margin-bottom: 5px;">Tipos de Licenca:</div>
                <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                    <span style="background: #FFD700; padding: 2px 6px; border-radius: 8px;">LP</span>
                    <span style="background: #FFA500; padding: 2px 6px; border-radius: 8px;">LI</span>
                    <span style="background: #32CD32; padding: 2px 6px; border-radius: 8px;">LO</span>
                </div>
            </div>
            
            <!-- Créditos -->
            <div style="
                margin-top: 15px;
                padding-top: 10px;
                border-top: 1px solid #eee;
                font-size: 9px;
                color: #999;
                text-align: center;
            ">
                Fonte: IPAAM - GECF/GELI<br>
                <a href="https://www.ipaam.am.gov.br" target="_blank" style="color: #4CAF50;">www.ipaam.am.gov.br</a>
            </div>
            
            <!-- Botão minimizar -->
            <button onclick="
                var p = document.getElementById('painel-stats');
                var c = document.getElementById('painel-content');
                if (c.style.display === 'none') {{
                    c.style.display = 'block';
                    this.innerHTML = '➖';
                }} else {{
                    c.style.display = 'none';
                    this.innerHTML = '➕';
                }}
            " style="
                position: absolute;
                top: 5px;
                right: 5px;
                background: none;
                border: none;
                cursor: pointer;
                font-size: 14px;
            ">➖</button>
        </div>
        '''
        
        self.mapa.get_root().html.add_child(folium.Element(painel_html))
        print("[OK] Painel de controle adicionado")
        return self.mapa
    
    def adicionar_controles(self) -> folium.Map:
        """Adiciona controles do mapa."""
        if self.mapa is None:
            self.criar_mapa()
        
        # Fullscreen
        Fullscreen(
            position='topleft',
            title='Tela Cheia',
            title_cancel='Sair da Tela Cheia'
        ).add_to(self.mapa)
        
        # Minimap
        MiniMap(
            toggle_display=True,
            position='bottomleft'
        ).add_to(self.mapa)
        
        # Layer Control
        folium.LayerControl(
            position='topleft',
            collapsed=True
        ).add_to(self.mapa)
        
        # Escala
        plugins.MousePosition(
            position='bottomright',
            separator=' | ',
            prefix='Coords:'
        ).add_to(self.mapa)
        
        print("[OK] Controles adicionados")
        return self.mapa
    
    def adicionar_busca(self) -> folium.Map:
        """Adiciona barra de busca."""
        if self.mapa is None:
            self.criar_mapa()
        
        # Criar GeoJSON para busca
        features = []
        for _, row in self.df.iterrows():
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row['longitude'], row['latitude']]
                },
                "properties": {
                    "name": row.get('razao_social', ''),
                    "municipio": row.get('municipio', ''),
                    "categoria": row.get('categoria', '')
                }
            })
        
        geojson = folium.GeoJson(
            {"type": "FeatureCollection", "features": features},
            name="Busca",
            show=False
        )
        geojson.add_to(self.mapa)
        
        Search(
            layer=geojson,
            geom_type='Point',
            placeholder='Buscar empresa ou municipio...',
            search_label='name',
            position='topleft',
            collapsed=False
        ).add_to(self.mapa)
        
        print("[OK] Busca adicionada")
        return self.mapa
    
    def adicionar_heatmap_toggle(self) -> folium.Map:
        """Adiciona heatmap como camada opcional."""
        if self.mapa is None:
            self.criar_mapa()
        
        from folium.plugins import HeatMap
        
        heat_data = [[row['latitude'], row['longitude'], 1] for _, row in self.df.iterrows()]
        
        heat_group = folium.FeatureGroup(name='🔥 Mapa de Calor', show=False)
        HeatMap(
            heat_data,
            radius=20,
            blur=15,
            max_zoom=10,
            gradient={0.2: '#ffffb2', 0.4: '#fecc5c', 0.6: '#fd8d3c', 0.8: '#f03b20', 1.0: '#bd0026'}
        ).add_to(heat_group)
        
        heat_group.add_to(self.mapa)
        print("[OK] Heatmap adicionado (camada opcional)")
        return self.mapa
    
    def gerar_mapa_completo(self, caminho_saida: str = None) -> folium.Map:
        """Gera o mapa completo com todas as melhorias."""
        print("\n" + "="*60)
        print("GERANDO MAPA MELHORADO IPAAM")
        print("="*60)
        
        self.criar_mapa()
        self.adicionar_marcadores_agrupados()
        self.adicionar_heatmap_toggle()
        self.adicionar_painel_controle()
        self.adicionar_controles()
        # self.adicionar_busca()  # Desabilitado por enquanto (conflito com clusters)
        
        if caminho_saida:
            self.mapa.save(caminho_saida)
            print(f"\n[OK] Mapa salvo em: {caminho_saida}")
        
        print("="*60)
        print("[OK] MAPA MELHORADO GERADO COM SUCESSO!")
        print("="*60)
        
        return self.mapa


if __name__ == "__main__":
    import os
    
    # Carregar dados
    pasta_dados = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados')
    arquivo = os.path.join(pasta_dados, 'licencas_ipaam_unificado.csv')
    
    if os.path.exists(arquivo):
        df = pd.read_csv(arquivo)
        
        # Gerar mapa
        pasta_output = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        os.makedirs(pasta_output, exist_ok=True)
        
        gerador = GeradorMapaMelhorado(df)
        mapa = gerador.gerar_mapa_completo(
            caminho_saida=os.path.join(pasta_output, 'mapa_ipaam_melhorado.html')
        )
    else:
        print(f"Arquivo não encontrado: {arquivo}")
