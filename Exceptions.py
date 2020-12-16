
'''

    AsyncLocalExceptions are generated in the client Worker's Env.

    A s y n c L o c a l M a x R e t r i e s

    AsyncLocalMaxRetries exceptions are generated when the maximum number of unsuccessful retries to a service
    Worker have been made (A makes max requests of B, A raises).


    AsyncRemoteExceptions are generated in the server Worker's Env.  They capture the remote exception TypeName,
    Value and TracebackStrings as attributes.

    A s y n c E x e c u t i o n E r r o r

    AsyncExecutionError remote exceptions are generated when a service Worker's methods raise an exception.


    A s y n c R e m o t e M a x R e t r i e s

    AsyncRemoteMaxRetries remote exceptions are generated when the maximum number of unsuccessful retries to a
    service Worker have been made to service a request from another service Worker (A makes a request of B who
    makes max requests of C to execute A's request, raised by B).


    A s y n c A t t r i b u t e E r r o r

    AsyncAttributeError remote exceptions are generated when the server Worker does not possess a requested
    atttribute.

'''



class AsyncLocalException(Exception):
    pass


class AsyncLocalMaxRetries(AsyncLocalException):
    pass


class AsyncRemoteException(Exception):
    def __init__(self, TypeName, Value, TracebackStrings):
        self.TypeName = TypeName
        self.Value = Value
        self.TracebackStrings = TracebackStrings


class AsyncExecutionError(AsyncRemoteException):
    def __init__(self, TypeName, Value, TracebackStrings):
        super().__init__(TypeName, Value, TracebackStrings)


class AsyncRemoteMaxRetries(AsyncRemoteException):
    def __init__(self, TypeName, Value, TracebackStrings):
        super().__init__(TypeName, Value, TracebackStrings)


class AsyncAttributeError(AsyncRemoteException):
    def __init__(self, TypeName, Value, TracebackStrings):
        super().__init__(TypeName, Value, TracebackStrings)
