import socketserver
import threading

class ServerOne(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            data = self.request.recv(1024).decode()
            print(f"Server One received: {data}")
            # Envía la respuesta de vuelta al otro servidor
            self.request.sendall("Hola desde Server One".encode())
            if (data.decode() == "exit"):
                break

class ServerTwo(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).decode()
        print(f"Server Two received: {data}")

        # Envía la respuesta de vuelta al otro servidor
        self.request.sendall("Hola desde Server Two".encode())

def start_servers():
    host = '127.0.0.1'
    port_one = 5555
    port_two = 6666

    server_one = socketserver.ThreadingTCPServer((host, port_one), ServerOne)
    server_two = socketserver.ThreadingTCPServer((host, port_two), ServerTwo)

    thread_one = threading.Thread(target=server_one.serve_forever)
    thread_two = threading.Thread(target=server_two.serve_forever)

    thread_one.start()
    thread_two.start()

    print(f"Server One listening on port {port_one}")
    print(f"Server Two listening on port {port_two}")

start_servers()
