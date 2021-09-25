'''
    EnvTable is a dict mapping EnvIds to EnvRecords.


    The EnvTableBase class is subclassed into EnvTable for regular Envs and CorpsEnvTable to support ContCorps and
    ExtCorps.

    The CorpsMgr manages the allocation of EnvIds for the Corps.

    All operations are protected by a lock.

    Needed to support Workers' LocType=Auto gen of a next Env to create a Worker in.  Placed it here since it
    required the highest EnvId already alloc'd as N in modulo-N.

'''



from threading import Lock
from copy import copy



class EnvTableBase():
    ''' Base class for all EnvTables '''

    def __init__(self, MinEnvId, MaxEnvId):
        self.MinEnvId = MinEnvId
        self.MaxEnvId = MaxEnvId
        self.NextEnvId = self.MinEnvId
        self.Dict = dict()
        self.Lock = Lock()


    def register(self, EnvId, anEnvRecord):
        ''' Register the EnvRecord of a given EnvId

            If EnvId is None the EnvTable assigns it

            Returns the EnvId
        '''

        if EnvId != None:
            assert EnvId >= self.MinEnvId, f'EnvTableBase register(): EnvId {EnvId} is too low'
            assert EnvId <= self.MaxEnvId, f'EnvTableBase register(): EnvId {EnvId} is too high'

        AlreadyExists = False

        self.Lock.acquire()

        if EnvId == None:
            # Find next unallocated EnvId
            while self.NextEnvId <= self.MaxEnvId:
                try:
                    ExistingEnvRecord = self.Dict[self.NextEnvId]

                except:
                    break

                else:
                    self.NextEnvId += 1

            if self.NextEnvId <= self.MaxEnvId:
                self.Dict[self.NextEnvId] = anEnvRecord

            # else:
                # implicit flag of EnvId too high via assert before exit

            NewEnvId = self.NextEnvId

        else:
            # Make sure given EnvId is not already allocated
            try:
                ExistingEnvRecord = self.Dict[EnvId]

            except:
                self.Dict[EnvId] = anEnvRecord

            else:
                AlreadyExists = True  # Flag EnvId already exists via assert before exit

            NewEnvId = EnvId


        self.NextEnvId += 1  # prep for next call

        self.Lock.release()

        assert NewEnvId <= self.MaxEnvId, f'EnvTableBase register(): EnvId {NewEnvId} is too high'
        assert AlreadyExists == False, f'EnvTableBase register(): EnvId {NewEnvId} already exists'

        return NewEnvId


    def num_Envs(self):
        ''' Returns number of Envs '''

        self.Lock.acquire()

        NumEnvs = len(self.Dict)

        self.Lock.release()

        return NumEnvs


    def update(self, EnvId, NewEnvRecord):
        ''' Overwrite the EnvRecord of a given EnvId with a replacement '''

        self.Lock.acquire()

        anEnvRecord = None
        try:
            anEnvRecord = self.Dict[EnvId]

        except:
            pass

        if anEnvRecord != None:
            self.Dict[EnvId] = NewEnvRecord

        self.Lock.release()

        assert anEnvRecord != None


    def get(self, EnvId):
        ''' Find and return the EnvRecord for a given EnvId '''

        self.Lock.acquire()

        anEnvRecord = None
        try:
            anEnvRecord = self.Dict[EnvId]

        except:
            pass

        self.Lock.release()

        assert anEnvRecord != None
        return copy(anEnvRecord)


    def unregister(self, EnvId):
        ''' Find and delete the EnvRecord of a given EnvId '''

        self.Lock.acquire()

        anEnvRecord = None
        try:
            anEnvRecord = self.Dict[EnvId]

        except:
            pass

        if anEnvRecord != None:
            del self.Dict[EnvId]

        self.Lock.release()

        assert anEnvRecord != None


    def __repr__(self):
        output = []

        self.Lock.acquire()

        for EnvId, anEnvRecord in self.Dict.items():
            output.append(f'\tEnv {EnvId} {anEnvRecord}\n')

        self.Lock.release()

        return ' '.join(output)


def next_Env(EnvDict, MinEnvId, MaxEnvId):

    '''
    Generator that returns the next Env and EnvRecord as a tuple from the Dict of an EnvTable

    Only returns EnvRecords for EnvIds between EnvIdMin and EnvIdMax, inclusive

    Danger! Danger!, Will Robinson!!

    Only to be used when the EnvTable the Dict is in is guaranteed to be stable, unchanging!

    That probably limits it to use in CorpsMgr methods since CorpsMgr is the only entity that can change or
    request EnvMgrs to change an EnvTable.

    Usage:
    NE: = next_Env(anEnvTable.Dict, MinEnvId, MaxEnvId)

    for EnvId_EnvRecord in NE:
        EnvId = EnvId_EnvRecord[0]
        anEnvRecord = EnvId_EnvRecord[1]
    '''

    for EnvId, anEnvRecord in EnvDict.items():
        if EnvId >= MinEnvId and EnvId <= MaxEnvId:
            yield(EnvId, anEnvRecord)


class EnvTable(EnvTableBase):
    def __init__(self, MinEnvId, MaxEnvId):
        super().__init__(MinEnvId, MaxEnvId)

        self.NextAutoEnvId = self.MinEnvId


    def next_AutoEnvId(self):
        ''' Support for Workers' create_Conc's LocType=Auto '''

        self.Lock.acquire()

        AutoEnvId = self.NextAutoEnvId

        self.NextAutoEnvId += 1
        if self.NextAutoEnvId > len(self.Dict)-1:
            self.NextAutoEnvId = self.MinEnvId

        self.Lock.release()

        return AutoEnvId


class CorpsEnvTable(EnvTableBase):
    def __init__(self, MinEnvId, MaxEnvId):
        super().__init__(MinEnvId, MaxEnvId)
        self.Tag2Id = dict()
        self.Id2Tag = dict()
        self.Lock2 = Lock()     # for us only, self.Lock to be used by EnvTableBase only


    def register(self, EnvId, aCorpsEnvRecord):
        ''' Register the EnvRecord of a given Tag and EnvId

            If EnvId is None the EnvTable assigns it

            Returns the EnvId
        '''

        assert aCorpsEnvRecord.Tag != '', f'CorpsEnvTable register: Tag must be non-empty'

        self.Lock2.acquire()

        anEnvId = None
        try:
            anEnvId = self.Tag2Id[aCorpsEnvRecord.Tag]

        except:
            anEnvId = super().register(EnvId, aCorpsEnvRecord)

            self.Tag2Id[aCorpsEnvRecord.Tag] = anEnvId
            self.Id2Tag[anEnvId] = aCorpsEnvRecord.Tag

        self.Lock2.release()

        return anEnvId


    def unregister(self, Tag='', EnvId=None):
        ''' Find and delete the EnvRecord of a given Tag or EnvId '''

        assert Tag != '' or EnvId != None, f'CorpsEnvTable unregister: Tag {Tag} or EnvId {EnvId}must be valid'

        self.Lock2.acquire()

        anEnvId = EnvId
        aTag = Tag

        if aTag != '':
            try:
                anEnvId = self.Tag2Id[aTag]

            except:
                pass

        elif anEnvId != None:
            try:
                aTag = self.Id2Tag[anEnvId]

            except:
                pass

        if aTag != '' and anEnvId != None:
            del self.Tag2Id[aTag]
            del self.Id2Tag[anEnvId]
            super().unregister(anEnvId)

        self.Lock2.release()

        assert aTag != '' and anEnvId != None, f'CorpsEnvTable unregister: Tag {aTag} or EnvId {anEnvId} not found'
