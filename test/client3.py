from socket import *

sk = socket(AF_INET, SOCK_DGRAM)
sk.bind(('127.0.0.1', 10031))
addr = ('127.0.0.1', 10030)

while True:
    send = input('->')
    sk.sendto(send.encode(), addr)