from itertools import count
import gc

class Obj(object):
  _ids = count(0)

  def __init__(self):
    self.id = next(self._ids)

  def __del__(self):
  	del self

g = Obj()
# del g

# print(g)

print(len(gc.get_objects()))
# print(Obj._ids)
# from collections import defaultdict
# import weakref

# class KeepRefs(object):
#     __refs__ = defaultdict(list)
#     def __init__(self):
#         self.__refs__[self.__class__].append(weakref.ref(self))

#     @classmethod
#     def get_instances(cls):
#         for inst_ref in cls.__refs__[cls]:
#             inst = inst_ref()
#             if inst is not None:
#                 yield inst

# class X(KeepRefs):
#     def __init__(self, name):
#         super(X, self).__init__()
#         self.name = name

# x = X("x")
# y = X("y")
# for r in X.get_instances():
#     print (r.name)
# del y
# for r in X.get_instances():
#     print (r.name)


# print(isinstance(None, str))