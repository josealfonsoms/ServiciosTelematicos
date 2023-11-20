import socket
from socketserver import ThreadingTCPServer, BaseRequestHandler

# Datos del servidor bank
dir_ip = "127.0.0.1"
puerto = 3458

liquor_store_address = ("127.0.0.1", 7559)  # Dirección y puerto del servidor LiquorStore

class BankServerHandler(BaseRequestHandler):
    accounts = {
        "1234": {"nombre": "Usuario1", "contraseña": "pass1", "saldo": 200},
        "5678": {"nombre": "Usuario2", "contraseña": "pass2", "saldo": 150},
        "9012": {"nombre": "Usuario3", "contraseña": "pass3", "saldo": 300},
    }

    def handle(self):
        bank_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bank_udp_socket.bind(("127.0.0.1", 3458))  # Asignar el puerto para la comunicación UDP

        while True:
            data, addr = bank_udp_socket.recvfrom(1024)
            message = data.decode().upper()  # Convertir el mensaje a mayúsculas

            # Enviar el mensaje en mayúsculas de vuelta al servidor "LIQUOR-STORE"
            bank_udp_socket.sendto(message.encode(), liquor_store_address)

        bank_udp_socket.close()

# Inicializar servidor
bank_server = ThreadingTCPServer((dir_ip, puerto), BankServerHandler)
print("BANK server started on port %s" % puerto)
bank_server.serve_forever()
