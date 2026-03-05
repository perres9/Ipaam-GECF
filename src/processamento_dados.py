"""
IPAAM - Processamento de Dados de Licenças Ambientais
======================================================
Módulo para processamento, limpeza e geocodificação dos dados
de licenças do IPAAM (GECF e GELI).

Autor: Engenheiro de Dados GIS
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import os
from typing import Optional, Tuple
import warnings

warnings.filterwarnings('ignore')


class ProcessadorDadosIPAAM:
    """
    Classe responsável pelo processamento dos dados de licenças do IPAAM.
    Inclui funcionalidades de:
    - Leitura e unificação de múltiplas planilhas
    - Limpeza e padronização de dados
    - Geocodificação de municípios sem coordenadas
    - Exportação para formatos compatíveis com GIS
    """
    
    # Coordenadas conhecidas dos principais municípios do Amazonas
    COORDENADAS_MUNICIPIOS_AM = {
        'manaus': (-3.1019, -60.0250),
        'parintins': (-2.6282, -56.7360),
        'itacoatiara': (-3.1432, -58.4442),
        'manacapuru': (-3.2996, -60.6213),
        'coari': (-4.0850, -63.1408),
        'tefé': (-3.3533, -64.7100),
        'tabatinga': (-4.2528, -69.9383),
        'maués': (-3.3833, -57.7186),
        'humaitá': (-7.5061, -63.0248),
        'lábrea': (-7.2578, -64.7836),
        'manicoré': (-5.8117, -61.2991),
        'borba': (-4.3881, -59.5939),
        'autazes': (-3.5783, -59.1306),
        'careiro': (-3.7678, -60.3647),
        'iranduba': (-3.2847, -60.1861),
        'novo airão': (-2.6206, -60.9439),
        'presidente figueiredo': (-2.0331, -60.0253),
        'rio preto da eva': (-2.6978, -59.7000),
        'são gabriel da cachoeira': (-0.1306, -67.0892),
        'santa isabel do rio negro': (-0.4142, -65.0194),
        'barcelos': (-0.9744, -62.9239),
        'eirunepé': (-6.6600, -69.8737),
        'envira': (-7.4367, -70.0181),
        'ipixuna': (-7.0511, -71.6908),
        'benjamin constant': (-4.3833, -70.0331),
        'atalaia do norte': (-4.3711, -70.1928),
        'fonte boa': (-2.5139, -66.0917),
        'jutaí': (-2.7508, -66.7647),
        'carauari': (-4.8833, -66.8958),
        'pauini': (-7.7133, -66.9764),
        'boca do acre': (-8.7525, -67.3972),
        'apuí': (-7.1967, -59.8914),
        'novo aripuanã': (-5.1206, -60.3797),
        'urucará': (-2.5339, -57.7553),
        'nhamundá': (-2.1889, -56.7133),
        'urucurituba': (-2.9861, -58.1575),
        'barreirinha': (-2.7958, -57.0706),
        'boa vista do ramos': (-2.9739, -57.5869),
        'silves': (-2.8381, -58.2072),
        'são sebastião do uatumã': (-2.5708, -57.8689),
        'codajás': (-3.8369, -62.0569),
        'anori': (-3.7694, -61.6578),
        'anamã': (-3.5817, -61.3969),
        'alvarães': (-3.2219, -64.8056),
        'uarini': (-2.9906, -65.1092),
        'japurá': (-1.8817, -66.9378),
        'maraã': (-1.8522, -65.5728),
        'santo antônio do içá': (-3.1014, -67.9392),
        'tonantins': (-2.8728, -67.8017),
        'amaturá': (-3.3681, -68.1981),
        'são paulo de olivença': (-3.4697, -68.8728)
    }
    
    def __init__(self, user_agent: str = "ipaam_gis_project"):
        """
        Inicializa o processador de dados.
        
        Args:
            user_agent: Identificador para o serviço de geocodificação
        """
        self.geolocator = Nominatim(user_agent=user_agent)
        self.df = None
        
    def carregar_csv(self, caminho: str) -> pd.DataFrame:
        """
        Carrega dados de um arquivo CSV.
        
        Args:
            caminho: Caminho para o arquivo CSV
            
        Returns:
            DataFrame com os dados carregados
        """
        self.df = pd.read_csv(caminho, parse_dates=['data_emissao', 'data_validade'])
        print(f"[OK] Carregados {len(self.df)} registros de {caminho}")
        return self.df
    
    def carregar_excel(self, caminho: str, sheet_name: str = 0) -> pd.DataFrame:
        """
        Carrega dados de um arquivo Excel.
        
        Args:
            caminho: Caminho para o arquivo Excel
            sheet_name: Nome ou índice da aba
            
        Returns:
            DataFrame com os dados carregados
        """
        self.df = pd.read_excel(caminho, sheet_name=sheet_name)
        print(f"[OK] Carregados {len(self.df)} registros de {caminho}")
        return self.df
    
    def unificar_planilhas(self, pasta: str, extensao: str = '.xlsx') -> pd.DataFrame:
        """
        Unifica múltiplas planilhas de uma pasta em um único DataFrame.
        
        Args:
            pasta: Caminho da pasta com as planilhas
            extensao: Extensão dos arquivos (.xlsx, .csv, etc.)
            
        Returns:
            DataFrame unificado
        """
        arquivos = [f for f in os.listdir(pasta) if f.endswith(extensao)]
        dfs = []
        
        for arquivo in arquivos:
            caminho = os.path.join(pasta, arquivo)
            try:
                if extensao == '.csv':
                    df_temp = pd.read_csv(caminho)
                else:
                    df_temp = pd.read_excel(caminho)
                df_temp['arquivo_origem'] = arquivo
                dfs.append(df_temp)
                print(f"  [OK] {arquivo}: {len(df_temp)} registros")
            except Exception as e:
                print(f"  [X] Erro ao carregar {arquivo}: {e}")
        
        if dfs:
            self.df = pd.concat(dfs, ignore_index=True)
            print(f"\n[OK] Total unificado: {len(self.df)} registros de {len(dfs)} arquivos")
        else:
            self.df = pd.DataFrame()
            print("[X] Nenhum arquivo encontrado para unificar")
            
        return self.df
    
    def padronizar_colunas(self, mapeamento: dict = None) -> pd.DataFrame:
        """
        Padroniza os nomes das colunas do DataFrame.
        
        Args:
            mapeamento: Dicionário de mapeamento {nome_antigo: nome_novo}
            
        Returns:
            DataFrame com colunas padronizadas
        """
        if self.df is None:
            raise ValueError("Nenhum dado carregado. Use carregar_csv() ou carregar_excel() primeiro.")
        
        # Mapeamento padrão
        mapeamento_padrao = {
            'razão social': 'razao_social',
            'razao social': 'razao_social',
            'empresa': 'razao_social',
            'nome': 'razao_social',
            'município': 'municipio',
            'municipio': 'municipio',
            'cidade': 'municipio',
            'tipo licença': 'tipo_licenca',
            'tipo de licença': 'tipo_licenca',
            'tipo_licenca': 'tipo_licenca',
            'licença': 'tipo_licenca',
            'licenca': 'tipo_licenca',
            'gerência': 'gerencia',
            'gerencia': 'gerencia',
            'setor': 'gerencia',
            'atividade': 'atividade',
            'tipo atividade': 'atividade',
            'descrição': 'atividade',
            'latitude': 'latitude',
            'lat': 'latitude',
            'longitude': 'longitude',
            'long': 'longitude',
            'lng': 'longitude',
            'lon': 'longitude',
            'data emissão': 'data_emissao',
            'data_emissao': 'data_emissao',
            'emissão': 'data_emissao',
            'data validade': 'data_validade',
            'data_validade': 'data_validade',
            'validade': 'data_validade',
            'vencimento': 'data_validade',
            'ano': 'ano'
        }
        
        if mapeamento:
            mapeamento_padrao.update(mapeamento)
        
        # Converter nomes para minúsculas e aplicar mapeamento
        self.df.columns = self.df.columns.str.lower().str.strip()
        self.df.rename(columns=mapeamento_padrao, inplace=True)
        
        print("[OK] Colunas padronizadas")
        return self.df
    
    def geocodificar_municipio(self, municipio: str, estado: str = "AM") -> Optional[Tuple[float, float]]:
        """
        Obtém coordenadas de um município usando geocodificação.
        
        Args:
            municipio: Nome do município
            estado: Sigla do estado (padrão: AM)
            
        Returns:
            Tupla (latitude, longitude) ou None se não encontrado
        """
        # Primeiro, verificar no cache local
        municipio_lower = municipio.lower().strip()
        if municipio_lower in self.COORDENADAS_MUNICIPIOS_AM:
            return self.COORDENADAS_MUNICIPIOS_AM[municipio_lower]
        
        # Se não encontrar no cache, usar API de geocodificação
        try:
            query = f"{municipio}, {estado}, Brasil"
            location = self.geolocator.geocode(query, timeout=10)
            if location:
                time.sleep(1)  # Respeitar rate limit
                return (location.latitude, location.longitude)
        except GeocoderTimedOut:
            print(f"  [!] Timeout ao geocodificar: {municipio}")
        except Exception as e:
            print(f"  [!] Erro ao geocodificar {municipio}: {e}")
            
        return None
    
    def preencher_coordenadas(self) -> pd.DataFrame:
        """
        Preenche coordenadas faltantes usando geocodificação.
        
        Returns:
            DataFrame com coordenadas preenchidas
        """
        if self.df is None:
            raise ValueError("Nenhum dado carregado.")
        
        # Identificar registros sem coordenadas
        mask_sem_coords = (
            self.df['latitude'].isna() | 
            self.df['longitude'].isna() |
            (self.df['latitude'] == 0) |
            (self.df['longitude'] == 0)
        )
        
        registros_sem_coords = self.df[mask_sem_coords]
        print(f"Geocodificando {len(registros_sem_coords)} registros sem coordenadas...")
        
        for idx in registros_sem_coords.index:
            municipio = self.df.loc[idx, 'municipio']
            coords = self.geocodificar_municipio(municipio)
            
            if coords:
                self.df.loc[idx, 'latitude'] = coords[0]
                self.df.loc[idx, 'longitude'] = coords[1]
                print(f"  [OK] {municipio}: {coords}")
            else:
                print(f"  [X] {municipio}: não encontrado")
        
        return self.df
    
    def classificar_atividade(self) -> pd.DataFrame:
        """
        Classifica a atividade em categorias padronizadas.
        
        Returns:
            DataFrame com coluna 'categoria' adicionada
        """
        if self.df is None:
            raise ValueError("Nenhum dado carregado.")
        
        def categorizar(row):
            # Se já tem categoria válida, preservar
            if 'categoria' in row.index and pd.notna(row.get('categoria')):
                cat_existente = str(row['categoria']).strip()
                if cat_existente in ['Manejo Florestal', 'Indústria Madeireira', 'Indústria Mobiliária']:
                    return cat_existente
            
            atividade_lower = str(row['atividade']).lower() if pd.notna(row.get('atividade')) else ''
            
            # Primeiro verificar Mobiliária (antes de Madeireira para evitar falso positivo)
            if 'móvel' in atividade_lower or 'movel' in atividade_lower or 'mobili' in atividade_lower:
                return 'Indústria Mobiliária'
            elif 'marcenaria' in atividade_lower:
                return 'Indústria Mobiliária'
            # Depois verificar Manejo Florestal
            elif 'manejo' in atividade_lower and 'florestal' in atividade_lower:
                return 'Manejo Florestal'
            elif 'plano de manejo' in atividade_lower:
                return 'Manejo Florestal'
            elif 'pmfs' in atividade_lower:
                return 'Manejo Florestal'
            elif 'autex' in atividade_lower or 'transporte' in atividade_lower and 'produto' in atividade_lower:
                return 'Manejo Florestal'
            # Por fim, Indústria Madeireira
            elif 'madeira' in atividade_lower or 'madeireira' in atividade_lower:
                return 'Indústria Madeireira'
            elif 'serraria' in atividade_lower or 'laminad' in atividade_lower or 'compensad' in atividade_lower:
                return 'Indústria Madeireira'
            elif 'desdobro' in atividade_lower or 'benefici' in atividade_lower:
                return 'Indústria Madeireira'
            elif 'depósito' in atividade_lower or 'deposito' in atividade_lower:
                return 'Indústria Madeireira'
            elif '0717' in atividade_lower or '07 -' in atividade_lower:
                return 'Indústria Madeireira'
            elif '08 -' in atividade_lower:
                return 'Indústria Mobiliária'
            elif '34 -' in atividade_lower:
                return 'Manejo Florestal'
            else:
                return 'Outros'
        
        self.df['categoria'] = self.df.apply(categorizar, axis=1)
        print("[OK] Atividades classificadas em categorias")
        return self.df
    
    def extrair_ano(self) -> pd.DataFrame:
        """
        Extrai o ano da data de emissão.
        
        Returns:
            DataFrame com coluna 'ano' atualizada
        """
        if self.df is None:
            raise ValueError("Nenhum dado carregado.")
        
        if 'data_emissao' in self.df.columns:
            self.df['data_emissao'] = pd.to_datetime(self.df['data_emissao'], errors='coerce')
            self.df['ano'] = self.df['data_emissao'].dt.year
        
        print("[OK] Anos extraídos das datas de emissão")
        return self.df
    
    def validar_dados(self) -> dict:
        """
        Valida a qualidade dos dados e retorna estatísticas.
        
        Returns:
            Dicionário com estatísticas de validação
        """
        if self.df is None:
            raise ValueError("Nenhum dado carregado.")
        
        stats = {
            'total_registros': len(self.df),
            'registros_sem_coordenadas': self.df['latitude'].isna().sum() + self.df['longitude'].isna().sum(),
            'registros_por_ano': self.df['ano'].value_counts().to_dict() if 'ano' in self.df.columns else {},
            'registros_por_categoria': self.df['categoria'].value_counts().to_dict() if 'categoria' in self.df.columns else {},
            'registros_por_tipo_licenca': self.df['tipo_licenca'].value_counts().to_dict() if 'tipo_licenca' in self.df.columns else {},
            'municipios_unicos': self.df['municipio'].nunique() if 'municipio' in self.df.columns else 0
        }
        
        print("\n" + "="*50)
        print("ESTATÍSTICAS DOS DADOS")
        print("="*50)
        print(f"Total de registros: {stats['total_registros']}")
        print(f"Registros sem coordenadas: {stats['registros_sem_coordenadas']}")
        print(f"Municípios únicos: {stats['municipios_unicos']}")
        print(f"\nRegistros por ano:")
        for ano, qtd in sorted(stats['registros_por_ano'].items()):
            print(f"  {ano}: {qtd}")
        print(f"\nRegistros por categoria:")
        for cat, qtd in stats['registros_por_categoria'].items():
            print(f"  {cat}: {qtd}")
        print("="*50)
        
        return stats
    
    def exportar_geojson(self, caminho: str) -> None:
        """
        Exporta os dados para formato GeoJSON.
        
        Args:
            caminho: Caminho do arquivo de saída
        """
        if self.df is None:
            raise ValueError("Nenhum dado carregado.")
        
        features = []
        for _, row in self.df.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [row['longitude'], row['latitude']]
                    },
                    "properties": {
                        k: str(v) if pd.notna(v) else None 
                        for k, v in row.items() 
                        if k not in ['latitude', 'longitude']
                    }
                }
                features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        import json
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] Exportado para GeoJSON: {caminho} ({len(features)} features)")
    
    def get_dataframe(self) -> pd.DataFrame:
        """Retorna o DataFrame processado."""
        return self.df


def processar_dados_ipaam(caminho_entrada: str, caminho_saida: str = None) -> pd.DataFrame:
    """
    Função de conveniência para processar dados do IPAAM.
    
    Args:
        caminho_entrada: Caminho do arquivo de entrada (CSV ou Excel)
        caminho_saida: Caminho opcional para exportar GeoJSON
        
    Returns:
        DataFrame processado
    """
    processador = ProcessadorDadosIPAAM()
    
    # Carregar dados
    if caminho_entrada.endswith('.csv'):
        processador.carregar_csv(caminho_entrada)
    else:
        processador.carregar_excel(caminho_entrada)
    
    # Processar
    processador.padronizar_colunas()
    processador.preencher_coordenadas()
    processador.classificar_atividade()
    processador.extrair_ano()
    processador.validar_dados()
    
    # Exportar se caminho fornecido
    if caminho_saida:
        processador.exportar_geojson(caminho_saida)
    
    return processador.get_dataframe()


if __name__ == "__main__":
    # Exemplo de uso
    import os
    
    # Caminho do arquivo de exemplo
    caminho_exemplo = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'dados',
        'licencas_ipaam_exemplo.csv'
    )
    
    if os.path.exists(caminho_exemplo):
        df = processar_dados_ipaam(caminho_exemplo)
        print("\nPrimeiras linhas do DataFrame processado:")
        print(df.head())
    else:
        print(f"Arquivo não encontrado: {caminho_exemplo}")
