"""
IPAAM - Mapa Interativo Profissional
=====================================
Design clean e corporativo:
- Marcadores circulares coloridos (sem emojis)
- Popups minimalistas
- Painel lateral elegante
- Cores institucionais

Autor: Engenheiro de Dados GIS
Versão: 3.0.0
"""

import folium
from folium import plugins
from folium.plugins import MarkerCluster, Fullscreen, MiniMap
import pandas as pd


class GeradorMapaProfissional:
    """Gerador de mapa interativo profissional para IPAAM."""
    
    CENTRO_AMAZONAS = [-3.4168, -65.8561]
    ZOOM_INICIAL = 6
    
    # Cores profissionais por categoria
    CATEGORIAS = {
        'Manejo Florestal': {
            'cor': '#2E7D32',  # Verde escuro
            'sigla': 'MF'
        },
        'Indústria Madeireira': {
            'cor': '#E65100',  # Laranja escuro
            'sigla': 'IM'
        },
        'Indústria Mobiliária': {
            'cor': '#1565C0',  # Azul escuro
            'sigla': 'MB'
        },
        'Outros': {
            'cor': '#616161',  # Cinza
            'sigla': 'OT'
        }
    }
    
    # Status por tipo de licença
    LICENCAS = {
        'LP': {'cor': '#FBC02D', 'nome': 'Licença Prévia'},
        'LI': {'cor': '#FF8F00', 'nome': 'Licença de Instalação'},
        'LO': {'cor': '#43A047', 'nome': 'Licença de Operação'}
    }
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df = self.df.dropna(subset=['latitude', 'longitude'])
        self.mapa = None
        print(f"[OK] {len(self.df)} registros carregados")
    
    def _criar_marcador_circular(self, categoria: str) -> folium.DivIcon:
        """Cria marcador circular minimalista."""
        config = self.CATEGORIAS.get(categoria, self.CATEGORIAS['Outros'])
        
        html = f'''
        <div style="
            width: 12px;
            height: 12px;
            background: {config['cor']};
            border: 2px solid white;
            border-radius: 50%;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
        "></div>
        '''
        return folium.DivIcon(
            html=html,
            icon_size=(16, 16),
            icon_anchor=(8, 8)
        )
    
    def _criar_popup_profissional(self, row: pd.Series) -> folium.Popup:
        """Cria popup com design profissional."""
        categoria = row.get('categoria', 'Outros')
        config = self.CATEGORIAS.get(categoria, self.CATEGORIAS['Outros'])
        tipo_lic = row.get('tipo_licenca', 'LO')
        info_lic = self.LICENCAS.get(tipo_lic, self.LICENCAS['LO'])
        
        data_emissao = str(row.get('data_emissao', '-'))[:10]
        data_validade = str(row.get('data_validade', '-'))[:10]
        
        html = f'''
        <div style="
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            width: 280px;
            line-height: 1.4;
        ">
            <!-- Header -->
            <div style="
                background: {config['cor']};
                color: white;
                padding: 12px 14px;
                border-radius: 6px 6px 0 0;
            ">
                <div style="font-size: 11px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">
                    {categoria}
                </div>
                <div style="font-size: 14px; font-weight: 600; margin-top: 4px;">
                    {row.get('razao_social', 'N/A')[:45]}
                </div>
            </div>
            
            <!-- Body -->
            <div style="padding: 14px; background: #fff; border: 1px solid #e0e0e0; border-top: none;">
                <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                    <tr>
                        <td style="color: #757575; padding: 4px 0; width: 90px;">Município</td>
                        <td style="font-weight: 500;">{row.get('municipio', '-')}</td>
                    </tr>
                    <tr>
                        <td style="color: #757575; padding: 4px 0;">Licença</td>
                        <td>
                            <span style="
                                display: inline-block;
                                background: {info_lic['cor']};
                                color: #333;
                                padding: 1px 8px;
                                border-radius: 3px;
                                font-size: 11px;
                                font-weight: 600;
                            ">{tipo_lic}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="color: #757575; padding: 4px 0;">Gerência</td>
                        <td style="font-weight: 500;">{row.get('gerencia', '-')}</td>
                    </tr>
                    <tr>
                        <td style="color: #757575; padding: 4px 0;">Emissão</td>
                        <td>{data_emissao}</td>
                    </tr>
                    <tr>
                        <td style="color: #757575; padding: 4px 0;">Validade</td>
                        <td>{data_validade}</td>
                    </tr>
                </table>
                
                <!-- Atividade -->
                <div style="
                    margin-top: 10px;
                    padding: 8px 10px;
                    background: #f5f5f5;
                    border-radius: 4px;
                    font-size: 11px;
                    color: #616161;
                    border-left: 3px solid {config['cor']};
                ">
                    {str(row.get('atividade', '-'))[:120]}...
                </div>
            </div>
            
            <!-- Footer -->
            <div style="
                padding: 8px 14px;
                background: #fafafa;
                border: 1px solid #e0e0e0;
                border-top: none;
                border-radius: 0 0 6px 6px;
                font-size: 10px;
                color: #9e9e9e;
            ">
                {row.get('latitude', 0):.5f}, {row.get('longitude', 0):.5f}
            </div>
        </div>
        '''
        return folium.Popup(html, max_width=300)
    
    def criar_mapa(self) -> folium.Map:
        """Cria mapa base com estilo profissional."""
        self.mapa = folium.Map(
            location=self.CENTRO_AMAZONAS,
            zoom_start=self.ZOOM_INICIAL,
            control_scale=True,
            prefer_canvas=True,
            tiles=None
        )
        
        # Tile padrão - Claro e limpo
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            attr='CartoDB',
            name='Claro',
            overlay=False
        ).add_to(self.mapa)
        
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='ESRI',
            name='Satélite',
            overlay=False
        ).add_to(self.mapa)
        
        folium.TileLayer(
            tiles='openstreetmap',
            name='OpenStreetMap',
            overlay=False
        ).add_to(self.mapa)
        
        return self.mapa
    
    def adicionar_marcadores(self) -> folium.Map:
        """Adiciona marcadores com clustering por ANO (mantendo cores por categoria)."""
        if self.mapa is None:
            self.criar_mapa()
        
        # Criar clusters por ANO
        anos = sorted(self.df['ano'].dropna().unique())
        clusters_ano = {}
        
        for ano in anos:
            ano_int = int(ano)
            
            # MarkerCluster por ano com estilo profissional
            cluster = MarkerCluster(
                name=f"Ano {ano_int}",
                overlay=True,
                control=True,
                show=(ano_int == 2025),  # Só 2025 visível por padrão
                icon_create_function='''
                function(cluster) {
                    var count = cluster.getChildCount();
                    var size = count < 10 ? 28 : count < 30 ? 34 : 40;
                    return L.divIcon({
                        html: '<div style="background: #2E7D32; color: white; width: ' + size + 'px; height: ' + size + 'px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 11px; box-shadow: 0 2px 6px rgba(0,0,0,0.25); border: 2px solid white;">' + count + '</div>',
                        className: 'marker-cluster',
                        iconSize: L.point(size, size)
                    });
                }
                '''
            )
            clusters_ano[ano_int] = cluster
        
        # Adicionar marcadores ao cluster do respectivo ano
        for _, row in self.df.iterrows():
            categoria = row.get('categoria', 'Outros')
            ano = int(row.get('ano', 2025))
            config = self.CATEGORIAS.get(categoria, self.CATEGORIAS['Outros'])
            
            # Marcador com ícone colorido por categoria
            marcador = folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=self._criar_popup_profissional(row),
                tooltip=f"<b>{row.get('razao_social', '')[:35]}</b><br>{row.get('municipio', '')}<br>Ano: {ano}",
                icon=self._criar_marcador_circular(categoria)
            )
            
            if ano in clusters_ano:
                marcador.add_to(clusters_ano[ano])
        
        # Adicionar clusters ao mapa
        for ano, cluster in sorted(clusters_ano.items()):
            cluster.add_to(self.mapa)
        
        print(f"[OK] {len(self.df)} marcadores em {len(clusters_ano)} anos (com clustering)")
        return self.mapa
    
    def adicionar_painel_estatisticas(self) -> folium.Map:
        """Adiciona painel lateral com estatísticas."""
        if self.mapa is None:
            self.criar_mapa()
        
        total = len(self.df)
        por_categoria = self.df['categoria'].value_counts().to_dict()
        por_ano = self.df['ano'].value_counts().sort_index().to_dict()
        municipios = self.df['municipio'].nunique()
        
        # Carregar logo em base64
        import os
        import base64
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'Logotipo-IPAAM-300x286.png')
        logo_base64 = ""
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_base64 = base64.b64encode(f.read()).decode()
        
        # Gerar barras por categoria
        barras_html = ""
        for cat, qtd in por_categoria.items():
            config = self.CATEGORIAS.get(cat, self.CATEGORIAS['Outros'])
            pct = (qtd / total) * 100
            barras_html += f'''
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 3px;">
                    <span style="color: #424242;">{cat}</span>
                    <span style="font-weight: 600; color: {config['cor']};">{qtd}</span>
                </div>
                <div style="background: #e0e0e0; border-radius: 2px; height: 6px; overflow: hidden;">
                    <div style="background: {config['cor']}; width: {pct}%; height: 100%;"></div>
                </div>
            </div>
            '''
        
        # Gerar lista por ano
        anos_html = ""
        for ano, qtd in sorted(por_ano.items()):
            anos_html += f'''
            <div style="display: flex; justify-content: space-between; font-size: 11px; padding: 4px 0; border-bottom: 1px solid #f5f5f5;">
                <span style="color: #424242;">{int(ano)}</span>
                <span style="font-weight: 600; color: #2E7D32;">{qtd}</span>
            </div>
            '''
        
        painel_html = f'''
        <div id="stats-panel" style="
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
            background: white;
            padding: 16px 18px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            width: 200px;
            border-top: 3px solid #2E7D32;
        ">
            <!-- Header -->
            <div style="
                padding-bottom: 12px;
                border-bottom: 1px solid #eee;
                margin-bottom: 14px;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <img src="data:image/png;base64,{logo_base64}" 
                     alt="IPAAM" 
                     style="width: 40px; height: 40px; object-fit: contain;">
                <div>
                    <div style="font-weight: 700; font-size: 14px; color: #2E7D32;">IPAAM GECF Maps</div>
                    <div style="font-size: 10px; color: #757575; margin-top: 2px;">
                        Licenciamento e Controle Florestal
                    </div>
                </div>
            </div>
            
            <!-- Números -->
            <div style="display: flex; gap: 15px; margin-bottom: 16px;">
                <div style="flex: 1; text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #2E7D32;">{total}</div>
                    <div style="font-size: 9px; color: #757575; text-transform: uppercase;">Licenças</div>
                </div>
                <div style="flex: 1; text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #1565C0;">{municipios}</div>
                    <div style="font-size: 9px; color: #757575; text-transform: uppercase;">Municípios</div>
                </div>
            </div>
            
            <!-- Por Categoria -->
            <div style="margin-bottom: 16px;">
                <div style="font-size: 10px; color: #9e9e9e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">
                    Por Categoria
                </div>
                {barras_html}
            </div>
            
            <!-- Por Ano -->
            <div style="margin-bottom: 16px;">
                <div style="font-size: 10px; color: #9e9e9e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">
                    Por Ano
                </div>
                {anos_html}
                <div style="font-size: 9px; color: #bdbdbd; margin-top: 6px; font-style: italic;">
                    Use o controle de camadas para filtrar
                </div>
            </div>
            
            <!-- Legenda Licenças -->
            <div style="
                padding-top: 12px;
                border-top: 1px solid #eee;
            ">
                <div style="font-size: 10px; color: #9e9e9e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                    Tipo de Licença
                </div>
                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                    <span style="background: #FBC02D; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: 600;">LP</span>
                    <span style="background: #FF8F00; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: 600;">LI</span>
                    <span style="background: #43A047; color: white; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: 600;">LO</span>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="
                margin-top: 14px;
                padding-top: 10px;
                border-top: 1px solid #eee;
                font-size: 9px;
                color: #bdbdbd;
                text-align: center;
            ">
                Dados: GECF - 2025<br>
                <a href="https://www.ipaam.am.gov.br" target="_blank" style="color: #2E7D32; text-decoration: none;">ipaam.am.gov.br</a>
            </div>
        </div>
        '''
        
        self.mapa.get_root().html.add_child(folium.Element(painel_html))
        print("[OK] Painel de estatísticas")
        return self.mapa
    
    def adicionar_painel_municipios(self) -> folium.Map:
        """Adiciona painel lateral com lista de municípios."""
        if self.mapa is None:
            self.criar_mapa()
        
        # Contagem por município
        por_municipio = self.df.groupby('municipio').agg({
            'razao_social': 'count',
            'categoria': lambda x: ', '.join(x.unique())
        }).reset_index()
        por_municipio.columns = ['municipio', 'qtd', 'categorias']
        por_municipio = por_municipio.sort_values('qtd', ascending=False)
        
        # Gerar lista de municípios
        lista_html = ""
        for _, row in por_municipio.iterrows():
            lista_html += f'''
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
            ">
                <div>
                    <div style="font-size: 12px; font-weight: 500; color: #333;">{row['municipio']}</div>
                    <div style="font-size: 9px; color: #999; margin-top: 2px;">{row['categorias'][:30]}</div>
                </div>
                <div style="
                    background: #2E7D32;
                    color: white;
                    font-size: 11px;
                    font-weight: 600;
                    padding: 2px 8px;
                    border-radius: 10px;
                    min-width: 20px;
                    text-align: center;
                ">{row['qtd']}</div>
            </div>
            '''
        
        painel_municipios_html = f'''
        <div id="municipios-panel" style="
            position: fixed;
            top: 10px;
            left: 50px;
            z-index: 999;
            background: white;
            padding: 0;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            width: 220px;
            max-height: 80vh;
            display: none;
        ">
            <!-- Header -->
            <div style="
                padding: 12px 14px;
                background: #2E7D32;
                color: white;
                border-radius: 8px 8px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div>
                    <div style="font-weight: 600; font-size: 13px;">Municípios</div>
                    <div style="font-size: 10px; opacity: 0.8;">{len(por_municipio)} municípios</div>
                </div>
                <button onclick="document.getElementById('municipios-panel').style.display='none'" style="
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 0;
                    line-height: 1;
                ">×</button>
            </div>
            
            <!-- Lista -->
            <div style="
                padding: 10px 14px;
                max-height: 60vh;
                overflow-y: auto;
            ">
                {lista_html}
            </div>
        </div>
        
        <!-- Botão para abrir painel de municípios -->
        <button onclick="
            var p = document.getElementById('municipios-panel');
            p.style.display = p.style.display === 'none' ? 'block' : 'none';
        " style="
            position: fixed;
            bottom: 30px;
            right: 10px;
            z-index: 1000;
            background: #2E7D32;
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 6px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        ">
            Municípios
        </button>
        '''
        
        self.mapa.get_root().html.add_child(folium.Element(painel_municipios_html))
        print("[OK] Painel de municípios")
        return self.mapa
    
    def adicionar_exportar_imagem(self) -> folium.Map:
        """Adiciona funcionalidade para exportar imagem do mapa por município."""
        if self.mapa is None:
            self.criar_mapa()
        
        # Criar dados dos municípios com coordenadas médias
        municipios_coords = self.df.groupby('municipio').agg({
            'latitude': 'mean',
            'longitude': 'mean',
            'razao_social': 'count'
        }).reset_index()
        municipios_coords.columns = ['municipio', 'lat', 'lng', 'qtd']
        
        # Gerar options do select
        options_html = '<option value="">-- Selecione um município --</option>'
        for _, row in municipios_coords.sort_values('municipio').iterrows():
            options_html += f'<option value="{row["lat"]},{row["lng"]}" data-nome="{row["municipio"]}">{row["municipio"]} ({int(row["qtd"])})</option>'
        
        # Gerar dados JSON para JavaScript
        municipios_json = municipios_coords.to_json(orient='records')
        
        exportar_html = f'''
        <!-- Biblioteca html2canvas para captura de tela -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        
        <!-- Painel de Exportação -->
        <div id="export-panel" style="
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            background: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.2);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            gap: 10px;
            align-items: center;
        ">
            <select id="municipio-select" style="
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                min-width: 200px;
                cursor: pointer;
            ">
                {options_html}
            </select>
            
            <button id="zoom-btn" onclick="zoomMunicipio()" style="
                background: #1565C0;
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
            ">
                Ir
            </button>
            
            <button id="capture-btn" onclick="capturarImagem()" style="
                background: #2E7D32;
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
            ">
                Capturar Imagem
            </button>
            
            <button onclick="voltarVisaoGeral()" style="
                background: #757575;
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: 4px;
                font-size: 12px;
                cursor: pointer;
            ">
                Visão Geral
            </button>
        </div>
        
        <script>
            // Referência ao mapa (Folium cria uma variável global)
            var mapElement = document.querySelector('.folium-map');
            var mapId = mapElement ? mapElement.id : null;
            
            function getMap() {{
                // Procura o objeto mapa do Leaflet
                for (var key in window) {{
                    if (window[key] && window[key]._leaflet_id && window[key].getCenter) {{
                        return window[key];
                    }}
                }}
                return null;
            }}
            
            function zoomMunicipio() {{
                var select = document.getElementById('municipio-select');
                var coords = select.value;
                if (!coords) {{
                    alert('Selecione um município');
                    return;
                }}
                
                var parts = coords.split(',');
                var lat = parseFloat(parts[0]);
                var lng = parseFloat(parts[1]);
                
                var map = getMap();
                if (map) {{
                    map.setView([lat, lng], 12);
                }}
            }}
            
            function voltarVisaoGeral() {{
                var map = getMap();
                if (map) {{
                    map.setView([-3.4168, -65.8561], 6);
                }}
            }}
            
            function capturarImagem() {{
                var select = document.getElementById('municipio-select');
                var nomeMunicipio = select.options[select.selectedIndex].dataset.nome || 'mapa';
                
                // Esconder painéis temporariamente
                var paineis = document.querySelectorAll('#stats-panel, #municipios-panel, #export-panel, .leaflet-control-container');
                paineis.forEach(function(p) {{ 
                    p.dataset.originalDisplay = p.style.display;
                    p.style.display = 'none'; 
                }});
                
                // Capturar após pequeno delay
                setTimeout(function() {{
                    var mapContainer = document.querySelector('.folium-map');
                    
                    html2canvas(mapContainer, {{
                        useCORS: true,
                        allowTaint: true,
                        scale: 2,
                        logging: false
                    }}).then(function(canvas) {{
                        // Restaurar painéis
                        paineis.forEach(function(p) {{ 
                            p.style.display = p.dataset.originalDisplay || '';
                        }});
                        
                        // Download da imagem
                        var link = document.createElement('a');
                        var dataAtual = new Date().toISOString().split('T')[0];
                        link.download = 'IPAAM_GECF_' + nomeMunicipio.replace(/\\s+/g, '_') + '_' + dataAtual + '.png';
                        link.href = canvas.toDataURL('image/png');
                        link.click();
                    }}).catch(function(err) {{
                        console.error('Erro ao capturar:', err);
                        alert('Erro ao capturar imagem. Tente novamente.');
                        paineis.forEach(function(p) {{ 
                            p.style.display = p.dataset.originalDisplay || '';
                        }});
                    }});
                }}, 500);
            }}
        </script>
        '''
        
        self.mapa.get_root().html.add_child(folium.Element(exportar_html))
        print("[OK] Exportar imagem")
        return self.mapa
    
    def adicionar_dark_mode(self) -> folium.Map:
        """Adiciona toggle para modo escuro."""
        if self.mapa is None:
            self.criar_mapa()
        
        dark_mode_html = '''
        <style>
            /* Estilos Dark Mode */
            .dark-mode #stats-panel,
            .dark-mode #municipios-panel,
            .dark-mode #export-panel,
            .dark-mode .legenda-box {
                background: #1e1e1e !important;
                color: #e0e0e0 !important;
                border-color: #333 !important;
            }
            
            .dark-mode #stats-panel *,
            .dark-mode #municipios-panel *,
            .dark-mode .legenda-box * {
                color: #e0e0e0 !important;
            }
            
            .dark-mode #stats-panel a,
            .dark-mode .dark-mode-text-green {
                color: #66BB6A !important;
            }
            
            .dark-mode #municipios-panel > div:first-child {
                background: #2E7D32 !important;
            }
            
            .dark-mode select {
                background: #333 !important;
                color: #e0e0e0 !important;
                border-color: #555 !important;
            }
            
            .dark-mode .leaflet-popup-content-wrapper,
            .dark-mode .leaflet-popup-tip {
                background: #2d2d2d !important;
                color: #e0e0e0 !important;
            }
            
            .dark-mode .leaflet-popup-content-wrapper * {
                color: #e0e0e0 !important;
            }
            
            .dark-mode .leaflet-control-layers {
                background: #1e1e1e !important;
                color: #e0e0e0 !important;
            }
            
            .dark-mode .leaflet-control-layers label {
                color: #e0e0e0 !important;
            }
        </style>
        
        <!-- Botão Dark Mode -->
        <button id="dark-mode-toggle" onclick="toggleDarkMode()" style="
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1001;
            background: #424242;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 6px;
        ">
            <span id="dark-icon">[D]</span>
            <span id="dark-text">Modo Escuro</span>
        </button>
        
        <script>
            var isDarkMode = false;
            var darkTileLayer = null;
            var lightTileLayer = null;
            
            function toggleDarkMode() {
                isDarkMode = !isDarkMode;
                var body = document.body;
                var btn = document.getElementById('dark-mode-toggle');
                var icon = document.getElementById('dark-icon');
                var text = document.getElementById('dark-text');
                var map = getMap();
                
                if (isDarkMode) {
                    body.classList.add('dark-mode');
                    icon.textContent = '[L]';
                    text.textContent = 'Modo Claro';
                    btn.style.background = '#66BB6A';
                    
                    // Trocar para tile escuro
                    if (map) {
                        // Remove tile claro e adiciona escuro
                        map.eachLayer(function(layer) {
                            if (layer._url) {
                                if (layer._url.includes('light_all') || layer._url.includes('openstreetmap')) {
                                    lightTileLayer = layer;
                                    map.removeLayer(layer);
                                }
                            }
                        });
                        
                        // Adiciona tile escuro
                        if (!darkTileLayer) {
                            darkTileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                                attribution: 'CartoDB Dark'
                            });
                        }
                        darkTileLayer.addTo(map);
                        darkTileLayer.bringToBack();
                    }
                } else {
                    body.classList.remove('dark-mode');
                    icon.textContent = '[D]';
                    text.textContent = 'Modo Escuro';
                    btn.style.background = '#424242';
                    
                    // Voltar para tile claro
                    if (map) {
                        // Remove tile escuro
                        if (darkTileLayer) {
                            map.removeLayer(darkTileLayer);
                        }
                        
                        // Adiciona tile claro
                        if (!lightTileLayer) {
                            lightTileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                                attribution: 'CartoDB Light'
                            });
                        }
                        lightTileLayer.addTo(map);
                        lightTileLayer.bringToBack();
                    }
                }
            }
        </script>
        '''
        
        self.mapa.get_root().html.add_child(folium.Element(dark_mode_html))
        print("[OK] Dark mode")
        return self.mapa
    
    def adicionar_legenda_mapa(self) -> folium.Map:
        """Adiciona legenda no mapa."""
        if self.mapa is None:
            self.criar_mapa()
        
        itens_html = ""
        for cat, config in self.CATEGORIAS.items():
            if cat != 'Outros':
                itens_html += f'''
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 10px; height: 10px; background: {config['cor']}; border-radius: 50%; margin-right: 8px; border: 1px solid white; box-shadow: 0 1px 2px rgba(0,0,0,0.2);"></div>
                    <span style="font-size: 11px; color: #424242;">{cat}</span>
                </div>
                '''
        
        legenda_html = f'''
        <div style="
            position: fixed;
            bottom: 30px;
            left: 10px;
            z-index: 1000;
            background: white;
            padding: 10px 14px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="font-size: 10px; color: #9e9e9e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                Legenda
            </div>
            {itens_html}
        </div>
        '''
        
        self.mapa.get_root().html.add_child(folium.Element(legenda_html))
        print("[OK] Legenda do mapa")
        return self.mapa
    
    def adicionar_controles(self) -> folium.Map:
        """Adiciona controles essenciais."""
        if self.mapa is None:
            self.criar_mapa()
        
        Fullscreen(position='topleft').add_to(self.mapa)
        
        MiniMap(
            toggle_display=True,
            position='bottomright',
            width=120,
            height=100
        ).add_to(self.mapa)
        
        folium.LayerControl(position='topleft', collapsed=True).add_to(self.mapa)
        
        print("[OK] Controles do mapa")
        return self.mapa
    
    def gerar_mapa(self, caminho_saida: str = None) -> folium.Map:
        """Gera o mapa completo profissional."""
        print("\n" + "="*50)
        print("  MAPA PROFISSIONAL IPAAM")
        print("="*50)
        
        self.criar_mapa()
        self.adicionar_marcadores()
        self.adicionar_painel_estatisticas()
        self.adicionar_painel_municipios()
        self.adicionar_exportar_imagem()
        self.adicionar_dark_mode()
        self.adicionar_legenda_mapa()
        self.adicionar_controles()
        
        if caminho_saida:
            self.mapa.save(caminho_saida)
            print(f"\n[SALVO] {caminho_saida}")
        
        print("="*50)
        print("  CONCLUIDO")
        print("="*50 + "\n")
        
        return self.mapa


if __name__ == "__main__":
    import os
    
    pasta_dados = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados')
    arquivo = os.path.join(pasta_dados, 'licencas_ipaam_unificado.csv')
    
    if os.path.exists(arquivo):
        df = pd.read_csv(arquivo)
        
        pasta_output = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        os.makedirs(pasta_output, exist_ok=True)
        
        gerador = GeradorMapaProfissional(df)
        mapa = gerador.gerar_mapa(
            caminho_saida=os.path.join(pasta_output, 'ipaam_gecf_maps.html')
        )
    else:
        print(f"Arquivo nao encontrado: {arquivo}")
