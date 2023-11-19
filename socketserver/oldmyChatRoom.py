from socketserver import ThreadingTCPServer,BaseRequestHandler

class myHandler(BaseRequestHandler):
    def broadcast_string(self, b_msg, skip_socket):
        for socket in SOCKETS_LIST:
            if socket != myServer and socket != skip_socket:
                socket.send(b_msg.encode())
        print (b_msg)
            
    def handle(self):
        SOCKETS_LIST.append(self.request)
        print (str(SOCKETS_LIST) + "\r\n")
        self.request.send(b"You're connected to the chatserver\r\n")
        host, port = self.client_address
        msg = "Client joined " + str(self.client_address) + "\r\n"
        self.broadcast_string(msg,self.request)
        while True:
            data = self.request.recv(1024)
            if data.decode() == "bye\r\n":
                msg = "Client left" + str(self.client_address) + "\r\n"
                SOCKETS_LIST.remove(self.request)
                self.broadcast_string(msg,self.request)
                break
            else:
                msg = "[%s:%s] %s" % (host, port, data.decode())
                self.broadcast_string(msg, self.request)

myServer = ThreadingTCPServer(("127.0.0.1",5556),myHandler)
SOCKETS_LIST = []
SOCKETS_LIST.append(myServer)
print ("ChatServer started on port %s" % 5556)
myServer.serve_forever()