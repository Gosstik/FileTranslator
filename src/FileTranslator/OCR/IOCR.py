from PIL import Image

from FileTranslator.Translator.ITranslator import ITranslator
from FileTranslator.Util.PathInfo import PathInfo
from FileTranslator.Util.TranslateInfo import TranslateInfo

################################################################################


class IOCR:
    # Exceptions
    class IncorrectTranslatedTextFormat(Exception):
        pass

    # API
    def init(self, path_info: PathInfo, translate_info: TranslateInfo) -> None:
        raise NotImplementedError

    def get_text_to_translate(self, image: Image, save_context: bool) -> str:
        raise NotImplementedError

    def translated_text_to_image(
        self, text: str, translator: ITranslator
    ) -> Image:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError
