
'''
    Status codes for Corps and Envs
'''



from enum import IntEnum


class MajorStatus(IntEnum):
    Nonexistent = -999
    Booting = 1
    Restarting = 2
    Running = 3
    Exiting = 4
    Impaired = 5
    Failed = 6


class MinorStatus(IntEnum):
    Undefined = 0