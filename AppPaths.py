"""
App Paths Module
----------------
Point unique pour les chemins de l'application, la lecture de la
configuration et la liste des bases pays disponibles.

Compatible avec un exécutable PyInstaller/cx_Freeze (sys.frozen).

Author: Boris du Reau
"""
import configparser
import sys
from pathlib import Path

CONFIG_FILE_NAME = "stamp_album.cfg"


def get_app_dir() -> Path:
    """Dossier de l'application (celui du .exe si l'application est compilée)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_config_path() -> Path:
    return get_app_dir() / CONFIG_FILE_NAME


def get_db_dir() -> Path:
    return get_app_dir() / "databases"


def get_photos_dir() -> Path:
    return get_app_dir() / "photos"


def get_images_dir() -> Path:
    return get_app_dir() / "images"


def get_help_dir() -> Path:
    return get_app_dir() / "Help"


CONFIG_ENCODING = "utf-8"


def read_config_into(parser: configparser.RawConfigParser, path: Path = None) -> configparser.RawConfigParser:
    """
    Charge le fichier de configuration dans le parser fourni.

    Le fichier est écrit en UTF-8, mais les anciennes versions l'écrivaient avec
    l'encodage par défaut de Windows (cp1252, où « © » vaut l'octet 0xA9).
    On essaie donc UTF-8, puis cp1252 : les deux formats restent lisibles.
    """
    path = path or get_config_path()
    if not path.exists():
        return parser

    for encoding in (CONFIG_ENCODING, "cp1252"):
        try:
            with open(path, "r", encoding=encoding) as f:
                parser.read_file(f, source=str(path))
            return parser
        except UnicodeDecodeError:
            parser.clear()
    # Dernier recours : ne jamais bloquer le démarrage à cause d'un caractère
    with open(path, "r", encoding=CONFIG_ENCODING, errors="replace") as f:
        parser.read_file(f, source=str(path))
    return parser


def read_config() -> configparser.RawConfigParser:
    """Lit stamp_album.cfg (retourne un parser vide si le fichier n'existe pas)."""
    return read_config_into(configparser.RawConfigParser())


def get_config_value(option: str, default: str = "") -> str:
    """Retourne une option de la section [CONF], ou la valeur par défaut."""
    parser = read_config()
    if parser.has_option('CONF', option):
        return parser.get('CONF', option)
    return default


def get_db_type() -> str:
    """'sqlite' (par défaut) ou 'Access'."""
    return get_config_value("database type", "sqlite")


def get_db_extension(db_type: str = None) -> str:
    """Extension des fichiers de base selon le moteur configuré."""
    db_type = db_type or get_db_type()
    return ".db" if db_type.lower() == "sqlite" else ".mdb"


def list_countries(db_type: str = None) -> list:
    """
    Liste triée des pays disponibles dans le dossier databases/,
    en ne gardant que les fichiers du moteur configuré (.db ou .mdb).
    """
    db_dir = get_db_dir()
    if not db_dir.is_dir():
        return []

    ext = get_db_extension(db_type)
    countries = [
        f.stem for f in db_dir.iterdir()
        if f.is_file() and f.suffix.lower() == ext and f.stem.lower() != "master"
    ]
    return sorted(countries, key=str.lower)
