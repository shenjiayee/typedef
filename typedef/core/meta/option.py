from typedef.types.base import CBuiltInDataType, CStructMetaBase, CDataTypeMetaBase
from types import MappingProxyType
from typing import Type, Tuple, List, Dict, Union


class StructureOptions(object):

    def __init__(self,
                 members: List[Union[Type['CBuiltInDataType'], Type['CStructMetaBase']]],
                 members_type: Dict[str, Union[Type['CBuiltInDataType'], Type[
                     'CStructMetaBase'], CDataTypeMetaBase]],
                 **extra_attrs):
        self.members = tuple(members)
        self.members_type = MappingProxyType(members_type)
        for attr_name, value in extra_attrs.items():
            setattr(self, attr_name, value)

    @property
    def m(self) -> Tuple[Union[Type['CBuiltInDataType'], Type['CStructMetaBase']]]:
        return self.members

    @property
    def t(self) -> List[Union[Type['CBuiltInDataType'], Type['CStructMetaBase']]]:
        return [
            self.members_type[name] for name in self.m
        ]

    @property
    def format(self) -> str:
        return ''.join(_type._meta.format if isinstance(_type, CBuiltInDataType)
                       else f'{_type._meta.length}s'
                       for _type in self.t)

    @property
    def length(self) -> int:
        return sum(_type._meta.length for _type in self.t)
