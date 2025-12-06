# Cliente PUB/SUB simples

import socket
import threading

def receber():
    """Thread para receber mensagens"""
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print(msg, end='')
        except:
            break

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect(('localhost', 5000))
    print("Conectado ao servidor!\n")
    
    # Thread de recepção
    t = threading.Thread(target=receber)
    t.daemon = True
    t.start()
    
    # Loop de entrada
    while True:
        cmd = input("> ")
        sock.send(cmd.encode())
        if cmd.upper() == 'SAIR':
            break

except ConnectionRefusedError:
    print("Erro: Servidor não está rodando em localhost:5000")
except KeyboardInterrupt:
    print("\nDesconectado")
finally:
    sock.close()
