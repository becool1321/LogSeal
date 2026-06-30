from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pathlib import Path

KEY_DIR = Path("pki/keys")
PRIVATE_KEY_PATH = KEY_DIR / "logseal_private_key.pem"
PUBLIC_KEY_PATH = KEY_DIR / "logseal_public_key.pem"


def generate_rsa_keys():
    KEY_DIR.mkdir(parents=True, exist_ok=True)

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(b"logseal-password")
    )

    public_key = private_key.public_key()

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    PRIVATE_KEY_PATH.write_bytes(private_pem)
    PUBLIC_KEY_PATH.write_bytes(public_pem)

    print("[KEYS GENERATED]")
    print(f"Private Key: {PRIVATE_KEY_PATH}")
    print(f"Public Key : {PUBLIC_KEY_PATH}")


if __name__ == "__main__":
    generate_rsa_keys()
