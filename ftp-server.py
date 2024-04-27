import socket

if __name__ == '__main__':
    conn = 0
    addr = 0
    try:
        host = '192.168.12.197'
        port = 8080
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(1)
        conn, addr = sock.accept()
        sock.settimeout(2)
        print(f'Client connected from {addr}')
        while True:
            data = conn.recv(1024).decode()
            if not data:
                continue
            print('Receiving file from client')
            filename = 'output.txt'
            with open('output.txt', 'w') as file:
                while data:
                    if not data:
                        print('Data empty')
                        break
                    else:
                        print('Writing:', data)
                        file.write(data)
                        data = conn.recv(1024).decode()
            print('Received successfully!')
    except socket.timeout:
        conn.close()
        print('Connection closed', addr, '\nClosing server.')
    except KeyboardInterrupt:
        conn.close()
        print('Connection closed', addr, '\nClosing server.')
