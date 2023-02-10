import os
import socket
import sys
import threading

"""
This function will deconstruct the protocols sent over from the client
The function will return the filename, size and body of the file from the protocol string
Example deconstruction of the protocol is as follows:
input = 'filename: file.txt filesize: 6 filebody: this is a file'
output = ('file.txt', '6', 'this is a file')
Note: the filesize and filebody will only have data for the PUSH command
"""


def deconstruct_protocol(p):
    name_index = 10
    size_index = p.find("filesize", 9)
    body_index = p.find("filebody", 18)

    name_val = p[10:size_index - 1]
    size_val = p[size_index + 10:]


    return (name_val, size_val)


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
            segment = connection.recv(1024)
            connection.sendall(b'got')
            filename, size = deconstruct_protocol(segment.decode("utf-8"))
            print(filename, size)
            file = open(path + "/" + filename, "wb")
            # body = connection.recv(1024)
            # body = body.decode("utf-8")
            # print(data)

            if int(size) > 0:
                loopcount = (int(size) // 1024)
                data = connection.recv(1024)
                for _ in range(loopcount):
                    data = data + connection.recv(1024)

            file.write(data)
            response = "Received the file " + filename + "!"
            response = response.encode("utf-8")
            connection.sendall(response)
            file.close()

        elif client_msg == "DELETE":
            segment = connection.recv(1024)

            filename, size = deconstruct_protocol(segment.decode("utf-8"))

            filelist = os.listdir(path)
            print(filelist)
            if filelist == []:
                connection.sendall(b'Server directory is empty!')
            elif filename not in filelist:
                connection.sendall(b'File not found!')
            else:
                os.remove(path + "/" + filename)
                connection.sendall(b'File found!')

        elif client_msg == "OVERWRITE":
            segment = connection.recv(1024)
            filename, size = deconstruct_protocol(segment.decode("utf-8"))

            print(filename)

            filelist = os.listdir(path)
            check = False
            for i in filelist:
                if i == filename:
                    check = True

            if not check:
                connection.sendall(b'File not found!')
            else:
                file = open(path + "/" + filename, "w")
                overwrite_body = "This is some hardcoded text to overwrite a file with."
                file.write(overwrite_body)
                response = "The file " + filename + " overwritten!"
                response = response.encode("utf-8")
                connection.sendall(response)
                file.close()

        elif client_msg == "EXIT":
            print(address, "Has gracefully exited the socket.")
            break
        else:
            print('no data from', client_address)
            print(client_msg)
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