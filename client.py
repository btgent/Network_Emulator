from socket import *
import sys
import random
import os

# check if the number of arguments is correct.
if len(sys.argv) != 3:
    print('Usage: incorrect number of arguments')
    sys.exit(1)
else:
    server_address = sys.argv[1]
    n_port = int(sys.argv[2])

# setup the control connection
#controlSocket = socket(AF_INET,SOCK_STREAM)
#controlSocket.connect((server_address,n_port))
#print('client sets up control connection')

while True:
    controlSocket = socket(AF_INET,SOCK_STREAM)
    controlSocket.connect((server_address,n_port))
    print('client sets up control connection')
    # input command
    command = raw_input('Enter request: ')
    # end client process and close control connection
    if command == 'EXIT':
        controlSocket.send(command.encode())
        print('EXIT: close control connection')
        controlSocket.close()
        break
    else:
        # send the command to server
        controlSocket.send(command.encode())
        # receive reponse from server
        response = controlSocket.recv(1024).decode()
        act = command[:3]  # determing if it is download or upload
        file = os.getcwd() + '/' + command[4:]
        if response == 'OK':
            print('receive OK')
            # Client set up a server socket
            r_port = random.randint(1025, 9999) # pick a random r_port number greater than 1024
            print("the transaction port number is: %s" % r_port)
            serverSocket = socket(AF_INET,SOCK_STREAM)
            serverSocket.bind(('',r_port))
            serverSocket.listen(1)
            print('The transaction server is ready to transfer')
            # Send client_address and port number over control connection
            client_address = getfqdn()
            controlSocket.send(client_address.encode())
            controlSocket.send(str(r_port).encode())
            
            connectionSocket, addr = serverSocket.accept()
            if act == 'PUT':
                if os.path.isfile(file): # check if the file exits in current folder
                    # send response to server if the file exits
                    msg = 'Ready to send file'
                    connectionSocket.send(msg.encode())
                    with open(file, 'rb') as f:
                        upload = f.read() # save the content of file into upload
                        connectionSocket.send(upload) # send the content of file
                    print('Transaction complete')
                else:
                    # send error msg to server if the file does not exit
                    msg = 'Error: the reqeusted file does not exit'
                    print(msg)
                    connectionSocket.send(msg.encode())
                    
            elif act == 'GET':
                # receive message from server
                msg = connectionSocket.recv(1024).decode()
                # when the file exits, it should transfer
                if msg[:5] != 'Error':
                    # make a new file with the same filename in command
                    f = open(command[4:], 'wb')
                    # receive the content of transferred file from server
                    download = connectionSocket.recv(4096)
                    # write the content into the new file
                    f.write(download)
                    print('Transaction complete')
                # when it is an error msg, refuse to transfer and print error msg.
                else:
                    print(msg)
            print('loop back to stage 1')
            # close the transaction connection after transaction completes
            connectionSocket.close()

