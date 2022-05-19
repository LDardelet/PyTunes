class AutoConfig:
    ConfigKey = ''
    Params = []
    def UpdateParams(self, config):
        '''Updates the instance params configuration from a json dictionnary.
        If the expected values don't exists, populates both the instance and the config dictionnary with given default values.
        '''
        config_keys = []
        found_config = False
        for Class in reversed(self.__class__.mro()):
            if Class != AutoConfig and not found_config:
                continue
            found_config = True
            if Class.ConfigKey:
                config_keys.append(Class.ConfigKey)
            for param, default in Class.Params:
                config_param = '.'.join(config_keys+[param])
                if config_param not in config:
                    value = default
                    config[config_param] = default
                else:
                    value = config[config_param]
                setattr(self, param.upper(), value)
