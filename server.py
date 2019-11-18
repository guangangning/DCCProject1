from socket import *
from method import *

upLayer_address = "127.0.0.1"
upLayer_port = 12200
phyLayer_address = "127.0.0.1"
phyLayer_port =12100
ADDRESS_UPLAYER = (upLayer_address, upLayer_port)
ADDRESS_PHYLAYER = (phyLayer_address, phyLayer_port)

server_socket = socket(AF_INET,SOCK_DGRAM)
server_socket.bind(ADDRESS_UPLAYER)

while (1):
    s = recvMessage(server_socket)
    # s = server_socket.recvfrom(4096)[0]
    # s = collectBinStr(s)
    print(s)

server_socket.close()
