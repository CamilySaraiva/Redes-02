import socket
import select
import time

HOST = '127.0.0.1'
PORT = 5000

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Aguarda 1 segundo para o servidor iniciar
    time.sleep(1)
    
    print("Cliente de Notícias (UDP)")
    print("\nComandos:")
    print("  INSCREVER tecnologia esportes")
    print("  LISTAR")
    print("  REMOVER tecnologia")
    print("  CATEGORIAS")
    print("  HISTORICO tecnologia")
    print("  SAIR\n")
    
    while True:
        try:
            # Usa select para fazer I/O não-bloqueante
            rlist, _, _ = select.select([sock], [], [], 0.1)
            
            # Se há mensagens do servidor
            if rlist:
                try:
                    dados, endereco = sock.recvfrom(4096)
                    mensagem = dados.decode('utf-8')
                    if mensagem.strip():
                        print(f"\n{mensagem}", end='', flush=True)
                except:
                    pass
            
            # Tenta ler entrada do usuário com timeout
            try:
                mensagem = input("> ").strip()
                
                if not mensagem:
                    continue
                
                if mensagem.upper() == 'SAIR':
                    print("👋 Até logo!")
                    break
                
                # Envia para servidor
                sock.sendto(mensagem.encode('utf-8'), (HOST, PORT))
                
            except EOFError:
                break
            
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except Exception as e:
            print(f"Erro: {e}")
    
    sock.close()

if __name__ == '__main__':
    main()