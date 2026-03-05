"""Script para verificar categorias e corrigir classificação"""
import pandas as pd

# Carregar dados
df = pd.read_csv(r'C:\Users\Anizio\Documents\PROGRAMAÇÃO\ipaam\dados\licencas_ipaam_unificado.csv')

print("=== CATEGORIAS NO ARQUIVO ===")
print(df['categoria'].value_counts())

print("\n=== ATIVIDADES ÚNICAS ===")
for cat in df['categoria'].unique():
    print(f"\n--- {cat} ---")
    atividades = df[df['categoria']==cat]['atividade'].unique()[:5]
    for a in atividades:
        print(f"  • {a[:80]}...")
