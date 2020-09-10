# typedef
python-dict &lt;-> c-struct-bytes; only for python3.7 or newer
## define a struct
```python
from typedef import CStruct
from typedef.types import UINT64, CHAR

class SampleStruct(CStruct):
    name = CHAR[20]
    version = UINT64
    
sample = SampleStruct({'name': 'typedef', 'version': 20200327})

# get struct bytes
bytes_ = sample.to_bytes(order='@')

sample2 = SampleStruct(bytes_, order='@')
dict_ = sample2.to_python()

# {'name': 'typedef', 'version': 20200327}

```

## allow nested defination
```python
class ComplexSample(CStruct):
    message CHAR[60]
    children SampleStruct[5]

sample = ComplexSample({'message': 'this is a message','chidren': [{'name': 'pkg_typedef', 'version': 1001}, {'name': 'pkg_serializer', 'version': 1003}])
bytes_ = sample.to_bytes(order='=')

```
