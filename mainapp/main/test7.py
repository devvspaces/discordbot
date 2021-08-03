from collections import defaultdict
import weakref

class KeepRefs(object):
    __refs__ = defaultdict(list)
    def __init__(self):
        self.__refs__[self.__class__].append(weakref.ref(self))

    @classmethod
    def get_instances(cls):
        for inst_ref in cls.__refs__[cls]:
            inst = inst_ref()
            if inst is not None:
                yield inst

    @classmethod
    def count_instances(cls):
        return len(list(cls.get_instances()))


class Driver(KeepRefs):
    def __init__(self):
        super(Driver, self).__init__()

        count = self.__class__.count_instances()
        print(count)
        if count > 3:
            print('No more than three instances of this')
            del self
class Gah:
    def __init__(self):
        return

for i in range(4):
    i = Driver()

print(list(Driver.get_instances()))

# print(list(Driver.get_instances()))
# print(Driver.count_instances())