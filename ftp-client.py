import socket

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8080
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    try:
        while True:
            while True:
                filename = input('Input filename you want to transfer: ')
                try:
                    with open(filename, 'r') as file:
                        print('Sending file:', filename)
                        data = file.read()
                        if not data:
                            break
                        while data:
                            sock.send(str(data).encode())
                            data = file.read()
                    print('File sent successfully.')
                except IOError:
                    print('Invalid filename.')
    except KeyboardInterrupt:
        print('Client closing.')
