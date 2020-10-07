from socket import *
import sys
import os

# check if the number of arguments is correct.
if len(sys.argv) != 2:
    print('Usage: incorrect number of arguments')
    sys.exit(1)
else:
    # save n_port
    n_port = int(sys.argv[1])
    
# setup the control server
controlSocket = socket(AF_INET,SOCK_STREAM)
controlSocket.bind(('',n_port))
controlSocket.listen(1)
print('The control server is ready to receive')


while True:
    # server waits on accept() for incming requests
    connectionSocket,addr = controlSocket.accept()
    command = connectionSocket.recv(1024).decode()
    print('received command: ' + command)
    
    # if the received command is 'EXIT', close control server
    if command == 'EXIT':
       connectionSocket.close()
       break

    act = command[:3] # determing if it is download or upload
    # save the file name and the path under current folder
    file = os.getcwd() + '/' + command[4:]


    # setup transaction connection if the command in valid.
    # go to next loop if the commnad is not 'GET' or 'PUT'
    if act == 'GET' or act == 'PUT':
        response = 'OK'
        connectionSocket.send(response.encode()) # send 'OK' response to client
        # receive client_address and r_port from client
        client_address = connectionSocket.recv(1024).decode()
        print('The received address is ' + client_address)
        r_port = connectionSocket.recv(1024).decode()
        print('The received port number is ' + r_port)
        r_port = int(r_port)   # convert r_port from str to int
        
        # set up transaction connection
        transactionSocket = socket(AF_INET,SOCK_STREAM)
        transactionSocket.connect((client_address,r_port))
        print('The transaction server is ready to transfer')
        
    if act == 'GET':
        if os.path.isfile(file): # check if the file exits in current folder
            # send reponse to client if the file exits
            msg = 'Ready to send file'
            transactionSocket.send(msg.encode())
            with open(file, 'rb') as f:
                data = f.read() # save the content of file into data
                transactionSocket.send(data) # send the content to client
            print('Transaction complete')
        else:
            # send error msg to client if the file does not exit
            msg = 'Error: the reqeusted file does not exit'
            print(msg)
            transactionSocket.send(msg.encode())
            
    elif act == 'PUT':
        # receive message from client
        msg = transactionSocket.recv(1024).decode()
        # when the file exits, it should transfer.
        if msg[:5] != 'Error':
            # make a new file with the same filename in command
            f = open(command[4:], 'wb')
            # receive the content of transferred file from server
            data = transactionSocket.recv(4096)
            # write the content into the new file
            f.write(data)
            print('Transaction completes')
        # when it is an error message, refuse to transfer and print the error msg.
        else:
            print(msg)
    # close the transaction connection after transaction completes
    transactionSocket.close()
        

