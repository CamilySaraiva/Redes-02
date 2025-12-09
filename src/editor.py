import socket
import time

HOST = '127.0.0.1'
PORT = 5000

# Estilos
RESET = '\033[0m'
BOLD = '\033[1m'

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Aguarda 1 segundo para o servidor iniciar
    time.sleep(1)
    
    print("\n=== EDITOR DE NOTÍCIAS (PUBLISHER UDP) ===")
    print(f"{BOLD}Categorias:{RESET} tecnologia, esportes, cultura, politica, saude\n")
    
    while True:
        try:
            titulo = input(f"{BOLD}Título{RESET} (ou Enter para sair): ").strip()
            if not titulo:
                break
            
            resumo = input(f"{BOLD}Resumo{RESET}: ").strip()
            categoria = input(f"{BOLD}Categoria{RESET}: ").strip().lower()
            
            # Monta mensagem
            mensagem = f"pub {titulo}|{resumo}|{categoria}"
            
            # Envia para servidor
            sock.sendto(mensagem.encode('utf-8'), (HOST, PORT))
            
            # Tenta receber confirmação
            try:
                sock.settimeout(2.0)
                dados, _ = sock.recvfrom(1024)
                print(dados.decode('utf-8'))
            except socket.timeout:
                print("[ERRO]  Sem resposta do servidor (ele está rodando?)")
            except Exception as e:
                print(f"Erro ao receber resposta: {e}")
            
            print("=" * 50 + "\n")
            print()
        
        except KeyboardInterrupt:
            print("\nAté logo!")
            break
        except Exception as e:
            print(f"Erro: {e}")
    
    sock.close()

if __name__ == '__main__':
    main()