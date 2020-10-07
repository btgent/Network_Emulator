# Network_Emulator
 
Implementing a Network Emulator in order to emulate an unrealiable network link/path that may discard and/or delay packets and/or deliver packets out of order.

There are three programs: sender, receiver, and emulator. They are going to send and receive files thru network emulator using UDP.

Packet Format:
struct {
	int type; // 0: ACK, 1: Data, 2: EOT;
	int seqnum; // sequence number starting from 0;
	int length; // length >= 0;
	String data // String with Max Length 500 Bytes;
};