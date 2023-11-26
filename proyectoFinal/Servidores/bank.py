from socketserver import ThreadingUDPServer, BaseRequestHandler

# Datos de servidores
bank_address = ("127.0.0.1", 3459)              # Dirección y puerto UDP del servidor Bank
liquorStoreUDP_address = ("127.0.0.1", 3555)     # Dirección y puerto UDP del servidor LiquorStore

class BankServerHandler(BaseRequestHandler):
    accounts = {
        "1234": {"nombre": "Usuario1", "contraseña": "pass1", "saldo": 200},
        "5678": {"nombre": "Usuario2", "contraseña": "pass2", "saldo": 150},
        "9012": {"nombre": "Usuario3", "contraseña": "pass3", "saldo": 300},
    }

    def verificarSaldo(self, usuario, contraseña, costo):
        # Verificar las credenciales del usuario
        if usuario in self.accounts and contraseña == self.accounts[usuario]["contraseña"]:
            saldo_disponible = self.accounts[usuario]["saldo"]
            print(f"Saldo disponible para {usuario}: {saldo_disponible}")
            print(f"Monto a descontar para la compra: {costo}")
            if saldo_disponible >= costo:
                # Si el usuario tiene saldo suficiente
                return "OK"
            else:
                return "Saldo insuficiente"
        else:
            return "Credenciales invalidas"
        
    def handle(self):
        data, conn = self.request  # Recibir datos de LIQUOR-STORE

        # Almacenar datos entrantes
        decoded_data = data.strip().decode().split()
        #peticion = decoded_data[0]                                  #Controlar peticiones
        if len(decoded_data) >= 3:
            usuario = decoded_data[0]
            contraseña = decoded_data[1]
            costo = int(decoded_data[2])                                # Convertir a entero para comparaciones
            response = self.verificarSaldo(usuario, contraseña, costo)
            print(response) 
            conn.sendto(response.encode(), liquorStoreUDP_address)      # Responder a LiquorStore
        elif len(decoded_data) == 1:
            confirmacion = decoded_data[0]
            print(confirmacion)
            print("Compra realizada!")

try:
    # Inicializar servidor
    bank_server = ThreadingUDPServer((bank_address), BankServerHandler)
    print("BANK inició por el puerto UDP: %s" % bank_address[1])
    bank_server.serve_forever()
except Exception as error:
    print(print(f"BANK no pudo iniciarse en puerto UDP {liquorStoreUDP_address[1]}: {error}"))

