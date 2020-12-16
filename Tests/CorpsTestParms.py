
'''
    Simple object to pass test paramters around in Corps Pythn Integration Tests


    NumGlobalServers, NumClients and NumClientsServers are per Env
'''



class CorpsTestParms():
    def __init__(self, NumEnvs, NumGlobalServers, NumClients, NumClientsServers, NumClientIters):
        self.NumEnvs = NumEnvs
        self.NumGlobalServers = NumGlobalServers
        self.NumClients = NumClients
        self.NumClientsServers = NumClientsServers
        self.NumClientIters = NumClientIters
