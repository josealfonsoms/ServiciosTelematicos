from socketserver import ThreadingTCPServer, BaseRequestHandler

# Datos simulados de inventario de licores
inventory = {
    1: {"code": 1, "name": "Licor1", "origin": "US", "units": 10, "cost_per_unit": 20.0},
    2: {"code": 2, "name": "Licor2", "origin": "FR", "units": 8, "cost_per_unit": 25.0},
    # ... Otros licores
}

class BankServer:
    def __init__(self):
        # Base de datos simulada para almacenar información de los clientes
        self.clients_db = {
            "123456": {"account": "123456", "name": "Cliente1", "password": "pass1", "balance": 500.0},
            "789012": {"account": "789012", "name": "Cliente2", "password": "pass2", "balance": 750.0},
            "345678": {"account": "345678", "name": "Cliente3", "password": "pass3", "balance": 300.0},
        }

    def authenticate_client(self, account, password):
        # Verificar si las credenciales son válidas
        client = self.clients_db.get(account)
        if client and client["password"] == password:
            return True
        return False

    def check_balance(self, account):
        # Consultar el saldo de un cliente
        client = self.clients_db.get(account)
        if client:
            return client["balance"]
        return None

    def deposit(self, account, amount):
        # Incrementar el saldo de un cliente
        client = self.clients_db.get(account)
        if client:
            client["balance"] += amount
            return True
        return False

    def withdraw(self, account, amount):
        # Decrementar el saldo de un cliente si hay fondos suficientes
        client = self.clients_db.get(account)
        if client and client["balance"] >= amount:
            client["balance"] -= amount
            return True
        return False

class BankHandler(BaseRequestHandler):
    bank_server = BankServer()

    def process_transaction(self, user_credentials, transaction_type, amount=None):
        account, password = user_credentials
        authenticated = self.bank_server.authenticate_client(account, password)

        if not authenticated:
            return "Error de autenticación: Credenciales inválidas."

        if transaction_type == "balance":
            balance = self.bank_server.check_balance(account)
            if balance is not None:
                return f"Saldo actual: {balance}"
            return "No se pudo obtener el saldo."

        elif transaction_type == "deposit":
            if amount is None:
                return "Falta el monto a depositar."
            if self.bank_server.deposit(account, amount):
                return f"Depósito de {amount} exitoso. Nuevo saldo: {self.bank_server.check_balance(account)}"
            return "No se pudo realizar el depósito."

        elif transaction_type == "withdraw":
            if amount is None:
                return "Falta el monto a retirar."
            if self.bank_server.withdraw(account, amount):
                return f"Retiro de {amount} exitoso. Nuevo saldo: {self.bank_server.check_balance(account)}"
            return "Fondos insuficientes para retirar."

        return "Comando no reconocido."


class LiquorStoreHandler(BaseRequestHandler):
    def broadcast_string(self, b_msg, skip_socket):
        for socket in self.server.sockets:
            if socket != self.request and socket != skip_socket:
                socket.send(b_msg.encode())
        print(b_msg)

    def process_purchase(self, user_credentials, liquor_code, quantity):
        bank_handler = BankHandler()
        liquor = inventory.get(int(liquor_code))

        if liquor:
            total_cost = liquor["cost_per_unit"] * int(quantity)
            response = bank_handler.process_transaction(user_credentials, "withdraw", amount=total_cost)

            if "exitoso" in response:
                if liquor["units"] >= int(quantity):
                    liquor["units"] -= int(quantity)
                    return f"{response}\n¡Compra exitosa! Has adquirido {quantity} unidades del licor {liquor['name']}."
                else:
                    return f"No hay suficientes unidades de {liquor['name']} disponibles."
            else:
                return response
        else:
            return "Código de licor inválido."
        
    def handle(self):
        self.server.sockets.append(self.request)
        self.request.send(b"You're connected to the LIQUOR-STORE server\r\n")
        host, port = self.client_address
        msg = "\r\n" + "Client joined " + str(self.client_address) + "\r\n"
        self.broadcast_string(msg, self.request)
        authenticated = False
        user_credentials = []

        while True:
            data = self.request.recv(1024)
            decoded_data = data.decode().split()
            command = decoded_data[0]

            if not authenticated:
                if command == "list":
                    # Imprimir la lista de licores de manera organizada
                    response = "\r\n".join([f"{key}: {value}" for key, value in inventory.items()]) + "\r\n"
                    self.request.sendall(response.encode())

                elif command == "buy":
                    self.request.sendall(b"You're about to make a purchase. Please log in to your bank account.\r\n")
                    self.request.sendall(b"Enter your username:\r\n")
                    username = self.request.recv(1024).decode().strip()
                    self.request.sendall(b"Now enter your password:\r\n")
                    password = self.request.recv(1024).decode().strip()
                    user_credentials = [username, password]

                    bank_handler = BankHandler()
                    authenticated = bank_handler.authenticate_client(username, password)

                    if authenticated:
                        client = bank_handler.clients_db.get(username)
                        self.request.sendall(f"Hello {client['name']}\r\n".encode())
                        self.request.sendall(b"Ahora puedes ver tu saldo, retirar o consignar.\r\n")
                    else:
                        self.request.sendall(b"Credenciales invalidas, intenta de nuevo o exit para salir\r\n")

                elif command == "exit":
                    msg = "Client left " + str(self.client_address) + "\r\n"
                    self.broadcast_string(msg, self.request)
                    self.server.sockets.remove(self.request)
                    break
                else:
                    self.request.sendall(b"Comando invalido, porfavor digital list, buy, o exit para salir\r\n")

            else:
                if command == "list":
                    # Imprimir la lista de licores de manera organizada
                    response = "\r\n".join([f"{key}: {value}" for key, value in inventory.items()]) + "\r\n"
                    self.request.sendall(response.encode())

                elif command.startswith("buy"):
                    # Lógica para procesar la compra
                    liquor_code = command.split()[1] if len(command.split()) > 1 else None
                    quantity = 1  # Se asume una cantidad predeterminada por ahora

                    if liquor_code:
                        response = self.process_purchase(user_credentials, liquor_code, quantity)
                        self.request.sendall(response.encode())
                    else:
                        self.request.sendall(b"Invalid purchase command. Please provide a valid liquor code.\r\n")

                elif command == "balance":
                    # Lógica para consultar saldo
                    bank_handler = BankHandler()
                    balance = bank_handler.check_balance(user_credentials[0])
                    if balance is not None:
                        self.request.sendall(f"Current balance: {balance}\r\n".encode())
                    else:
                        self.request.sendall(b"Unable to retrieve balance.\r\n")

                elif command.startswith("consignar"):
                    # Lógica para consignar
                    amount = float(command.split()[1]) if len(command.split()) > 1 else None
                    if amount:
                        bank_handler = BankHandler()
                        if bank_handler.deposit(user_credentials[0], amount):
                            self.request.sendall(f"Deposited {amount}. New balance: {bank_handler.check_balance(user_credentials[0])}\r\n".encode())
                        else:
                            self.request.sendall(b"Unable to deposit. Please try again.\r\n")
                    else:
                        self.request.sendall(b"Invalid deposit command. Please provide a valid amount.\r\n")

                elif command.startswith("retirar"):
                    # Lógica para retirar
                    amount = float(command.split()[1]) if len(command.split()) > 1 else None
                    if amount:
                        bank_handler = BankHandler()
                        if bank_handler.withdraw(user_credentials[0], amount):
                            self.request.sendall(f"Withdrew {amount}. New balance: {bank_handler.check_balance(user_credentials[0])}\r\n".encode())
                        else:
                            self.request.sendall(b"Unable to withdraw. Insufficient funds or invalid operation.\r\n")
                    else:
                        self.request.sendall(b"Invalid withdraw command. Please provide a valid amount.\r\n")

                elif command == "exit":
                    msg = "Client left " + str(self.client_address) + "\r\n"
                    self.broadcast_string(msg, self.request)
                    self.server.sockets.remove(self.request)
                    break

                else:
                    self.request.sendall(b"Invalid command. Please try again.\r\n")

        self.request.close()

# Datos del servidor LiquorStore
dir_ip = "127.0.0.1"
puerto = 7551
# Inicializar servidor
liquor_server = ThreadingTCPServer((dir_ip, puerto), LiquorStoreHandler)
liquor_server.sockets = []  # Lista para almacenar los sockets de los clientes
print("LIQUOR-STORE server started on port %s" % puerto)
liquor_server.serve_forever()