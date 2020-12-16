'''

R e a l   W o r l d

The Old World solution to a regular expression search of all files in a directory tree or sub-tree is fully functional.

That is, it works, and it turned out to be fairly simple.  Unfortunately, it's too simple.

Remember we wanted to "plan for the possibilities that the number and size of the files is large and the
computational costs of searching for a particular regex is high and we want a given run to complete in a reasonable
amount of time."?

Our current solution only runs in a single thread in a single process.  It will likely spend more time waiting for
the disk than it will searching for patterns.

It clearly will not meet our performance criteria for the assumed possible use case.

A typical Old World solution would be to fire up some threads and processes, create a custom synchronization and data
transfer solution, assign the threads/processes a portion of the work, sync up, transfer and collate the data, and
kill all of the threads/processes.

Corps Python makes extensive use of threads and processes behind the scenes.  But few software developers are
comfortable with them. They are not like objects and functions, are a little difficult to use, and it's too easy to
create synchronization problems.

Another issue is that we can only create threads and processes on our own host.  So we are limited to a relatively
small number of cores/processors, and therefore processes.

Truly large jobs may need hundreds, or even thousands, of cores/processors running on many hosts.

So now, in addition to local threads and processes, we are talking about network stacks, message formats, data
marshalling and unmarshalling, remote daemons, remote processes, new synchronization tactics, etc.

Complicated and a bit of a nightmare for most developers, but all handled transparently within Corps Python.

So we will skip any further pursuit of a traditional Old World solution and move on to a Corps Python solution.


N e w   W o r l d

To accomplish a lot of work over many processors on many hosts we will need a lot of Workers who can operate in
parallel.  We will rely on a type of Worker called a Conc, which is the concurrent (asynchronous) equivalent of a
regular, class-based Python object.

Concurrent entities can be differentiated by their "grain-size".  The floating point numbers in vectors that GPUs
operate on are small-grained.  Processes have a large grain-size (and despite their name, so are Microservices),
while threads are medium-grained.  Corps Python supports both medium and large grain sizes, while various Python
packages such as NumPy support small-grained operations.

Generally you want to use the appropriate grain-size for the computational needs and the necessary synchronization
costs.  For instance you wouldn't want to use multiple threads or processes to add a pair of numbers.  Any benefit
to running them in parallel would be dwarfed by the costs of creating them and communicating between them.

So why did we choose a Conc for our "a lot of Workers"?  Because they are a medium grain-sized entity and that is
probably the appropriate grain-size for doing a regex search of a single file.

We can describe the Concs as hosted by, or contained within, the Corps, who is considered their Manager, or Mgr.
And if one of those Concs creates other Workers they are hosted by, or contained within, the creating Conc, and the
creating Conc is their Mgr, and so on.

In this manner, among others, we can achieve a virtually unlimited degree of concurrency and therefore parallelism.
We also have a natural management hierarchy which is useful for behaviors such as orderly cleanup and shutdowns and
Auto-Healing.

Corps, on the other hand are large-grained.  The Concs are hosted by the Corps and run inside the various Envs of
the Corps.  Each Env has an adaptively-sized pool of threads that perform various tasks for the Corps Python runtime
(think of it as a concurrent operating system inside of each Corps) including executing the code for the Concs.  Each
Env operates inside of a process and so is itself large-grained.

Defining our Searcher Conc is straightforward.  If the Old World search_file had been a method of a Searcher class
we would have only needed to create a new class which inherited from both Searcher and Conc.

But since search_file is simply a function, we will create Searcher by inheriting from Conc and making search_file
a method (we just need to add self to the args list).  We also need to init the Conc superclass in Searcher's
__init__:

    class Searcher(Conc):
        def __init__(self):
            super().__init__()


        def search_file(self, Filename, CompiledRegex):
            f = open(Filename, "r")

            Matches = []

            while True:
                try:
                    Line = f.readline()

                except:
                    ei = exc_info()
                    return Filename, [f'E x c e p t i o n : {ei[0].__name__} {ei[1]}']

                if Line:
                    Match = CompiledRegex.search(Line)

                    if Match:
                        Matches.append(Line)

                else:
                    break

            f.close()
            return Filename, Matches


Our RegexServer Corps will create all the Searcher Concs in __init__:

    class RegexServer(Corps):
        def __init__(self, NumSearchers):
            super().__init__()

            self.Searchers = create_Workers(self.my_Name(), Searcher, LocType=LocType.PerEnv, Num=NumSearchers)


The NumSearchers __init__ arg is the number of Searchers we want to create per Env.  We chose that because the
Workers factory function create_Workers has that as an option for the location type and unit.

The create_Workers interface is documented in the Corps Python Reference.  But let's take a quick look.

The two required arguments are the Manager Name, which is the Corp's Name, and the Worker's class.  Any positional
args to be passed to the Workers' __init__ should be placed after them.

Here we are specifying non-default keyword args for LocType and Num.  Keyword args for the Workers's __init__ can
be placed anywhere amongst them (before, between, after, etc).  We have no args or kwargs for Searcher itself.

In the Old World version we had __main__ use the next_file generator to iterate over all the files and search
each in turn.  Here we will create a method for RegexServer, search_files, which takes the top-level Dir and the
CompiledRegex as args, and will iterate over the files.

But instead of searching synchronously and sequentially and waiting for the result, it will issue them asynchronously
and concurrently to the Searcher Concs.  It will wait for all of the results to complete, collate them, and return
the full set to __main__.

One simplifying assumption we are making is that all Searcher Concs in all Envs in all Hosts will have access to all
files.  But if the job is large the file server may need to be enterprise-class and different sets of Searchers may
need to operate on only the directory trees they have access to.

Since Searcher's search_file returns a tuple of the FileName and a list of lines that match the regex, RegexServer's
search_files will return a list of those tuples.

We will need a list to hold the Future results, FutRets, and a list of the tuples with a match, AllMatches:

    def search_files(self, Dir, CompiledRegex):
        FutRets = []
        AllMatches = []


As we did with Old World we need to declare an instance of next_file:

        nextf = next_file(Dir)


We also need a way to choose to which Searcher we assign the next file.  We will just use a simple round-robin
method and for that we create a simple modulo-N generator:

    def next_i(Max):
        i = 0

        while True:
            yield i

            i += 1
            if i >= Max:
                i = 0


And we can declare an instance of it for search_files with Max as the total number of Searchers:

    next_name = next_i(len(self.Searchers))


Now iterating over the files and assigning them to individual Searchers is simple:

    for f in nextf:
        ns = next(next_name)
        FutRets.append(self.Searchers[ns].search_file(f, CompiledRegex))


We will use Future's wait_all to wait for all results to complete.  Its interface is wait_all(FutRets, InitDelay=
0.05, DelayIncPct=20, MaxTries=25).  It waits until all Futures results have completed or we exceed MaxTries waits
for uncompleted results.  It uses a sleepy waiting algorithm with exponential backoff which has an initial wait time
of InitDelay seconds which then increases DelayIncPct for each wait thereafter.

If MaxTries are exceeded it raise a AsyncLocalMaxRetries exception and in turn we will raise a AsyncRemoteMaxRetries
exception.  We will just use the defaults for wait_all, but limits might need to be raised for large jobs:

    try:
        wait_all(FutRets)

    except AsyncLocalMaxRetries:
        ei = exc_info()
        ftb = format_exception(ei[0], ei[1], ei[2])
        raise AsyncRemoteMaxRetries(ei[0].__name__, ei[1], ''.join(ftb))


We then only have to collect and return the full set of results. Remember that the return from Searcher's search_file
is an empty Matches list (the second element in the tuple) if there are no matches, which is why we are testing
File_and_Matches[1]:

    for FutRet in FutRets:
        try:
            File_and_Matches = FutRet.Ret

        except:
            print('search_files: Exception: exec_info: {exc_info()}\n')

        else:
            if File_and_Matches[1]:
                AllMatches.append(File_and_Matches)

    return AllMatches


Here is the full listing for RegexServer's search_files:

    def search_files(self, Dir, CompiledRegex):
        FutRets = []
        AllMatches = []

        nextf = next_file(Dir)
        next_name = next_i(len(self.Searchers))

        for f in nextf:
            ns = next(next_name)
            FutRets.append(self.Searchers[ns].search_file(f, CompiledRegex))


        try:
            wait_all(FutRets)

        except AsyncLocalMaxRetries:
            ei = exc_info()
            ftb = format_exception(ei[0], ei[1], ei[2])
            raise AsyncRemoteMaxRetries(ei[0].__name__, ei[1], ''.join(ftb))


        for FutRet in FutRets:
            try:
                File_and_Matches = FutRet.Ret

            except:
                print('search_files: Exception: exec_info: {exc_info()}\n')

            else:
                if File_and_Matches[1]:
                    AllMatches.append(File_and_Matches)

        return AllMatches


Our __main__ is fairly simple.  After loading a RegexServer Corps and asynchronously issuing the request to
search_files, it simply blocks waiting for the results and iterates over them and prints them:

    RegexCorps = load_Corps(RegexServer, NumSearchers)

    FutRet = RegexCorps.search_files(Dir, CompiledRegex)

    try:
        AllMatches = FutRet.Ret

    except:
        print(f'\nE x c e p t i o n: exec_info: {exc_info()}\n')

    else:
        for File, Matches in AllMatches:
            print(f'\n{File}:\n')

            for Match in Matches:
                print(f'\t>> {Match}')


    RegexCorps.exit()


The full signature for load_Corps is load_Corps(CorpsClass, *args, ConfigFiles=[], **kwargs) where ConfigFiles is a
list of Config file names and *args and **kwargs are regular parameters to the Corps class's __init__.  We are using
the defaults for the ConfigFiles list and the keyword args, but pass NumSearchers as an arg to RegexServer __init__.
See the Corps Python Reference for the Workers' load_Corps and the Config file documentation.

Like Dir and Regex, NumSearchers (per Env) is simply an attribute in __main__ that is hardcoded now but could be
user-provided in an appropriate front-end.  But big questions remain: How many Hosts?  How many Envs?  How many
Searchers? etc.

These are best left for a future lesson.  While the number of Envs and NumSearchers are parameters that need to be
tuned, we have created the foundation for a scalable service that can run on a large configuration.  And we have
accomplished that without much added complexity.

The full New World listing is included below:

'''



from re import compile
from os import listdir
from os.path import isfile, isdir, join
from Corps import Corps
from Conc import Conc
from Workers import load_Corps, create_Workers, LocType
from Future import wait_all
from sys import exc_info
from Exceptions import AsyncLocalMaxRetries, AsyncRemoteMaxRetries
from traceback import format_exception



class Searcher(Conc):
    def __init__(self):
        super().__init__()


    def search_file(self, Filename, CompiledRegex):
        f = open(Filename, "r")

        Matches = []

        while True:
            try:
                Line = f.readline()

            except:
                ei = exc_info()
                return Filename, [f'E x c e p t i o n : {ei[0].__name__} {ei[1]}']

            if Line:
                Match = CompiledRegex.search(Line)

                if Match:
                    Matches.append(Line)

            else:
                break

        f.close()
        return Filename, Matches


def next_file(Dir):
    ''' Directory tree traversal generator '''

    for Filename in listdir(Dir):
        Path = join(Dir, Filename)

        if isdir(Path):
            for Entry in next_file(Path):
                yield Entry

        elif isfile(Path):
            yield Path


def next_i(Max):
    ''' Modulo N generator '''

    i = 0

    while True:
        yield i

        i += 1
        if i >= Max:
            i = 0


class RegexServer(Corps):
    def __init__(self, NumSearchers):
        ''' Create NumSearchers Searcher Concs per Env '''

        super().__init__()

        self.Searchers = create_Workers(self.my_Name(), Searcher, LocType=LocType.PerEnv, Num=NumSearchers)


    def search_files(self, Dir, CompiledRegex):
        ''' Search all files in Dir and its sub-diectories for the compiled regex '''

        FutRets = []
        AllMatches = []

        nextf = next_file(Dir)
        next_name = next_i(len(self.Searchers))

        for f in nextf:
            ns = next(next_name)
            FutRets.append(self.Searchers[ns].search_file(f, CompiledRegex))


        try:
            wait_all(FutRets)

        except AsyncLocalMaxRetries:
            ei = exc_info()
            ftb = format_exception(ei[0], ei[1], ei[2])
            raise AsyncRemoteMaxRetries(ei[0].__name__, ei[1], ''.join(ftb))


        for FutRet in FutRets:
            try:
                File_and_Matches = FutRet.Ret

            except:
                print('search_files: Exception: exec_info: {exc_info()}\n')

            else:
                if File_and_Matches[1]:
                    AllMatches.append(File_and_Matches)

        return AllMatches


if __name__ == '__main__':

    print('\n\nN e w   W o r l d')

    NumSearchers = 8    # per Env

    Dir = 'C:\\Users\\Joe Schmoe\\Documents'
    Regex = 'xyzzy'

    CompiledRegex = compile(Regex)


    RegexCorps = load_Corps(RegexServer, NumSearchers)

    FutRet = RegexCorps.search_files(Dir, CompiledRegex)

    try:
        AllMatches = FutRet.Ret

    except:
        print(f'\nE x c e p t i o n: exec_info: {exc_info()}\n')

    else:
        for File, Matches in AllMatches:
            print(f'\n{File}:\n')

            for Match in Matches:
                print(f'\t>> {Match}')


    RegexCorps.exit()
