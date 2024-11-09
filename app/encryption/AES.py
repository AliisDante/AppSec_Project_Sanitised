import os.path
from base64 import b64encode, b64decode

from app import app

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import unpad, pad


def generate_key():
    key = get_random_bytes(16)
    with open(os.path.join(app.root_path, "secrets", "key.txt"), 'wb') as file_out:
        file_out.write(key)


def save_iv_to_file(iv):
    iv_base64 = b64encode(iv).decode('utf-8')
    with open(os.path.join(app.root_path, "secrets", "iv.txt"), 'w') as file_out:
        file_out.write(iv_base64)


def encrypt(plaintext_bytes):
    with open(os.path.join(app.root_path, "secrets", "key.txt"), 'rb') as file_in:
        key = file_in.read()

    iv = read_iv_from_file()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext_bytes = cipher.encrypt(pad(plaintext_bytes, AES.block_size))

    return ciphertext_bytes


def read_iv_from_file():
    with open(os.path.join(app.root_path, "secrets", "iv.txt"), 'r') as file_in:
        iv_base64 = file_in.read()
    iv = b64decode(iv_base64)
    return iv


def decrypt(ciphertext_bytes):
    with open(os.path.join(app.root_path, "secrets", "key.txt"), 'rb') as file_in:
        key = file_in.read()

    iv = read_iv_from_file()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext_bytes = unpad(cipher.decrypt(ciphertext_bytes), AES.block_size)
    return plaintext_bytes


if __name__ == "__main__":
    plaintext = 'Hello world!'
    ciphertext = encrypt(plaintext)
    print(ciphertext)
    decrypted_text = decrypt(ciphertext)
    print(decrypted_text)
