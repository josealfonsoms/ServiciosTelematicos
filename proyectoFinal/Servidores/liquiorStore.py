from socketserver import ThreadingTCPServer, ThreadingUDPServer, BaseRequestHandler
from threading import Thread
from socket import *

# Datos simulados de inventario de licores
inventory = {
    1: {"nombre": "Licor1", "origen": "US", "unidades": 10, "precio": 20},
    2: {"nombre": "Licor2", "origen": "FR", "unidades": 8, "precio": 25},
    # ... Otros licores
}
responses = []                                  # Lista compartida para respuestas a clientes

# PUERTOS USADOS
liquorStoreTCP_address = ("127.0.0.1", 8000)    # TCP LiquorStore

liquorStoreUDP_address = ("127.0.0.1", 3555)    # UDP LiquorStore
bankUDP_adress = ("127.0.0.1", 3459)            # UDP Bank

class LiquorStore(BaseRequestHandler):
    def menu(self, usuariosConectados):
            mensaje = f"Usuarios conectados: ({usuariosConectados})\n"
            mensaje += f"\nMEMU PRINCIPAL:\n"
            mensaje += f"1. Ver licores disponibles.\n"
            mensaje += f"2. Comprar un licor.\n"
            mensaje += f"3. Salir.\n"
            mensaje += f"4. Actualizar menu principal.\n"
            self.request.send(mensaje.encode())
    
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
        self.server.usuariosConectados += 1
        self.request.send(b"\nBIENVENIDO A LIQUOR-STORE.\r\n")
        self.menu(self.server.usuariosConectados)
        
        # Iniciar hilo para enviar respuestas a los clientes
        response_thread = Thread(target=self.responderCliente)
        response_thread.start()
        
        while True:
            data = self.request.recv(1024)
            decoded_data = data.decode().split()
            command = decoded_data[0]

            if command == "1":
                # Imprimir la lista de licores organizada
                response = "\r\n".join([f"{key}: {value}" for key, value in inventory.items()]) + "\r\n"
                self.request.sendall(response.encode())
            elif command == "2":
                # Comprar
                self.request.sendall("Ingrese el codigo del licor que desea comprar.\r\n".encode())
                liquor_code = self.request.recv(1024).decode().strip()
                if liquor_code:
                    user_credentials = self.procesarCompra(liquor_code) # Hacer una compra
                    self.enviar_a_Banco(user_credentials)               # Enviar la informacion al banco
            elif command == "3":
                # Salir
                self.server.usuariosConectados -= 1                                 # Decrementar usuario que abandona
                self.server.sockets.remove(self.request)
                break
            elif command == "4":
                self.menu(self.server.usuariosConectados)
            else:
                self.request.sendall("Comando invalido.\r\n".encode())
                self.menu(self.server.usuariosConectados)
        self.request.close()

class respBankHandler(BaseRequestHandler):

    def enviar_a_Banco(self, mensaje):
        # Enviar al banco
        bank_socket = socket(AF_INET, SOCK_DGRAM)
        bank_socket.sendto(mensaje.encode(), bankUDP_adress)
        
    def handle(self):
        data, conn = self.request
        resp_bank = data.decode()
        print(resp_bank.upper())
        if resp_bank == "OK":
            responses.append("Desea confirmar la compra? y/n\r\n")
            # Recibir la confirmación del cliente a través del socket TCP
            confirmacion = self.request.recvfrom(1024).decode().strip().lower() # CORREGIR!
            print(confirmacion)
            if confirmacion == 'y' or confirmacion == 'n':
                # Enviar la confirmación al banco a través de UDP
                self.enviar_a_Banco(confirmacion)
            else:
                print("Entrada no válida. Debe ingresar 'y' o 'n'.")


        elif resp_bank == "Saldo insuficiente":
            responses.append("Usted no posee saldo suficiente para hacer esta compra.\r\n")
        elif resp_bank == "Credenciales invalidas":
            responses.append("Error de autenticacion, intente de nuevo.\r\n")
        else:
            responses.append("Error al procesar respuesta con su banco, intente nuevamente.\r\n")

try:
    # Inicializar servidor TCP
    liquor_server1 = ThreadingTCPServer(liquorStoreTCP_address, LiquorStore)
    liquor_server1.usuariosConectados = 0    # Manejar usuarios conectados
    liquor_server1.sockets = []              # Lista para almacenar los sockets de los clientes
    liquorStore_TCP = Thread(target=liquor_server1.serve_forever)
    liquorStore_TCP.start()
    print(f"LIQUOR-STORE inició en puerto TCP {liquorStoreTCP_address[1]}")
except Exception as error:
    print(f"LIQUOR-STORE no pudo iniciarse en puerto TCP {liquorStoreTCP_address[1]}: {error}")

try:
    # Inicializar servidor UDP
    liquor_server2 = ThreadingUDPServer(liquorStoreUDP_address, respBankHandler)
    liquorStore_UDP = Thread(target=liquor_server2.serve_forever)
    liquorStore_UDP.start()
    print(f"LIQUOR-STORE inició en puerto UDP {liquorStoreUDP_address[1]}")
except Exception as error:
    print(f"LIQUOR-STORE no pudo iniciarse en puerto UDP {liquorStoreUDP_address[1]}: {error}")

