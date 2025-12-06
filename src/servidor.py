# Servidor PUB/SUB simples com Sockets TCP

import socket
import threading
import json

# Dados globais
clientes = {}  # {socket: {'categorias': set}}
noticias = []
categorias = {'tecnologia', 'esportes', 'cultura', 'politica', 'saude'}
lock = threading.Lock()

def gerenciar_cliente(sock, addr):
    """Gerencia conexão de um cliente ou editor"""
    nome = f"Cliente_{addr[1]}"
    eh_editor = False
    
    with lock:
        clientes[sock] = {'categorias': set(), 'nome': nome}
    
    print(f"[+] {nome} conectado")
    
    try:
        sock.send("Bem-vindo! Categorias: tecnologia, esportes, cultura, politica, saude\n".encode())
        sock.send("Digite: INSCREVER <cat>, REMOVER <cat>, LISTAR ou SAIR\n".encode())
        
        while True:
            cmd = sock.recv(1024).decode().strip()
            if not cmd or cmd.upper() == 'SAIR':
                break
            
            # Verifica se é comando de publicação
            if cmd.startswith('pub '):
                eh_editor = True
                partes = cmd[4:].split('|')
                if len(partes) == 3:
                    publicar(partes[0].strip(), partes[1].strip(), partes[2].strip())
                    sock.send("Noticia publicada!\n".encode())
                else:
                    sock.send("Erro: formato deve ser: pub titulo|resumo|categoria\n".encode())
                continue
            
            partes = cmd.split()
            acao = partes[0].upper()
            
            with lock:
                if sock not in clientes:
                    break
                    
                if acao == 'INSCREVER' and len(partes) > 1:
                    for cat in partes[1:]:
                        if cat.lower() in categorias:
                            clientes[sock]['categorias'].add(cat.lower())
                            sock.send(f"OK: inscrito em {cat}\n".encode())
                        else:
                            sock.send(f"Erro: {cat} inválido\n".encode())
                
                elif acao == 'REMOVER' and len(partes) > 1:
                    for cat in partes[1:]:
                        clientes[sock]['categorias'].discard(cat.lower())
                    sock.send(f"OK: removido\n".encode())
                
                elif acao == 'LISTAR':
                    cats = ', '.join(clientes[sock]['categorias']) or 'nenhuma'
                    sock.send(f"Inscrições: {cats}\n".encode())
                
                else:
                    sock.send("Comando inválido\n".encode())
    
    except:
        pass
    
    with lock:
        if sock in clientes:
            print(f"[-] {clientes[sock]['nome']} desconectado")
            del clientes[sock]
    
    sock.close()

def publicar(titulo, resumo, cat):
    """Publica notícia para inscritos"""
    cat = cat.lower()
    if cat not in categorias:
        print("Categoria inválida")
        return
    
    msg = f"[{cat.upper()}] {titulo}: {resumo}\n"
    
    with lock:
        noticias.append({'titulo': titulo, 'categoria': cat})
        notificados = 0
        for sock, info in list(clientes.items()):
            if cat in info['categorias']:
                try:
                    sock.send(msg.encode())
                    notificados += 1
                except:
                    pass
    
    print(f"Publicada: {titulo} -> {notificados} clientes")

def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(('localhost', 5000))
    servidor.listen(5)
    
    print("Servidor rodando em localhost:5000")
    print("Aguardando clientes e publicadores...\n")
    
    def aceitar_conexoes():
        while True:
            try:
                sock, addr = servidor.accept()
                t = threading.Thread(target=gerenciar_cliente, args=(sock, addr))
                t.daemon = True
                t.start()
            except:
                break
    
    t = threading.Thread(target=aceitar_conexoes)
    t.daemon = True
    t.start()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServidor encerrando...")
    finally:
        servidor.close()

if __name__ == '__main__':
    main()
