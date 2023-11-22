import socket
import socketserver
import threading
from Crypto.Cipher import AES

class BankHandler(socketserver.BaseRequestHandler):
    key = b'16bytessecretkey'  # Cambia esto por tu llave secreta

    @staticmethod
    def decrypt_message(ciphertext):
        cipher = AES.new(BankHandler.key, AES.MODE_EAX)
        nonce = ciphertext[:16]
        tag = ciphertext[16:32]
        ciphertext = ciphertext[32:]
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('utf-8')

    @staticmethod
    def send_to_liquor_store(message):
        liquorstore_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        liquorstore_socket.sendto(message, ('127.0.0.1', 7556))
        liquorstore_socket.close()

    def handle(self):
        while True:
            # Esperar mensaje de la tienda
            liquorstore_request = self.request[0]
            decrypted_message = self.decrypt_message(liquorstore_request)
            print("LiquorStore:", decrypted_message)

if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 3555
    server = socketserver.UDPServer((HOST, PORT), BankHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    while True:
        message = input("Bank: ")
        cipher = AES.new(BankHandler.key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
        encrypted_message = nonce + tag + ciphertext

        BankHandler.send_to_liquor_store(encrypted_message)
