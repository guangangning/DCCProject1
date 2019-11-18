from socket import *

upLayer_address = "127.0.0.1"
upLayer_port = 12100
phyLayer_address = "127.0.0.1"
phyLayer_port =12200
ADDRESS_UPLAYER = (upLayer_address, upLayer_port)
ADDRESS_PHYLAYER = (phyLayer_address, phyLayer_port)

client_socket = socket(AF_INET,SOCK_DGRAM)
client_socket.bind(ADDRESS_UPLAYER)

a = '111000'
while (1):
    a = input()
    client_socket.sendto(a.encode(), ADDRESS_PHYLAYER)
    recv = client_socket.recvfrom(1000)[0].decode()
    print(recv)

client_socket.close()
