from socket import *
import time

upLayer_address = "127.0.0.1"
upLayer_port = 12200
phyLayer_address = "127.0.0.1"
phyLayer_port =12100
ADDRESS_UPLAYER = (upLayer_address, upLayer_port)
ADDRESS_PHYLAYER = (phyLayer_address, phyLayer_port)

server_socket = socket(AF_INET,SOCK_DGRAM)
server_socket.bind(ADDRESS_UPLAYER)

a = 0
while(1):
    a += 1
    try:
        server_socket.settimeout(2)
        recv, addr= server_socket.recvfrom(4096)
        print(recv.decode())
        time.sleep(1)
        server_socket.sendto(recv, addr)
    except timeout:
        print('timeout')
        continue
    print(a)
        
server_socket.close()
