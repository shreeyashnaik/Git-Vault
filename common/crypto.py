class Crypto:
    def __init__(self, cipher_suite):
        self.cipher_suite = cipher_suite
    def encrypt(self, exposed_text):
        self.cipher_suite.encrypt(exposed_text.encode())
    def decrypt(self, decrypted_text):
        self.cipher_suite.decrypt(decrypted_text).decode()