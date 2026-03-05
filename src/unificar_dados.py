"""
Script para preencher coordenadas faltantes e unificar dados
"""
import pandas as pd
import os

# Coordenadas conhecidas dos municípios do Amazonas
COORDS_AM = {
    'manaus': (-3.1019, -60.0250),
    'parintins': (-2.6282, -56.7360),
    'itacoatiara': (-3.1432, -58.4442),
    'manacapuru': (-3.2996, -60.6213),
    'humaitá': (-7.5061, -63.0248),
    'humaita': (-7.5061, -63.0248),
    'manicoré': (-5.8117, -61.2991),
    'manicore': (-5.8117, -61.2991),
    'novo aripuanã': (-5.1206, -60.3797),
    'novo aripuana': (-5.1206, -60.3797),
    'apuí': (-7.1967, -59.8914),
    'apui': (-7.1967, -59.8914),
    'lábrea': (-7.2578, -64.7836),
    'labrea': (-7.2578, -64.7836),
    'itapiranga': (-2.7544, -58.0303),
    'silves': (-2.8381, -58.2072),
    'iranduba': (-3.2847, -60.1861),
    'rio preto da eva': (-2.6978, -59.7000),
    'careiro': (-3.7678, -60.3647),
    'canutama': (-6.5339, -64.3831),
    'nova olinda do norte': (-3.8933, -59.0944),
    'carauari': (-4.8833, -66.8958),
    'presidente figueiredo': (-2.0331, -60.0253),
    'itacoatiara e silves': (-3.0, -58.3),
    'manacapuru-am.': (-3.2996, -60.6213),
    'manaus- am': (-3.1019, -60.0250),
    'manaus-am': (-3.1019, -60.0250),
    'coari': (-4.0850, -63.1408),
    'tefé': (-3.3533, -64.7100),
    'tefe': (-3.3533, -64.7100),
    'borba': (-4.3881, -59.5939),
    'autazes': (-3.5783, -59.1306),
    'barcelos': (-0.9744, -62.9239),
    'nhamundá': (-2.1889, -56.7133),
    'nhamunda': (-2.1889, -56.7133),
    'barreirinha': (-2.7958, -57.0706),
    'maués': (-3.3833, -57.7186),
    'maues': (-3.3833, -57.7186),
    'urucará': (-2.5339, -57.7553),
    'urucara': (-2.5339, -57.7553),
    'são sebastião do uatumã': (-2.5708, -57.8689),
    'sao sebastiao do uatuma': (-2.5708, -57.8689),
}

def preencher_coordenadas(df):
    """Preenche coordenadas faltantes usando tabela de municípios."""
    count = 0
    for idx, row in df.iterrows():
        if pd.isna(row['latitude']) or pd.isna(row['longitude']):
            mun = str(row['municipio']).lower().strip()
            if mun in COORDS_AM:
                df.loc[idx, 'latitude'] = COORDS_AM[mun][0]
                df.loc[idx, 'longitude'] = COORDS_AM[mun][1]
                count += 1
                print(f"  + {row['municipio']}: {COORDS_AM[mun]}")
    return df, count

def main():
    print("="*60)
    print("PREENCHENDO COORDENADAS E UNIFICANDO DADOS")
    print("="*60)
    
    # Caminhos
    pasta_dados = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados')
    
    arquivo_2025 = os.path.join(pasta_dados, 'licencas_2025_processado.csv')
    arquivo_exemplo = os.path.join(pasta_dados, 'licencas_ipaam_exemplo.csv')
    arquivo_final = os.path.join(pasta_dados, 'licencas_ipaam_unificado.csv')
    
    # Carregar dados de 2025
    print("\n1. Carregando dados de 2025...")
    df_2025 = pd.read_csv(arquivo_2025)
    print(f"   Registros: {len(df_2025)}")
    print(f"   Com coordenadas: {df_2025['latitude'].notna().sum()}")
    
    # Preencher coordenadas faltantes
    print("\n2. Preenchendo coordenadas faltantes...")
    df_2025, count = preencher_coordenadas(df_2025)
    print(f"   Preenchidas: {count}")
    print(f"   Total com coordenadas: {df_2025['latitude'].notna().sum()}/{len(df_2025)}")
    
    # Salvar 2025 atualizado
    df_2025.to_csv(arquivo_2025, index=False)
    print(f"\n3. Arquivo 2025 atualizado: {arquivo_2025}")
    
    # Carregar exemplo (2018-2024)
    print("\n4. Carregando dados exemplo (2018-2024)...")
    df_exemplo = pd.read_csv(arquivo_exemplo)
    print(f"   Registros: {len(df_exemplo)}")
    
    # Padronizar colunas para unificação
    colunas_comuns = ['razao_social', 'municipio', 'tipo_licenca', 'gerencia', 
                      'atividade', 'latitude', 'longitude', 'data_emissao', 
                      'data_validade', 'ano']
    
    # Adicionar categoria ao exemplo se não existir
    if 'categoria' not in df_exemplo.columns:
        def categorizar(atividade):
            atividade_lower = str(atividade).lower()
            if 'móvel' in atividade_lower or 'movel' in atividade_lower or 'mobili' in atividade_lower:
                return 'Indústria Mobiliária'
            elif 'manejo' in atividade_lower and 'florestal' in atividade_lower:
                return 'Manejo Florestal'
            elif 'plano de manejo' in atividade_lower or 'pmfs' in atividade_lower:
                return 'Manejo Florestal'
            elif 'madeira' in atividade_lower or 'madeireira' in atividade_lower:
                return 'Indústria Madeireira'
            elif 'serraria' in atividade_lower or 'laminad' in atividade_lower or 'compensad' in atividade_lower:
                return 'Indústria Madeireira'
            else:
                return 'Outros'
        df_exemplo['categoria'] = df_exemplo['atividade'].apply(categorizar)
    
    colunas_comuns.append('categoria')
    
    # Selecionar apenas colunas comuns
    df_2025_sel = df_2025[[c for c in colunas_comuns if c in df_2025.columns]].copy()
    df_exemplo_sel = df_exemplo[[c for c in colunas_comuns if c in df_exemplo.columns]].copy()
    
    # Unificar
    print("\n5. Unificando dados...")
    df_unificado = pd.concat([df_exemplo_sel, df_2025_sel], ignore_index=True)
    
    # Ordenar por ano
    df_unificado = df_unificado.sort_values('ano')
    
    # Salvar
    df_unificado.to_csv(arquivo_final, index=False)
    print(f"   Arquivo unificado salvo: {arquivo_final}")
    
    # Estatísticas finais
    print("\n" + "="*60)
    print("ESTATÍSTICAS FINAIS")
    print("="*60)
    print(f"Total de registros: {len(df_unificado)}")
    print(f"Com coordenadas: {df_unificado['latitude'].notna().sum()}")
    print(f"\nPor ano:")
    for ano, qtd in df_unificado['ano'].value_counts().sort_index().items():
        print(f"  {int(ano)}: {qtd}")
    print(f"\nPor categoria:")
    for cat, qtd in df_unificado['categoria'].value_counts().items():
        print(f"  {cat}: {qtd}")
    print("="*60)

if __name__ == "__main__":
    main()
