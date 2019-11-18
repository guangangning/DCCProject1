import binascii
from socket import *
import time
import datetime

KEY_START  = '1000101001010001'
KEY_END    = '1111010110101111'
FINISHFLAG = '1111000011110000'
ACKFLAG    = '11101100'
REJFLAG    = '11101111'
MAX_FRAME_NUM = 256
BUF_SIZE = 5000
WIN_SIZE = 16

frameNum = 0
shouldRecvNum = 0
sendBuf = []
sendCnt = 0

def printTime():
    print("%.2d:%.2d.%.6d->" %(datetime.datetime.now().minute, datetime.datetime.now().second, datetime.datetime.now().microsecond), end='')

# To locate the frame.
def frameAlignment(text, keyStart, keyEnd):
    posStart = text.find(keyStart)
    posEnd = text.find(keyEnd)
    # print("start ", end="")
    # print(posStart)
    # print("end ", end="")
    # print(posEnd)
    if (posStart==-1 or posEnd==-1):
        return -1
    if (posEnd - posStart != 304):
        return -1
    return text[posStart+len(keyStart):posEnd]
    
# Change a string into binarryString.
def str2Bin(text):
    code = list(text.encode())
    return ''.join(bin(i)[2:].zfill(8) for i in code)

# Change a binarryString into string.
def bin2Byte(binStr):
    s = b''
    code = [eval('0b' + binStr[i*8 : i*8+8]) for i in range(len(binStr)//8)]
    for i in code:
        s += binascii.unhexlify(hex(i)[2:].zfill(2).encode()) 
    return s

# Collect binarry from physical layer.
def collectBinStr(text):
    code = list(text)
    return ''.join(bin(i)[2:].zfill(8) for i in code)

# Build a correction code.
def correctionEncode(binstr):
    binlist = []
    row = ''
    column = ''
    for i in range(16):
        binlist.append(binstr[i*16:i*16+16])
        singleRowXor = 0
        #print(binlist)
        for j in range(16):
            #print(i,j)
            singleRowXor ^= int(binlist[i][j])
        row += str(singleRowXor)

    for i in range(16):
        singleColXor = 0
        for j in range(16):
            singleColXor ^= int(binlist[j][i])
        column += str(singleColXor)
    return row + column

# Correct the frame.
def errorCorrect(rawtext):
    text = rawtext[0:32*8]
    recvCode = rawtext[32*8:36*8]
    generateCode = correctionEncode(text)
    if generateCode == recvCode:
        return text
    cnt = 0
    row = -1
    col = -1
    for i in range(32):
        if generateCode[i] != recvCode[i]:
            cnt += 1
            if i < 16:
                row = i
            else :
                col = i - 16
    if cnt > 2 or row == -1 or col == -1:
        return -1
    binlist = list(text)
    binlist[row*16+col] = str(int(binlist[row*16+col]) ^ 1)
    text = ''.join(binlist)
    printTime()
    print('Correct an error')
    return text

def makeFrame(frameNum, text):
    global KEY_START, KEY_END
    bin_frameNum = bin(frameNum)[2:].zfill(8)
    text = bin_frameNum + text
    correctionCode = correctionEncode(text)
    return bin2Byte(KEY_START + text + correctionCode + KEY_END)

def storeInQueue(text):
    global frameNum
    text = str2Bin(text)
    frameCnt = (len(text)-1)//248+1
    print('total frame cnt', end='')
    print(frameCnt + 1)
    for i in range(frameCnt):
        cuttedBinStr = text[i*248:i*248+248].ljust(248,'0')
        frame = makeFrame(frameNum, cuttedBinStr)
        sendBuf.append((frameNum, frame))
        frameNum = (frameNum + 1) % MAX_FRAME_NUM
    finishFrame = makeFrame(frameNum, FINISHFLAG.ljust(248,'0')) # Send a finishFrame to tell server this message is finished.
    sendBuf.append((frameNum, finishFrame))
    frameNum = (frameNum + 1) % MAX_FRAME_NUM

# Send the rest frames in the window.
def sendWindow(sk, addr):
    global sendCnt
    while (sendCnt<len(sendBuf) and sendCnt<WIN_SIZE):
        sk.sendto(sendBuf[sendCnt][1], addr)
        printTime()
        print('send frame ', end='')
        print(sendBuf[sendCnt][0])
        sendCnt += 1

# Recognize the frame is ack or rej. 0 for ack, 1 for rej.
def recognizeFrame(text):
    pos = text.find(ACKFLAG)
    if (pos != -1):
        return 0
    pos = text.find(REJFLAG)
    if (pos != -1):
        return 1

def slideWindow(frameNum):
    global sendCnt
    while (sendCnt>0 and len(sendBuf)!=0 and sendBuf[0][0]!= frameNum):
        sendCnt -= 1
        printTime()
        print('pop ', end='')
        print(sendBuf.pop(0)[0])

def sendMessage(sk, text, addr):
    global sendBuf, sendCnt
    resentCnt = 0

    storeInQueue(text)
    # print(sendBuf)
    while (len(sendBuf)!=0):
        sendWindow(sk, addr)
        try:
            sk.settimeout(1)
            recv = sk.recvfrom(BUF_SIZE)[0]
            resentCnt = 0
            recv = collectBinStr(recv)
            recv = frameAlignment(recv, KEY_START, KEY_END)
            if (recv==-1):
                printTime()
                print("Located failed")
                continue
            recv = errorCorrect(recv)
            # print(recv)
            if (recv == -1):
                printTime()
                print('Wrong frame')
                continue
            frameNum = eval('0b' + recv[0:8])
            if (frameNum < sendBuf[0][0] and (frameNum+MAX_FRAME_NUM-sendBuf[0][0])>=WIN_SIZE):
                print('<')
                continue
            frameType = recognizeFrame(recv)
            if (frameType == 0):
                printTime()
                print('recv ack ', end='')
                print(frameNum)
            else:
                printTime()
                print('recv rej ', end='')
                print(frameNum)
            slideWindow(frameNum)
            if (frameType == 1):
                sendCnt = 0
        except timeout:
            printTime()
            print('timeout')
            sendCnt = 0
            if (resentCnt>10):
                break
            resentCnt += 1
        print()

    return 1

def sendAck(sk, frameNum, addr):
    ackFrame = makeFrame(frameNum, ACKFLAG.ljust(248,'0'))
    sk.sendto(ackFrame, addr)

def sendRej(sk, frameNum, addr):
    rejFrame = makeFrame(frameNum, REJFLAG.ljust(248,'0'))
    sk.sendto(rejFrame, addr)

def recvMessage(sk):
    global shouldRecvNum
    flag_rej = 0
    message = ""
    while (1):
        recv, addr= sk.recvfrom(BUF_SIZE)
        recv = collectBinStr(recv)
        recv = frameAlignment(recv, KEY_START, KEY_END)
        if (recv == -1):
            printTime()
            print("Located failed")
            continue
        recv = errorCorrect(recv)
        # print(recv)
        # time.sleep(0.1)
        if (recv == -1):
            printTime()
            print('Wrong frame.')
            continue
        frameNum = eval('0b' + recv[0:8])
        if (frameNum != shouldRecvNum):
            if (not flag_rej):
                sendRej(sk, shouldRecvNum, addr)
                flag_rej = 1
                printTime()
                print('sendRej',end='')
                print(shouldRecvNum)
            continue
        flag_rej = 0
        shouldRecvNum = (frameNum + 1) % MAX_FRAME_NUM
        sendAck(sk, shouldRecvNum, addr)
        printTime()
        print("sendAck",end='')
        print(shouldRecvNum)
        if (recv.find(FINISHFLAG)!=-1):
            break
        else:
            message += recv[8:]
            
    return bin2Byte(message).decode()

if __name__ == '__main__':
    # s = '11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'
    # a = sendMessage(s, s, s)
    print(bin2Byte(KEY_END).decode())