from typedef.core.meta.base import CStructMeta
from typedef.types.base import CBuiltInDataType, Array, DEFAULT_ENCODING
from typedef.types.char import PADDING
import struct
import inspect


def is_padding(_type):
    if not inspect.isclass(_type):
        _type = type(_type)
    if issubclass(_type, PADDING):
        return True
    if issubclass(_type, Array):
        if issubclass(_type.member_type(), PADDING):
            return True
    return False


class CStruct(metaclass=CStructMeta):

    def __init__(self, data: bytes or dict=None, **kwargs):
        if isinstance(data, bytes):
            order = kwargs.pop('order', '@')
            encoding = kwargs.pop('encoding',
                                  getattr(self._meta, 'encoding', None) or DEFAULT_ENCODING)
            self.from_bytes(data, order=order, encoding=encoding)
            return
        attrs = dict(**data or {})
        attrs.update(kwargs)
        self.from_python(attrs)

    def from_python(self, data: dict):
        """
        load data from python dict
        :param data:
        :return:
        """
        for k, v in data.items():
            if k not in self._meta.members_type:
                raise KeyError(k)
            setattr(self, k, v)

    def from_bytes(self, b: bytes, order='@', encoding=DEFAULT_ENCODING):
        """
        load data from bytes
        :param b:
        :param order: byte order
            | Character  | Byte order             | Size      | Alignment  |
            | @          | native                 | native    | native     |
            | =          | native                 | standard  | none       |
            | <          | little-endian          | standard  | none       |
            | >          | big-endian             | standard  | none       |
            | !          |network (= big-endian)  | standard  | none       |
        :return:
        """
        if order not in ('@', '=', '<', '>', '!'):
            raise ValueError(f'Unexpected byte order character: {order}')
        fmt = f'{order}{self._meta.format}'
        field = [
            name for name in self._meta.m if not isinstance(self._meta.members_type[name], PADDING)
        ]
        split_data = struct.unpack(fmt, b)
        for name, d in zip(field, split_data):
            setattr(self, name, self._meta.members_type[name](d, order=order, encoding=encoding))

    def to_bytes(self, order='@', encoding=DEFAULT_ENCODING):
        """
        translate to bytes
        :param order: byte order
        :return:
        """
        return b''.join(
            getattr(self, att_name).to_bytes(order=order, encoding=encoding) for att_name in self._meta.m
        )

    def to_python(self):
        """
        translate to python dict
        :return:
        """
        def _attrs():
            for att_name in self._meta.m:
                structure = getattr(self, att_name)
                if is_padding(structure):
                    continue
                yield att_name, structure.to_python()

        return dict(_attrs())

    def __getattribute__(self, att_name):
        """
        allow get the value of a field by obj.field
        :param att_name:
        :return:
        """
        _meta = super().__getattribute__('_meta')
        if att_name in _meta.members_type:
            m_type = _meta.members_type[att_name]
            if is_padding(m_type):
                return m_type()
            _dict = super().__getattribute__('__dict__')
            if att_name in _dict:
                _data = _dict[att_name]
                if isinstance(_data, (CStruct, CBuiltInDataType)):
                    return _data
                _type = _meta.members_type[att_name]
                _object = _type(_data)
                setattr(self, att_name, _object)
                return _object
            else:
                raise AttributeError(f'{att_name} has no value')
        return super().__getattribute__(att_name)
