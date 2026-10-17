from AppPaths import get_config_value

_cached_lang = None


def get_language():
    """Lit la langue dans le fichier de configuration une seule fois au démarrage."""
    global _cached_lang
    if _cached_lang is not None:
        return _cached_lang

    # Langue par défaut : "fr" (lecture tolérante UTF-8 / cp1252 via AppPaths)
    _cached_lang = get_config_value('language', "fr")
    return _cached_lang