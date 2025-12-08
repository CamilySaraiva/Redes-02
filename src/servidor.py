import socket
import threading
import json
import os
from datetime import datetime

# Configurações
HOST = '127.0.0.1'
PORT = 5000
ARQUIVO_NOTICIAS = 'noticias.json'

# Armazena clientes: {endereço: [categorias]}
clientes = {}
categorias_disponiveis = ['tecnologia', 'esportes', 'cultura', 'politica', 'saude']

# Repositório de notícias em memória
repositorio_noticias = []

# Lock para acesso seguro
lock = threading.Lock()

def carregar_noticias():
    """Carrega notícias do arquivo JSON ao iniciar o servidor"""
    global repositorio_noticias
    if os.path.exists(ARQUIVO_NOTICIAS):
        try:
            with open(ARQUIVO_NOTICIAS, 'r', encoding='utf-8') as f:
                repositorio_noticias = json.load(f)
            print(f"[INFO] {len(repositorio_noticias)} noticia(s) carregada(s) do arquivo")
        except Exception as e:
            print(f"[ERRO] Erro ao carregar noticias: {e}")
            repositorio_noticias = []
    else:
        repositorio_noticias = []

def salvar_noticias():
    """Salva notícias no arquivo JSON"""
    try:
        with open(ARQUIVO_NOTICIAS, 'w', encoding='utf-8') as f:
            json.dump(repositorio_noticias, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERRO] Erro ao salvar noticias: {e}")

def adicionar_noticia(titulo, resumo, categoria):
    """Adiciona notícia ao repositório"""
    noticia = {
        'id': len(repositorio_noticias) + 1,
        'titulo': titulo,
        'resumo': resumo,
        'categoria': categoria,
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    repositorio_noticias.append(noticia)
    salvar_noticias()
    print(f"[SALVO] Noticia #{noticia['id']} salva no repositorio")
    return noticia

def listar_noticias_categoria(categoria):
    """Lista notícias de uma categoria específica"""
    return [n for n in repositorio_noticias if n['categoria'] == categoria]

def publicar_noticia(noticia, sock):
    """Publica noticia para clientes inscritos"""
    categoria = noticia['categoria']
    mensagem_noticia = f"\n{'='*50}\n[NOTICIA] #{noticia['id']} [{categoria.upper()}]\n{'-'*50}\n{noticia['titulo']}\n{noticia['resumo']}\n{noticia['data']}\n{'='*50}\n"
    enviados = 0
    
    with lock:
        for endereco, cats in clientes.items():
            if categoria in cats:
                try:
                    sock.sendto(mensagem_noticia.encode('utf-8'), endereco)
                    enviados += 1
                    print(f"  [ENVIADO] Para {endereco}")
                except Exception as e:
                    print(f"[ERRO] Falha ao enviar para {endereco}: {e}")
    
    print(f"[PUBLICADO] #{noticia['id']} '{noticia['titulo']}' em '{categoria}' para {enviados} cliente(s)")

def processar_mensagem(dados, endereco, sock):
    """Processa mensagem do cliente/editor"""
    try:
        mensagem = dados.decode('utf-8').strip()
        print(f"\n[RECEBIDO] {endereco}: {mensagem}")
        
        partes = mensagem.split(maxsplit=1)
        comando = partes[0].upper()
        resposta = None
        
        # Processa comando
        if comando == 'INSCREVER':
            if len(partes) > 1:
                cats = partes[1].split()
                with lock:
                    if endereco not in clientes:
                        clientes[endereco] = []
                        print(f"[NOVO] Cliente {endereco}")
                    
                    for cat in cats:
                        cat = cat.lower()
                        if cat in categorias_disponiveis and cat not in clientes[endereco]:
                            clientes[endereco].append(cat)
                    
                    resposta = f"[OK] Inscrito em: {', '.join(clientes[endereco])}"
                    print(f"[INSCRITO] {endereco} em {clientes[endereco]}")
            else:
                resposta = "[ERRO] Uso: INSCREVER categoria1 categoria2 ..."
        
        elif comando == 'REMOVER':
            with lock:
                if endereco in clientes and len(partes) > 1:
                    cats = partes[1].split()
                    for cat in cats:
                        cat = cat.lower()
                        if cat in clientes[endereco]:
                            clientes[endereco].remove(cat)
                    resposta = f"[OK] Removido. Inscricoes atuais: {', '.join(clientes[endereco]) or 'Nenhuma'}"
                else:
                    resposta = "[ERRO] Voce nao esta inscrito em nenhuma categoria"
        
        elif comando == 'LISTAR':
            with lock:
                if endereco in clientes and clientes[endereco]:
                    resposta = f"Suas inscricoes: {', '.join(clientes[endereco])}"
                else:
                    resposta = "Voce nao esta inscrito em nenhuma categoria"
        
        elif comando == 'CATEGORIAS':
            resposta = f"Categorias disponíveis: {', '.join(categorias_disponiveis)}"
        
        elif comando == 'HISTORICO':
            if len(partes) > 1:
                categoria = partes[1].strip().lower()
                noticias = listar_noticias_categoria(categoria)
                if noticias:
                    resposta = f"\n📚 HISTÓRICO [{categoria.upper()}] - {len(noticias)} notícia(s):\n"
                    for n in noticias[-10:]:
                        resposta += f"\n#{n['id']} - {n['data']}\n📌 {n['titulo']}\n💬 {n['resumo']}\n{'-'*40}"
                else:
                    resposta = f"Nenhuma notícia encontrada em '{categoria}'"
            else:
                total = len(repositorio_noticias)
                resposta = f"📚 Total de notícias no repositório: {total}\nUso: HISTORICO categoria"
        
        elif comando == 'PUB':
            if len(partes) > 1:
                dados_noticia = partes[1].split('|')
                if len(dados_noticia) == 3:
                    titulo, resumo, categoria = [d.strip() for d in dados_noticia]
                    categoria = categoria.lower()
                    
                    if categoria in categorias_disponiveis:
                        with lock:
                            noticia = adicionar_noticia(titulo, resumo, categoria)
                        publicar_noticia(noticia, sock)
                        resposta = f"✓ Notícia #{noticia['id']} publicada e salva!"
                    else:
                        resposta = f"✗ Categoria inválida. Use: {', '.join(categorias_disponiveis)}"
                else:
                    resposta = "✗ Formato: pub titulo|resumo|categoria"
            else:
                resposta = "✗ Formato: pub titulo|resumo|categoria"
        
        else:
            resposta = f"✗ Comando desconhecido: {comando}"
        
        # Envia resposta
        if resposta:
            try:
                sock.sendto((resposta + "\n").encode('utf-8'), endereco)
                print(f"  📤 Resposta enviada para {endereco}")
            except Exception as e:
                print(f"[ERRO] Falha ao enviar resposta: {e}")
    
    except Exception as e:
        print(f"[ERRO] processar_mensagem: {e}")

def main():
    carregar_noticias()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(1.0)
    
    print(f"🚀 Servidor UDP rodando em {HOST}:{PORT}")
    print(f"📂 Categorias: {', '.join(categorias_disponiveis)}")
    print(f"💾 Repositório: {len(repositorio_noticias)} notícia(s) em memória\n")
    
    rodando = True
    while rodando:
        try:
            dados, endereco = sock.recvfrom(4096)
            # Processa na thread principal para evitar race conditions
            processar_mensagem(dados, endereco, sock)
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            print("\n\n[SERVIDOR] Encerrando...")
            print(f"💾 {len(repositorio_noticias)} notícia(s) salva(s) em '{ARQUIVO_NOTICIAS}'")
            rodando = False
        except Exception as e:
            print(f"[ERRO] main loop: {e}")
    
    sock.close()

if __name__ == '__main__':
    main()