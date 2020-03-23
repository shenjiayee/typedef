from typedef.types.exc import DataTypeValidateError
from typing import List, Tuple, Type
import abc
import struct


DEFAULT_ENCODING = 'utf-8'


class CDataTypeMetaBase(abc.ABCMeta):
    """
    metaclass of c-datatype class
    """
    _meta = None

    def __getitem__(cls, max_count):
        """
        define a array with TYPE[count]
        :param max_count:
        :return:
        """
        return Array.define(member_type=cls, max_count=max_count)


class CBuiltInDataType(metaclass=CDataTypeMetaBase):
    """
    base of C builtin data type
    """
    @abc.abstractmethod
    class _meta:
        format = ''
        length = 0
        array_attr = {} # attribute when create array-type

    def __init__(self, data, **kwargs):
        if isinstance(data, bytes):
            order = kwargs.pop('order', '@')
            encoding = kwargs.pop('encoding', DEFAULT_ENCODING)
            self.from_bytes(data, order=order, encoding=encoding)
        else:
            self.validator(data)
            self.from_python(data)

    def __str__(self):
        return str(self.to_python())

    @abc.abstractmethod
    def validator(self, data):
        """
        validate the data onload
        :return:
        """

    @abc.abstractmethod
    def from_bytes(self, b: bytes, order='@', encoding=DEFAULT_ENCODING):
        """
        load data from bytes
        :return:
        """

    @abc.abstractmethod
    def from_python(self, pd: dict):
        """
        load data from python dict
        :param pd:
        :return:
        """

    @abc.abstractmethod
    def to_bytes(self, order='@'):
        """
        translate to bytes
        :return:
        """

    @abc.abstractmethod
    def to_python(self):
        """
        translate to python dict
        :return:
        """

class CStructMetaBase(CDataTypeMetaBase):
    """
    metaclass of c-structure
    """
    class _meta:
        format = ''
        length = 0
        array_attr = {}


class Array(CBuiltInDataType):

    _member_type = None
    _max_count = None

    def __init__(self, data, **kwargs):
        self._value = [None] * self._max_count
        super().__init__(data, **kwargs)

    class _meta:
        format = ''
        length = 0

    @classmethod
    def define(cls,
               *,
               member_type: Type['CBuiltInDataType'] or Type['CStructMetaBase'],
               max_count: int, ):
        """
        array factory method
        :param member_type: the base type
        :param max_count: max length
        :return:
        """
        if not isinstance(member_type, CDataTypeMetaBase):
            raise TypeError(member_type)
        if not isinstance(max_count, int):
            raise TypeError(max_count)
        if max_count <= 0:
            raise ValueError

        class meta:
            length = member_type._meta.length * max_count
            format = f'{length}s'

        namespace = {
                        '_member_type': member_type,
                        '_max_count': max_count,
                        '_meta': meta
                    }
        namespace.update(
            getattr(member_type._meta, 'array_attr', {})
        )
        new_type = type(f'{member_type.__name__}_Array',
                        (Array,),
                        namespace)
        return new_type

    def __iter__(self):
        yield from self._value

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise TypeError(item)
        return self._value[item]

    @classmethod
    def member_type(cls):
        return cls._member_type

    @classmethod
    def max_count(cls):
        return cls._max_count

    def validator(self, data):
        print(data)
        if isinstance(data, (tuple, list)):
            if len(data) <= self._max_count:
                return
        raise DataTypeValidateError

    def from_bytes(self, b: bytes, order='@', encoding=DEFAULT_ENCODING):
        """
        load data from bytes
        :param b:
        :return:
        """
        if not isinstance(b, bytes):
            raise TypeError(b)
        fmt = f'{order}{self._member_type._meta.length}s' * self._max_count
        split_bytes = struct.unpack(fmt, b)
        for index, item in enumerate(split_bytes):
            self._value[index] = self._member_type(item, order=order, encoding=encoding)

    def from_python(self, pd: List or Tuple):
        """
        load data from python dict
        :param pd:
        :return:
        """
        for index, item in enumerate(pd):
            self._value[index] = self._member_type(item)

    def to_bytes(self, order='@'):
        """
        translate to bytes
        :return:
        """
        bytes_ = b''.join(
            item.to_bytes() for item in self._value if item is not None
        )
        return struct.pack(
            f'{order}{self._member_type._meta.length * self._max_count}s'
            f'{self._meta.length - self._member_type._meta.length * self._max_count}x',
            bytes_
        )

    def to_python(self):
        """
        translate to python dict
        :param encoding:
        :return:
        """
        return list(
            m.to_python() for m in self._value if m
        )

