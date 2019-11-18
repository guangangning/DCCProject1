from socket import *
from method import *

BUF_SIZE = 5000

upLayer_address = "127.0.0.1"
upLayer_port = 11200
phyLayer_address = "127.0.0.1"
phyLayer_port =11100
ADDRESS_UPLAYER = (upLayer_address, upLayer_port)
ADDRESS_PHYLAYER = (phyLayer_address, phyLayer_port)

client_socket = socket(AF_INET,SOCK_DGRAM)
client_socket.bind(ADDRESS_UPLAYER)

while (1):
    s = input()
    a = sendMessage(client_socket, s, ADDRESS_PHYLAYER)
    # client_socket.sendto(s.encode(), ADDRESS_PHYLAYER)

client_socket.close()
