from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


def encrypt_file(file_path):

    # Read log archive
    with open(file_path, "rb") as f:
        data = f.read()

    # Generate AES-256 key
    aes_key = get_random_bytes(32)

    # AES Encryption
    cipher_aes = AES.new(aes_key, AES.MODE_GCM)

    ciphertext, tag = cipher_aes.encrypt_and_digest(data)

    encrypted_file = file_path + ".enc"

    with open(encrypted_file, "wb") as f:
        f.write(cipher_aes.nonce)
        f.write(tag)
        f.write(ciphertext)

    # Load RSA Public Key
    with open("pki/keys/logseal_public_key.pem", "rb") as f:
        public_key = RSA.import_key(f.read())

    # Encrypt AES key using RSA
    cipher_rsa = PKCS1_OAEP.new(public_key)

    encrypted_key = cipher_rsa.encrypt(aes_key)

    with open(encrypted_file + ".key", "wb") as f:
        f.write(encrypted_key)

    print("[HYBRID ENCRYPTION COMPLETE]")
    print("Encrypted File :", encrypted_file)
    print("Encrypted Key  :", encrypted_file + ".key")
