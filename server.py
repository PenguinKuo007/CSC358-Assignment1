import os
import socket
import sys
import threading

"""
This function will deconstruct the protocols sent over from the client
The function will return the filename & size of the file from the protocol string
Example deconstruction of the protocol is as follows:
input = 'filename: file.txt filesize: 6'
output = ('file.txt', '6')
Note: filesize will only have values for the PUSH command
"""
def deconstruct_protocol(protocol):

    # Index variable for each attribute
    name_index = 10
    size_index = protocol.find("filesize", 9)

    # Get each value from the protocol string
    name_val = protocol[10:size_index - 1]
    size_val = protocol[size_index + 10:]

    return (name_val, size_val)


"""
This function will be given to each new thread to execute.
Will loop for new requests and appropriately send responses back to clients. 
"""
def handle_client(connection, address):
    # The server will wait for the assigned client to send a command
    while True:
        # Grab and decode the client's byte string message 
        data = connection.recv(1024)
        client_msg = data.decode("utf-8")

        # First message from the client will be to connect to the server. 
        if client_msg == 'Connect':
            # Response back to the client with an Acknowledgement 
            connection.sendall(b'Welcome to the File Server!')

        # If the command is LIST, grab the list of files in the server and 
        # send it back in a string.
        elif client_msg == "LIST":
            # Get the list of files
            filelist = os.listdir(path)
            fileformat = ""
            # Add each file to a formatted string
            for i in filelist:
                fileformat = fileformat + i + "\n"

            # Send the list of files as a response or whether the directory is empty. 
            if fileformat == '':
                connection.sendall(b'Server directory is empty!')
            else:
                fileformat = fileformat[:len(fileformat)-1]
                file = fileformat.encode('utf-8') # Encode as a bytestring
                connection.sendall(file)

        # If the command is PUSH, grab the first segment to determine the size
        # of the file and then grab subsequent segments as needed.
        elif client_msg == "PUSH":
            # First segment with the protocol string
            segment = connection.recv(1024)
            # Deconstruct the protocol string to get the filename and size of the file
            filename, size = deconstruct_protocol(segment.decode("utf-8"))
            file = open(path + "/" + filename, "wb")
            # Send a response to separate the two sendall calls in the client side. 
            connection.sendall(b'Separate')

            #  Use loop to get receive all content of a file if the size is over 1024 bytes
            if int(size) > 0:
                loopcount = (int(size) // 1024) + 1
                data = connection.recv(1024)
                for _ in range(loopcount):
                    data = data + connection.recv(1024)

            # Write the file onto the server's directory and send a successful Acknowledgment
            file.write(data)
            response = "Received the file " + filename + "!"
            response = response.encode("utf-8") # Encode as a bytestring
            connection.sendall(response)
            file.close()

        # If the command is DELETE, find if the file exists and remove it accordingly
        elif client_msg == "DELETE":
            # First segment with the protocol string
            segment = connection.recv(1024)
            # Deconstruct the protocol string to get the filename of the file
            filename, size = deconstruct_protocol(segment.decode("utf-8"))
            # Get the list of files
            filelist = os.listdir(path)

            # Send a response back according to whether the directory is empty, 
            # the file is not found or the file has been deleted.
            if filelist == []:
                connection.sendall(b'Server directory is empty!')
            elif filename not in filelist:
                connection.sendall(b'File not found!')
            else:
                os.remove(path + "/" + filename)
                msg = 'The file ' + filename + ' deleted!'
                connection.sendall(msg.encode("utf-8"))

        # If the command is OVERWRITE, find if the file exists and overwrite it accordingly
        elif client_msg == "OVERWRITE":
            # First segment with the protocol string
            segment = connection.recv(1024)
            # Deconstruct the protocol string to get the filename of the file
            filename, size = deconstruct_protocol(segment.decode("utf-8"))
             # Get the list of files
            filelist = os.listdir(path)

            # Check if the file is in the list of files
            check = False
            for i in filelist:
                if i == filename:
                    check = True

            # Send a response back according to whether the file is not found 
            # or the file has been overwritten.
            if not check:
                connection.sendall(b'File not found!')
            else:
                file = open(path + "/" + filename, "w")
                overwrite_body = "This is some hardcoded text to overwrite a file with."
                file.write(overwrite_body)
                response = "The file " + filename + " overwritten!"
                response = response.encode("utf-8") # Encode as a bytestring
                connection.sendall(response)
                file.close()

        # Clients may send an incorrect command.  
        else:
            print('no data from', client_address)
            print(client_msg)
            break
    
    connection.close()


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port 
server_address = ('142.1.46.51', 10001)
print('[STARTING] Server is starting...')
sock.bind(server_address)
# Listen for incoming connections
sock.listen()

# COmbine the absolute and relative path to create the path needed when referring to files. 
absolute_path = os.path.dirname(os.path.abspath(__file__))
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
