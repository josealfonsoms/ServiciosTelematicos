from socketserver import TCPServer, UDPServer, BaseRequestHandler
from sys import argv

class myHandler(BaseRequestHandler):
    def handle (self):
        print("Entra")
        # if(len(argv!=3)):
        # #     print("Use: scan.py [Protocol][IP_Address] [TCP_Port]")
        # else:
        if (argv[1] == "tcp"):
            print ("Connection from ", str(self.client_address))
            while True:
                data = self.request.recv(1024)
                if data.decode() == "bye\r\n": break
                self.request.send(data.upper())
            self.request.close()
        elif(argv[1] == "udp"):
            print ("Connection from ", str(self.client_address))
            data, conn = self.request
            conn.sendto(data.upper(),self.client_address)
        else:
            print("protocolo no valido")

if (argv[1]== "tcp"):
    print("HOLA SERVIDOR")
    myServer = TCPServer((argv[2], int(argv[3])), myHandler)
    myServer.serve_forever()
elif (argv[1]=="udp"):
    myServer = UDPServer((argv[2], int(argv[3])), myHandler)
    myServer.serve_forever()