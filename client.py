#Einav, Bitton, 318231750
#liron, hamo ,207973603
#Daniel,Assayag,316614320
#ohad,shalom,204525505

import socket
import threading
import time

servers={}

def listenTomsg(sock,port,servers):
    print("Listening to msgs")
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while True:
        data = sock.recv(6)
        print("Msg recived")
        data = data.decode()
        type = data[0]
        subtype = data[1]
        leng = int(data[2:4])
        sublen = int(data[4:6])
        if(type=='1'):
            data = sock.recv(int(leng))
            data = data.decode().split('\0')
            print(data)
            print(data.pop())
            for d in data:
                temp = d.split(':')
                ip = temp[0]
                p = temp[1]
                if p != port:  # add all ports instead of mine
                    servers[p] = ip
            print(servers)
            elapsed={}
            for p in servers.keys():
                sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock2.bind(('0.0.0.0', port+2))
                sock2.connect((servers[p], int(p)))
                start=time.time()
                sock2.send("310000".encode())
                sock2.recv(6)
                done=time.time()
                elapsed[p]=done-start
                print("rtt is:",elapsed[p])
                sock2.close()
            print(elapsed)
            min,p_min=10,0
            for p in elapsed.keys():
                if elapsed[p]<min:
                    min=elapsed[p]
                    p_min=int(p)
            sock.shutdown(socket.SHUT_RDWR)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', port))
            sock.connect(('127.0.0.1', p_min))
            print("Connected to port:",p_min)

        elif(type=='3'):
            msg=sock.recv(leng).decode()
            print(msg)
            sender=msg[:sublen]
            sender=sender.split('\x00')[0]
            pmsg=msg[sublen:]
            print("Sender:",sender,"\nMsg:",pmsg)

def printMenu():
    print("""
    1.Send message
    2.Request servers
    4.Exit
    """)

port = int(input("Enter port number 1111-9999\n"))
flag =True
my_name=input('Enter your name\n')




sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', port))
serverport=int(input('Enter server port number\n'))
sock.connect(('127.0.0.1',serverport))


threading.Thread(target=listenTomsg, args=(sock,port,servers)).start()

#Register to server
header='21'
if len(my_name)<10:
    header+='0'+str(len(my_name))
header+='00'
sock.send(header.encode())
sock.send(my_name.encode())

while flag:
    printMenu()
    menu_op=str(input("Choose\n"))
    if menu_op=='1':
        name=input("Enter the user you want to send message to\n")
        name_len=len(name)
        mes=name
        mes+=input("Enter your message(0-99b)\n")
        if(len(mes)+len(name)>99):
            print("Message to long only 0-99b will be taken")
            mes=mes[0:100-len(name)]
        header='30'+str(len(mes)+name_len)
        if name_len<10:
            header=header+'0'+str(name_len)
        else:
            header=header+str(name_len)
        print(header)

        sock.send(header.encode())
        sock.send(mes.encode())
    elif menu_op=='2':
        header='000000'
        sock.send(header.encode())
    elif menu_op=='4':
        sock.close()
        flag=False
    else:
        print("Bad input")

