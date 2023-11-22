import socket
import socketserver
import threading
from Crypto.Cipher import AES

class LiquorStoreHandler(socketserver.BaseRequestHandler):
    key = b'16bytessecretkey'  # Cambia esto por tu llave secreta

    @staticmethod
    def encrypt_message(message):
        cipher = AES.new(LiquorStoreHandler.key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
        return nonce + tag + ciphertext

    @staticmethod
    def send_to_bank(message):
        bank_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bank_socket.sendto(message, ('127.0.0.1', 3555))
        bank_socket.close()

    @staticmethod
    def decrypt_message(ciphertext):
        cipher = AES.new(LiquorStoreHandler.key, AES.MODE_EAX)
        nonce = ciphertext[:16]
        tag = ciphertext[16:32]
        ciphertext = ciphertext[32:]
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('utf-8')

    def handle(self):
        while True:
            # Esperar mensaje del banco
            bank_response, _ = self.request[1].recvfrom(1024)
            decrypted_message = self.decrypt_message(bank_response)
            print("Bank:", decrypted_message)

if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 7556
    server = socketserver.UDPServer((HOST, PORT), LiquorStoreHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    while True:
        message = input("LiquorStore: ")
        encrypted_message = LiquorStoreHandler.encrypt_message(message)
        LiquorStoreHandler.send_to_bank(encrypted_message)
