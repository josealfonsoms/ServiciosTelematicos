from socketserver import ThreadingUDPServer, BaseRequestHandler

# Datos de servidores
bank_address = ("127.0.0.1", 3458)              # Dirección y puerto UDP del servidor Bank
liquorStore_address = ("127.0.0.1", 7556)     # Dirección y puerto TCP del servidor LiquorStore

class BankServerHandler(BaseRequestHandler):
    accounts = {
        "1234": {"nombre": "Usuario1", "contraseña": "pass1", "saldo": 200},
        "5678": {"nombre": "Usuario2", "contraseña": "pass2", "saldo": 150},
        "9012": {"nombre": "Usuario3", "contraseña": "pass3", "saldo": 300},
    }

    def handle(self):
        data, conn = self.request  # Datos recibidos y socket del cliente

        # Extraer usuario, contraseña y costo de los datos recibidos
        decoded_data = data.strip().decode().split()
        usuario = decoded_data[0]
        contraseña = decoded_data[1]
        costo = int(decoded_data[2])  # Convertir a entero para comparaciones
        print(f'Usuario: {usuario}, Contraseña: {contraseña}')

        # Verificar las credenciales del usuario
        if usuario in self.accounts and contraseña == self.accounts[usuario]["contraseña"]:
            saldo_disponible = self.accounts[usuario]["saldo"]
            print(f"Saldo disponible para {usuario}: {saldo_disponible}")
            print(f"Monto a descontar para la compra: {costo}")
            if saldo_disponible >= costo:
                # Si el usuario tiene saldo suficiente
                response = "OK"
            else:
                # Si el usuario no tiene saldo suficiente
                response = "Bank: Saldo insuficiente"
        else:
            # Si las credenciales no son válidas
            response = "Bank: Credenciales invalidas"
        # Responder a LiquorStore
        print(response) 
        conn.sendto(response.encode(), liquorStore_address)

# Inicializar servidor
bank_server = ThreadingUDPServer((bank_address), BankServerHandler)
print("BANK server started on port %s" % bank_address[1])
bank_server.serve_forever()
