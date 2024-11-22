import os
import qrcode
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def get_qr_code(url):
    """
    Generates or retrieves a QR code for the given URL.
    """
    # Generate a unique filename based on the URL
    filename = f"qr_{hash(url)}.png"
    qr_code_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', filename)
    qr_code_url = f"{settings.MEDIA_URL}qr_codes/{filename}"

    # Check if the QR code file exists; if not, create it
    if not os.path.exists(qr_code_path):
        os.makedirs(os.path.dirname(qr_code_path), exist_ok=True)

        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Save the QR code to the media folder
        img = qr.make_image(fill="black", back_color="white")
        img.save(qr_code_path)

    return qr_code_url
