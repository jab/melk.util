from ConfigParser import ConfigParser
import os

__all__ = ['load_pylons_config']

def load_pylons_config(ini_file):
    cfg_parser = ConfigParser()
    cfg_parser.readfp(open(ini_file))

    # XXX this grabs the app:main section, it shouldn't. 
    # would be nice if we could push model config to 
    # more reasonable section name, but how would pylons
    # access it? 
    SECTION = 'app:main'
    
    # convert this strange hunk of trash into something useful-ish
    interp = {'here': os.path.abspath(os.path.dirname(ini_file))}
    config = {}
    for option in cfg_parser.options(SECTION):
        config[option] = cfg_parser.get(SECTION, option, 0, interp)

    return config