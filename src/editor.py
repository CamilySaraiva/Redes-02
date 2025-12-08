import socket
import time

HOST = '127.0.0.1'
PORT = 5000

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Aguarda 1 segundo para o servidor iniciar
    time.sleep(1)
    
    print("📝 Editor de Notícias (UDP)")
    print("Categorias: tecnologia, esportes, cultura, politica, saude\n")
    
    while True:
        try:
            titulo = input("Título (ou Enter para sair): ").strip()
            if not titulo:
                break
            
            resumo = input("Resumo: ").strip()
            categoria = input("Categoria: ").strip().lower()
            
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
                print("⚠️  Sem resposta do servidor (ele está rodando?)")
            except Exception as e:
                print(f"Erro ao receber resposta: {e}")
            
            print()
        
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except Exception as e:
            print(f"Erro: {e}")
    
    sock.close()

if __name__ == '__main__':
    main()