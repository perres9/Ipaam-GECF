"""
IPAAM - Script de Scraping/Download de Dados
=============================================
Script auxiliar para baixar dados do Portal de Transparência
Técnica do IPAAM.

ATENÇÃO: Este script é apenas um modelo de referência.
O site do IPAAM pode ter estrutura diferente ou exigir
navegação manual. Sempre verifique a estrutura atual do site.

Autor: Engenheiro de Dados GIS
Versão: 1.0.0
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from typing import List, Dict, Optional
import time
import warnings

warnings.filterwarnings('ignore')


class ScraperIPAAM:
    """
    Classe para auxiliar na coleta de dados do Portal de Transparência do IPAAM.
    
    IMPORTANTE: O site do IPAAM pode mudar sua estrutura a qualquer momento.
    Este script serve como ponto de partida e pode precisar de ajustes.
    """
    
    BASE_URL = "https://www.ipaam.am.gov.br"
    TRANSPARENCIA_URL = f"{BASE_URL}/transparencia-tecnica/"
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    def __init__(self, pasta_downloads: str = 'downloads'):
        """
        Inicializa o scraper.
        
        Args:
            pasta_downloads: Pasta para salvar arquivos baixados
        """
        self.pasta_downloads = pasta_downloads
        os.makedirs(pasta_downloads, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def listar_links_planilhas(self) -> List[Dict]:
        """
        Lista links de planilhas disponíveis na página de transparência.
        
        Returns:
            Lista de dicionários com informações dos links
        """
        print(f"Acessando: {self.TRANSPARENCIA_URL}")
        
        try:
            response = self.session.get(self.TRANSPARENCIA_URL, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERRO] Erro ao acessar o site: {e}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        
        # Buscar links para arquivos Excel/CSV
        extensoes = ['.xlsx', '.xls', '.csv', '.pdf']
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            texto = a.get_text(strip=True)
            
            for ext in extensoes:
                if ext in href.lower():
                    link_info = {
                        'texto': texto,
                        'url': href if href.startswith('http') else f"{self.BASE_URL}{href}",
                        'extensao': ext
                    }
                    links.append(link_info)
                    break
        
        print(f"[OK] Encontrados {len(links)} links de arquivos")
        
        for i, link in enumerate(links, 1):
            print(f"   {i}. {link['texto'][:50]}... ({link['extensao']})")
        
        return links
    
    def baixar_arquivo(self, url: str, nome_arquivo: str = None) -> Optional[str]:
        """
        Baixa um arquivo da URL especificada.
        
        Args:
            url: URL do arquivo
            nome_arquivo: Nome para salvar (opcional)
            
        Returns:
            Caminho do arquivo baixado ou None se falhar
        """
        if not nome_arquivo:
            nome_arquivo = url.split('/')[-1]
        
        caminho = os.path.join(self.pasta_downloads, nome_arquivo)
        
        print(f"Baixando: {nome_arquivo}")
        
        try:
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            with open(caminho, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"[OK] Salvo em: {caminho}")
            return caminho
            
        except requests.RequestException as e:
            print(f"[ERRO] Erro ao baixar: {e}")
            return None
    
    def baixar_todos(self, filtro_extensao: str = None) -> List[str]:
        """
        Baixa todos os arquivos encontrados.
        
        Args:
            filtro_extensao: Filtrar por extensão (.xlsx, .csv, etc.)
            
        Returns:
            Lista de caminhos dos arquivos baixados
        """
        links = self.listar_links_planilhas()
        
        if filtro_extensao:
            links = [l for l in links if l['extensao'] == filtro_extensao]
        
        arquivos_baixados = []
        
        for link in links:
            time.sleep(1)  # Respeitar o servidor
            caminho = self.baixar_arquivo(link['url'])
            if caminho:
                arquivos_baixados.append(caminho)
        
        return arquivos_baixados


def manual_instrucoes():
    """
    Exibe instruções para coleta manual dos dados.
    """
    instrucoes = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║           INSTRUÇÕES PARA COLETA MANUAL DOS DADOS                ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    Como o site do IPAAM organiza os dados em arquivos separados (muitas
    vezes PDFs ou planilhas anuais), siga estes passos:
    
    PASSO 1: Acessar o Portal
    ────────────────────────────
    1. Acesse: https://www.ipaam.am.gov.br/transparencia-tecnica/
    2. Procure por "Licenças Concedidas" ou seções similares
    3. Navegue pelos anos de 2018 a 2025
    
    PASSO 2: Baixar Planilhas
    ────────────────────────────
    1. Baixe as planilhas/PDFs de cada ano
    2. Foque nas seções:
       - GECF (Gerência de Controle Florestal)
       - GELI (Gerência de Licenciamento Industrial)
    3. Salve tudo na pasta 'downloads/' deste projeto
    
    PASSO 3: Converter PDFs (se necessario)
    ──────────────────────────────────────────
    Se os dados estiverem em PDF, use ferramentas como:
    - Tabula (https://tabula.technology/)
    - Adobe Acrobat
    - Camelot (biblioteca Python)
    
    PASSO 4: Unificar os Dados
    ─────────────────────────────
    1. Abra todas as planilhas no Excel
    2. Padronize as colunas conforme o formato:
       - razao_social
       - municipio
       - tipo_licenca (LP, LI, LO)
       - gerencia (GECF, GELI)
       - atividade
       - latitude (se disponível)
       - longitude (se disponível)
       - data_emissao
       - data_validade
       - ano
    3. Una tudo em uma única planilha
    4. Salve como CSV em: dados/licencas_ipaam.csv
    
    PASSO 5: Geocodificar (se nao houver coordenadas)
    ────────────────────────────────────────────────────
    O script processamento_dados.py faz isso automaticamente!
    Ele converterá os nomes dos municípios em coordenadas.
    
    PASSO 6: Executar o Projeto
    ──────────────────────────────
    python main.py
    
    ════════════════════════════════════════════════════════════════════
    
    LINKS UTEIS:
    ───────────────
    • Portal Transparência: https://www.ipaam.am.gov.br/transparencia-tecnica/
    • Geoportal IPAAM: http://geoportal.ipaam.am.gov.br/
    • SIMLAM: https://simlam.ipaam.am.gov.br/ (Sistema de Licenciamento)
    
    ════════════════════════════════════════════════════════════════════
    """
    print(instrucoes)


def verificar_estrutura_site():
    """
    Verifica a estrutura atual do site do IPAAM e sugere abordagem.
    """
    print("\nVerificando estrutura do site IPAAM...")
    
    scraper = ScraperIPAAM()
    
    try:
        response = scraper.session.get(scraper.TRANSPARENCIA_URL, timeout=30)
        
        if response.status_code == 200:
            print("[OK] Site acessivel!")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Contar tipos de links
            todos_links = soup.find_all('a', href=True)
            links_xlsx = [l for l in todos_links if '.xlsx' in l['href'].lower() or '.xls' in l['href'].lower()]
            links_csv = [l for l in todos_links if '.csv' in l['href'].lower()]
            links_pdf = [l for l in todos_links if '.pdf' in l['href'].lower()]
            
            print(f"\nAnalise da pagina:")
            print(f"   • Links Excel (.xlsx/.xls): {len(links_xlsx)}")
            print(f"   • Links CSV: {len(links_csv)}")
            print(f"   • Links PDF: {len(links_pdf)}")
            
            if links_xlsx or links_csv:
                print("\n[OK] Ha planilhas disponiveis para download automatico!")
                print("   Execute: scraper.baixar_todos()")
            elif links_pdf:
                print("\n[!] Os dados parecem estar em PDF.")
                print("   Será necessário conversão manual para Excel/CSV.")
            else:
                print("\n[!] Nao foram encontrados arquivos de dados diretos.")
                print("   Pode ser necessário navegação manual no site.")
            
            # Listar seções encontradas
            headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            if headers:
                print("\nSecoes encontradas na pagina:")
                for h in headers[:10]:
                    texto = h.get_text(strip=True)
                    if texto:
                        print(f"   • {texto[:60]}")
        else:
            print(f"[!] Status: {response.status_code}")
            
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        print("\nSugestao: Acesse o site manualmente e siga as instrucoes.")
    
    manual_instrucoes()


if __name__ == "__main__":
    verificar_estrutura_site()
