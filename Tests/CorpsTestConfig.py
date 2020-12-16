
'''
    Sample user-supplied Config File


    This file is used in the Corps Python Integraton Tests and should not be edited lest you f' things up.

    All settable variables are contained in ConfigGlobals.py.  Also see external documentation.

    Do not declare any the settable variables as global.  The processing of Config files handles that.

    Two examples are illustrated below.

    NumEnvs is assumed to set as an environment variable.  Here we read it from the environment using a function
    from the os module and then set it.

    Max_Msg_Request_Attempts is set directly.
'''



import os



# NumEnvs is set as an environment variable in CorpsPythonTest before the Tests are begun
NumEnvs = int(os.environ['NumEnvs'])

# Example of simple setting of a Config variable
Max_Msg_Request_Attempts = 100