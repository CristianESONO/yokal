import io
import qrcode
from django.core.files.base import ContentFile


def generate_qr_image(token: str) -> ContentFile:
    """Generate a QR code PNG for a given token string, returns ContentFile."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(str(token))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=f'qr_{token}.png')
