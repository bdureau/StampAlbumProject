import configparser
from SCAppPaths import get_config_path

_cached_lang = None


def get_language(force_reload=False):
    """
    Lit la langue dans StampCatalogue.cfg (supporte les sections [General] et [CONF]).
    """
    global _cached_lang
    if _cached_lang is not None and not force_reload:
        return _cached_lang

    config_path = get_config_path()
    lang = "fr"

    if config_path.exists():
        config = configparser.ConfigParser()
        try:
            config.read(config_path, encoding='utf-8')
            if 'General' in config and 'language' in config['General']:
                lang = config['General']['language']
            elif 'CONF' in config and 'language' in config['CONF']:
                lang = config['CONF']['language']
        except Exception:
            pass

    _cached_lang = lang
    return _cached_lang