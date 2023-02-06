import os
import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10001)
print('[STARTING] Server is starting...')
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
absolute_path = os.path.dirname(__file__)
print(absolute_path)
relative_path = "/server_data"
path = absolute_path + relative_path

while True:
    # Wait for a connection
    print('[LISTENTING] server is listening...')
    connection, client_address = sock.accept()
    try:
        print('[NEW CONNECTION]', client_address, 'connected.')

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1024)
            realmes = data.decode("utf-8")
            if realmes == 'Connect':
                connection.sendall(b'Welcome to the File Server!')
            elif realmes == "LIST":
                filelist = os.listdir(path)
                fileformat = ""
                for i in filelist:
                    fileformat = fileformat + i + "\n"
                print(fileformat)

                if fileformat == '':
                    connection.sendall(b'Server directory is empty!')
                else:
                    file = fileformat.encode('utf-8')
                    connection.sendall(file)

            else:
                print('no data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
