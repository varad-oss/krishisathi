"""Server-side image validation (never trust the client's Content-Type)."""
import io

from PIL import Image, UnidentifiedImageError

from core.errors import ApiError

ALLOWED_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
MIN_DIMENSION_PX = 64
MAX_PIXELS = 40_000_000


def sniff_image(data: bytes) -> str:
    """Validates the bytes are a real, reasonably sized JPEG/PNG/WebP image; returns its MIME type."""
    try:
        with Image.open(io.BytesIO(data)) as img:
            fmt = img.format
            width, height = img.size
            if width * height > MAX_PIXELS:
                raise ApiError(413, "IMAGE_TOO_LARGE", "Image resolution is too large.")
            img.verify()
    except ApiError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError, Image.DecompressionBombError):
        raise ApiError(415, "UNSUPPORTED_MEDIA_TYPE", "The file is not a readable JPEG, PNG or WebP image.")
    if fmt not in ALLOWED_FORMATS:
        raise ApiError(415, "UNSUPPORTED_MEDIA_TYPE", "Only JPEG, PNG and WebP images are supported.")
    if min(width, height) < MIN_DIMENSION_PX:
        raise ApiError(422, "IMAGE_TOO_SMALL", "The image is too small to analyse. Please take a closer photo.")
    return ALLOWED_FORMATS[fmt]
