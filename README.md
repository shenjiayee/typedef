# typedef
python-dict &lt;-> c-struct-bytes; only for python3.7 or newer
## define a struct
```python
from typedef import CStruct
from typedef.types import UINT64, CHAR

class SampleStruct(CStruct)
    name CHAR[20]
    version UINT64
    
sample = SampleStruct({'name': 'typedef', 'version': 20200327})

# get struct bytes
bytes_ = sample.to_types()
```
