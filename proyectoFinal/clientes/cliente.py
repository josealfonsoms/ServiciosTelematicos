import socket

# Dirección y puerto del servidor LiquorStore
liquor_store_address = ("127.0.0.1", 7559)

# Crear socket TCP para conectarse al servidor LiquorStore
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(liquor_store_address)

# Enviar el comando "bank" seguido de un mensaje al servidor
message = "bank hola, como estas"  # Asegúrate de enviar el mensaje después de "bank"
client_socket.sendall(message.encode())

# Recibir y mostrar la respuesta del servidor
response = client_socket.recv(1024)
print("Respuesta del servidor LiquorStore:", response.decode())

# Cerrar el socket del cliente
client_socket.close()
