'''

    Caches results for individual service Concs

    Used so we don't retry completed non-idempotent methods for particular requests from client Concs.

    We cache all results since we don't know which methods are idempotent and those not.

    Locking is not needed since this will be called from Conc main(), which is assumed to be atomic (one method is
    completed before another is initiated).

    Retries in the the context of forwarding will result in more timeouts (and more retries) but upstream results
    will get cached as well.

    The cache is implemented as an ordered dict (newest entries stored last).

    Each entry has a timestamp and after each get() an attempt is made to clean (purge) old entries if at least
    (Config variable) ResultsCache_Min_Clean_Interval seconds have passed since the last cleaning.

    The entry is removed if it has resided in the cache for longer than (Config variable) ResultsCache_Max_Entry_TTL
    seconds.

    An entry's timestamp is refreshed (set to current time) if a cache entry is found (i.e. a cache hit) during a
    get().
'''



from collections import namedtuple, OrderedDict
from ConfigGlobals import ResultsCache_Max_Entry_TTL, ResultsCache_Min_Clean_Interval
from datetime import datetime, timezone, timedelta



ResultsCacheKey = namedtuple('ResultsCacheKey', 'IP Port MsgId')

ResultsCacheValue = namedtuple('ResultsCacheValue', 'TimeStamp Res')


class ResultsCache():
    def __init__(self):
        self.Cache = OrderedDict()
        self.LastCleaning = datetime.now(tz = timezone.utc)


    def set(self, Key, Res):
        assert type(Key) == ResultsCacheKey, f'ResultsCache.set: Invalid Key type {type(Key)}'

        self.Cache[Key] = ResultsCacheValue(datetime.now(tz = timezone.utc), Res)
    

    def get(self, Key):    
        assert type(Key) == ResultsCacheKey, f'ResultsCache.get: Invalid Key type {type(Key)}'

        Value = None

        try:
            Value = self.Cache[Key]

        except:
            pass

        else:
            # refresh the entry
            del self.Cache[Key]
            self.Cache[Key] = ResultsCacheValue(datetime.now(tz = timezone.utc), Value.Res)

        self.__clean__()

        if Value != None:
            return Value.Res

        else:
            return None
         
    
    def __clean__(self):
        Now = datetime.now(tz = timezone.utc)

        if Now - self.LastCleaning < ResultsCache_Min_Clean_Interval:
            return

        CleanedEntries = 0
        for Key, Value in self.Cache.items():
            if Now - Value.TimeStamp >= ResultsCache_Max_Entry_TTL:
                CleanedEntries += 1

            else:
                break

        for Entry in range(CleanedEntries):
            self.Cache.popitem(last=False)

        self.LastCleaning = datetime.now(tz = timezone.utc)


    def __repr__(self):
        output = []

        output.append(f'ResultsCache with id {id(self)}\n')

        for Key, Value in self.Cache.items():
            output.append(f'\t{Key}: {Value}\n')

        return ' '.join(output)



if __name__ == '__main__':

    from time import sleep
    from ipaddress import ip_address



    ip = ip_address('127.0.0.1')
    port = 10101

    # Values from ConfigGlobals...reinitialize them here to control for testing
    ResultsCache_Max_Entry_TTL = timedelta(seconds=0.1)
    ResultsCache_Min_Clean_Interval = timedelta(seconds=0.2)


    r = ResultsCache()

    k1 = ResultsCacheKey(ip, port, 1)
    k2 = ResultsCacheKey(ip, port, 2)
    k3 = ResultsCacheKey(ip, port, 3)


    # 1 entry total

    # empty
    assert r.get(k1) == None

    # new
    r.set(k1, 1)
    assert r.get(k1) == 1

    #  old, refreshed
    sleep(0.21)
    assert r.get(k1) == 1       # there the first time, then refreshed
    assert r.get(k1) == 1       # still there

    # old, not refreshed
    sleep(0.21)
    assert r.get(k2) == None    # k2 has never been there, cleans old k1
    assert r.get(k1) == None    # should be gone


    # 2 entries total

    r.set(k2, 2)                # the other first

    # empty
    assert r.get(k1) == None

    # new
    r.set(k1, 1)
    assert r.get(k1) == 1

    #  old, refreshed
    sleep(0.21)
    assert r.get(k1) == 1       # there the first time, then refreshed
    assert r.get(k1) == 1       # still there
    assert r.get(k2) == None    # k2 now gone

    # old, not refreshed
    r.set(k2, 2)                # put k2 back in
    sleep(0.21)
    assert r.get(k2) == 2       # cleans old k1
    assert r.get(k1) == None    # should be gone


    # 3 entries total

    # new
    r.set(k2, 2)
    r.set(k1, 1)
    r.set(k3, 3)
    assert r.get(k1) == 1

    #  old, refreshed
    sleep(0.21)
    assert r.get(k1) == 1       # there the first time, then refreshed
    assert r.get(k1) == 1       # still there
    assert r.get(k2) == None    # k2 now gone
    assert r.get(k3) == None    # k3 now gone

    # old, not refreshed
    r.set(k2, 2)                # put k2 back in
    r.set(k3, 3)                # put k2 back in
    sleep(0.21)
    assert r.get(k2) == 2       # cleans old k1
    assert r.get(k1) == None    # should be gone
    assert r.get(k3) == None    # k3 now gone

    print('done....')
