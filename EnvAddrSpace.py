
'''
    Corps's Env Address Space

    - 32 bit
        - -2**31 + 1 to 2**31 - 1

    The Env space (proper) has about 2B possible entries.

    Each ContCorps and ExtCorps is treated as an Env with about 1B possible entries each.

    We have dedicated entries for the CorpsMgr Env and the Corps' Mgr (also a Corps).

    For unknown future uses 1000 entries are reserved.
'''




# Envs other than CorpsMgr's
MAX_ENVID = pow(2, 31)-1
MIN_ENVID_plus_1 = 1

# CorpsMgr Env, Corps Env
CORPSMGR_ENVID = 0
CORPS_ENVID = CORPSMGR_ENVID
MIN_ENVID = CORPSMGR_ENVID

# Reserved
MAX_RESERVED = CORPSMGR_ENVID-1
MIN_RESERVED = -1000

# Contained Envs
MAX_CONT_CORPS_ENVID = MIN_RESERVED-1
MIN_CONT_CORPS_ENVID = -pow(2, 31)/2

# External Envs that are Linked (i.e. our Corps is the Mgr)
MAX_EXT_CORPS_ENVID = MIN_CONT_CORPS_ENVID-1
MIN_EXT_CORPS_ENVID = -pow(2, 31)+1

