"""
IPAAM - Script para Ajustar Planilha Excel 2025
================================================
Este script lê a planilha original do IPAAM e converte
para o formato padronizado do projeto.

Autor: Engenheiro de Dados GIS
"""

import pandas as pd
import numpy as np
import re
import os


def converter_coordenadas_dms_para_decimal(coord_str):
    """
    Converte coordenadas em formato DMS (graus, minutos, segundos) para decimal.
    
    Exemplos de formatos aceitos:
    - -3°00'35,763" -56°44'10,707"
    - 03°03'07,029"S e 59°59'29,105"W
    - S 03° 17' 8.55100 W 60° 37' 39.26300
    """
    if pd.isna(coord_str) or str(coord_str).strip() == '':
        return None, None
    
    coord_str = str(coord_str).strip()
    
    # Padrão para extrair latitude e longitude
    # Tenta encontrar dois conjuntos de coordenadas
    
    # Padrão 1: -3°00'35,763" -56°44'10,707"
    pattern1 = r"(-?\d+)[°º](\d+)['\'](\d+[,.]?\d*)[\"″]?\s*[SsNn]?\s*[eE]?\s*(-?\d+)[°º](\d+)['\'](\d+[,.]?\d*)[\"″]?\s*[WwOo]?"
    
    # Padrão 2: S 03° 17' 8.55100 W 60° 37' 39.26300
    pattern2 = r"[SsNn]?\s*(-?\d+)[°º]\s*(\d+)['\']?\s*(\d+[,.]?\d*)[\"″]?\s*[SsNn]?\s*[WwOoEe]?\s*(-?\d+)[°º]\s*(\d+)['\']?\s*(\d+[,.]?\d*)"
    
    # Padrão 3: 03°03'07,029"S e 59°59'29,105"W
    pattern3 = r"(\d+)[°º](\d+)['\'](\d+[,.]?\d*)[\"″]?\s*([SsNn])\s*[eE]?\s*(\d+)[°º](\d+)['\'](\d+[,.]?\d*)[\"″]?\s*([WwOoEe])"
    
    lat, lon = None, None
    
    try:
        # Tentar padrão 3 primeiro (mais específico)
        match = re.search(pattern3, coord_str)
        if match:
            lat_d, lat_m, lat_s, lat_dir, lon_d, lon_m, lon_s, lon_dir = match.groups()
            lat_s = lat_s.replace(',', '.')
            lon_s = lon_s.replace(',', '.')
            lat = float(lat_d) + float(lat_m)/60 + float(lat_s)/3600
            lon = float(lon_d) + float(lon_m)/60 + float(lon_s)/3600
            if lat_dir.upper() == 'S':
                lat = -lat
            if lon_dir.upper() in ['W', 'O']:
                lon = -lon
            return lat, lon
        
        # Tentar padrão 2
        match = re.search(pattern2, coord_str)
        if match:
            lat_d, lat_m, lat_s, lon_d, lon_m, lon_s = match.groups()
            lat_s = lat_s.replace(',', '.')
            lon_s = lon_s.replace(',', '.')
            lat = float(lat_d) + float(lat_m)/60 + float(lat_s)/3600
            lon = float(lon_d) + float(lon_m)/60 + float(lon_s)/3600
            # Assumir sul e oeste para o Amazonas
            if lat > 0 and 'S' in coord_str.upper():
                lat = -lat
            if lon > 0 and ('W' in coord_str.upper() or 'O' in coord_str.upper()):
                lon = -lon
            # Se ainda positivo e não tem indicador, assumir negativo (Amazonas)
            if lat > 0:
                lat = -lat
            if lon > 0:
                lon = -lon
            return lat, lon
        
        # Tentar padrão 1
        match = re.search(pattern1, coord_str)
        if match:
            lat_d, lat_m, lat_s, lon_d, lon_m, lon_s = match.groups()
            lat_s = lat_s.replace(',', '.')
            lon_s = lon_s.replace(',', '.')
            lat = float(lat_d) + float(lat_m)/60 + float(lat_s)/3600
            lon = float(lon_d) + float(lon_m)/60 + float(lon_s)/3600
            if lat > 0:
                lat = -lat
            if lon > 0:
                lon = -lon
            return lat, lon
            
    except Exception as e:
        print(f"  [!] Erro ao converter: {coord_str} - {e}")
    
    return None, None


def classificar_atividade(atividade, codigo=None):
    """
    Classifica a atividade em categorias padronizadas.
    """
    atividade_lower = str(atividade).lower() if pd.notna(atividade) else ''
    codigo_lower = str(codigo).lower() if pd.notna(codigo) else ''
    
    # Verificar pelo código primeiro
    if '08' in codigo_lower or 'mobili' in codigo_lower:
        return 'Indústria Mobiliária'
    elif '07' in codigo_lower or 'madeira' in codigo_lower:
        return 'Indústria Madeireira'
    elif '34' in codigo_lower or 'manejo' in codigo_lower or 'florestal' in codigo_lower:
        return 'Manejo Florestal'
    
    # Verificar pela atividade
    if 'móvel' in atividade_lower or 'movel' in atividade_lower or 'mobili' in atividade_lower or 'marcenaria' in atividade_lower:
        return 'Indústria Mobiliária'
    elif 'manejo' in atividade_lower and 'florestal' in atividade_lower:
        return 'Manejo Florestal'
    elif 'pmfs' in atividade_lower:
        return 'Manejo Florestal'
    elif 'madeira' in atividade_lower or 'madeireira' in atividade_lower or 'serraria' in atividade_lower:
        return 'Indústria Madeireira'
    elif 'depósito' in atividade_lower or 'deposito' in atividade_lower:
        if 'madeira' in atividade_lower:
            return 'Indústria Madeireira'
    
    return 'Outros'


def determinar_gerencia(categoria):
    """
    Determina a gerência com base na categoria.
    """
    if categoria == 'Manejo Florestal':
        return 'GECF'
    elif categoria in ['Indústria Madeireira', 'Indústria Mobiliária']:
        return 'GELI'
    else:
        return 'GELI'


def determinar_tipo_licenca(atividade):
    """
    Determina o tipo de licença (LP, LI, LO).
    Por padrão, assume LO (Licença de Operação) para funcionamento.
    """
    atividade_lower = str(atividade).lower() if pd.notna(atividade) else ''
    
    if 'funcionamento' in atividade_lower or 'operação' in atividade_lower:
        return 'LO'
    elif 'instalação' in atividade_lower or 'instalacao' in atividade_lower:
        return 'LI'
    elif 'prévia' in atividade_lower or 'previa' in atividade_lower:
        return 'LP'
    else:
        return 'LO'  # Padrão


def processar_planilha_2025(caminho_entrada, caminho_saida=None):
    """
    Processa a planilha Excel de 2025 e converte para o formato padronizado.
    """
    print("="*60)
    print(" PROCESSANDO PLANILHA EXCEL 2025")
    print("="*60)
    
    # Ler Excel pulando as primeiras linhas de cabeçalho
    print(f"\n Lendo: {caminho_entrada}")
    df = pd.read_excel(caminho_entrada, header=4)  # Cabeçalho na linha 5 (índice 4)
    
    print(f"[OK] Carregadas {len(df)} linhas")
    print(f"  Colunas originais: {df.columns.tolist()}")
    
    # Remover linhas completamente vazias
    df = df.dropna(how='all')
    
    # Renomear colunas para nomes padronizados
    mapeamento_colunas = {
        'Processo': 'processo',
        'Interessado': 'razao_social',
        'Atividade': 'atividade',
        'Codigo da atividade': 'codigo_atividade',
        'Municipio': 'municipio',
        'Volume (m³)': 'volume_m3',
        'Emissao (Mês)': 'mes_emissao',
        'Validade (anos)': 'validade_anos',
        'Coordenadas geograficas': 'coordenadas',
        'POTENCIAL POLUIDOR/DEGRADADOR': 'potencial_poluidor'
    }
    
    df.rename(columns=mapeamento_colunas, inplace=True)
    
    # Remover colunas sem nome (Unnamed)
    df = df[[col for col in df.columns if not col.startswith('Unnamed')]]
    
    print(f"[OK] Colunas após renomear: {df.columns.tolist()}")
    
    # Remover linhas onde razao_social é vazia
    df = df.dropna(subset=['razao_social'])
    print(f"[OK] {len(df)} registros válidos após limpeza")
    
    # Converter coordenadas
    print("\nConvertendo coordenadas...")
    latitudes = []
    longitudes = []
    
    for idx, coord in enumerate(df['coordenadas']):
        lat, lon = converter_coordenadas_dms_para_decimal(coord)
        latitudes.append(lat)
        longitudes.append(lon)
        if lat is not None:
            print(f"  [OK] {df.iloc[idx]['municipio']}: ({lat:.4f}, {lon:.4f})")
    
    df['latitude'] = latitudes
    df['longitude'] = longitudes
    
    # Contar coordenadas convertidas
    coords_ok = df['latitude'].notna().sum()
    print(f"[OK] {coords_ok}/{len(df)} coordenadas convertidas com sucesso")
    
    # Classificar atividades
    print("\nClassificando atividades...")
    df['categoria'] = df.apply(
        lambda row: classificar_atividade(row['atividade'], row.get('codigo_atividade')), 
        axis=1
    )
    
    # Determinar gerência
    df['gerencia'] = df['categoria'].apply(determinar_gerencia)
    
    # Determinar tipo de licença
    df['tipo_licenca'] = df['atividade'].apply(determinar_tipo_licenca)
    
    # Criar datas de emissão e validade
    df['ano'] = 2025
    
    # Mapear mês para número
    meses = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marco': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }
    
    def get_mes(mes_str):
        if pd.isna(mes_str):
            return 6  # Padrão junho
        mes_lower = str(mes_str).lower().strip()
        return meses.get(mes_lower, 6)
    
    df['mes'] = df['mes_emissao'].apply(get_mes)
    df['data_emissao'] = pd.to_datetime(
        df.apply(lambda row: f"2025-{row['mes']:02d}-15", axis=1),
        format='%Y-%m-%d'
    )
    
    # Calcular validade
    def calcular_validade(row):
        try:
            anos = int(row['validade_anos']) if pd.notna(row['validade_anos']) else 2
            return row['data_emissao'] + pd.DateOffset(years=anos)
        except:
            return row['data_emissao'] + pd.DateOffset(years=2)
    
    df['data_validade'] = df.apply(calcular_validade, axis=1)
    
    # Selecionar e ordenar colunas finais
    colunas_finais = [
        'razao_social', 'municipio', 'tipo_licenca', 'gerencia', 'atividade',
        'latitude', 'longitude', 'data_emissao', 'data_validade', 'ano', 'categoria',
        'processo', 'volume_m3', 'potencial_poluidor'
    ]
    
    # Manter apenas colunas que existem
    colunas_existentes = [col for col in colunas_finais if col in df.columns]
    df_final = df[colunas_existentes].copy()
    
    # Mostrar estatísticas
    print("\n" + "="*60)
    print(" ESTATÍSTICAS")
    print("="*60)
    print(f"Total de registros: {len(df_final)}")
    print(f"\nPor categoria:")
    for cat, qtd in df_final['categoria'].value_counts().items():
        print(f"  • {cat}: {qtd}")
    print(f"\nPor município:")
    for mun, qtd in df_final['municipio'].value_counts().head(10).items():
        print(f"  • {mun}: {qtd}")
    print(f"\nCoordenadas:")
    print(f"  • Com coordenadas: {df_final['latitude'].notna().sum()}")
    print(f"  • Sem coordenadas: {df_final['latitude'].isna().sum()}")
    
    # Salvar
    if caminho_saida is None:
        caminho_saida = caminho_entrada.replace('.xlsx', '_processado.csv')
    
    df_final.to_csv(caminho_saida, index=False)
    print(f"\n[OK] Arquivo salvo em: {caminho_saida}")
    
    print("="*60)
    
    return df_final


if __name__ == "__main__":
    # Caminhos
    pasta_dados = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados')
    
    arquivo_entrada = os.path.join(pasta_dados, 'Planilha das licencas_2025_Anizio - Copia.xlsx')
    arquivo_saida = os.path.join(pasta_dados, 'licencas_2025_processado.csv')
    
    if os.path.exists(arquivo_entrada):
        df = processar_planilha_2025(arquivo_entrada, arquivo_saida)
        print("\n Primeiras linhas do arquivo processado:")
        print(df.head().to_string())
    else:
        print(f"[ERRO] Arquivo não encontrado: {arquivo_entrada}")
