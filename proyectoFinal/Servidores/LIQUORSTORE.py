from socketserver import ThreadingTCPServer, BaseRequestHandler

# Datos simulados de inventario de licores
inventory = {
    1: {"code": 1, "name": "Licor1", "origin": "US", "units": 10, "cost_per_unit": 20.0},
    2: {"code": 2, "name": "Licor2", "origin": "FR", "units": 8, "cost_per_unit": 25.0},
    # ... Otros licores
}

class LiquorStoreHandler(BaseRequestHandler):
    def broadcast_string(self, b_msg, skip_socket):
        for socket in self.server.sockets:
            if socket != self.request and socket != skip_socket:
                socket.send(b_msg.encode())
        print(b_msg)

    def process_purchase(self, user_credentials, liquor_code):
        # Lógica simulada de conexión con el servidor BANK para verificar credenciales y saldo
        # Aquí se realizaría la lógica real de conexión con el servidor BANK
        # bank_approved = check_with_bank(user_credentials, liquor_code, inventory[liquor_code]["cost_per_unit"])

        bank_approved = True  # Suponemos aprobación para simplificar

        if bank_approved:
            liquor = inventory.get(liquor_code)
            if liquor and liquor["units"] > 0:
                liquor["units"] -= 1
                return "¡Compra exitosa! Has adquirido el licor."
            else:
                return "El licor no está disponible en este momento."
        else:
            return "La compra fue rechazada por el banco debido a saldo insuficiente o credenciales inválidas."

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
            else:
                self.request.sendall("Invalid command".encode())

        self.request.close()

# Crear el servidor
dir_ip = "127.0.0.1"
puerto = 7559
# Inicializar servidor
liquor_server = ThreadingTCPServer((dir_ip, puerto), LiquorStoreHandler)
liquor_server.sockets = []  # Lista para almacenar los sockets de los clientes
print("LIQUOR-STORE server started on port %s" % puerto)
liquor_server.serve_forever()
