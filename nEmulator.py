from socket import *
import sys
import struct
import os
import random
import time

# check if the number of input arguments is correct
if len(sys.argv) != 10:
    print('Usage: incorrect number of arguments')
    sys.exit(1)
else:
    forward_port = int(sys.argv[1])
    receiver_address = sys.argv[2]
    receiver_port = int(sys.argv[3])
    backward_port = int(sys.argv[4])
    sender_address = sys.argv[5]
    sender_port = int(sys.argv[6])
    delay = int(sys.argv[7])
    prob = float(sys.argv[8])
    mode = int(sys.argv[9])

# setup socket for forwarding packets
forwardSocket = socket(AF_INET,SOCK_DGRAM)
forwardSocket.bind(('',forward_port))
forwardSocket.settimeout(0.0)
# setup socket for backwarding packets
backwardSocket = socket(AF_INET,SOCK_DGRAM)
backwardSocket.bind(('',backward_port))
backwardSocket.settimeout(0.0)

while True:
    try: # receive packet from sender
        forward_packet,address = forwardSocket.recvfrom(512)
        fp_type, fp_seqnum, fp_length = struct.unpack('3i',forward_packet[:12])

        if mode == 1: # verbose mode is on
            if fp_type == 2: # receive EOT
                msg = 'receiving Packet EOT'
            else: # receive a packet
                msg = 'receiving Packet ' + str(fp_seqnum)
            print(msg)

        if fp_type == 1 and random.random() >= prob: # receive a data packet and it is discarded
            forward_delay = random.randint(0,delay)
            time.sleep(forward_delay/1000) # wait for delay
            forwardSocket.sendto(forward_packet,(receiver_address,receiver_port)) # forward the data packet
            if mode == 1: # show message if verbose mode is on
                msg = 'forwarding Packet ' + str(fp_seqnum)
                print(msg)

        elif fp_type == 2: # receive EOT
            forwardSocket.sendto(forward_packet,(receiver_address,receiver_port)) # forward EOT
            if mode == 1: # show message if verbose mode is on
                msg = 'forwarding Packet EOT'
                print(msg)

        else: # discard this packet
            if mode == 1: # show message if verbose mode is on
                msg = 'discarding Packet ' + str(fp_seqnum)
                print(msg)
    except error:
        pass

    try: # receive packet from receiver
        backward_packet,address = backwardSocket.recvfrom(12)
        bp_type, bp_seqnum, bp_length = struct.unpack('3i',backward_packet[:12])

        if mode == 1: # verbose mode is on
            if bp_type == 2: # receive EOT
                msg = 'receiving ACK EOT'
            else: # receive ack packet
                msg = 'receiving ACK ' + str(fp_seqnum)
            print(msg)

        if bp_type == 0 and random.random() >= prob: # receive ack packet and it is discarded
            backward_delay = random.randint(0,delay)
            time.sleep(backward_delay/1000) # wait for delay
            backwardSocket.sendto(backward_packet,(sender_address,sender_port)) # backward ack packet
            if mode == 1: # show message if verbose mode is on
                msg = 'forwarding ACK ' + str(bp_seqnum)
                print(msg)

        elif bp_type == 2: # receive EOT
            backwardSocket.sendto(backward_packet,(sender_address,sender_port)) # backward EOT
            if mode == 1: # show message if verbose mode is on
                msg = 'forwarding ACK EOT'
                print(msg)
                print('Transmission is complete, exit') # network emulator exits after backward EOT
            break

        else: # discard ack packet
            if mode == 1: # show message if verbose mode is on
                msg = 'discarding ACK ' + str(bp_seqnum)
                print(msg)

    except error:
        pass
