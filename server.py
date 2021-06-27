#Einav, Bitton, 318231750
#liron, hamo ,207973603
#Daniel,Assayag,316614320
#Ohad,shalom,204525505

import socket
import threading

servers = {}
users = {}
# Each address will be a tuple (IP,PORT)
addresses_list = [('127.0.0.1',9999),('127.0.0.1',8888),('127.0.0.1',7777),('127.0.0.1',6666)]
ports = [9999, 8888, 7777, 6666, 5555]
sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

port = int(input("Enter port number 1111-9999\n"))

def new_conn(conn_socket,c_addr,servers,users):
    main_user=''
    try:
        while True:
            #print('start listening from ', c_addr)
            data = conn_socket.recv(6)
            data = data.decode()
            if(len(data)==0):
                continue
            type = data[0]
            subtype = data[1]
            leng = int(data[2:4])
            sublen = int(data[4:6])
            # Type 0
            if type == '0':#Info on connections
                if subtype == '0':
                    # Building the message
                    m = ''
                    print(servers)
                    for s in servers.keys():
                        d = str(servers[s]) + ':' + str(s) + '\0'
                        if len(m) + len(d) > 99:
                            print("Server list too long")
                            break
                        m = m + d
                    # Header
                    print(m)
                    data = '10' + str(len(m)) + '00'
                    conn_socket.send(data.encode())
                    conn_socket.send(m.encode())
                if subtype == '1':
                    # Building the message
                    m = ''
                    for s in users.keys():
                        d = str(s) + '\0'
                        if len(d) + len(s) > 99:
                            break
                        m = m + d
                    # Header
                    data = '11' + str(len(m)) + '00'
                    conn_socket.send(data.encode())
                    conn_socket.send(m.encode())
            # Type 1
            if type == '1':#responded with info
                if subtype == '0':
                    data = conn_socket.recv(int(leng))
                    data = data.decode().split('\0')
                    for d in data:
                        ip, p = d.split(':')
                        servers[p] = ip
                if subtype == '1':
                    data = conn_socket.recv(int(leng))
                    data = data.decode().split('\0')
                    for d in data:
                        users.append(d)
            # Type 2
            if type == '2':#Adding client/server
                if subtype == '0':
                    servers[c_addr[1]] = c_addr[0]
                    print("New server registered:", c_addr[0], ":", c_addr[1])
                if subtype == '1':
                    user_name = conn_socket.recv(int(leng)).decode()
                    users[user_name] = conn_socket
                    print("New user registered:", user_name)
                    print(users)
            # Type 3
            if type == '3':#Message passing
                if subtype == '0':
                    data1 = conn_socket.recv(leng).decode()
                    reciver = data1[0:sublen]
                    msg = data1[sublen:]
                    print(reciver, msg)
                    sender=None
                    for s in users.keys():
                        if conn_socket == users[s]:
                            sender = s
                            print(s)
                    if sender == None:
                        print("User not found")
                        continue
                    if reciver not in users.keys():
                        print("User not found sending to all servers")
                        for s in servers.keys():
                            ip=s
                            po=servers[s]
                            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            sock.connect((ip, po))
                            sock.send(data)
                            sock.send(data1)
                        continue
                    newuser = sender + '\0' + reciver
                    newmsg = newuser + msg
                    newlen = len(newmsg)
                    newsublen = len(sender + '\0' + reciver)
                    if newsublen > 99:
                        newmsg = newuser[:99] + msg
                        newsublen = len(newuser[:99])
                    if newlen > 99:
                        newmsg = newmsg[:99]
                        newlen = len(newmsg)
                    header = '30'
                    if newlen < 10:
                        header += '0' + str(newlen)
                    else:
                        header += str(newlen)
                    if newsublen < 10:
                        header += '0' + str(newsublen)
                    else:
                        header += str(newsublen)
                    print(users[reciver])
                    users[reciver].send(header.encode())
                    users[reciver].send(newmsg.encode())
                    #send to client
                if subtype == '1':#Echo msg
                    print("Sending Echo")
                    conn_socket.send('320000'.encode())
                    # TODO
                if subtype == '2':
                    print("Echo recived")
    except(ConnectionResetError):
        print("Caught reset")
        for s in users.keys():
            if conn_socket == users[s]:
                sender = s
                print(s)
        users.pop(s,None)
        print(users)
    conn_socket.close()


def be_a_server(sock, port,servers,users):
    print("Starting server")
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    while True:
        print("Before accept")
        conn_socket, c_addr = sock.accept()
        threading.Thread(target=new_conn, args=(conn_socket, c_addr, servers, users)).start()


threading.Thread(target=be_a_server, args=(sock1, port,servers,users)).start()

for adr in addresses_list:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', port))
        if(adr[1]==port):#if its my server
            sock.close()
            continue
        sock.connect((adr[0], adr[1]))
        print("Connected to",adr[0],':',adr[1])
        # register to connected server
        sock.send('200000'.encode())
        #server[port]=ip
        servers[adr[1]]=adr[0]
        # Collect all servers
        sock.send('000000'.encode())
        data = sock.recv(6)
        data = data.decode()
        type = data[0]
        subtype = data[1]
        leng = int(data[2:4])
        sublen = int(data[4:6])
        data=sock.recv(int(leng))
        data = data.decode().split('\0')
        print(data.pop())
        for d in data:
            temp = d.split(':')
            ip=temp[0]
            p=temp[1]
            if p!=port:#add all ports instead of mine
                servers[p] = ip
        sock.close()
    except ConnectionRefusedError:
        print("No server at ",adr[0],adr[1])



