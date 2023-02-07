import os
import socket
import sys
import threading

"""
This function will be given to each new thread to execute.
Will loop for new actions and appropriate send responses. 
"""
def handle_client(connection, address):
# Receive the data in small chunks and retransmit it
    while True:
        data = connection.recv(1024)
        client_msg = data.decode("utf-8")
        if client_msg == 'Connect':
            connection.sendall(b'Welcome to the File Server!')
        elif client_msg == "LIST":
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
        elif client_msg == "PUSH":
            filename = connection.recv(1024)
            filename = filename.decode("utf-8")
            print(filename)
            file = open(path + "/" + filename, "w")
            body = connection.recv(1024)
            body = body.decode("utf-8")
            print(data)
            file.write(body)
            response = "Received the file " + filename + "!"
            response = response.encode("utf-8")
            connection.sendall(response)
            file.close()
        elif client_msg == "DELETE":
            print('here')
            filename = connection.recv(1024)
            filename = filename.decode("utf-8")
            filelist = os.listdir(path)
            print(filelist)
            if filelist == []:
                connection.sendall(b'Server directory is empty!')
            elif filename not in filelist:
                connection.sendall(b'File not found!')
            else:
                os.remove(path + "/" + filename)
                connection.sendall(b'File found!')
        elif client_msg == "EXIT":
            print(address, "Has gracefully exited the socket.")
            break
        else:
            print('no data from', client_address)
            break

    connection.close()


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10001)
print('[STARTING] Server is starting...')
sock.bind(server_address)

# Listen for incoming connections
sock.listen()
absolute_path = os.path.dirname(__file__)
print(absolute_path)
relative_path = "/server_data"
path = absolute_path + relative_path
print('[LISTENTING] server is listening...')

while True:
    # Wait for a connection
    connection, client_address = sock.accept()
    print('[NEW CONNECTION]', client_address, 'connected.')
    # Create and start a new thread for every new connection
    t = threading.Thread(target=handle_client, args=(connection, client_address))
    t.start()

        
