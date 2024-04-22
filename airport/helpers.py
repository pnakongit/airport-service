import uuid
from pathlib import Path

from django.utils.text import slugify


def airplane_image_file_path(instance, filename: str) -> Path:
    extension = Path(filename).suffix
    filename = Path(f"{slugify(instance.name)}-{uuid.uuid4()}{extension}")
    return "upload/airplane/" / filename
