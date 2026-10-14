import configparser
import sys
from pathlib import Path

_cached_lang = None


def get_language():
    """Lit la langue dans le fichier de configuration une seule fois au démarrage."""
    global _cached_lang
    if _cached_lang is not None:
        return _cached_lang

    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parent

    config_path = base_dir / 'stamp_album.cfg'
    lang = "fr"  # Langue par défaut

    if config_path.exists():
        parser = configparser.RawConfigParser()
        parser.read(config_path)
        if parser.has_option('CONF', 'language'):
            lang = parser.get('CONF', 'language')

    _cached_lang = lang
    return _cached_lang