
'''
    Corps's Env Address Space


    - 32 bit
        - -2**31 + 1 to 2**31 - 1
'''



# Envs other than CorpsMgr's
MAX_ENVID = pow(2, 31) - 1
MIN_ENVID = 0

# CorpsMgr Env
CORPSMGR_ENVID = MIN_ENVID

# Containing Env (if we are Contained)
CONTAINING_ENVID = MIN_ENVID-1

# Reserved
MAX_RESERVED = CONTAINING_ENVID-1
MIN_RESERVED = -1000

# Contained Envs
MAX_CONT_CORPS_ENVID = MIN_RESERVED-1
MIN_CONT_CORPS_ENVID = -pow(2, 31)/2

# External Envs
MAX_EXT_CORPS_ENVID = MIN_CONT_CORPS_ENVID-1
MIN_EXT_CORPS_ENVID = -pow(2, 31) + 1

