
from datetime import datetime, date
from sortedcontainers import SortedDict

class BaseSerializer:
    _serialize = []

    def to_dict(self):
            def serialize_value(value):
                try:
                    if isinstance(value, datetime):
                        return value.isoformat()
                    elif isinstance(value, date):
                        return value.isoformat()
                    elif isinstance(value, SortedDict):
                        return dict(value)
                    elif isinstance(value, list):
                        return [serialize_value(v) for v in value]
                    elif isinstance(value, dict):
                        return {serialize_value(k): serialize_value(v) for k, v in value.items()}  
                    elif hasattr(value, "to_dict"):
                        return value.to_dict()
                    else:
                        return value
                except Exception as e:
                    print(str(e))
            return {attr: serialize_value(getattr(self, attr)) for attr in self._serialize if hasattr(self, attr)}

if __name__ == '__main__':
    class Test(BaseSerializer):
        _serialize = ['a', 'b', 'c']

        def __init__(self):
            self.a = 1
            self.b = 'test'
            self.c = {datetime.now(): datetime.now()}
        
        # def __hash__(self):
        #     return hash((self.a))

    test = Test()
    value = {
        str(test): test
    }
    value.pop(str(test))
    print(f"Identifier: {str(test)}")