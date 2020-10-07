from socket import *
import sys
import struct
import os
import time

# check if the number of input arguments is correct
if len(sys.argv) != 5:
    print('Usage: incorrect number of arguments')
    sys.exit(1)
else:
    nemu_address = sys.argv[1]
    nemu_port = int(sys.argv[2])
    sender_port = int(sys.argv[3])
    inputFile = sys.argv[4]
    seqnum_log = open('seqnum.log','wb')
    ack_log = open('ack.log','wb')

# setup sender's socket
senderSocket = socket(AF_INET,SOCK_DGRAM)
senderSocket.bind(('',sender_port))
senderSocket.settimeout(0.0) # no timeout allowed
print('sender is ready to send')

file = os.getcwd() + '/' + inputFile # record input file's directory
seqnum_lst = [] # record sequence numbers
ack_lst = [] # record ack numbers
packet_lst = [] # record all data packets
eot = 0 # eot flag indicates if the eot has been sent

if os.path.isfile(file): # if input file exists
    print('Start to transmit')
    # read 500 bytes from input file every time
    with open(inputFile,'rb') as f:
        seqnum = 0
        data = f.read(500)
        while data != b'':
            seqnum = seqnum%32 # module 32 sequence number
            length = len(data) # length of data read in
            # make up a meaningless string "makeup" if data read in is less than 500 bytes
            makeup_len = 500 - length
            if makeup_len == 0: # if data is 500 bytes, no need to make up
                packet = struct.pack('3i'+str(length)+'s',1,seqnum,length,data.encode('utf-8'))
            else: # if data is less than 500 bytes, need to make up
                makeup = ''
                for i in range(0,makeup_len):
                    makeup += ' '
                packet = struct.pack('3i'+str(length)+'s'+str(makeup_len)+'s',1,seqnum,length,data.encode('utf-8'),makeup.encode('utf-8'))

            packet_lst.append(packet) # record every data packet in order to resend after
            senderSocket.sendto(packet,(nemu_address,nemu_port))
            print('A packet has been sent')
            seqnum_log.write(str(seqnum)+'\n') # record a sequence number
            seqnum_lst.append(seqnum)
            seqnum += 1 # sequence number increment by 1 every time 
            data = f.read(500)
    seqnum_log.close()
    seqnum_lst.sort()
    # sender waits 200ms
    time.sleep(0.2)

    while True:
        if seqnum_lst == ack_lst and eot == 0:
        # all data packets has been transmitted successfully and eto has not been sent yet.
            eot_data = '' # make up a meaningless string to take place data in packet
            for i in range(500):
                eot_data += ' '
            eot_packet = struct.pack('3i500s',2,0,0,eot_data.encode('utf-8'))
            senderSocket.sendto(eot_packet,(nemu_address,nemu_port))
            print('EOT has been sent')
            eot = 1 # set flat to 1

        try: # receive ack packet that only takes 12 bytes (3 integers)
            recv_packet,address = senderSocket.recvfrom(12)
            packet_type, seqnum, length = struct.unpack('3i',recv_packet[:12])
            if packet_type == 2: # receive eot
                ack_log.close()
                print('EOT has been received. Connection exit')
                break
            if packet_type == 0: # receive ack
                print('a ACK has been received')
                ack_log.write(str(seqnum)+'\n')
                ack_lst.append(seqnum)
                ack_lst.sort()
                continue
        except error: # resent data packets without ack if no packet is received
            for i in seqnum_lst:
                if i not in ack_lst:
                    senderSocket.sendto(packet_lst[i],(nemu_address,nemu_port))
                    print('A packet has been sent')
            time.sleep(0.2) # waits 200ms
            continue

else:
    print('Error: the input file does not exit')

