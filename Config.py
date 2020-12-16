
''' Load Config attrs from a list of Config files and overwrite those in a Globals module '''



from sys import modules



def load_config(GlobalsFile, ConfigFiles=[]):
    ''' Load Config attrs from a list of Config files and overwrite those in a Globals module '''

    # Load the Config files into this module
    ConfigFile = ''
    for ConfigFile in ConfigFiles:
        exec(open(f'./{ConfigFile}').read())

    # Iterate over the loaded attributes and overwrite the Globals value
    ConfigAttrs = locals()
    GlobalsModule = modules[GlobalsFile]

    for attr, val in ConfigAttrs.items():
        try:
            getattr(GlobalsModule, attr)

        except:
            # Not a Config variable, skip
            pass

        else:
            setattr(GlobalsModule, attr, val)
