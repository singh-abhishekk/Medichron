"""
QR Code generation utilities.
"""
import os
import qrcode
from pathlib import Path

from app.core.config import settings


def generate_qr_code(data: str, filename: str) -> str:
    """
    Generate a QR code for the given data.

    Args:
        data: The data to encode in the QR code
        filename: Name of the file to save (without extension)

    Returns:
        Relative path to the generated QR code image
    """
    # Ensure QR code directory exists
    qr_dir = Path(settings.QR_CODE_DIR)
    qr_dir.mkdir(parents=True, exist_ok=True)

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=5,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save image
    file_path = qr_dir / f"{filename}.png"
    img.save(str(file_path))

    # Return relative path
    return f"{settings.QR_CODE_DIR}/{filename}.png"


def qr_code_exists(filename: str) -> bool:
    """
    Check if a QR code file already exists.

    Args:
        filename: Name of the file (without extension)

    Returns:
        True if file exists, False otherwise
    """
    file_path = Path(settings.QR_CODE_DIR) / f"{filename}.png"
    return file_path.exists()


def get_qr_code_path(filename: str) -> str:
    """
    Get the path to a QR code file.

    Args:
        filename: Name of the file (without extension)

    Returns:
        Relative path to the QR code
    """
    return f"{settings.QR_CODE_DIR}/{filename}.png"
