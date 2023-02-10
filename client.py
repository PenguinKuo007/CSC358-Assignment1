import socket
import sys
import os

"""
This function will construct the protocols sent over to the server
The protocol is a byte string with the filename, size and body of the file.
Example construction of the protocol is as follows:
input = ('file.txt', 6, 'this is a file')
output = b'filename: file.txt filesize: 14 filebody: this is a file'
Note: the filesize and filebody will only have data for the PUSH command
"""

def construct_protocol(name, size):
    protocol = f'filename: {name} filesize: {size}'

    return protocol.encode("utf-8")


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10001)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:

    sock.sendall(b'Connect')  # connect to the server side
    data = sock.recv(1024)
    print(data.decode("utf-8"))

    while True:
        command = input(">")  # ask user to input the command

        # If the command is a LIST command, then send corresponding protocol to server
        if 'LIST' in command:
            sock.sendall(b'LIST')

        # If the command is a PUSH command, then send corresponding protocol to server
        elif 'PUSH' in command:
            sock.sendall(b'PUSH')
            filename = command.replace('PUSH', '')
            filename = filename.replace(' ', '')
            # sock.sendall(filename.encode("utf-8"))
            file = open('client_data/' + filename, "rb")
            body = file.read()

            # Get the attributes of the file to get the filesize in bytes
            file_stats = os.stat('client_data/' + filename)
            # Construct the protocol using the helper function with the file info
            segment = construct_protocol(filename, file_stats.st_size)
            # Send the segment
            sock.sendall(segment)
            # Separating the the sendall
            sock.recv(1024)
            # Send the content of the file
            sock.sendall(body)
            file.close()

        # If the command is a DELETE command, then send corresponding protocol to server
        elif 'DELETE' in command:
            sock.sendall(b'DELETE')
            filename = command.replace('DELETE', '')
            filename = filename.replace(' ', '')
            # Construct the protocol using the helper function
            segment = construct_protocol(filename, '')
            # Send the segment
            sock.sendall(segment)

        # If the command is a OVERWRITE command, then send corresponding protocol to server
        elif 'OVERWRITE' in command:
            sock.sendall(b'OVERWRITE')
            filename = command.replace('OVERWRITE', '')
            filename = filename.replace(' ', '')
            # Construct the protocol using the helper function
            segment = construct_protocol(filename, '')
            # Send the segment
            sock.sendall(segment)

        # If the command is a EXIT command, then disconnect from the server
        elif command == 'EXIT':
            sock.sendall(b'EXIT')
            break

        # Receive the response from the server
        data = sock.recv(1024)
        print(data.decode("utf-8"))


finally:
    print('Disconnected from the server!')
    sock.close()
