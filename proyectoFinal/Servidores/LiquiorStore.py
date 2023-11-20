import socket
from socketserver import ThreadingTCPServer, BaseRequestHandler

# Datos del servidor LiquorStore
dir_ip = "127.0.0.1"
puerto = 7559

bank_server_address = ("127.0.0.1", 3458)  # Dirección y puerto del servidor BANK
# Datos simulados de inventario de licores
inventory = {
    1: {"code": 1, "name": "Licor1", "origin": "US", "units": 10, "cost_per_unit": 20.0},
    2: {"code": 2, "name": "Licor2", "origin": "FR", "units": 8, "cost_per_unit": 25.0},
    # ... Otros licores
}

class LiquorStore(BaseRequestHandler):
    def broadcast_string(self, b_msg, skip_socket):
        for socket in self.server.sockets:
            if socket != self.request and socket != skip_socket:
                socket.send(b_msg.encode())
        print(b_msg)

    def handle(self):
        self.server.sockets.append(self.request)
        self.request.send(b"You're connected to the LIQUOR-STORE server\r\n")
        host, port = self.client_address
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
                # Lógica para procesar la compra
                response = self.process_purchase(*decoded_data[1:])  # Simplemente para ejemplificar
                self.request.sendall(response.encode())

            elif command == "exit":
                msg = "Client left " + str(self.client_address) + "\r\n"
                self.broadcast_string(msg, self.request)
                self.server.sockets.remove(self.request)
                break

            elif command == "bank":
                # Recolectar el mensaje escrito por el cliente
                message = ' '.join(decoded_data[1:]).lower()
                
                # Enviar el mensaje al servidor BANK
                bank_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                bank_udp_socket.sendto(message.encode(), bank_server_address)

                # Recibir la respuesta del servidor BANK
                response, _ = bank_udp_socket.recvfrom(1024)
                self.request.sendall(response)
                bank_udp_socket.close()

            else:
                self.request.sendall("Comando invalido".encode())



        self.request.close()

# Inicializar servidor
liquor_server = ThreadingTCPServer((dir_ip, puerto), LiquorStore)
liquor_server.sockets = []  # Lista para almacenar los sockets de los clientes
print("LIQUOR-STORE server started on port %s" % puerto)
liquor_server.serve_forever()
