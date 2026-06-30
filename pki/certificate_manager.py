import subprocess
from pathlib import Path

ROOT_CA = Path("pki/certs/rootCA.crt")
APP_CERT = Path("pki/certs/logseal.crt")
CRL_FILE = Path("pki/ca/rootCA.crl")


def run_cmd(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return str(e)


def get_certificate_status():
    verify_output = run_cmd(
        f"openssl verify -CAfile {ROOT_CA} -CRLfile {CRL_FILE} -crl_check {APP_CERT}"
    )

    fingerprint = run_cmd(
        f"openssl x509 -in {APP_CERT} -noout -fingerprint -sha256"
    )

    details = run_cmd(
        f"openssl x509 -in {APP_CERT} -noout -subject -issuer -dates -serial"
    )

    return {
        "verify_output": verify_output,
        "fingerprint": fingerprint,
        "details": details
    }
