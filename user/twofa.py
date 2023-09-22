import io
from hashlib import sha512

import pyotp
from qrcode.constants import ERROR_CORRECT_L
from qrcode.main import QRCode


def generate_qr(key:str, username:str):
    totp = pyotp.totp.TOTP(key, digest=sha512, digits=8)
    uri = totp.provisioning_uri(name=username, issuer_name="DRCK Banking")
    qr = QRCode(
        error_correction=ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    qr = qr.make_image()
    stream = io.BytesIO()
    qr.save(stream)
    stream.seek(0)
    return stream


def verify_otp(key:str, otp:str):
    totp = pyotp.TOTP(key, digest=sha512, digits=8)
    return totp.verify(otp)

