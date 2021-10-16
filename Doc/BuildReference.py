
'''
    Script to build the Reference text from developer-facing doc strings
'''



from importlib import import_module



MainTitle = 'C o r p s   P y t h o n   V e r s i o n   0 . 1   R e f e r e n c e'

RefFile = '.\Doc\Reference.txt'

Files = [
    ('W o r k e r s', 'Workers'),
    ('C o r p s', 'Corps'),
    ('C o n c s', 'Conc'),
    ('F u t u r e s', 'Future'),
    ('E x c e p t i o n s', 'Exceptions'),
    ('C o n f i g  F i l e s', 'ConfigGlobals')
    ]

RelPath = ''

TitleSeparator = '\n'
SectionSeparator = '\n\n'


OutFile = open(RefFile, 'w')

print(f'{SectionSeparator}{MainTitle}{SectionSeparator}', file=OutFile)

for Title, Source in Files:
    SourceModule = import_module(RelPath + Source)
    Doc = SourceModule.__doc__
    print(f'{Title}{TitleSeparator}{Doc}{SectionSeparator}', file=OutFile)
