from socket import *
from select import *
import time

sk1 = socket(AF_INET, SOCK_DGRAM)
sk1.bind(('127.0.0.1', 10010))

sk2 = socket(AF_INET, SOCK_DGRAM)
sk2.bind(('', 10020))

sk3 = socket(AF_INET, SOCK_DGRAM)
sk3.bind(('', 10030))

input = [sk1, sk2, sk3]

while True:
    print("new round")
    r_list, w_list, e_list = select(input, [], input, 1)

    for sk in r_list:
        recv, addr= sk.recvfrom(1024)
        print(recv.decode(), end='')
        print(addr)
        print(list(addr))
