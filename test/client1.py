from socket import *

sk = socket(AF_INET, SOCK_DGRAM)
sk.bind(('127.0.0.1', 10011))
addr = ('127.0.0.1', 10010)

while True:
    send = input('->')
    sk.sendto(send.encode(), addr)