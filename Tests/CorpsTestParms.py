
'''
    Simple object to pass test paramters around in Corps Python Integration Tests

    Any of these may be ignored in a given test

    NumGlobalServers, NumClients and NumClientsServers are per Env
'''



class CorpsTestParms():
    def __init__(self, CorpsDepth, NumEnvs, NumGlobalServers, NumClients, NumClientsServers, NumClientIters):
        self.CorpsDepth = CorpsDepth
        self.NumEnvs = NumEnvs
        self.NumGlobalServers = NumGlobalServers
        self.NumClients = NumClients
        self.NumClientsServers = NumClientsServers
        self.NumClientIters = NumClientIters
