from typedef.types.base import CBuiltInDataType, DEFAULT_ENCODING
from typedef.types.exc import DataTypeValidateError
import struct


def char_array_to_bytes(self, order='@', encoding=DEFAULT_ENCODING):
    value = self._value.encode(encoding)
    return struct.pack(f'{order}{self._meta.format}', value)

def char_array_to_python(self, *_, **__):
    return self._value

def char_array_from_bytes(self, b, order='@', encoding=DEFAULT_ENCODING):
    value, = struct.unpack(f'{order}{self._meta.format}', b)
    self._value = value.decode(encoding)

def char_array_from_python(self, pd):
    self._value = pd

def char_array_validator(_, data):
    if not isinstance(data, str):
        raise DataTypeValidateError


class CHAR(CBuiltInDataType):
    """
    char
    """
    def __init__(self, b, **kwargs):
        if isinstance(b, int) and 0 <= b < 256:
            b = bytes([b])
        if isinstance(b, bytes):
            order = kwargs.pop('order', '@')
            encoding = kwargs.pop('encoding', DEFAULT_ENCODING)
            super().__init__(b, order=order, encoding=encoding)
        else:
            super().__init__(b)

    class _meta:
        format = 'c'
        length = 1

        array_attr = {
            'to_bytes': char_array_to_bytes,
            'to_python': char_array_to_python,
            'from_bytes': char_array_from_bytes,
            'from_python': char_array_from_python,
            'validator': char_array_validator
        }

    def validator(self, data):
        if not isinstance(data, str):
            raise DataTypeValidateError
        if len(data) != 1:
            raise DataTypeValidateError

    def from_bytes(self, b: bytes, order='@', encoding=DEFAULT_ENCODING):
        value, = struct.unpack(f'{order}{self._meta.format}', b)
        self._value = value.decode(encoding)

    def from_python(self, pd):
        self._value = pd

    def to_bytes(self, order='@', encoding=DEFAULT_ENCODING):
        return struct.pack(f'{order}{self._meta.format}', self._value.encode(encoding))

    def to_python(self):
        return self._value


def padding_to_python(*_, **__):
    raise ValueError

def padding_from_python(*_, **__):
    raise NotImplementedError

def padding_init(self, *_, **__):
    self._value = [PADDING()] * self._max_count


class PADDING(CBuiltInDataType):
    """
    padding: char == \x00
    """
    class _meta:
        format = 'x'
        length = 1

        array_attr = {
            'to_python': padding_to_python,
            'from_python': padding_from_python,
            '__init__': padding_init
        }

    def __init__(self, *_, **__):
        super().__init__(b'\x00')

    def validator(self, data):
        raise DataTypeValidateError

    def from_bytes(self, b: bytes, *_, **__):
        self._value = b

    def from_python(self, pd):
        raise NotImplementedError

    def to_bytes(self, *_, **__):
        return self._value

    def to_python(self, *_, **__):
        raise NotImplementedError
