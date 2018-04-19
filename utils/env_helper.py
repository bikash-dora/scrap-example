from os import environ as env


def check_env(keys: list):
    for key in keys:
        if not env.get(key):
            raise KeyError('Environment variable {} not set'.format(key))
