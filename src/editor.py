# Editor simples - publica notícias

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect(('localhost', 5000))
    print("Conectado ao servidor de notícias\n")
    print("Categorias: tecnologia, esportes, cultura, politica, saude\n")
    
    while True:
        titulo = input("Título: ").strip()
        if not titulo:
            break
        
        resumo = input("Resumo: ").strip()
        categoria = input("Categoria: ").strip()
        
        # Formato: pub titulo|resumo|categoria
        sock.send(f"pub {titulo}|{resumo}|{categoria}\n".encode())
        print()

except ConnectionRefusedError:
    print("Erro: Servidor não está rodando")
except KeyboardInterrupt:
    print("\nFinalizado")
finally:
    sock.close()
