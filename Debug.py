
''' Debug Support '''



from functools import wraps


def debug(func):
    msg = func.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"{msg}:  args: {args}  kwargs: {kwargs}\n")
        return func(*args, **kwargs)

    return wrapper


def debugmethods(cls):
    for name, val in vars(cls).items():
        if callable(val):
            setattr(cls, name, debug(val))
    return cls


def dump_obj(obj, name, und=False):
    print(f'\nDump {name}')
    for attr in dir(obj):  # also lists names inherited from super classes
        val = getattr(obj, attr)
        if und == True or attr.startswith('_') == False:
            print(f'\tattr {attr}: {val}')
    print('\n')


if __name__ == '__main__':

    class Orig():
        def __init__(self):
            self.a = 22

        def __getattribute__(self, name):
            return super().__getattribute__(name)

        def __setattr__(self, name, value):
            self.__dict__[name] = value

        def foo(self, x, y, z=3):
            return x + y + z

        def bar(self, a, b, c=3):
            return a * b * c

        @classmethod
        def cm_foo(self, x, y, z=3):
            return x + y + z

        @staticmethod
        def sm_bar(self, a, b, c=3):
            return a * b * c

    def foobar(x, y, z=3):
        return x + y + z


    func = debug(foobar)
    res = func(1, 2, z=3)
    print(f"foobar res: {res}\n")


    debugmethods(Orig)
    wo = Orig()
    print(f"wo foo: {wo.foo(1, 2, z=5)}")
    wo.a = 10
    print(f"wo getattr: {wo.a}")


