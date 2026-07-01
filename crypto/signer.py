from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from pathlib import Path
import base64

PRIVATE_KEY_PATH = Path("pki/keys/logseal_private_key.pem")
PUBLIC_KEY_PATH = Path("pki/keys/logseal_public_key.pem")
KEY_PASSWORD = b"logseal-password"


def sign_hash(final_hash):
    private_key = serialization.load_pem_private_key(
        PRIVATE_KEY_PATH.read_bytes(),
        password=KEY_PASSWORD
    )

    signature = private_key.sign(
        final_hash.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return base64.b64encode(signature).decode()


def verify_signature(final_hash, signature_b64):
    public_key = serialization.load_pem_public_key(
        PUBLIC_KEY_PATH.read_bytes()
    )

    signature = base64.b64decode(signature_b64)

    try:
        public_key.verify(
            signature,
            final_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True

    except Exception:
        return False
