from typedef.types.base import CBuiltInDataType
from typedef.types.exc import DataTypeValidateError
import struct


class Integer(CBuiltInDataType):
    """
    int
    """
    def __init__(self, data, **kwargs):
        self._value = 0
        if isinstance(data, bytes):
            order = kwargs.pop('order', '@')
            super().__init__(data, order=order)
        else:
            super().__init__(data)

    def validator(self, data):
        if not isinstance(data, int):
            raise DataTypeValidateError

    def from_bytes(self, b: bytes, order='@', *_, **__):
        value = struct.unpack(f'{order}{self._meta.format}', b)
        self._value, = value

    def from_python(self, pd):
        self._value = pd

    def to_bytes(self, order='@', *_, **__):
        return struct.pack(f'{order}{self._meta.format}', self._value)

    def to_python(self, *_, **__):
        return self._value


class INT8(Integer):
    """
    signed int8
    """
    class _meta:
        format = 'b'
        length = 1

    def validator(self, data):
        super().validator(data)
        if not -127 <= data <= 127:
            raise DataTypeValidateError


class BYTE(Integer):
    """
    BYTE, unsigned int8
    """
    class _meta:
        format = 'B'
        length = 1

    def validator(self, data):
        super().validator(data)
        if not 0 <= data <= 255:
            raise DataTypeValidateError

UINT8 = BYTE


class UINT16(Integer):
    """
    WORD, unsigned int16
    """
    class _meta:
        format = 'H'
        length = 2

    def validator(self, data):
        super().validator(data)
        if not 0 <= data <= 65535:
            raise DataTypeValidateError

WORD = UINT16


class UINT32(Integer):
    """
    unsigned int32
    """
    class _meta:
        format = 'I'
        length = 4

    def validator(self, data):
        super().validator(data)
        if not 0 <= data <= 4294967295:
            raise DataTypeValidateError


class UINT64(Integer):
    """
    unsigned int64
    """
    class _meta:
        format = 'Q'
        length = 8

    def validator(self, data):
        super().validator(data)
        if not 0 <= data:
            raise DataTypeValidateError
