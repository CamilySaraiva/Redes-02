import socket
import threading
import sys
import time

HOST = '127.0.0.1'
PORT = 5000

# Flag para controlar quando estamos esperando resposta de comando
esperando_resposta = False #Flag: True quando aguardamos resposta de comando
lock = threading.Lock() # Semáforo para acesso seguro à flag

def receber_mensagens(sock):
    """Thread dedicada para receber mensagens do servidor"""
    global esperando_resposta
    while True: # Loop infinito para receber mensagens
        try:
            sock.settimeout(0.5)  # Timeout curto para verificar flags
            try:
                dados, _ = sock.recvfrom(4096) # Recebe dados (até 4KB)
                mensagem = dados.decode('utf-8')
                
                if mensagem.strip():
                    with lock:
                        # Se estamos esperando resposta de comando, não imprime aqui
                        if not esperando_resposta:
                            # Limpa a linha atual e imprime a mensagem (notificação push)
                            print(f"\r{mensagem}")
                            # Reimprime o prompt
                            print("> ", end='', flush=True)
                        else:
                            # Deixa a mensagem no buffer para o main thread pegar
                            # Retorna para o buffer "simulado" através de uma nova recepção
                            pass
            except socket.timeout:
                continue
        except Exception as e:
            break

def main():
    global esperando_resposta
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print("\n=== CLIENTE DE NOTÍCIAS (UDP) ===")
    print("\nComandos:")
    print("  INSCREVER categoria1 categoria2")
    print("  LISTAR")
    print("  REMOVER categoria")
    print("  CATEGORIAS")
    print("  HISTORICO categoria")
    print("  SAIR\n")
    
    # Inicia thread para receber mensagens
    thread_receber = threading.Thread(target=receber_mensagens, args=(sock,), daemon=True)
    thread_receber.start()
    
    while True:
        try:
            mensagem = input("> ").strip() # aguarda entrada do usuário
            
            if not mensagem:
                continue
            
            if mensagem.upper() == 'SAIR':
                print("Saindo...")
                break
            
            # Marca que estamos esperando resposta
            with lock:
                esperando_resposta = True
            
            # Envia para servidor
            sock.sendto(mensagem.encode('utf-8'), (HOST, PORT))
            
            # Aguarda resposta do comando
            try:
                sock.settimeout(2.0)
                dados, _ = sock.recvfrom(4096)
                resposta = dados.decode('utf-8')
                print(resposta)
            except socket.timeout:
                print("[TIMEOUT] Sem resposta do servidor")
            finally:
                with lock:
                    esperando_resposta = False
            
        except KeyboardInterrupt:
            print("\nAté logo!")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"Erro: {e}")
    
    sock.close()

if __name__ == '__main__':
    main()