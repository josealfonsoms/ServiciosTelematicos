import socket
from socketserver import ThreadingUDPServer, BaseRequestHandler

# Datos del servidor bank
dir_ip = "127.0.0.1"
puerto = 3458

liquor_store_address = ("127.0.0.1", 7558)  # Dirección y puerto del servidor LiquorStore

class BankServerHandler(BaseRequestHandler):
    accounts = {
        "1234": {"nombre": "Usuario1", "contraseña": "pass1", "saldo": 200},
        "5678": {"nombre": "Usuario2", "contraseña": "pass2", "saldo": 150},
        "9012": {"nombre": "Usuario3", "contraseña": "pass3", "saldo": 300},
    }

    def handle(self):
        data = self.request[0].strip()  # Datos recibidos
        socket = self.request[1]  # Socket del cliente

        decoded_data = data.decode().split()

        usuario = decoded_data[0]
        contraseña = decoded_data[1]
        costo = int(decoded_data[2])  # Convertir a entero para comparaciones
        print(usuario)
        # Verificar las credenciales del usuario
        if usuario in self.accounts and contraseña == self.accounts[usuario]["contraseña"]:
            saldo_disponible = self.accounts[usuario]["saldo"]
            if saldo_disponible >= costo:
                # Si el usuario tiene saldo suficiente, enviar 'OK' al servidor LiquorStore
                response = "OK"
                self.request.sendto(response.encode(), liquor_store_address)
            else:
                # Si el usuario no tiene saldo suficiente, enviar 'NO_DISPONIBLE'
                response = "Saldo insuficiente"
                self.request.sendto(response.encode(), liquor_store_address)
        else:
            # Si las credenciales no son válidas, enviar 'INVALIDO'
            response = "Credenciales invalidas"

# Inicializar servidor
bank_server = ThreadingUDPServer((dir_ip, puerto), BankServerHandler)
print("BANK server started on port %s" % puerto)
bank_server.serve_forever()
