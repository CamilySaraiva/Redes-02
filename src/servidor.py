import socket
import threading
import json
import os
import textwrap
from datetime import datetime

# Configurações
HOST = '127.0.0.1' # localhost - servidor que roda localmente
PORT = 5000 #porta que o servidor escuta
ARQUIVO_NOTICIAS = 'noticias.json' # arquivo para persistência das notícias

# Cores para terminal
class Cor:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    VERDE = '\033[92m'
    AZUL = '\033[94m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    CIANO = '\033[96m'
    MAGENTA = '\033[95m'
    CINZA = '\033[90m'

# Categorias e suas cores
CORES_CATEGORIA = {
    'tecnologia': Cor.CIANO,
    'esportes': Cor.AMARELO,
    'cultura': Cor.MAGENTA,
    'politica': Cor.VERMELHO,
    'saude': Cor.VERDE
}

clientes = {}          # Mapeia endereços de clientes para suas inscrições
categorias_disponiveis = ['tecnologia', 'esportes', 'cultura', 'politica', 'saude']
repositorio_noticias = []       # Lista de todas as notícias em memória
lock = threading.Lock()         # Semáforo para evitar race condition entre threads


def formatar_noticia_card(noticia):
    #Cria um visual de cartão usando caracteres de caixa
    largura = 60
    cat = noticia['categoria']
    cor_tema = CORES_CATEGORIA.get(cat, Cor.RESET)
    
    # Bordas da caixinha
    borda_sup = f"{cor_tema}╔{'═' * largura}╗{Cor.RESET}"
    borda_inf = f"{cor_tema}╚{'═' * largura}╝{Cor.RESET}"
    sep = f"{cor_tema}╟{'─' * largura}╢{Cor.RESET}"
    lateral = f"{cor_tema}║{Cor.RESET}"
    
    # Conteúdo Formatado
    titulo_lines = textwrap.wrap(noticia['titulo'], width=largura-4)
    resumo_lines = textwrap.wrap(noticia['resumo'], width=largura-4)
    
    card = []
    card.append(borda_sup)          # Topo da caixa
    
    titulo_lines = textwrap.wrap(noticia['titulo'].upper(), width=largura-4)    # Título
    
    for line in titulo_lines:
        card.append(f"{lateral} {Cor.BOLD}{line:<{largura-2}}{Cor.RESET} {lateral}")
    
    card.append(sep)    # Separador
    resumo_lines = textwrap.wrap(noticia['resumo'], width=largura-4)    # Resumo
    
    if not resumo_lines:            # Se não tiver resumo, coloca uma linha em branco
        resumo_lines = [""]

    for line in resumo_lines:
        card.append(f"{lateral} {line:<{largura-2}} {lateral}")
        
    card.append(sep)    # Separador
    
    meta_info = f"[{cat.upper()}]  {noticia['data']}  ID:{noticia['id']}"     # Rodapé (categoria | data | id)
    
    if len(meta_info) > largura - 2:
        meta_info = meta_info[:largura-5] + "..."
        
    # Adiciona o rodapé
    card.append(f"{lateral} {Cor.CINZA}{meta_info:<{largura-2}}{Cor.RESET} {lateral}")
    card.append(borda_inf)
    
    return "\n".join(card)

def carregar_noticias():
    #Carrega notícias do arquivo JSON ao iniciar o servidor
    global repositorio_noticias 
    if os.path.exists(ARQUIVO_NOTICIAS):
        try:
            with open(ARQUIVO_NOTICIAS, 'r', encoding='utf-8') as f:
                repositorio_noticias = json.load(f) #carrega o json
            print(f"{Cor.VERDE}[INFO] {len(repositorio_noticias)} noticias carregadas.{Cor.RESET}")
        except Exception as e:
            print(f"{Cor.VERMELHO}[ERRO] {e}{Cor.RESET}")
            repositorio_noticias = [] # Se der erro, inicia vazio
    else:
        repositorio_noticias = [] # Inicia vazio se o arquivo não existir

def salvar_noticias():
    #Salva notícias no arquivo JSON
    try:
        with open(ARQUIVO_NOTICIAS, 'w', encoding='utf-8') as f:
            json.dump(repositorio_noticias, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{Cor.VERMELHO}[ERRO] Erro ao salvar noticias: {e}{Cor.RESET}")

def adicionar_noticia(titulo, resumo, categoria):
    #Adiciona notícia ao repositório
    noticia = {
        'id': len(repositorio_noticias) + 1,
        'titulo': titulo,
        'resumo': resumo,
        'categoria': categoria,
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    repositorio_noticias.append(noticia) # Adiciona à lista
    salvar_noticias() # Salva no arquivo  
    print(f"{Cor.VERDE}[SALVO]{Cor.RESET} Noticia #{noticia['id']} adicionada.")
    return noticia

def listar_noticias_categoria(categoria):
    #Lista notícias de uma categoria específica
    return [n for n in repositorio_noticias if n['categoria'] == categoria]

def publicar_noticia(noticia, sock):
    # Publica notícia para os clientes inscritos na categoria
    mensagem_visual = formatar_noticia_card(noticia)
    categoria = noticia['categoria']
    enviados = 0
    
    with lock: # Evita race conditions ao acessar clientes
        for endereco, cats in clientes.items():
            if categoria in cats:
                try:
                    # Envia a notícia formatada via UDP para o endereço do cliente
                    sock.sendto(mensagem_visual.encode('utf-8'), endereco)
                    enviados += 1
                    print(f"  {Cor.VERDE}[ENVIADO]{Cor.RESET} Para {endereco}")
                except Exception as e:
                    print(f"{Cor.VERMELHO}[ERRO] Falha ao enviar para {endereco}: {e}{Cor.RESET}")
    
    print(f"{Cor.AZUL}[PUBLICADO]{Cor.RESET} #{noticia['id']} para {enviados} cliente(s).")

def processar_mensagem(dados, endereco, sock):
    #Processa mensagem do cliente/editor
    try:
        mensagem = dados.decode('utf-8').strip() #Decodifica bytes para string
        print(f"\n{Cor.AZUL}[RECEBIDO]{Cor.RESET} {endereco}: {mensagem}")
        
        partes = mensagem.split(maxsplit=1) # Divide comando e argumentos
        comando = partes[0].upper() # Comando em maiúsculas
        resposta = None 
        
        # Processamento dos comandos
        if comando == 'INSCREVER':
            if len(partes) > 1:
                cats = partes[1].split() # Divide categorias por espaço
                with lock: # protege acesso a clientes
                    if endereco not in clientes:
                        clientes[endereco] = []
                        print(f"{Cor.AZUL}[NOVO]{Cor.RESET} Cliente {endereco}")
                    
                    added = []
                    for cat in cats:
                        cat = cat.lower()
                        if cat in categorias_disponiveis and cat not in clientes[endereco]:
                            clientes[endereco].append(cat)
                            added.append(cat)
                    
                    resposta = f"{Cor.VERDE}[OK] ✓ Inscrito em: {', '.join(clientes[endereco])}{Cor.RESET}"
            else:
                resposta = f"{Cor.AMARELO}⚠ Uso: INSCREVER categoria{Cor.RESET}"
        
        elif comando == 'REMOVER':
            with lock:
                if endereco in clientes and len(partes) > 1:
                    cats = partes[1].split()
                    for cat in cats:
                        cat = cat.lower()
                        if cat in clientes[endereco]:
                            clientes[endereco].remove(cat)
                    resposta = f"{Cor.VERDE}[OK] Removido. Inscricoes atuais: {', '.join(clientes[endereco]) or 'Nenhuma'}{Cor.RESET}"
                else:
                    resposta = f"{Cor.VERMELHO}✗ Erro ou não inscrito.{Cor.RESET}"

        elif comando == 'LISTAR':
            with lock:
                if endereco in clientes and clientes[endereco]:
                    resposta = f"{Cor.CINZA}Suas inscricoes: {', '.join(clientes[endereco])}{Cor.RESET}"
                else:
                    resposta = f"{Cor.CINZA}Nenhuma inscrição ativa.{Cor.RESET}"
        
        elif comando == 'CATEGORIAS':
            resposta = f"{Cor.AMARELO}Categorias:{Cor.RESET} {Cor.BOLD}{', '.join(categorias_disponiveis)}{Cor.RESET}"
        
        elif comando == 'HISTORICO':
            if len(partes) > 1:
                categoria = partes[1].strip().lower()
                noticias = listar_noticias_categoria(categoria)
                if noticias:
                    resposta = f"\n{Cor.BOLD}=== HISTÓRICO: {categoria.upper()} ==={Cor.RESET}\n"
                    for n in noticias[-10:]:  # Últimas 10 notícias
                        resposta += formatar_noticia_card(n) + "\n"
                else:
                    resposta = f"Nenhuma notícia em '{categoria}'"
            else:
                resposta = f"{Cor.AMARELO}Uso: HISTORICO categoria{Cor.RESET}"

        elif comando == 'PUB':
            if len(partes) > 1:
                # formato: pub titulo|resumo|categoria
                dados_noticia = partes[1].split('|')
                if len(dados_noticia) == 3:
                    titulo, resumo, categoria = [d.strip() for d in dados_noticia]
                    categoria = categoria.lower()
                    
                    if categoria in categorias_disponiveis:
                        with lock:
                            noticia = adicionar_noticia(titulo, resumo, categoria)
                        publicar_noticia(noticia, sock)
                        resposta = f"{Cor.VERDE}✓ Publicado #{noticia['id']}{Cor.RESET}"
                    else:
                        resposta = f"{Cor.VERMELHO}✗ Categoria inválida{Cor.RESET}"
                else:
                    resposta = f"{Cor.AMARELO}Formato incorreto{Cor.RESET}"
            else:
                resposta = f"{Cor.AMARELO}Formato: pub titulo|resumo|cat{Cor.RESET}"
        
        else:
            resposta = f"{Cor.VERMELHO}✗ Comando desconhecido: {comando}{Cor.RESET}"
        
        # Envia resposta
        if resposta:
            try:
                sock.sendto((resposta + "\n").encode('utf-8'), endereco)
                print(f"  Resposta enviada para {Cor.VERDE}{endereco}{Cor.RESET}")
            except Exception as e:
                print(f"{Cor.VERMELHO}[ERRO] Falha ao enviar resposta:{Cor.RESET} {e}")
    
    except Exception as e:
        print(f"{Cor.VERMELHO}[ERRO] processar:{Cor.RESET} {e}")

def main():
    carregar_noticias() # Carrega notícias salvas ao iniciar
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Cria socket UDP
    sock.bind((HOST, PORT)) # Liga ao endereço e porta
    sock.settimeout(1.0)
    
    print(f"{Cor.BOLD}SERVIDOR UDP ONLINE{Cor.RESET} porta {PORT}")
    
    rodando = True
    while rodando:
        try:
            dados, endereco = sock.recvfrom(4096) # espera receber dados (até 4KB)
            processar_mensagem(dados, endereco, sock)   # Processa na thread principal
        except socket.timeout:
            continue # Timeout para permitir checagem de encerramento
        except KeyboardInterrupt: # Ctrl+C para encerrar
            print(f"\n\n{Cor.AMARELO}[SERVIDOR] Encerrando...{Cor.RESET}")
            print(f"{Cor.CINZA}💾 {len(repositorio_noticias)} notícia(s) salva(s) em '{ARQUIVO_NOTICIAS}'{Cor.RESET}")
            rodando = False
            salvar_noticias() # Salva notícias ao encerrar
    sock.close() # Fecha o socket

if __name__ == '__main__':
    main()