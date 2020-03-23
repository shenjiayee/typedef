from typedef.types.base import CDataTypeMetaBase, CStructMetaBase, Array
from typedef.core.meta.option import StructureOptions


class CStructMeta(CStructMetaBase):
    """
    metaclass of c_structure
    """
    _meta_attrs = ('encoding', )

    def __new__(mcs, name, bases, attrs, **kwargs):
        members = []
        members_type = dict()
        new_attrs = {}
        slots = []
        attr_meta = attrs.pop('_meta', None)
        for k, v in attrs.items():
            if isinstance(v, CDataTypeMetaBase):
                members.append(k)
                members_type[k] = v
                slots.append(k)
            else:
                new_attrs[k] = v
        new_class = super().__new__(mcs, name, bases, new_attrs)
        extra_attrs = {
            name: getattr(attr_meta, name) for name in mcs._meta_attrs
            if hasattr(attr_meta, name)
        }
        setattr(new_class, '_meta', StructureOptions(members, members_type, **extra_attrs))
        setattr(new_class, '__slots__', tuple(slots))
        return new_class

    def __getitem__(cls, max_count):
        return Array.define(member_type=cls, max_count=max_count)
