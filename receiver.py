from socket import *
import sys
import struct
import os

# check if the number of input arguments is correct
if len(sys.argv) != 5:
    print('Usage: incorrect number of arguments')
    sys.exit(1)
else:
    nemu_address = sys.argv[1]
    nemu_port = int(sys.argv[2])
    receiver_port = int(sys.argv[3])
    outputFile = sys.argv[4]
    arrival_log = open('arrival.log','wb')

# setup receiver's socket
receiverSocket = socket(AF_INET,SOCK_DGRAM)
receiverSocket.bind(('',receiver_port))
receiverSocket.settimeout(0.0) # no timeout allowed
print('receiver is ready to receive')
seqnum_lst = []  # record sequence numbers
packet_lst = []  # record ack numbers

while True:
    try:
        # receive 512 bytes (3 integers and a string of length 500)
        recv_packet,address = receiverSocket.recvfrom(512)
        packet_type, seqnum, length = struct.unpack('3i',recv_packet[:12])

        if packet_type == 2: # the packet is EOT
            print('EOT has been received')
            # sent back EOT
            receiverSocket.sendto(recv_packet,(nemu_address,nemu_port))
            print('EOT has been sent')
            arrival_log.close()
            # record data packets into output file in order
            out_file = open(outputFile,'wb')
            for i in seqnum_lst:
               for packet in packet_lst:
                   p_type, seq, p_length = struct.unpack('3i',packet[:12])
                   if p_type == 1 and i == seq:
                        data, = struct.unpack('%ds'% p_length,packet[12:(12+p_length)])
                        out_file.write(data.decode('utf-8'))
                        break
            print('outputFile is saved. Connection exits')
            break

        if packet_type == 1: # the packet is data
            if seqnum not in seqnum_lst: # store a new data packet
                seqnum_lst.append(seqnum)
                packet_lst.append(recv_packet)
                print('A new packet has been received')
                arrival_log.write(str(seqnum)+'\n')
                seqnum_lst.sort()
            # discard duplicate ones
            data = ''
            packet = struct.pack('3i0s',0,seqnum,0,data.encode('utf-8'))
            receiverSocket.sendto(packet,(nemu_address,nemu_port))
            print('a ACK has been sent')
    except error:
        pass

