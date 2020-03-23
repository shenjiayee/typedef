import struct
from functools import wraps


def padding(length):
    """
    长度补足
    :param length: 长度，字节
    :return:
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            # bytes
            assert isinstance(ret, bytes)
            ret_l = len(ret)
            # 长度不超过
            assert ret_l <= length
            return struct.pack(
                f'{ret_l}s{length - ret_l}x',
                ret
            )
        return wrapper
    return decorate
