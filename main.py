"""
IPAAM - Script Principal
========================
Script principal para geração do mapa histórico e comparativo
das licenças ambientais do IPAAM (Amazonas).

Este script:
1. Carrega e processa os dados de licenças
2. Gera mapa interativo com Folium (Time Slider + Heatmap)
3. Gera visualizações complementares com Plotly

Autor: Engenheiro de Dados GIS
Versão: 1.0.0
Data: 2025
"""

import os
import sys
import pandas as pd

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.processamento_dados import ProcessadorDadosIPAAM, processar_dados_ipaam
from src.mapa_folium import GeradorMapaIPAAM
from src.mapa_premium import GeradorMapaPremium, criar_mapa_premium
from src.visualizacao_plotly import VisualizadorPlotlyIPAAM, criar_visualizacoes_plotly


def main():
    """
    Função principal que orquestra todo o processo de geração dos mapas.
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║       IPAAM - MAPA HISTÓRICO DE LICENÇAS AMBIENTAIS              ║
    ║                                                                  ║
    ║   Instituto de Proteção Ambiental do Amazonas                    ║
    ║   Gerências: GECF (Controle Florestal)                           ║
    ║              GELI (Licenciamento Industrial)                     ║
    ║                                                                  ║
    ║   Versão Premium 4.0                                             ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Definir caminhos
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DADOS_DIR = os.path.join(BASE_DIR, 'dados')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    
    # Criar pasta de output se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'plotly'), exist_ok=True)
    
    # Caminho do arquivo de dados
    # Priorizar arquivo unificado, depois o processado de 2025, depois o exemplo
    ARQUIVO_UNIFICADO = os.path.join(DADOS_DIR, 'licencas_ipaam_unificado.csv')
    ARQUIVO_2025 = os.path.join(DADOS_DIR, 'licencas_2025_processado.csv')
    ARQUIVO_EXEMPLO = os.path.join(DADOS_DIR, 'licencas_ipaam_exemplo.csv')
    
    if os.path.exists(ARQUIVO_UNIFICADO):
        ARQUIVO_DADOS = ARQUIVO_UNIFICADO
        print(f"Usando dados UNIFICADOS: {ARQUIVO_DADOS}")
    elif os.path.exists(ARQUIVO_2025):
        ARQUIVO_DADOS = ARQUIVO_2025
        print(f"Usando dados 2025: {ARQUIVO_DADOS}")
    elif os.path.exists(ARQUIVO_EXEMPLO):
        ARQUIVO_DADOS = ARQUIVO_EXEMPLO
        print(f"Usando dados exemplo: {ARQUIVO_DADOS}")
    else:
        ARQUIVO_DADOS = None
    
    # Verificar se arquivo existe
    if ARQUIVO_DADOS is None or not os.path.exists(ARQUIVO_DADOS):
        print(f"[ERRO] Arquivo de dados nao encontrado: {ARQUIVO_DADOS}")
        print("\nPara usar seus proprios dados:")
        print("   1. Acesse: https://www.ipaam.am.gov.br/transparencia-tecnica/")
        print("   2. Baixe as planilhas de licenças (2018-2025)")
        print("   3. Unifique os dados em um arquivo CSV ou Excel")
        print("   4. Salve na pasta 'dados/' com o nome 'licencas_ipaam.csv'")
        return
    
    # ═══════════════════════════════════════════════════════════════════
    # ETAPA 1: PROCESSAMENTO DOS DADOS
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("ETAPA 1: PROCESSAMENTO DOS DADOS")
    print("="*60)
    
    # Carregar e processar dados
    processador = ProcessadorDadosIPAAM()
    processador.carregar_csv(ARQUIVO_DADOS)
    processador.padronizar_colunas()
    processador.preencher_coordenadas()
    processador.classificar_atividade()
    processador.extrair_ano()
    
    # Validar e mostrar estatísticas
    stats = processador.validar_dados()
    
    # Obter DataFrame processado
    df = processador.get_dataframe()
    
    # Exportar GeoJSON
    caminho_geojson = os.path.join(OUTPUT_DIR, 'licencas_ipaam.geojson')
    processador.exportar_geojson(caminho_geojson)
    
    # ═══════════════════════════════════════════════════════════════════
    # ETAPA 2: GERAÇÃO DO MAPA PREMIUM (PRINCIPAL)
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("ETAPA 2: GERACAO DO MAPA PREMIUM (PRINCIPAL)")
    print("="*60)
    
    # Gerar mapa premium - design moderno e profissional
    mapa_premium = criar_mapa_premium(
        df, 
        caminho_saida=os.path.join(OUTPUT_DIR, 'mapa_ipaam_premium.html')
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # ETAPA 3: GERAÇÃO DO MAPA FOLIUM (Time Slider + Heatmap)
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("ETAPA 3: GERACAO DO MAPA INTERATIVO (FOLIUM)")
    print("="*60)
    
    # Gerar mapa completo com Folium
    gerador_folium = GeradorMapaIPAAM(df)
    mapa_folium = gerador_folium.gerar_mapa_completo(
        com_marcadores=True,
        com_time_slider=True,
        com_heatmap=True,
        com_legenda=True,
        com_estatisticas=True,
        caminho_saida=os.path.join(OUTPUT_DIR, 'mapa_ipaam_completo.html')
    )
    
    # Gerar mapa apenas com Time Slider (sem heatmap estático para evitar sobreposição)
    gerador_folium2 = GeradorMapaIPAAM(df)
    gerador_folium2.criar_mapa_base()
    gerador_folium2.adicionar_time_slider()
    gerador_folium2.adicionar_heatmap(por_tempo=True)  # Heatmap temporal
    gerador_folium2.adicionar_legenda()
    gerador_folium2.adicionar_creditos()
    gerador_folium2.adicionar_controle_camadas()
    gerador_folium2.adicionar_fullscreen()
    gerador_folium2.mapa.save(os.path.join(OUTPUT_DIR, 'mapa_ipaam_temporal.html'))
    print(f"[OK] Mapa temporal salvo em: {os.path.join(OUTPUT_DIR, 'mapa_ipaam_temporal.html')}")
    
    # ═══════════════════════════════════════════════════════════════════
    # ETAPA 4: GERAÇÃO DAS VISUALIZAÇÕES PLOTLY
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("ETAPA 4: GERACAO DAS VISUALIZACOES (PLOTLY)")
    print("="*60)
    
    # Gerar todas as visualizações Plotly
    criar_visualizacoes_plotly(df, os.path.join(OUTPUT_DIR, 'plotly'))
    
    # ═══════════════════════════════════════════════════════════════════
    # RESUMO FINAL
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "="*60)
    print("PROCESSO CONCLUIDO COM SUCESSO!")
    print("="*60)
    print("\nArquivos gerados:")
    print(f"   {OUTPUT_DIR}/")
    print("   ├── mapa_ipaam_premium.html     ★ MAPA PRINCIPAL (RECOMENDADO)")
    print("   ├── mapa_ipaam_completo.html    (Mapa com todas as camadas)")
    print("   ├── mapa_ipaam_temporal.html    (Mapa com animacao temporal)")
    print("   ├── licencas_ipaam.geojson      (Dados em formato GeoJSON)")
    print("   └── plotly/")
    print("       ├── mapa_animado.html       (Mapa Plotly animado)")
    print("       ├── mapa_densidade.html     (Mapa de calor)")
    print("       ├── evolucao_anual.html     (Grafico de barras)")
    print("       ├── top_municipios.html     (Top municipios)")
    print("       ├── distribuicao_categorias.html")
    print("       ├── timeline.html           (Linha do tempo)")
    print("       └── dashboard_completo.html (Dashboard unificado)")
    
    print("\nPara visualizar:")
    print(f"   Abra os arquivos .html no seu navegador")
    print(f"   ★ Recomendado: mapa_ipaam_premium.html")
    
    print("\nEstatisticas dos dados:")
    print(f"   • Total de licenças: {stats['total_registros']}")
    print(f"   • Municípios únicos: {stats['municipios_unicos']}")
    print(f"   • Período: {min(stats['registros_por_ano'].keys()):.0f} - {max(stats['registros_por_ano'].keys()):.0f}")
    
    print("\n" + "="*60)
    print("Fonte: Dados abertos IPAAM - GECF/GELI")
    print("   https://www.ipaam.am.gov.br/transparencia-tecnica/")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
