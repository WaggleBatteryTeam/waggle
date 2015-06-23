#!/usr/bin/env python
import socket, os, os.path, time, PacketHandler
from multiprocessing import Process, Queue
#from internal_communicator import server, client_push, client_pull
    
class internal_communicator(object):
    """ This class acts as the channel of communication to and from the GN and the NC. The internal_msg_handler pulls messages from the data cache, parses the header, and sends the message to the appropriate location. 
    It also recieves messages from the GNs and pushes them into the data cache.""" 
    
    def __init__(self):
        pass
    
    DC_push = Queue()
    incoming_1 = Queue()
    
class client_push(Process):
    """ A client process that connects to the data cache and pushes outgoing messages. """
    
    def run(self):
        comm = internal_communicator()
        while True:
            try:
                if not comm.DC_push.empty(): #if the queue is not empty, connect to DC and send msg
                    if os.path.exists('/tmp/Data_Cache_push_server'):
                        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        client_sock.connect('/tmp/Data_Cache_push_server')
                        print "Ready"
                        data = comm.DC_push.get() #theoretically pushes messages from the GN into a queue
                        print "sending: " , data
                        client_sock.sendall()
                        client_sock.close() #closes socket after each message is sent #TODO is there a better way to do this?
                    else: 
                        print 'Unable to connect to DC...'
                else: 
                    print 'sleeping'
                    time.sleep(1) #else, wait until messages are in queue
            except KeyboardInterrupt, k:
                    print "Shutting down."
                    break
                
        #print "Connecting to data cache..."
        #if os.path.exists('/tmp/Data_Cache_unix_socket'):
            #client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            #client_sock.connect('/tmp/Data_Cache_unix_socket')
            #print "Ready"
            #print "Ctrl-C to quit."
            #print "Sending 'DONE' shuts down the server and quits."
            #while True:
                #print 'while True....'
                #try:
                    #if not comm.DC_push.empty(): #if the queue is not empty, send message
                        #data = comm.DC_push.get() #theoretically pushes messages from the GN into a queue
                        #print "sending: " , data
                        #client_sock.sendall(str(data))
                        
                    #else:
                        #print 'sleeping'
                        #time.sleep(1) #else, wait and try again
                #except KeyboardInterrupt, k:
                    #print "Shutting down."
                    #break
            #client_sock.close()
        #else:
            #print "Couldn't Connect!"
        #print "Done."
        
class client_pull(Process):
    """ A client process that connects to the data cache and pulls incoming messages out. Sends a request in the format 'i,dev' and recieves the message"""
    #TODO fix this! 
    
    def run(self):
        comm = internal_communicator()
        print "Connecting to data cache... client_pull"
        if os.path.exists('/tmp/Data_Cache_pull_server'):
            client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client_sock.connect('/tmp/Data_Cache_pull_server')
            print "Ready"
            print "Ctrl-C to quit."
            print "Sending 'DONE' shuts down the server and quits."
            while True:
                #TODO add another layer that can sleep if no messages are in the queue
                try: 
                    data = comm.DC_push.get() #theoretically pushes messages from the GN into a queue
                    if not data:
                        print "sending: " , data
                        client_sock.send(data)
                        if 'DONE' == data:
                            print 'Shutting down.'
                            break
                except KeyboardInterrupt, k:
                    print "Shutting down."
                    break
            client_sock.close()
        else:
            print "Couldn't Connect!"
        print "Done."
        
class server(Process):
    """ Server process that listens for connections from GNs. Gets messages from the guest nodes, parses head to get device ID (can also use device IP), and msg_p, 
    puts in tuple form along with indicator flag specifying that it is an outgoing message, stores it in DC_push queue... for now."""
    #TODO handle outgoing messages
    
    def run(self):
        print 'server process started'
        comm = internal_communicator()
        HOST = '0.0.0.0'
        PORT = 9090
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST,PORT))
        server.listen(5) #supports up to 5 threads, one for each GN
        
        while True:
            conn, addr = server.accept()
            print "Connected to ", addr
            while True:
                try:
                    data = conn.recv(4028) 
                    if not data:
                        processor(data)
                    else:
                       pass
                except KeyboardInterrupt, k:
                    print "Shutting down."
                    break
            server.close()
            
def processor(data):
    """ This class takes a packet, unpacks the header, extracts flags and sender and reciever data, puts it in the appropriate queue. """
        header = PacketHandler.unpack_header(data)
        if header['r_uniqid'] == 'cloud': #TODO replace with the actual unique ID for the cloud
            dev, msg, order = header['flags'] #unpacks the tuple containing the flags
            #adds each onto the msg string #TODO will this work with pickled things?
            data += (str(order) + '|')
            data += (str(msg) + ',')
            data += (str(dev) +',')
            data += 'o,' #indicates that it is an outgoing message
            internal_communicator.DC_push.put(data)
        else:
            pass 
            #TODO figure out how to send data to the GNs
        
        
    

if __name__ == "__main__":
    try:
        
        serv = server()
        serv.start()
      
        push = client_push()
        push.start()
        while True:
            pass
        
    except KeyboardInterrupt, k:
        server.terminate()
        push.terminate()
        print 'Done.'
    
                