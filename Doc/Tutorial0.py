'''

H e l l o   W o r l d

How easy is it to code the obligatory Hello World program?

Let's dig in.

All Corps Python Workers are created by a Worker Factory in the Workers module.

To load our Corps we call Workers's load_Corps:

    load_Corps(CorpsClass, *args, ConfigFiles=[], **kwargs)

where:

    - ConfigFiles=List of Config file names

    - *args and **kwargs are regular parameters to CorpsClass's __init__

If we ignore the Config files for now and just use defaults, and our HelloWorld Corps has no __init__ params we can
simply call:

    OurCorps = load_Corps(HelloWorld)

The return from load_Corps is a Name.  It has the same interface as the Worker and may be passed as an arg.

But a Name is not a regular attribute - it is a proxy for the Worker.

By invoking one of the Worker's methods via a Name we are asking Corps Python's runtime system to build and send
a message to the Worker, execute the method, and build a return message and send it back to us.

All of this happens transparently.

The actual HellowWorld Corps is quite simple:

    class HelloWorld(Corps):
     def __init__(self):
        super().__init__()


       def say_hello(self):
            return'Hello World!'

We can invoke the method as we normally would:

    FutRet = OurCorps.say_hello()

What is different here from a normal method invocation is the return value, a Corps Python Future (not to be
confused with futures types from Python's asyncio or concurrent modules).

We can retrieve the actual result by accessing the Ret (ret also works, if you prefer PEP 8) attribute of the Future:

    Ret = FutRet.Ret

If the result has not been returned yet, this attempt to access the result will block the caller until it is
available.

If you want to check if the result is ready you can check without blocking:

    if FutRet.ret_ready():  # returns True or False
        Ret = FutRet

    else:
        do_something_else()

Finally, when we are done we can exit the Corps:

    OurCorps.exit()


We have everything we need now.  The full listing is below.

'''

from Corps import Corps


class HelloWorld(Corps):
    def __init__(self):
        super().__init__()


    def say_hello(self):
        return 'Hello World!'


if __name__ == '__main__':

    from Workers import load_Corps


    OurCorps = load_Corps(HelloWorld)

    FutRet = OurCorps.say_hello()
    print(f'\n{FutRet.Ret}\n')

    OurCorps.exit()
