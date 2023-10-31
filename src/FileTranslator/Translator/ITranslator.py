from FileTranslator.Util.PathInfo import PathInfo
from FileTranslator.Util.TranslateInfo import TranslateInfo

################################################################################


class ITranslator:
    # API
    def init(self, path_info: PathInfo, translate_info: TranslateInfo) -> None:
        raise NotImplementedError

    def translate(self, text: str) -> str:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError

    src_lang: str
    trg_lang: str
