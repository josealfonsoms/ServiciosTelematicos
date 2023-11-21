import socket
from socketserver import ThreadingTCPServer, ThreadingUDPServer, BaseRequestHandler

bank_server_address = ("127.0.0.1", 3458)   # Dirección y puerto del servidor bank
liquor_store_address = ("127.0.0.1", 8888)  # Dirección y puerto del servidor LiquorStore

class BankServerHandler(BaseRequestHandler):
    accounts = {
        "1234": {"nombre": "Usuario1", "contraseña": "pass1", "saldo": 200},
        "5678": {"nombre": "Usuario2", "contraseña": "pass2", "saldo": 150},
        "9012": {"nombre": "Usuario3", "contraseña": "pass3", "saldo": 300},
    }

    def handle(self):
        print("Connection from ", str(self.client_address))
        while True:
            data = self.request.recv(1024)
            self.request.send(data.upper())
        self.request.close()

class LiquiorStoreHandler(BaseRequestHandler):
    def handle(self):
        print("Connection from ", str(self.client_address))
        data, conn = self.request
        conn.sendto(data.upper(), self.client_address)

# Inicializar servidor
bank_server = ThreadingTCPServer((bank_server_address), BankServerHandler)
liquorStore_server = ThreadingUDPServer((liquor_store_address), LiquiorStoreHandler)
print("Se ha iniciado el servidor BANK TCP en el puerto %s" % bank_server_address[1])
print("Se ha iniciado el servidor LIQUORSTORE UDP en el puerto %s" % liquor_store_address[1])
bank_server.serve_forever()
liquorStore_server.serve_forever()