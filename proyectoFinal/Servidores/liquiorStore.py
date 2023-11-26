from socketserver import ThreadingTCPServer, ThreadingUDPServer, BaseRequestHandler
from threading import Thread
from socket import *

# Datos simulados de inventario de licores
inventory = {
    1: {"codigo": 1, "nombre": "Licor1", "origen": "US", "unidades": 10, "precio": 20},
    2: {"codigo": 2, "nombre": "Licor2", "origen": "FR", "unidades": 8, "precio": 25},
    # ... Otros licores
}

# Puertos liquor
liquorStoreTCP_address = ("127.0.0.1", 7581)    # TCP
liquorStoreUDP_address = ("127.0.0.1", 3558)    # UDP

# Puertos bank
bankUDP_adress = ("127.0.0.1", 3459)    # UDP

# Lista compartida para respuestas a clientes
responses = []

class LiquorStore(BaseRequestHandler):
    def menu(self):
            self.request.sendall("1. Listar inventario.\r\n".encode())
            self.request.sendall("2. Comprar un licor.\r\n".encode())
            self.request.sendall("3. Salir.\r\n".encode())

    def broadcast_string(self, b_msg, skip_socket):
        for socket in self.server.sockets:
            if socket != self.request and socket != skip_socket:
                socket.send(b_msg.encode())
        print(b_msg)
    
    def procesarCompra(self, liquor_code):
        licor = inventory.get(int(liquor_code))
        if licor:
            self.request.sendall(b"Estas intentado realizar una compra, por favor ingresar en tu banco.\r\n")
            self.request.sendall(b"Numero de cuenta:")
            username = self.request.recv(1024).decode().strip()
            self.request.sendall(b"Ahora ingresa el password:")
            password = self.request.recv(1024).decode().strip()
            costo = licor["precio"]
            user_credentials = f"{username} {password} {costo}"
            return user_credentials
        
    def enviar_a_Banco(self, mensaje):
        # Enviar al banco
        bank_socket = socket(AF_INET, SOCK_DGRAM)
        bank_socket.sendto(mensaje.encode(), bankUDP_adress)

    def responderCliente(self):
        while True:
            if responses:
                response = responses.pop(0)
                for socket in self.server.sockets:
                    socket.send(response.encode())

    def handle(self):
        self.server.sockets.append(self.request)
        self.request.send(b"BIENVENIDO A LIQUOR-STORE. Para ver opciones ingrese: help\r\n")
        self.menu()
        msg = "\r\n" + "Client joined " + str(self.client_address) + "\r\n"
        self.broadcast_string(msg, self.request)
        
        # Iniciar hilo para enviar respuestas a los clientes
        response_thread = Thread(target=self.responderCliente)
        response_thread.start()
        
        while True:
            data = self.request.recv(1024)
            decoded_data = data.decode().split()
            command = decoded_data[0]

            if command == "1":
                # Imprimir la lista de licores de manera organizada
                response = "\r\n".join([f"{key}: {value}" for key, value in inventory.items()]) + "\r\n"
                self.request.sendall(response.encode())
            elif command == "2":
                # Comprar
                self.request.sendall("Ingrese el codigo del licor que desea comprar.\r\n".encode())
                liquor_code = self.request.recv(1024).decode().strip()
                if liquor_code:
                    # Hacer una compra
                    user_credentials = self.procesarCompra(liquor_code)
                    # Enviar al informacion al banco
                    self.enviar_a_Banco(user_credentials)
            elif command == "3":
                # Salir
                msg = "Client left " + str(self.client_address) + "\r\n"
                self.broadcast_string(msg, self.request)
                self.server.sockets.remove(self.request)
                break
            elif command == "help":
                self.menu()
            else:
                self.request.sendall("Comando invalido.\r\n".encode())
                self.menu()
        self.request.close()

class BankServer(BaseRequestHandler):
    def handle(self):
        data, conn = self.request
        decoded_data = data.decode()
        print(decoded_data.upper())
        if decoded_data == "OK":
            responses.append("Desea confirmar la compra? y/n\r\n")

        elif decoded_data == "Saldo insuficiente":
            responses.append("Usted no posee saldo suficiente para hacer esta compra.\r\n")

        elif decoded_data == "Credenciales invalidas":
            responses.append("Error de autenticacion, intente de nuevo.\r\n")
        else:
            responses.append("Error al procesar respuesta con su banco, intente nuevamente.\r\n")

# Inicializar servidor
liquor_server1 = ThreadingTCPServer(liquorStoreTCP_address, LiquorStore)
liquor_server2 = ThreadingUDPServer(liquorStoreUDP_address, BankServer)

liquorStore_TCP = Thread(target=liquor_server1.serve_forever)
liquorStore_UDP = Thread(target=liquor_server2.serve_forever)

# Iniciar hilos
liquorStore_TCP.start()
liquorStore_UDP.start()

liquor_server1.sockets = []  # Lista para almacenar los sockets de los clientes
print(f"LIQUOR-STORE TCP server started on port {liquorStoreTCP_address[1]}")
print(f"LIQUOR-STORE UDP server started on port {liquorStoreUDP_address[1]}")
