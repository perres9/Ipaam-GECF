"""
IPAAM - Mapa Premium
====================
Mapa interativo com design moderno, limpo e profissional.

Características:
- Layout responsivo e alinhado
- Sidebar colapsável
- Filtros dinâmicos
- Marcadores modernos com animação
- Popups elegantes
- Controles intuitivos
- Dark mode suave

Autor: Engenheiro de Dados GIS
Versão: 4.0.0
"""

import folium
from folium import plugins
from folium.plugins import MarkerCluster, Fullscreen, MiniMap
import pandas as pd
import os


class GeradorMapaPremium:
    """Gerador de mapa premium para IPAAM com design moderno."""
    
    CENTRO_AMAZONAS = [-3.4168, -65.8561]
    ZOOM_INICIAL = 6
    
    # Paleta de cores moderna
    CORES = {
        'primary': '#006B3F',      # Verde IPAAM
        'secondary': '#00A367',    # Verde claro
        'accent': '#FFB700',       # Amarelo dourado
        'dark': '#1A1A2E',         # Fundo escuro
        'light': '#F8F9FA',        # Fundo claro
        'text': '#2D3748',         # Texto principal
        'muted': '#718096',        # Texto secundário
    }
    
    # Categorias com cores harmoniosas
    CATEGORIAS = {
        'Manejo Florestal': {
            'cor': '#059669',      # Esmeralda
            'cor_clara': '#D1FAE5',
            'icone': 'leaf'
        },
        'Indústria Madeireira': {
            'cor': '#D97706',      # Âmbar
            'cor_clara': '#FEF3C7',
            'icone': 'industry'
        },
        'Indústria Mobiliária': {
            'cor': '#2563EB',      # Azul
            'cor_clara': '#DBEAFE',
            'icone': 'couch'
        },
        'Outros': {
            'cor': '#64748B',      # Cinza
            'cor_clara': '#F1F5F9',
            'icone': 'circle'
        }
    }
    
    LICENCAS = {
        'LP': {'cor': '#FBBF24', 'nome': 'Licença Prévia', 'desc': 'Fase inicial'},
        'LI': {'cor': '#F59E0B', 'nome': 'Licença de Instalação', 'desc': 'Em instalação'},
        'LO': {'cor': '#10B981', 'nome': 'Licença de Operação', 'desc': 'Em operação'}
    }
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o gerador de mapa premium."""
        self.df = df.copy()
        self.df = self.df.dropna(subset=['latitude', 'longitude'])
        self.mapa = None
        self._calcular_estatisticas()
        print(f"[PREMIUM] {len(self.df)} registros carregados")
    
    def _calcular_estatisticas(self):
        """Pré-calcula estatísticas para uso nos painéis."""
        self.stats = {
            'total': len(self.df),
            'municipios': self.df['municipio'].nunique(),
            'por_categoria': self.df['categoria'].value_counts().to_dict(),
            'por_ano': self.df['ano'].value_counts().sort_index().to_dict(),
            'top_municipios': self.df['municipio'].value_counts().head(10).to_dict()
        }
    
    def _criar_estilo_global(self) -> str:
        """Retorna CSS global para o mapa."""
        return f'''
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            :root {{
                --primary: {self.CORES['primary']};
                --secondary: {self.CORES['secondary']};
                --accent: {self.CORES['accent']};
                --dark: {self.CORES['dark']};
                --light: {self.CORES['light']};
                --text: {self.CORES['text']};
                --muted: {self.CORES['muted']};
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            
            /* Sidebar */
            .ipaam-sidebar {{
                position: fixed;
                top: 0;
                right: 0;
                width: 320px;
                height: 100vh;
                background: white;
                box-shadow: -4px 0 20px rgba(0,0,0,0.1);
                z-index: 1000;
                display: flex;
                flex-direction: column;
                transition: transform 0.3s ease;
            }}
            
            .ipaam-sidebar.collapsed {{
                transform: translateX(280px);
            }}
            
            .ipaam-sidebar-toggle {{
                position: absolute;
                left: -40px;
                top: 50%;
                transform: translateY(-50%);
                width: 40px;
                height: 48px;
                background: white;
                border: none;
                border-radius: 8px 0 0 8px;
                box-shadow: -4px 0 10px rgba(0,0,0,0.1);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                color: var(--text);
                transition: all 0.2s;
            }}
            
            .ipaam-sidebar-toggle:hover {{
                background: var(--light);
            }}
            
            .ipaam-sidebar-header {{
                padding: 20px;
                background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                color: white;
            }}
            
            .ipaam-logo-area {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 12px;
            }}
            
            .ipaam-logo {{
                width: 48px;
                height: 48px;
                background: white;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                color: var(--primary);
                font-size: 14px;
            }}
            
            .ipaam-title {{
                font-size: 18px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
            
            .ipaam-subtitle {{
                font-size: 12px;
                opacity: 0.85;
                margin-top: 2px;
            }}
            
            .ipaam-sidebar-content {{
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }}
            
            .ipaam-stats-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin-bottom: 24px;
            }}
            
            .ipaam-stat-card {{
                background: var(--light);
                padding: 16px;
                border-radius: 12px;
                text-align: center;
            }}
            
            .ipaam-stat-value {{
                font-size: 28px;
                font-weight: 700;
                color: var(--primary);
                line-height: 1;
            }}
            
            .ipaam-stat-label {{
                font-size: 11px;
                color: var(--muted);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 6px;
            }}
            
            .ipaam-section {{
                margin-bottom: 24px;
            }}
            
            .ipaam-section-title {{
                font-size: 11px;
                font-weight: 600;
                color: var(--muted);
                text-transform: uppercase;
                letter-spacing: 0.8px;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .ipaam-section-title::after {{
                content: '';
                flex: 1;
                height: 1px;
                background: #E2E8F0;
            }}
            
            .ipaam-category-list {{
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}
            
            .ipaam-category-item {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .ipaam-category-dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
                flex-shrink: 0;
            }}
            
            .ipaam-category-info {{
                flex: 1;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .ipaam-category-name {{
                font-size: 13px;
                color: var(--text);
            }}
            
            .ipaam-category-count {{
                font-size: 13px;
                font-weight: 600;
                color: var(--primary);
            }}
            
            .ipaam-category-bar {{
                height: 4px;
                background: #E2E8F0;
                border-radius: 2px;
                overflow: hidden;
                margin-top: 4px;
            }}
            
            .ipaam-category-fill {{
                height: 100%;
                border-radius: 2px;
                transition: width 0.3s ease;
            }}
            
            .ipaam-year-list {{
                display: flex;
                flex-direction: column;
                gap: 6px;
            }}
            
            .ipaam-year-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 12px;
                background: var(--light);
                border-radius: 8px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.2s;
            }}
            
            .ipaam-year-item:hover {{
                background: #E2E8F0;
            }}
            
            .ipaam-year-item.active {{
                background: var(--primary);
                color: white;
            }}
            
            .ipaam-year-count {{
                font-weight: 600;
            }}
            
            .ipaam-license-types {{
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }}
            
            .ipaam-license-badge {{
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }}
            
            .ipaam-license-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
            }}
            
            .ipaam-sidebar-footer {{
                padding: 16px 20px;
                border-top: 1px solid #E2E8F0;
                font-size: 11px;
                color: var(--muted);
                text-align: center;
            }}
            
            .ipaam-sidebar-footer a {{
                color: var(--primary);
                text-decoration: none;
                font-weight: 500;
            }}
            
            /* Legenda flutuante */
            .ipaam-legend {{
                position: fixed;
                bottom: 24px;
                left: 24px;
                background: white;
                padding: 16px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.12);
                z-index: 999;
            }}
            
            .ipaam-legend-title {{
                font-size: 11px;
                font-weight: 600;
                color: var(--muted);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 10px;
            }}
            
            .ipaam-legend-items {{
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            
            .ipaam-legend-item {{
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 12px;
                color: var(--text);
            }}
            
            .ipaam-legend-dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            }}
            
            /* Controls personalizados */
            .ipaam-controls {{
                position: fixed;
                top: 24px;
                left: 24px;
                display: flex;
                flex-direction: column;
                gap: 8px;
                z-index: 999;
            }}
            
            /* Controles nativos do Leaflet - reposicionar */
            .leaflet-top.leaflet-left {{
                top: 180px !important;
                left: 10px !important;
            }}
            
            .leaflet-control-zoom {{
                border: none !important;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
                border-radius: 10px !important;
                overflow: hidden;
            }}
            
            .leaflet-control-zoom a {{
                width: 36px !important;
                height: 36px !important;
                line-height: 36px !important;
                font-size: 18px !important;
                border: none !important;
                color: var(--text) !important;
            }}
            
            .leaflet-control-zoom a:hover {{
                background: var(--light) !important;
            }}
            
            .leaflet-control-layers {{
                border: none !important;
                border-radius: 10px !important;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
            }}
            
            .leaflet-control-fullscreen {{
                border: none !important;
                border-radius: 10px !important;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
            }}
            
            .leaflet-control-fullscreen a {{
                width: 36px !important;
                height: 36px !important;
                line-height: 36px !important;
                border-radius: 10px !important;
            }}
            
            /* Seletor de Municípios */
            .ipaam-municipio-selector {{
                position: fixed;
                bottom: 24px;
                left: 50%;
                transform: translateX(-50%);
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                padding: 12px 16px;
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 12px;
                max-width: 90%;
            }}
            
            .ipaam-municipio-selector label {{
                font-weight: 600;
                color: var(--text);
                white-space: nowrap;
                font-size: 14px;
            }}
            
            .ipaam-municipio-selector select {{
                padding: 8px 32px 8px 12px;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                font-size: 14px;
                color: var(--text);
                background: white;
                cursor: pointer;
                min-width: 200px;
                appearance: none;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%232D3748' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10l-5 5z'/%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: right 10px center;
            }}
            
            .ipaam-municipio-selector select:focus {{
                outline: none;
                border-color: var(--primary);
            }}
            
            .ipaam-municipio-btn {{
                padding: 8px 16px;
                background: var(--primary);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
            }}
            
            .ipaam-municipio-btn:hover {{
                background: var(--secondary);
                transform: scale(1.02);
            }}
            
            body.dark-mode .ipaam-municipio-selector {{
                background: #16213E;
            }}
            
            body.dark-mode .ipaam-municipio-selector label {{
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-municipio-selector select {{
                background-color: #1F2937;
                border-color: #374151;
                color: #FFFFFF;
                -webkit-appearance: none;
                -moz-appearance: none;
                appearance: none;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%23FFFFFF' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10l-5 5z'/%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: right 10px center;
            }}
            
            body.dark-mode .ipaam-municipio-selector select option {{
                background-color: #1F2937;
                color: #FFFFFF;
            }}
            
            body.dark-mode .leaflet-control-zoom a,
            body.dark-mode .leaflet-control-layers {{
                background: #1F2937 !important;
                color: #FFFFFF !important;
            }}
            
            body.dark-mode .leaflet-control-zoom {{
                background: #1F2937 !important;
            }}
            
            body.dark-mode .leaflet-control-layers-base label {{
                color: #FFFFFF !important;
            }}
            
            .ipaam-control-btn {{
                width: 44px;
                height: 44px;
                background: white;
                border: none;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                color: var(--text);
                transition: all 0.2s;
            }}
            
            .ipaam-control-btn:hover {{
                background: var(--light);
                transform: scale(1.05);
            }}
            
            /* Popup moderno */
            .leaflet-popup-content-wrapper {{
                border-radius: 12px;
                padding: 0;
                box-shadow: 0 10px 40px rgba(0,0,0,0.15);
                overflow: hidden;
            }}
            
            .leaflet-popup-content {{
                margin: 0;
                width: 280px !important;
            }}
            
            .leaflet-popup-tip {{
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            
            .ipaam-popup {{
                font-family: 'Inter', sans-serif;
            }}
            
            .ipaam-popup-header {{
                padding: 16px;
                color: white;
            }}
            
            .ipaam-popup-category {{
                font-size: 11px;
                opacity: 0.9;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .ipaam-popup-title {{
                font-size: 15px;
                font-weight: 600;
                margin-top: 4px;
                line-height: 1.3;
            }}
            
            .ipaam-popup-body {{
                padding: 16px;
            }}
            
            .ipaam-popup-row {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #F1F5F9;
                font-size: 13px;
            }}
            
            .ipaam-popup-row:last-child {{
                border-bottom: none;
            }}
            
            .ipaam-popup-label {{
                color: var(--muted);
            }}
            
            .ipaam-popup-value {{
                font-weight: 500;
                color: var(--text);
            }}
            
            .ipaam-popup-badge {{
                display: inline-block;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
            }}
            
            .ipaam-popup-activity {{
                margin-top: 12px;
                padding: 12px;
                background: var(--light);
                border-radius: 8px;
                font-size: 12px;
                color: var(--muted);
                line-height: 1.5;
            }}
            
            .ipaam-popup-footer {{
                padding: 12px 16px;
                background: var(--light);
                font-size: 11px;
                color: var(--muted);
                display: flex;
                justify-content: space-between;
            }}
            
            /* Marker styling */
            .ipaam-marker {{
                transition: transform 0.2s ease;
            }}
            
            .ipaam-marker:hover {{
                transform: scale(1.2);
            }}
            
            /* Custom cluster */
            .marker-cluster {{
                background: transparent !important;
            }}
            
            .ipaam-cluster {{
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                font-weight: 600;
                font-size: 13px;
                color: white;
                border: 3px solid white;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            }}
            
            /* Dark mode */
            body.dark-mode {{
                background: var(--dark);
            }}
            
            body.dark-mode .ipaam-sidebar {{
                background: #16213E;
            }}
            
            body.dark-mode .ipaam-sidebar-content {{
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-stat-card {{
                background: #1F2937;
            }}
            
            body.dark-mode .ipaam-stat-value {{
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-stat-label,
            body.dark-mode .ipaam-category-name {{
                color: #CBD5E1;
            }}
            
            body.dark-mode .ipaam-section-title {{
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-category-count {{
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-year-item {{
                background: #1F2937;
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-year-count {{
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-legend {{
                background: #16213E;
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-legend-title {{
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-legend-label {{
                color: #CBD5E1;
            }}
            
            body.dark-mode .ipaam-control-btn {{
                background: #1F2937;
                color: #FFFFFF;
            }}
            
            body.dark-mode .leaflet-popup-content-wrapper {{
                background: #16213E;
            }}
            
            body.dark-mode .ipaam-popup-title {{
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-popup-body,
            body.dark-mode .ipaam-popup-row {{
                color: #FFFFFF;
                border-color: #374151;
            }}
            
            body.dark-mode .ipaam-popup-label {{
                color: #CBD5E1;
            }}
            
            body.dark-mode .ipaam-popup-value {{
                color: #FFFFFF;
            }}
            
            body.dark-mode .ipaam-popup-activity,
            body.dark-mode .ipaam-popup-footer {{
                background: #1F2937;
                color: #CBD5E1;
            }}
            
            body.dark-mode .ipaam-sidebar-footer {{
                color: #CBD5E1;
            }}
            
            body.dark-mode .ipaam-sidebar-footer a {{
                color: #60A5FA;
            }}
            
            /* Animações */
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            
            .loading {{
                animation: pulse 1.5s ease-in-out infinite;
            }}
            
            /* Responsivo */
            @media (max-width: 768px) {{
                .ipaam-sidebar {{
                    width: 280px;
                }}
                
                .ipaam-sidebar.collapsed {{
                    transform: translateX(240px);
                }}
                
                .ipaam-legend {{
                    bottom: 16px;
                    left: 16px;
                    padding: 12px;
                }}
            }}
        </style>
        '''
    
    def _criar_sidebar_html(self) -> str:
        """Cria HTML da sidebar com estatísticas."""
        
        # Carregar logo base64
        logo_base64 = ""
        try:
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo_base64.txt')
            with open(logo_path, 'r') as f:
                logo_base64 = f.read().strip()
        except:
            logo_base64 = ""
        
        # Categorias
        categorias_html = ""
        for cat, qtd in self.stats['por_categoria'].items():
            config = self.CATEGORIAS.get(cat, self.CATEGORIAS['Outros'])
            pct = (qtd / self.stats['total']) * 100
            categorias_html += f'''
            <div class="ipaam-category-item">
                <div class="ipaam-category-dot" style="background: {config['cor']};"></div>
                <div style="flex: 1;">
                    <div class="ipaam-category-info">
                        <span class="ipaam-category-name">{cat}</span>
                        <span class="ipaam-category-count">{qtd}</span>
                    </div>
                    <div class="ipaam-category-bar">
                        <div class="ipaam-category-fill" style="width: {pct}%; background: {config['cor']};"></div>
                    </div>
                </div>
            </div>
            '''
        
        # Anos
        anos_html = ""
        for ano, qtd in sorted(self.stats['por_ano'].items(), reverse=True):
            anos_html += f'''
            <div class="ipaam-year-item" data-ano="{int(ano)}" onclick="filtrarAno({int(ano)})">
                <span>{int(ano)}</span>
                <span class="ipaam-year-count">{qtd}</span>
            </div>
            '''
        
        # Licenças
        licencas_html = ""
        for tipo, info in self.LICENCAS.items():
            licencas_html += f'''
            <div class="ipaam-license-badge" style="background: {info['cor']}20;">
                <div class="ipaam-license-dot" style="background: {info['cor']};"></div>
                <span style="color: {info['cor']};">{tipo}</span>
            </div>
            '''
        
        return f'''
        <div class="ipaam-sidebar" id="sidebar">
            <button class="ipaam-sidebar-toggle" id="sidebar-toggle" onclick="toggleSidebar()">
                ◀
            </button>
            
            <div class="ipaam-sidebar-header">
                <div class="ipaam-logo-area">
                    <div class="ipaam-logo"><img src="data:image/png;base64,{logo_base64}" alt="IPAAM" style="width: 100%; height: 100%; object-fit: contain;"></div>
                    <div>
                        <div class="ipaam-title">GECF Maps</div>
                        <div class="ipaam-subtitle">Controle Florestal</div>
                    </div>
                </div>
            </div>
            
            <div class="ipaam-sidebar-content">
                <div class="ipaam-stats-grid">
                    <div class="ipaam-stat-card">
                        <div class="ipaam-stat-value">{self.stats['total']}</div>
                        <div class="ipaam-stat-label">Licenças</div>
                    </div>
                    <div class="ipaam-stat-card">
                        <div class="ipaam-stat-value">{self.stats['municipios']}</div>
                        <div class="ipaam-stat-label">Municípios</div>
                    </div>
                </div>
                
                <div class="ipaam-section">
                    <div class="ipaam-section-title">Por Categoria</div>
                    <div class="ipaam-category-list">
                        {categorias_html}
                    </div>
                </div>
                
                <div class="ipaam-section">
                    <div class="ipaam-section-title">Por Ano</div>
                    <div class="ipaam-year-list">
                        {anos_html}
                    </div>
                </div>
                
                <div class="ipaam-section">
                    <div class="ipaam-section-title">Tipo de Licença</div>
                    <div class="ipaam-license-types">
                        {licencas_html}
                    </div>
                </div>
            </div>
            
            <div class="ipaam-sidebar-footer">
                Dados: GECF/IPAAM 2025<br>
                <a href="https://www.ipaam.am.gov.br" target="_blank">ipaam.am.gov.br</a>
            </div>
        </div>
        '''
    
    def _criar_legenda_html(self) -> str:
        """Cria HTML da legenda flutuante."""
        items_html = ""
        for cat, config in self.CATEGORIAS.items():
            if cat != 'Outros':
                items_html += f'''
                <div class="ipaam-legend-item">
                    <div class="ipaam-legend-dot" style="background: {config['cor']};"></div>
                    <span>{cat}</span>
                </div>
                '''
        
        return f'''
        <div class="ipaam-legend">
            <div class="ipaam-legend-title">Categorias</div>
            <div class="ipaam-legend-items">
                {items_html}
            </div>
        </div>
        '''
    
    def _criar_popup_html(self, row: pd.Series) -> str:
        """Cria HTML moderno do popup."""
        categoria = row.get('categoria', 'Outros')
        config = self.CATEGORIAS.get(categoria, self.CATEGORIAS['Outros'])
        tipo_lic = row.get('tipo_licenca', 'LO')
        info_lic = self.LICENCAS.get(tipo_lic, self.LICENCAS['LO'])
        
        data_emissao = str(row.get('data_emissao', '-'))[:10]
        data_validade = str(row.get('data_validade', '-'))[:10]
        razao_social = str(row.get('razao_social', 'N/A'))[:50]
        atividade = str(row.get('atividade', '-'))[:150]
        
        return f'''
        <div class="ipaam-popup">
            <div class="ipaam-popup-header" style="background: {config['cor']};">
                <div class="ipaam-popup-category">{categoria}</div>
                <div class="ipaam-popup-title">{razao_social}</div>
            </div>
            
            <div class="ipaam-popup-body">
                <div class="ipaam-popup-row">
                    <span class="ipaam-popup-label">Município</span>
                    <span class="ipaam-popup-value">{row.get('municipio', '-')}</span>
                </div>
                <div class="ipaam-popup-row">
                    <span class="ipaam-popup-label">Licença</span>
                    <span class="ipaam-popup-badge" style="background: {info_lic['cor']};">{tipo_lic}</span>
                </div>
                <div class="ipaam-popup-row">
                    <span class="ipaam-popup-label">Emissão</span>
                    <span class="ipaam-popup-value">{data_emissao}</span>
                </div>
                <div class="ipaam-popup-row">
                    <span class="ipaam-popup-label">Validade</span>
                    <span class="ipaam-popup-value">{data_validade}</span>
                </div>
                
                <div class="ipaam-popup-activity">
                    {atividade}...
                </div>
            </div>
            
            <div class="ipaam-popup-footer">
                <span>{row.get('gerencia', 'GECF')}</span>
                <span>{row.get('ano', '-')}</span>
            </div>
        </div>
        '''
    
    def _criar_marcador(self, categoria: str) -> folium.DivIcon:
        """Cria marcador visual moderno."""
        config = self.CATEGORIAS.get(categoria, self.CATEGORIAS['Outros'])
        
        html = f'''
        <div class="ipaam-marker" style="
            width: 14px;
            height: 14px;
            background: {config['cor']};
            border: 2.5px solid white;
            border-radius: 50%;
            box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        "></div>
        '''
        return folium.DivIcon(
            html=html,
            icon_size=(18, 18),
            icon_anchor=(9, 9)
        )
    
    def _criar_scripts(self) -> str:
        """Cria scripts JavaScript do mapa."""
        return '''
        <!-- Biblioteca html2canvas para captura de tela -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        
        <script>
            // Variáveis globais
            var mapaLeaflet = null;
            var clustersAno = {};
            var anoAtual = null;
            var isCapturing = false;
            
            // Encontrar o mapa Leaflet
            function getMap() {
                if (mapaLeaflet) return mapaLeaflet;
                for (var key in window) {
                    if (window[key] && window[key]._leaflet_id && window[key].getCenter) {
                        mapaLeaflet = window[key];
                        return mapaLeaflet;
                    }
                }
                return null;
            }
            
            // Toggle sidebar
            function toggleSidebar() {
                var sidebar = document.getElementById('sidebar');
                var toggle = document.getElementById('sidebar-toggle');
                sidebar.classList.toggle('collapsed');
                toggle.textContent = sidebar.classList.contains('collapsed') ? '▶' : '◀';
            }
            
            // Toggle dark mode
            function toggleDarkMode() {
                document.body.classList.toggle('dark-mode');
                var map = getMap();
                if (map) {
                    // Trocar tile layer
                    var isDark = document.body.classList.contains('dark-mode');
                    map.eachLayer(function(layer) {
                        if (layer._url && (layer._url.includes('light') || layer._url.includes('dark'))) {
                            map.removeLayer(layer);
                        }
                    });
                    
                    var tileUrl = isDark 
                        ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
                        : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
                    
                    L.tileLayer(tileUrl, {attribution: 'CartoDB'}).addTo(map).bringToBack();
                }
            }
            
            // Filtrar por ano
            function filtrarAno(ano) {
                // Atualizar UI
                document.querySelectorAll('.ipaam-year-item').forEach(function(el) {
                    el.classList.remove('active');
                    if (parseInt(el.dataset.ano) === ano) {
                        el.classList.add('active');
                    }
                });
                
                // Atualizar camadas (controlado pelo LayerControl do Folium)
                var map = getMap();
                if (map) {
                    // Focar no controle de camadas
                    console.log('Filtrar ano: ' + ano);
                }
            }
            
            // Zoom para localização
            function zoomTo(lat, lng, zoom) {
                var map = getMap();
                if (map) {
                    map.setView([lat, lng], zoom || 12);
                }
            }
            
            // Ir para município selecionado
            function irParaMunicipio() {
                var select = document.getElementById('municipio-select');
                var value = select.value;
                if (value) {
                    var coords = value.split(',');
                    var lat = parseFloat(coords[0]);
                    var lng = parseFloat(coords[1]);
                    zoomTo(lat, lng, 10);
                }
            }
            
            // Resetar visão
            function resetView() {
                var map = getMap();
                if (map) {
                    map.setView([-3.4168, -65.8561], 6);
                }
            }
            
            // Capturar/Print do mapa
            function printMap() {
                if (isCapturing) return;
                isCapturing = true;
                
                var btn = document.querySelector('.ipaam-print-btn');
                var originalText = btn.innerHTML;
                btn.innerHTML = '⏳';
                btn.style.opacity = '0.7';
                
                // Elementos a esconder durante captura
                var elementsToHide = [
                    '.ipaam-sidebar',
                    '.ipaam-controls',
                    '.ipaam-legend',
                    '.ipaam-municipio-selector',
                    '.leaflet-control-container'
                ];
                
                var hiddenElements = [];
                elementsToHide.forEach(function(selector) {
                    var el = document.querySelector(selector);
                    if (el) {
                        hiddenElements.push({el: el, display: el.style.display});
                        el.style.display = 'none';
                    }
                });
                
                // Pequeno delay para garantir que tudo foi escondido
                setTimeout(function() {
                    var mapContainer = document.querySelector('.folium-map');
                    
                    html2canvas(mapContainer, {
                        useCORS: true,
                        allowTaint: true,
                        scale: 2,
                        logging: false,
                        backgroundColor: null
                    }).then(function(canvas) {
                        // Restaurar elementos
                        hiddenElements.forEach(function(item) {
                            item.el.style.display = item.display || '';
                        });
                        
                        // Gerar nome do arquivo
                        var now = new Date();
                        var dateStr = now.toISOString().split('T')[0];
                        var timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-');
                        var filename = 'IPAAM_GECF_Mapa_' + dateStr + '_' + timeStr + '.png';
                        
                        // Download da imagem
                        var link = document.createElement('a');
                        link.download = filename;
                        link.href = canvas.toDataURL('image/png');
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        
                        // Restaurar botão
                        btn.innerHTML = originalText;
                        btn.style.opacity = '1';
                        isCapturing = false;
                        
                    }).catch(function(err) {
                        console.error('Erro ao capturar:', err);
                        
                        // Restaurar elementos
                        hiddenElements.forEach(function(item) {
                            item.el.style.display = item.display || '';
                        });
                        
                        // Restaurar botão
                        btn.innerHTML = originalText;
                        btn.style.opacity = '1';
                        isCapturing = false;
                        
                        alert('Erro ao capturar imagem. Tente novamente.');
                    });
                }, 300);
            }
            
            // Inicialização
            document.addEventListener('DOMContentLoaded', function() {
                // Ajustar mapa para não ficar atrás da sidebar
                setTimeout(function() {
                    var map = getMap();
                    if (map) {
                        map.invalidateSize();
                    }
                }, 500);
            });
        </script>
        '''
    
    def criar_mapa(self) -> folium.Map:
        """Cria o mapa base com tiles modernos."""
        self.mapa = folium.Map(
            location=self.CENTRO_AMAZONAS,
            zoom_start=self.ZOOM_INICIAL,
            control_scale=True,
            prefer_canvas=True,
            tiles=None
        )
        
        # Tile principal - limpo e moderno
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            attr='CartoDB Positron',
            name='Claro',
            overlay=False
        ).add_to(self.mapa)
        
        # Satélite
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='ESRI Satellite',
            name='Satélite',
            overlay=False
        ).add_to(self.mapa)
        
        # OpenStreetMap
        folium.TileLayer(
            tiles='openstreetmap',
            name='OpenStreetMap',
            overlay=False
        ).add_to(self.mapa)
        
        return self.mapa
    
    def adicionar_marcadores(self) -> folium.Map:
        """Adiciona marcadores agrupados por ano com clustering moderno."""
        if self.mapa is None:
            self.criar_mapa()
        
        anos = sorted(self.df['ano'].dropna().unique())
        ano_mais_recente = max(anos) if anos else 2025
        
        for ano in anos:
            ano_int = int(ano)
            
            cluster = MarkerCluster(
                name=f"📅 {ano_int}",
                overlay=True,
                control=True,
                show=(ano_int == ano_mais_recente),
                icon_create_function=f'''
                function(cluster) {{
                    var count = cluster.getChildCount();
                    var size = count < 10 ? 36 : count < 50 ? 44 : 52;
                    return L.divIcon({{
                        html: '<div class="ipaam-cluster" style="width:' + size + 'px;height:' + size + 'px;">' + count + '</div>',
                        className: 'marker-cluster',
                        iconSize: L.point(size, size)
                    }});
                }}
                '''
            )
            
            df_ano = self.df[self.df['ano'] == ano]
            
            for _, row in df_ano.iterrows():
                categoria = row.get('categoria', 'Outros')
                
                marcador = folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(self._criar_popup_html(row), max_width=300),
                    tooltip=f"<b>{row.get('razao_social', '')[:35]}</b><br>{row.get('municipio', '')}",
                    icon=self._criar_marcador(categoria)
                )
                marcador.add_to(cluster)
            
            cluster.add_to(self.mapa)
        
        print(f"[PREMIUM] {len(self.df)} marcadores em {len(anos)} anos")
        return self.mapa
    
    def adicionar_controles(self) -> folium.Map:
        """Adiciona controles do mapa."""
        if self.mapa is None:
            self.criar_mapa()
        
        Fullscreen(position='topleft').add_to(self.mapa)
        
        MiniMap(
            toggle_display=True,
            position='bottomright',
            width=150,
            height=120
        ).add_to(self.mapa)
        
        folium.LayerControl(position='topleft', collapsed=True).add_to(self.mapa)
        
        return self.mapa
    
    def gerar_mapa(self, caminho_saida: str = None) -> folium.Map:
        """Gera o mapa premium completo."""
        print("\n" + "═"*60)
        print("  IPAAM PREMIUM MAP")
        print("═"*60)
        
        self.criar_mapa()
        self.adicionar_marcadores()
        self.adicionar_controles()
        
        # Adicionar CSS global
        self.mapa.get_root().html.add_child(folium.Element(self._criar_estilo_global()))
        
        # Adicionar sidebar
        self.mapa.get_root().html.add_child(folium.Element(self._criar_sidebar_html()))
        
        # Adicionar legenda
        self.mapa.get_root().html.add_child(folium.Element(self._criar_legenda_html()))
        
        # Adicionar scripts
        self.mapa.get_root().html.add_child(folium.Element(self._criar_scripts()))
        
        # Adicionar controles customizados
        controles_html = '''
        <div class="ipaam-controls">
            <button class="ipaam-control-btn" onclick="resetView()" title="Visão geral">
                🏠
            </button>
            <button class="ipaam-control-btn" onclick="toggleDarkMode()" title="Modo escuro">
                🌙
            </button>
            <button class="ipaam-control-btn ipaam-print-btn" onclick="printMap()" title="Capturar imagem">
                📷
            </button>
        </div>
        '''
        self.mapa.get_root().html.add_child(folium.Element(controles_html))
        
        # Criar seletor de municípios
        municipios_coords = self.df.groupby('municipio').agg({
            'latitude': 'mean',
            'longitude': 'mean'
        }).reset_index()
        municipios_coords = municipios_coords.sort_values('municipio')
        
        opcoes_municipios = '<option value="">Selecione um município...</option>'
        for _, row in municipios_coords.iterrows():
            opcoes_municipios += f'<option value="{row["latitude"]},{row["longitude"]}">{row["municipio"]}</option>'
        
        seletor_html = f'''
        <div class="ipaam-municipio-selector">
            <label for="municipio-select">📍 Município:</label>
            <select id="municipio-select" onchange="irParaMunicipio()">
                {opcoes_municipios}
            </select>
        </div>
        '''
        self.mapa.get_root().html.add_child(folium.Element(seletor_html))
        
        if caminho_saida:
            self.mapa.save(caminho_saida)
            print(f"\n[SALVO] {caminho_saida}")
        
        print("═"*60)
        print("  MAPA PREMIUM GERADO COM SUCESSO!")
        print("═"*60 + "\n")
        
        return self.mapa


def criar_mapa_premium(df: pd.DataFrame, caminho_saida: str) -> folium.Map:
    """Função auxiliar para criar mapa premium."""
    gerador = GeradorMapaPremium(df)
    return gerador.gerar_mapa(caminho_saida)


if __name__ == "__main__":
    pasta_dados = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados')
    arquivo = os.path.join(pasta_dados, 'licencas_ipaam_unificado.csv')
    
    if os.path.exists(arquivo):
        df = pd.read_csv(arquivo)
        
        pasta_output = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        os.makedirs(pasta_output, exist_ok=True)
        
        criar_mapa_premium(df, os.path.join(pasta_output, 'mapa_ipaam_premium.html'))
    else:
        print(f"Arquivo não encontrado: {arquivo}")
