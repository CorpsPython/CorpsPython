'''

O l d   W o r l d

Creating programs like HelloWorld can be fun.  Just how small can it we make?  Look how little boilerplate is needed!

But it is a toy that provides only the briefest of glimpses into what is required in a real-world context.

Nevertheless, thus far we have been introduced to some important Corps Python concepts: Corps, Workers, Name, and
Future.

Let's begin to create something that is potentially useful and could actually be deployed.

Imagine we want a service or app that searches for regular expressions ("regex") over a number of files.

We want to plan for the possibilities that the number and size of the files is large and the computational costs of
searching for a particular regex is high and we want a given run to complete in a reasonable amount of time.

Our program will just search for a regex given a start directory.  It will traverse the directory tree and return
a list of the lines in each file that contain the regex.

Python already has a regex library, re, that provides us the low-level functionality we need.

We will rely on re's search function which scans through a string and returns a MatchObject after the first match or
None if no match is found.

So we can search for the first instance of digits in a string by calling:

    match = search('\d+', 'My work id is 123456789 and my gym id is 987654321')
    print(match)


This produces a Match object:

    <_sre.SRE_Match object; span=(14, 23), match='123456789'>


Since we will be returning the entire line from a file (our input to the search function), we will not be using the
returned Match object except to let us know we have a match.

Since we are going to call search repeatedly it will be more efficient if we take advantage of re's compile function
so the regex only gets compiled once (regular re.search does it upon each invocation).  The compile function returns a
compiled regex object which has it own search method.

Our search_file function takes a full path filename and a compiled regex object as args and just iterates over all of
the lines in the file and appends any matching lines to our list, Matches.  It returns the filename and the list of
matches as a tuple:

    def search_file(Filename, CompiledRegex):
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


Using readline to read a line at a time may seem inefficient.  Why not just read in the entire file?

Remember the file may be large.  And the file system and possibly Python's implementation will be buffering one or
more disk blocks for each file.

Many files types (.dll, .exe, etc) cause exceptions because they don't really have "lines".  In a real system you
may want to include or exclude certain files types.  Alternatively, instead of lines you could read a fixed number
of bytes at a time.

Given a start directory we need to be able to traverse the file system from that point to produce full-path file
names.  We could use the os module's walk function, but I find it a little awkward to use, and writing our own is
fairly straightforward.

A list comprehension seems a bit wasteful so a generator is probably a better solution.

We iterate over the files the directory and when we encounter a file in a given directory we yield it and when we
encounter another directory we recurse:

    def next_file(Dir):
        for Filename in listdir(Dir):
            Path = join(Dir, Filename)

            if isdir(Path):
                for Entry in next_file(Path):
                    yield Entry

            elif isfile(Path):
                yield Path


Using next_file is simple. We declare an instance of it, passing our starting directory to initialize it, and then
we can use it by utilizing the iterator protocol (i.e. __next__):

    nextf = next_file(Dir)

    for f in nextf:
        print(f'File: {f}')


Now we just need to put it all together with a simple script.  Our __main__ iterates over all of the files, using
next_file, and prints all of the file's matches if any are found.

We'll assume that an approopriate front-end such as a CLI, GUI, or REST calls us in a fully-deployable version of
our program.  For demonstration's sake we will just hardcode the start directory and regex as attributes in our
script (which is a stand-in for the deployable-version's front-end, at least for now).

Here is the full listing:

'''

from re import compile
from os import listdir
from os.path import isfile, isdir, join
from sys import exc_info



def search_file(Filename, CompiledRegex):
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
    for Filename in listdir(Dir):
        Path = join(Dir, Filename)

        if isdir(Path):
            for Entry in next_file(Path):
                yield Entry

        elif isfile(Path):
            yield Path


if __name__ == '__main__':

    print('\n\nO l d   W o r l d')

    Dir = 'C:\\Users\\Joe Schmoe\\Documents'
    Regex = 'xyzzy'

    CompiledRegex = compile(Regex)

    nextf = next_file(Dir)

    for f in nextf:
        try:
            File, Matches = search_file(f, CompiledRegex)

        except:
            print(f'\n{f}:\n\tE x c e p t i o n: exec_info: {exc_info()}\n')

        else:
            if Matches:
                print(f'\n{File}:\n')

                for Match in Matches:
                    print(f'\t>> {Match}')



