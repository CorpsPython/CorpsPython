
'''
    create_config_delta()

        Load Config attrs from a list of Config files and a list of Config dicts and create a dict of attrs to be
        changed

    apply_config_delta()

        Given a config delta, adict of attrs to be changed, overwrite those attrs in the Globals module
'''

'''
    todo:
        replace error msgs with log msgs (get log vars from config?)
        log all deltas applied?
'''

from sys import modules



def create_config_delta(GlobalsFile, ConfigFiles=[], ConfigDicts=[]):
    ''' Return a dict of Config deltas from Config files and Config dicts
        The files are processed in list order first, overwriting any previous Config Delta entries,
        then the Config dicts are handled the same way '''

    # Grab the GlobalsFile's module and Dict
    GlobalsModule = modules[GlobalsFile]
    GlobalsDict = getattr(GlobalsModule, 'GlobalsDict')

    # Load the Config files into this module
    for ConfigFile in ConfigFiles:
        exec(open(f'./{ConfigFile}').read())

    ConfigAttrs = locals()

    # Iterate over entries from the ConfigFiles and add to ConfigDelta
    ConfigDelta = {}
    for attr, val in ConfigAttrs.items():
        try:
            val1 = GlobalsDict[attr]

        except:
            # Not a Config variable, skip silently
            pass

        else:
            ConfigDelta[attr] = val

    # Iterate over entries from the ConfigDicts and add to ConfigDelta
    for ConfigDict in ConfigDicts:
        for attr, val in ConfigDict.items():
            try:
                val1 = GlobalsDict[attr]

            except:
                # Not a Config variable, skip silently
                print(f'\tWarning: {attr} is Not a Config variable, skipping')
                pass

            else:
                ConfigDelta[attr] = val

    return ConfigDelta


def apply_config_delta(GlobalsFile, ConfigDelta):
    ''' Apply the ConfigDelta dict entries to the GlobalsFile module '''

    # Grab the GlobalsFile's module and Dict
    GlobalsModule = modules[GlobalsFile]
    GlobalsDict = getattr(GlobalsModule, 'GlobalsDict')

    # Iterate over the ConfigDelta entries, overwriting GlobalsModule and GlobalsDict entries
    for attr, val in ConfigDelta.items():
        try:
            val1 = GlobalsDict[attr]

        except:
            print(f'Error: {attr} is Not a Config variable, skipping')
            pass

        else:
            setattr(GlobalsModule, attr, val)
            GlobalsDict[attr] = val
