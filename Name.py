
'''

'''
'''
    Name.py creates remote proxies known to end-developers as Names.

    Names are comprised of local proxies (the actual Name) which have a remote proxy (which is also located in our Env).

    The Name class exists because we can't pickle instances of remote proxies that we programmatically create (because
    they are not defined in the top level of a module).

    In essence we have a local proxy, Name, that passes everything through to the remote proxy.

    We initialize Name to remember how to recreate the initialized remote proxy in an other Env.

    The remote proxy is created by proxy().  It parses a class and creates a new class with the same api which assumes
    the Worker to which it is a proxy is "remote" (i.e. in another thread or process).

    Most of the api's methods are simply wrappers for calls to ___proxy_make_request(), which actually makes the
    remote call. The function which creates the wrapper for each of a proxied object's methods is call_proxy_method().
    See ProxyMakeRequest.py also.

    Some of the api's methods are replacements for magic methods that do special processing related to it being a
    proxy and not the actual object being proxied.  Among these are ___proxy_init___() for __init__(),
    ___proxy_getattribute___() for __getattribute__(), ___proxy_getattr___() for __getattr__() and
    ___proxy_setattr___() for __setattr__().
'''



from ProxyMakeRequest import ___proxy_make_request
from functools import update_wrapper
from inspect import signature
from os import getpid
from logging import error



def call_proxy_method(method):
    '''
        Create wrapper of a method to make a remote method request.

        Assumes the Worker Addr is stored in self.___target___ of the remote proxy
    '''

    name = method.__name__

    def remote_method(self, *args, **kwargs):
        return ___proxy_make_request(self, self.___target___, name, *args, **kwargs)

    remote_method.__name__ = name

    try:
        Sig = signature(method)

    except ValueError:
        pass

    else:
        remote_method.__signature__ = Sig

    update_wrapper(remote_method, method)
    return remote_method


def ___proxy_init___(self, target):
    ''' Replacement for class's __init__() in remote proxy '''

    object.__setattr__(self, '___target___', target)


def ___proxy_getattribute___(self, name):
    ''' Replacement for class's __getattribute__() in remote proxy '''

    try:
        val = object.__getattribute__(self, name)
        return val

    except:
        val = self.___remote_getattr___(name)
        return val


def ___proxy_getattr___(self, name):
    ''' Replacement for class's __getattr__() in remote proxy '''

    return self.___remote_getattr___(name)


def ___proxy_setattr___(self, name, val):
    ''' Replacement for class's __setattr__() in remote proxy '''

    try:
        object.__getattribute__(self, name)
        return object.__setattr__(self, name, val)

    except:
        return self.___remote_setattr___(name, val).Ret


def proxy(FromClass, NewName, CallingModule):
    ''' Parse a class and create a remote proxy for it '''

    try:
        NameClass = getattr(CallingModule, NewName)

    except:             # Name class doesn't exist, we'll create it
        pass

    else:
        return NameClass


    # Parse the target class...
    AddedMethods = {}


    # First pass for FromClass's attributes
    for name, val in vars(FromClass).items():
        if isinstance(val, classmethod) or isinstance(val, staticmethod):
            continue

        elif callable(val):
            new_method = call_proxy_method(val)
            AddedMethods[name] = new_method


    # Second pass for inherited attributes
    for name in dir(FromClass):
        val = getattr(FromClass, name)

        if name in AddedMethods or name == '__new__':
            continue

        if isinstance(val, classmethod) or isinstance(val, staticmethod):
            continue

        elif callable(val):
            new_method = call_proxy_method(val)
            AddedMethods[name] = new_method


    # Create the remote proxy class
    ProxyClass = type(NewName, (FromClass,), AddedMethods)


    # Add the special methods' replacements, giviing them the same identifiers
    setattr(ProxyClass, '__init__', ___proxy_init___)
    setattr(ProxyClass, '__getattribute__', ___proxy_getattribute___)
    setattr(ProxyClass, '__getattr__', ___proxy_getattr___)
    setattr(ProxyClass, '__setattr__', ___proxy_setattr___)
    setattr(ProxyClass, '___proxy_make_request', ___proxy_make_request)


    # Make the proxy visible in the calling module
    setattr(CallingModule, NewName, ProxyClass)

    return ProxyClass


class Name():
    '''
        The Name class exists because we can't pickle instances of remote proxies that we programmatically create
        (because they are not defined in the top level of a module).

        In essence we have a local proxy, Name, that passes everything through to the remote proxy (which is also
        located in our Env).

        When we reference our own data attributes we have to go through object's api since we must redefine
        __getattr__ and __setattr__ to do the pass through to the remote proxy.

        Names can be passed between Envs but we must do special pickle processing.  Note that remote proxies can be used
        directly but must not be passed due to pickling exceptions being generated.

        We initialize Name to remember how to recreate the initialized remote proxy in an other Env.

        __getstate__ is called by the pickler and returns the remote proxy's target along with the target reference's
            class name and the module name it is defined in.  For example if Conc derivative class Foo, defined in
            FooFile.py, has a remote proxy class FooName created by proxy(), an instance of the remote proxy would store
            the instance of Foo as its ConcAddr in its ___target___.  It is ___target___ we pickle along with 'Foo' and
            'FooFile.py'.

        __setstate__ is called by the unpickler and must recreate the initialized remote proxy and restore our state.
    '''

    def __init__(self, Proxy, TheClassName, TheModuleName):
        object.__setattr__(self, 'Proxy', Proxy)
        object.__setattr__(self, 'TheClassName', TheClassName)
        object.__setattr__(self, 'TheModuleName', TheModuleName)


    def __getattr__(self, name):
        return getattr(self.Proxy, name)


    def __setattr__(self, name, val):
        self.Proxy.__setattr__(name, val)


    def __getstate__(self):
        return (object.__getattribute__(self, 'Proxy').___target___, object.__getattribute__(self, 'TheClassName'),
                                                                        object.__getattribute__(self, 'TheModuleName'))

    def __setstate__(self, state):
        ProxyTarget, TheClassName, TheModuleName = state

        from importlib import import_module
        TheModule = import_module(TheModuleName)

        TheClass = None
        try:
            TheClass = getattr(TheModule, TheClassName)
        except:
            error(f'__setstate__ process {getpid()} gettattr for {TheClassName} failed')

        TheProxyClass = proxy(ProxyTarget, TheClassName+'Name', TheModule)

        TheProxy = TheProxyClass(ProxyTarget)

        object.__setattr__(self, 'Proxy', TheProxy)
        object.__setattr__(self, 'TheClassName', TheClassName)
        object.__setattr__(self, 'TheModuleName', TheModuleName)


    def __repr__(self):
        # return ''.join((f'Name({object.__getattribute__(self, "Proxy").___target___} ',
        #                                                 f'{object.__getattribute__(self, "TheModuleName")}.',
        #                                                 f'{object.__getattribute__(self, "TheClassName")})'))
        return f'{object.__getattribute__(self, "Proxy").___target___}'




# def call_proxy_function(target, function):
#   ''' Store the Function Name in ___target___'''
#
#     name = function.__name__
#
#     def remote_function(*args, **kwargs):
#         return function(*args, **kwargs)
#
#     remote_function.__name__ = name
#     remote_function.___target___ = target
#     remote_function.__signature__ = signature(function)
#     update_wrapper(remote_function, function)
#     return remote_function

#if __name__ == '__main__':

    # print('\nT e s t   F u n c t i o n   P r o x y\n')
    # def sumit(a,b,c):
    #     return a + b + c
    #
    # def sumall(lst):
    #     return(sum(lst))
    #
    # def exec_func(f, a):
    #     return f(a)
    #
    # func_name = 'MgrEnv: 12, ObjId: 23'
    #
    # sumit_proxy = call_proxy_function(func_name, sumit)
    # print(f"simple function: {sumit_proxy(12,6,18)} equals {12 + 6 + 18}")
    #
    # alst = [1,2,3,4,5,6,7,8,9,10]
    #
    # sumall_proxy = call_proxy_function(func_name, sumall)
    # print(f'sum a list: {sum(alst)} equals {sumall(alst)} equals {sumall_proxy(alst)}')
    #
    # exec_func_proxy = call_proxy_function(func_name, exec_func)
    # print(f'pass a function as arg: {sum(alst)} equals {exec_func(sum, alst)} equals {exec_func_proxy(sum, alst)}')
    # print(f'pass a lambda as arg: {sum(alst)} equals {exec_func(lambda x: sum(x), alst)} equals {exec_func_proxy(lambda x: sum(x), alst)}')



