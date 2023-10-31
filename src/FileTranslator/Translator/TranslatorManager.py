from FileTranslator.Translator.ITranslator import ITranslator
from FileTranslator.Translator.YandexOnlineTranslator import (
    YandexOnlineTranslator,
)
import FileTranslator.Util.Logs as Logs
from FileTranslator.Util.PathInfo import PathInfo
from FileTranslator.Util.TranslateInfo import TranslateInfo

################################################################################


_translator_map = {"yandex": YandexOnlineTranslator()}

################################################################################


def get_translator(
    path_info: PathInfo, translate_info: TranslateInfo
) -> ITranslator:
    alias = translate_info.translator_alias
    if alias not in _translator_map.keys():
        Logs.error(
            "Incorrect translator alias. "
            "Supported ocr and their aliases: "
            f"{_translator_map}"
        )
    translator = _translator_map[alias]
    translator.init(path_info, translate_info)
    Logs.user(f"'{alias}' translator constructed")
    return translator
