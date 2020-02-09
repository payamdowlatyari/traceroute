from socket import *
import os
import sys
import struct
import time
import select
import binascii  
		
ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT  = 2.0 
TRIES    = 2

# The packet that we shall send to each router along the path is the ICMP echo
# request packet. We need to build this packet ourselves.
def checksum(string): 
	csum = 0
	countTo = (len(string) // 2) * 2  
	count = 0

	while count < countTo:
		thisVal = ord(string[count+1]) * 256 + ord(string[count]) 
		csum = csum + thisVal 
		csum = csum & 0xffffffff  
		count = count + 2
	
	if countTo < len(string):
		csum = csum + ord(string[len(string) - 1])
		csum = csum & 0xffffffff 
	
	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum 
	answer = answer & 0xffff 
	answer = answer >> 8 | (answer << 8 & 0xff00)
	return answer 

def build_packet():
	# Firstly the header of our packet to be sent must be made,  
	# secondly the checksum must be appended to the header and
	# finally the complete packet must be sent to the destination.

	# Header is type (8), code (8), checksum (16), sequence (16)

	#Fill in start
	myChecksum = 0
	# Make a dummy header with a 0 checksum
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
	data = struct.pack("d", time.time())
	# You need to use `struct` to interpret strings as packed binary data
	# Calculate the checksum on the data and the dummy header.
	myChecksum = checksum(header + data)
	
	# Get the right checksum, and put in the header
	if sys.platform == 'darwin':
		myChecksum = socket.htons(myChecksum) & 0xffff  # Convert 16-bit integers from host to network  byte order
		myChecksum = htons(myChecksum) & 0xffff		
	else:
		myChecksum = htons(myChecksum)

	# Append checksum to the header.
	print ("The header sent with the ICMP request is ", ICMP_ECHO_REQUEST,0,myChecksum,ID,1)
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)

	# Don’t send the packet yet , just return the final packet in this function.
	#Fill in end	

	# So the function ending should look like this

	packet = header + data
	return packet

def get_route(hostname):
	timeLeft = TIMEOUT
	for ttl in range(1,MAX_HOPS):
		for tries in range(TRIES):

			destAddr = gethostbyname(hostname)
			#Fill in start
			# Make a raw socket named mySocket
			icmp = socket.getprotobyname("icmp")
			mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)			
			#Fill in end
			mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
			mySocket.settimeout(TIMEOUT)
			try:
				d = build_packet()
				mySocket.sendto(d, (hostname, 0))
				t= time.time()
				startedSelect = time.time()
				whatReady = select.select([mySocket], [], [], timeLeft)
				howLongInSelect = (time.time() - startedSelect)
				if whatReady[0] == []: # Timeout
					print("  *        *        *    Request timed out.")
				recvPacket, addr = mySocket.recvfrom(1024)
				timeReceived = time.time()
				timeLeft = timeLeft - howLongInSelect
				if timeLeft <= 0:
					print("  *        *        *    Request timed out.")
				
			except timeout:
				continue			
			
			else:
				#Fill in start
				#Fetch the icmp type from the IP packet
				icmpHeaderContent = recvPacket[20:28]
				type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeaderContent)
				printname = get_name_or_ip(addr[0])
				#Fill in end

				if types == 11:
					bytes = struct.calcsize("d") 
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived -t)*1000, addr[0]))
				
				elif types == 3:
					bytes = struct.calcsize("d") 
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived-t)*1000, addr[0]))
				
				elif types == 0:
					bytes = struct.calcsize("d") 
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived - timeSent)*1000, addr[0]))
					return
			
				else:
					print("error")			
				break	
			finally:				
				mySocket.close()

get_route("google.com")	

