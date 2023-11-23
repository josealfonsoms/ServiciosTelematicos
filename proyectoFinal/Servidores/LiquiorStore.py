from socketserver import ThreadingTCPServer, BaseRequestHandler
import threading
from socket import *

# Datos de Servidores
liquorStore_address = ("127.0.0.1", 7556)    # Dirección y puerto del servidor LiquorStore
bank_address = ("127.0.0.1", 3458)           # Dirección y puerto del servidor Bank

# Datos simulados de inventario de licores
inventory = {
    1: {"code": 1, "name": "Licor1", "origin": "US", "units": 10, "cost_per_unit": 20},
    2: {"code": 2, "name": "Licor2", "origin": "FR", "units": 8, "cost_per_unit": 25},
    # ... Otros licores
}

class LiquorStore(BaseRequestHandler):
    def broadcast_string(self, b_msg, skip_socket):
        for socket in self.server.sockets:
            if socket != self.request and socket != skip_socket:
                socket.send(b_msg.encode())
        print(b_msg)
    
    def extraerprecio(self, liquor_code):
        liquor = inventory.get(int(liquor_code))
        if (liquor):
            costo = liquor["cost_per_unit"]
            return costo

    def handle(self):
        self.server.sockets.append(self.request)
        self.request.send(b"You're connected to the LIQUOR-STORE server\r\n")
        msg = "\r\n" + "Client joined " + str(self.client_address) + "\r\n"
        self.broadcast_string(msg, self.request)
        
        while True:
            data = self.request.recv(1024)
            decoded_data = data.decode().split()
            command = decoded_data[0]

            if command == "list":
                # Imprimir la lista de licores de manera organizada
                response = "\r\n".join([f"{key}: {value}" for key, value in inventory.items()]) + "\r\n"
                self.request.sendall(response.encode())

            elif command == "buy":
                liquor_code = decoded_data[1] if len(decoded_data) > 1 else None
                if (liquor_code):
                    costo = self.extraerprecio(liquor_code)
                    self.request.sendall(b"You're about to make a purchase. Please log in to your bank account.\r\n")
                    self.request.sendall(b"Enter your username:")
                    username = self.request.recv(1024).decode().strip()
                    self.request.sendall(b"Now enter your password:")
                    password = self.request.recv(1024).decode().strip()
                    user_credentials = f"{username} {password} {costo}"
                    
                    # Enviar al banco
                    bank_socket = socket(AF_INET, SOCK_DGRAM)
                    bank_socket.sendto(user_credentials.encode(), (bank_address))

                    # Recibir respuesta del banco
                    response_bank, _ = bank_socket.recvfrom(1024)
                    decoded_response_bank = response_bank.decode().strip()
                    print(decoded_response_bank)

                    if decoded_response_bank == "OK":
                        self.request.sendall(b"Desea confirmar la compra?\r\n")
                    else:
                        self.request.sendall(b"Saldo insuficiente\r\n")

            elif command == "exit":
                msg = "Client left " + str(self.client_address) + "\r\n"
                self.broadcast_string(msg, self.request)
                self.server.sockets.remove(self.request)
                break

            else:
                self.request.sendall("Comando invalido".encode())

        self.request.close()

# Inicializar servidor
liquor_server = ThreadingTCPServer((liquorStore_address), LiquorStore)
liquor_server.sockets = []  # Lista para almacenar los sockets de los clientes
print("LIQUOR-STORE server started on port %s" % liquorStore_address[1])
liquor_server.serve_forever()
