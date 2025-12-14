import re
from typing import Callable
import base64

from django.db.models import ImageField
from django.db.models.fields.files import FieldFile
from typeguard import typechecked
from fiordispino.core.exceptions import ImageEncoderException

@typechecked
def pattern(regex: str) -> Callable[[str], bool]:
    r = re.compile(regex)
    def res(value):
        return bool(r.fullmatch(value))
    res.__name__ = f'pattern({regex})'
    return res

@typechecked
def encode_image_to_base64(img: FieldFile) -> str: # the image is saved as an image file, however at runtime image fields are handled with a field file proxy
    if not img:
        raise ImageEncoderException(detail="No box art found for game")

    try:
        with img.open('rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        return encoded_string
    except:
        raise ImageEncoderException()
